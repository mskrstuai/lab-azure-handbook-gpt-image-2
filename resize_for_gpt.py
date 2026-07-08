import argparse
from pathlib import Path

from PIL import Image


MIN_PIXELS = 655_360      # 최소 (예: 1024x640)
MAX_PIXELS = 8_294_400    # 최대 (예: 3840x2160, 4K)
MULTIPLE = 16             # 폭/높이는 16 의 배수
MIN_RATIO = 1 / 3         # 종횡비 하한 (세로로 긴 한계)
MAX_RATIO = 3.0           # 종횡비 상한 (가로로 긴 한계)


def parse_size(text):
    try:
        width, height = text.lower().split("x")
        return int(width), int(height)
    except (ValueError, AttributeError):
        raise ValueError(f"size 는 'WxH' 형식이어야 합니다 (받은 값: {text!r})")


def optimal_size(width, height):
    """(width, height) 를 gpt-image-2 규칙에 맞는 (w, h) 로 최적화한다.

    종횡비를 1:3~3:1 로 클램프하고, 총 픽셀 수를 허용 범위로 스케일한 뒤,
    폭/높이를 16 의 배수로 맞춘다.
    """
    w, h = float(width), float(height)

    # 1) 종횡비 클램프
    if w / h > MAX_RATIO:
        w = h * MAX_RATIO
    elif w / h < MIN_RATIO:
        h = w / MIN_RATIO

    # 2) 총 픽셀 수를 허용 범위로 스케일 (종횡비 유지)
    pixels = w * h
    if pixels > MAX_PIXELS:
        factor = (MAX_PIXELS / pixels) ** 0.5
        w, h = w * factor, h * factor
    elif pixels < MIN_PIXELS:
        factor = (MIN_PIXELS / pixels) ** 0.5
        w, h = w * factor, h * factor

    # 3) 16 의 배수로 내림 (내림이므로 상한을 넘지 않음)
    w = max(MULTIPLE, int(w // MULTIPLE) * MULTIPLE)
    h = max(MULTIPLE, int(h // MULTIPLE) * MULTIPLE)

    # 4) 내림으로 하한을 밑돌면 짧은 쪽을 키워 보정
    while w * h < MIN_PIXELS:
        if w <= h:
            w += MULTIPLE
        else:
            h += MULTIPLE

    return w, h


def resized_path(path):
    p = Path(path)
    return str(p.with_name(f"{p.stem}-resized{p.suffix}"))


def resize_image(src_path, out_path, size, resample):
    with Image.open(src_path) as im:
        im.resize(size, resample=resample).save(out_path)
    return out_path


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="이미지/마스크를 gpt-image-2 지원 size 로 리사이즈",
    )
    parser.add_argument(
        "--image", default="input.jpg", help="입력 이미지 경로",
    )
    parser.add_argument(
        "--mask", default="input-mask-gpt.png", help="입력 마스크 경로",
    )
    parser.add_argument(
        "--out-image", default=None,
        help="리사이즈 이미지 저장 경로 (기본: 입력 이름 + '-resized')",
    )
    parser.add_argument(
        "--out-mask", default=None,
        help="리사이즈 마스크 저장 경로 (기본: 입력 이름 + '-resized')",
    )
    parser.add_argument(
        "--size", default=None,
        help="목표 크기 WxH. 규칙에 어긋나면 최적화됨. 미지정 시 이미지 크기 기준",
    )
    args = parser.parse_args()

    if args.size:
        target_w, target_h = parse_size(args.size)
    else:
        with Image.open(args.image) as im:
            target_w, target_h = im.width, im.height
    size = optimal_size(target_w, target_h)
    print(f"target size: {size[0]}x{size[1]} ({size[0] * size[1]:,}px)")

    out_image = args.out_image or resized_path(args.image)
    out_mask = args.out_mask or resized_path(args.mask)
    # 이미지는 부드럽게(LANCZOS), 마스크는 경계 보존(NEAREST) 으로 리사이즈
    print("saved:", resize_image(args.image, out_image, size, Image.LANCZOS))
    print("saved:", resize_image(args.mask, out_mask, size, Image.NEAREST))
