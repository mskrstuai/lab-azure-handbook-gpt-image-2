"""gpt-image-2 API 사용 예제 (openai.OpenAI)

준비:
    pip install openai pillow
    export OPENAI_API_KEY="sk-..."          # 공용 OpenAI
    # 또는 Azure OpenAI:
    # export OPENAI_API_KEY="<azure-key>"
    # export OPENAI_BASE_URL="https://<resource>.openai.azure.com/openai/v1/"

실행 (모든 인자에 default 있음):
    python gpt_image_2.py                                  # generate (기본)
    python gpt_image_2.py generate --prompt "a red car"    # 프롬프트로 생성
    python gpt_image_2.py edit                             # 000122.jpg 편집
    python gpt_image_2.py edit --image my.jpg --mask my-mask.png --prompt "..."
"""

import argparse
import base64

from openai import OpenAI

MODEL = "gpt-image-2"


def get_client() -> OpenAI:
    """OPENAI_API_KEY / OPENAI_BASE_URL 환경변수로 클라이언트 생성 (지연)."""
    return OpenAI()


def save(b64: str, path: str) -> None:
    """base64 응답을 PNG 파일로 저장."""
    with open(path, "wb") as f:
        f.write(base64.b64decode(b64))


def generate(prompt: str, out_path: str = "generated.png") -> str:
    """프롬프트로 이미지 생성."""
    result = get_client().images.generate(
        model=MODEL,
        prompt=prompt,
        size="1024x1024",
    )
    save(result.data[0].b64_json, out_path)
    return out_path


def edit(prompt: str, image_path: str, mask_path: str,
         out_path: str = "edited.png") -> str:
    """마스크 영역만 편집.

    mask_path 는 gpt-image-2 규격의 RGBA PNG여야 한다
    (투명 영역 = 편집 대상). Imagen 3 / Gemini 마스크는
    convert_mask.py 로 먼저 변환할 것.
    """
    with open(image_path, "rb") as image, open(mask_path, "rb") as mask:
        result = get_client().images.edit(
            model=MODEL,
            image=image,
            mask=mask,
            prompt=prompt,
            size="1024x1024",
        )
    save(result.data[0].b64_json, out_path)
    return out_path


def main() -> None:
    parser = argparse.ArgumentParser(description="gpt-image-2 생성/편집")
    parser.add_argument(
        "task", nargs="?", default="generate", choices=["generate", "edit"],
        help="작업 종류 (기본: generate)",
    )
    parser.add_argument(
        "--prompt", default="A cozy reading nook with warm sunlight",
        help="생성/편집 프롬프트",
    )
    parser.add_argument(
        "--image", default="000122.jpg", help="편집할 입력 이미지 (edit)",
    )
    parser.add_argument(
        "--mask", default="000122-mask.png",
        help="Imagen/Gemini 스타일 마스크 (흰색=편집, edit 시 자동 변환)",
    )
    parser.add_argument("--out", default=None, help="출력 경로")
    args = parser.parse_args()

    if args.task == "generate":
        out = generate(args.prompt, args.out or "generated.png")
    else:
        # Imagen/Gemini 마스크를 gpt-image-2 규격(투명=편집)으로 변환 후 편집
        from convert_mask import convert_mask
        gpt_mask = convert_mask(args.mask, "mask-gpt.png")
        out = edit(args.prompt, args.image, gpt_mask, args.out or "edited.png")

    print(f"saved: {out}")


if __name__ == "__main__":
    main()
