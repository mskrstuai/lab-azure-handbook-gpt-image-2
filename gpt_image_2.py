"""gpt-image-2 API 사용 예제 (openai.OpenAI)

준비:
    pip install openai
    export OPENAI_API_KEY="sk-..."          # 공용 OpenAI
    # 또는 Azure OpenAI:
    # export OPENAI_API_KEY="<azure-key>"
    # export OPENAI_BASE_URL="https://<resource>.openai.azure.com/openai/v1/"
"""

import base64

from openai import OpenAI

client = OpenAI()  # OPENAI_API_KEY / OPENAI_BASE_URL 환경변수 사용

MODEL = "gpt-image-2"


def save(b64: str, path: str) -> None:
    """base64 응답을 PNG 파일로 저장."""
    with open(path, "wb") as f:
        f.write(base64.b64decode(b64))


def generate(prompt: str, out_path: str = "generated.png") -> str:
    """프롬프트로 이미지 생성."""
    result = client.images.generate(
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
        result = client.images.edit(
            model=MODEL,
            image=image,
            mask=mask,
            prompt=prompt,
            size="1024x1024",
        )
    save(result.data[0].b64_json, out_path)
    return out_path


if __name__ == "__main__":
    # 테스트 이미지: 000122.jpg + 000122-mask.png
    # 1) Imagen/Gemini 마스크를 gpt-image-2 규격으로 변환
    from convert_mask import convert_mask
    convert_mask("000122-mask.png", "000122-mask-gpt.png")
    # 2) 변환한 마스크로 편집
    edit("Fill the masked area naturally",
         "000122.jpg", "000122-mask-gpt.png", "000122-edited.png")
