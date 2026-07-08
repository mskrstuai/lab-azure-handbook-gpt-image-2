# lab-azure-handbook-gpt-image-2

gpt-image-2 를 사용하는 방법을 가이드합니다.

## 설치

```bash
pip install -r requirements.txt
```

## 1. 마스크 변환 — `convert_mask.py`

Imagen/Gemini 마스크를 gpt-image-2 마스크 규격에 맞춰 변환한다.

| API | 편집 대상 영역 | 포맷 |
|-----|----------------|------|
| Imagen 3 / Gemini | **흰색(255)** | grayscale PNG |
| gpt-image-2 | **투명(alpha=0)** | RGBA PNG |

`edit` 에 넣을 마스크는 gpt-image-2 규격이어야 하므로 Imagen/Gemini 마스크를 먼저 변환한다.

### 인자

| 인자 | 필수 | 기본값 | 설명 |
|------|------|--------|------|
| `src` | No | `input-mask-gcp.png` | 입력 Imagen/Gemini 마스크 경로 (png/jpg 모두 가능) |
| `--out` | No | `input-mask-gpt.png` | 출력 gpt 마스크 경로 (항상 png) |
| `--threshold` | No | `128` | 편집 영역 판정 임계값 (0-255) |

### 실행

```bash
# input-mask-gcp.png -> input-mask-gpt.png 변환
python convert_mask.py
# jpg 마스크도 그대로 gpt png 마스크로 변환됨
python convert_mask.py my-mask-gcp.jpg --out my-mask-gpt.png --threshold 128
```

## 2. `gpt_image_2.py` - 이미지 생성 · 편집

```bash
python gpt_image_2.py --api-key sk-... --base-url https://api.openai.com/v1/          # generate
python gpt_image_2.py generate --api-key sk-... --base-url <url> --prompt "a red sports car"
python gpt_image_2.py edit --api-key sk-... --base-url <url>                          # input.jpg + input-mask-gpt.png
python gpt_image_2.py edit --api-key sk-... --base-url <url> --image my.jpg --mask my-mask-gpt.png --prompt "fill naturally"

# Azure OpenAI: --base-url 에 Azure 엔드포인트 지정
python gpt_image_2.py --api-key <azure-key> \
    --base-url https://<resource>.openai.azure.com/openai/v1/
```

`edit` 의 `--mask` 는 1번에서 변환한 gpt-image-2 마스크(투명=편집)를 준다.

### 인자

| 인자 | 필수 | 기본값 | 설명 |
|------|------|--------|------|
| `task` | No | `generate` | 작업 종류: `generate` 또는 `edit` (위치 인자) |
| `--api-key` | Yes | — | OpenAI/Azure API 키 (환경변수 미사용) |
| `--base-url` | Yes | — | API 엔드포인트 (공용 OpenAI 또는 Azure OpenAI) |
| `--prompt` | No | `A cozy reading nook with warm sunlight` | 생성/편집 프롬프트 |
| `--image` | No | `input.jpg` | 편집할 입력 이미지 (`edit`) |
| `--mask` | No | `input-mask-gpt.png` | gpt-image-2 마스크(투명=편집), 1번에서 변환한 파일 |
| `--out` | No | `generated.png` / `edited.png` | 출력 경로 |
