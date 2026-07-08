"""마스크 변환: Imagen 3 / Gemini  ->  gpt-image-2

마스크 규칙이 서로 다르다:
  - Imagen 3 / Gemini : 흰색(255) 영역 = 편집 대상 (grayscale PNG)
  - gpt-image-2       : 투명(alpha=0) 영역 = 편집 대상 (RGBA PNG)

즉, "흰색 = 편집" 을 "투명 = 편집" 으로 뒤집어 alpha 채널에 넣으면 된다.

준비:
    pip install pillow
"""

from PIL import Image

# 이 값 이상이면 "편집" 영역으로 본다 (이진 마스크의 경계도 안전하게 처리).
THRESHOLD = 128


def convert_mask(src_path: str, out_path: str = "mask_gpt.png") -> str:
    """Imagen/Gemini 마스크(흰=편집)를 gpt-image-2 마스크(투명=편집)로 변환.

    반환: 저장한 RGBA PNG 경로.
    """
    gray = Image.open(src_path).convert("L")

    # 편집 영역이면 alpha=0(투명), 유지 영역이면 alpha=255(불투명).
    alpha = gray.point(lambda v: 0 if v >= THRESHOLD else 255)

    mask = Image.new("RGBA", gray.size, (0, 0, 0, 255))
    mask.putalpha(alpha)
    mask.save(out_path, format="PNG")
    return out_path


if __name__ == "__main__":
    # 테스트 마스크: 000122-mask.png (흰색=편집) -> 000122-mask-gpt.png (투명=편집)
    convert_mask("000122-mask.png", "000122-mask-gpt.png")
