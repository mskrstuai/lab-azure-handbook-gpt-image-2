"""gpt-image-2 API 사용 예제 (openai.OpenAI)

준비:
    pip install openai pillow

API 키/엔드포인트는 환경변수 없이 인자로 직접 넘긴다 (--api-key, --base-url 필수):
    python gpt_image_2.py --api-key sk-... --base-url https://api.openai.com/v1/
    python gpt_image_2.py generate --api-key sk-... --base-url <url> --prompt "a red car"
    # edit 의 --mask 는 gpt-image-2 마스크(투명=편집). Imagen/Gemini 마스크는
    # convert_mask.py 로 먼저 변환한다:
    python convert_mask.py input-mask.png --out input-mask-gpt.png
    python gpt_image_2.py edit --api-key sk-... --base-url <url> \\
        --image my.jpg --mask input-mask-gpt.png
    # Azure OpenAI:
    python gpt_image_2.py --api-key <azure-key> \\
        --base-url https://<resource>.openai.azure.com/openai/v1/
"""

import argparse
import base64

from openai import OpenAI

MODEL = "gpt-image-2"


def get_client(api_key: str, base_url: str | None = None) -> OpenAI:
    """인자로 받은 키/엔드포인트로 클라이언트 생성 (환경변수 미사용).

    base_url 을 주면 Azure OpenAI 등 커스텀 엔드포인트로 향한다.
    """
    return OpenAI(api_key=api_key, base_url=base_url)


def save(b64: str, path: str) -> None:
    """base64 응답을 PNG 파일로 저장."""
    with open(path, "wb") as f:
        f.write(base64.b64decode(b64))


def generate(client: OpenAI, prompt: str,
             out_path: str = "generated.png") -> str:
    """프롬프트로 이미지 생성."""
    result = client.images.generate(
        model=MODEL,
        prompt=prompt,
        size="1024x1024",
    )
    save(result.data[0].b64_json, out_path)
    return out_path


def edit(client: OpenAI, prompt: str, image_path: str, mask_path: str,
         out_path: str = "edited.png") -> str:
    """마스크 영역만 편집.

    mask_path 는 gpt-image-2 규격의 RGBA PNG여야 한다
    (투명 영역 = 편집 대상). Imagen 3 / Gemini 마스크는
    convert_mask.py 로 먼저 변환할 것.
    """
    with open(image_path, "rb") as image, open(mask_path, "rb") as mask:
        result = client.images.edit(
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
        "--image", default="input.jpg", help="편집할 입력 이미지 (edit)",
    )
    parser.add_argument(
        "--mask", default="input-mask-gpt.png",
        help="gpt-image-2 마스크 (투명=편집). convert_mask.py 로 변환한 파일",
    )
    parser.add_argument("--out", default=None, help="출력 경로")
    parser.add_argument(
        "--api-key", required=True, help="OpenAI/Azure API 키 (환경변수 미사용)",
    )
    parser.add_argument(
        "--base-url", required=True,
        help="API 엔드포인트 (공용 OpenAI 또는 Azure OpenAI)",
    )
    args = parser.parse_args()

    client = get_client(args.api_key, args.base_url)

    if args.task == "generate":
        out = generate(client, args.prompt, args.out or "generated.png")
    else:
        # --mask 는 이미 gpt-image-2 규격(투명=편집)이어야 한다.
        # Imagen/Gemini 마스크라면 convert_mask.py 로 먼저 변환할 것.
        out = edit(client, args.prompt, args.image, args.mask,
                   args.out or "edited.png")

    print(f"saved: {out}")


if __name__ == "__main__":
    main()
