import argparse
import base64
import time

from openai import OpenAI
from PIL import Image


MODEL = "gpt-image-2"
DEFAULT_PROMPTS = {
    "generate": "A cozy reading nook with warm sunlight",
    "edit": "remove the object and fill the area to match the surrounding",
}


def resolve_size(image_path: str) -> str:
    try:
        with Image.open(image_path) as im:
            return f"{im.width}x{im.height}"
    except (FileNotFoundError, OSError):
        return "1024x1024"  # generate 시 입력 이미지를 읽을 수 없을 때의 폴백 크기.


def report_metrics(label: str, result: object, latency_s: float) -> None:
    print(f"[{label}] latency: {latency_s:.2f}s")
    usage = getattr(result, "usage", None)
    if usage is None:
        print(f"[{label}] token usage: (응답에 usage 없음)")
        return
    total = getattr(usage, "total_tokens", "?")
    inp = getattr(usage, "input_tokens", "?")
    out = getattr(usage, "output_tokens", "?")
    print(f"[{label}] tokens: total={total} input={inp} output={out}")


def generate(client: OpenAI, prompt: str, out_path: str, size: str) -> str:
    start = time.perf_counter()
    result = client.images.generate(
        model=MODEL,
        prompt=prompt,
        size=size,
    )
    report_metrics("generate", result, time.perf_counter() - start)

    with open(out_path, "wb") as f:
        f.write(base64.b64decode(result.data[0].b64_json))

    return out_path


def edit(client: OpenAI, prompt: str, image_path: str, mask_path: str,
         out_path: str, size: str) -> str:
    with open(image_path, "rb") as image, open(mask_path, "rb") as mask:
        start = time.perf_counter()
        result = client.images.edit(
            model=MODEL,
            image=image,
            mask=mask,
            prompt=prompt,
            size=size,
        )
        report_metrics("edit", result, time.perf_counter() - start)

    with open(out_path, "wb") as f:
        f.write(base64.b64decode(result.data[0].b64_json))

    return out_path


def main() -> None:
    parser = argparse.ArgumentParser(description="gpt-image-2 생성/편집")
    parser.add_argument(
        "task",
        nargs="?",
        default="generate",
        choices=["generate", "edit"],
        help="작업 종류 (기본: generate)",
    )
    parser.add_argument(
        "--api-key", required=True, help="Azure OpenAI API 키",
    )
    parser.add_argument(
        "--base-url", required=True, help="Azure OpenAI 엔드포인트",
    )
    parser.add_argument(
        "--prompt", default=None, help="생성/편집 프롬프트",
    )
    parser.add_argument(
        "--image", default="input-resized.jpg", help="편집할 입력 이미지 경로",
    )
    parser.add_argument(
        "--mask", default="input-mask-gpt-resized.png", help="gpt 마스크 경로",
    )
    parser.add_argument("--out", default=None, help="출력 경로")
    args = parser.parse_args()

    client = OpenAI(api_key=args.api_key, base_url=args.base_url)
    prompt = args.prompt or DEFAULT_PROMPTS[args.task]
    if args.task == "generate":
        out = generate(client, prompt, args.out or "generated.png", "1024x1024")
    else:
        out = edit(client, prompt, args.image, args.mask,
                   args.out or "edited.png", resolve_size(args.image))

    print(f"saved: {out}")


if __name__ == "__main__":
    main()
