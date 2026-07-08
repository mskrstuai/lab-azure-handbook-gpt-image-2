import argparse

from PIL import Image


THRESHOLD = 128 # 이 값 이상이면 "편집" 영역으로 본다 (이진 마스크의 경계도 안전하게 처리)


def convert_mask(src_path: str, out_path: str, threshold: int) -> str:
    gray = Image.open(src_path).convert("L")

    # 편집 영역이면 alpha=0(투명), 유지 영역이면 alpha=255(불투명)
    alpha = gray.point(lambda v: 0 if v >= threshold else 255)

    mask = Image.new("RGBA", gray.size, (0, 0, 0, 255))
    mask.putalpha(alpha)
    mask.save(out_path, format="PNG")
    return out_path


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Imagen3/Gemini 마스크 -> gpt-image-2 마스크 변환",
    )
    parser.add_argument(
        "src",
        nargs="?",
        default="input-mask-gcp.png",
        help="입력 Imagen/Gemini 마스크 파일 경로. 기본: input-mask-gcp.png",
    )
    parser.add_argument(
        "--out",
        default="input-mask-gpt.png",
        help="출력 gpt-image-2 마스크 파일 경로",
    )
    parser.add_argument(
        "--threshold",
        type=int,
        default=THRESHOLD,
        help=f"편집 영역 판정 임계값 0-255 (기본: {THRESHOLD})",
    )
    args = parser.parse_args()

    out = convert_mask(args.src, args.out, args.threshold)
    print(f"saved: {out}")
