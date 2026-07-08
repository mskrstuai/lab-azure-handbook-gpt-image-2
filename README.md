# lab-azure-handbook-gpt-image-2

OpenAI SDK 로 gpt-image-2 이미지를 생성·편집하고, Imagen 3 / Gemini(GCP) 마스크를 gpt-image-2 규격으로 변환하는 방법을 담은 실습 핸드북입니다.

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
# my-mask-gcp.png -> my-mask-gpt.png 변환
python convert_mask.py my-mask-gcp.jpg --out my-mask-gpt.png --threshold 128
```

## 2. 리사이즈 — `resize_for_gpt.py`

gpt-image-2 는 지원하는 크기 규칙이 있어, 입력 이미지와 마스크를 그 규칙에 맞게 리사이즈한다. `edit` 에 쓰려면 이미지와 마스크가 **같은 크기**여야 한다.

| 규칙 | 값 |
|------|-----|
| 폭 · 높이 | 16 의 배수 |
| 종횡비 | 1:3 ~ 3:1 |
| 총 픽셀 수 | 655,360 ~ 8,294,400 (최대 `3840x2160`) |

`--size WxH` 를 주면 그 크기를 목표로 하되, 규칙에 어긋나면 자동으로 최적화한다 — 너무 작으면 최소 크기로 키우고, 너무 크면 줄이고, 종횡비가 벗어나면 1:3~3:1 로 맞춘 뒤 16 의 배수로 정렬한다. 미지정 시 입력 이미지 크기를 기준으로 최적화한다.

### 인자

| 인자 | 필수 | 기본값 | 설명 |
|------|------|--------|------|
| `--image` | No | `input.jpg` | 입력 이미지 경로 (png/jpg) |
| `--mask` | No | `input-mask-gpt.png` | 입력 마스크 경로 (png/jpg 모두 지원) |
| `--out-image` | No | 입력 이름 + `-resized` | 리사이즈 이미지 저장 경로 |
| `--out-mask` | No | 입력 이름 + `-resized` | 리사이즈 마스크 저장 경로 (확장자 유지) |
| `--size` | No | 입력 이미지 크기 | 목표 크기 `WxH`. 규칙 위반 시 자동 최적화 |

### 실행

```bash
# resize
python resize_for_gpt.py
# 입력 지정 resize
python resize_for_gpt.py --image my.jpg --mask my-mask-gpt.png
# target size 지정 (규칙에 어긋나면 자동 최적화)
python resize_for_gpt.py --size 1536x1024
```

## 3. 이미지 생성 · 편집 - `gpt_image_2.py`

gpt-image-2 을 이용해서 이미지를 생성하고 마스크기반의 편집 API 를 사용한다. 각 호출마다 latency 와 token usage 를 함께 출력한다.

### 인자

| 인자 | 필수 | 기본값 | 설명 |
|------|------|--------|------|
| `task` | No | `generate` | 작업 종류: `generate` 또는 `edit` (위치 인자) |
| `--api-key` | Yes | — | OpenAI/Azure API 키 (환경변수 미사용) |
| `--base-url` | Yes | — | API 엔드포인트 (공용 OpenAI 또는 Azure OpenAI) |
| `--prompt` | No | `generate` - `A cozy reading nook with warm sunlight` <br>`edit` - `remove the object and fill the area to match the surrounding` | 생성/편집 프롬프트 |
| `--image` | No | `input-resized.jpg` | 편집할 입력 이미지 경로 (2번에서 리사이즈한 파일) |
| `--mask` | No | `input-mask-gpt-resized.png` | gpt 마스크 경로, 1번에서 변환한 파일 |
| `--out` | No | `generated.png` / `edited.png` | 출력 이미지 경로 |

출력 크기는 `generate`는 `1024x1024`, `edit`은 입력 이미지 크기를 따른다.

### 실행

```bash
# generate
python gpt_image_2.py --api-key <azure-openai-api-key> --base-url <azure-openai-base-url>
# generate with custom prompt
python gpt_image_2.py generate --api-key <azure-openai-api-key> --base-url <azure-openai-base-url> --prompt "a red sports car"
# edit a image (input.jpg)
python gpt_image_2.py edit --api-key <azure-openai-api-key> --base-url <azure-openai-base-url>
# edit a image with custom prompt
python gpt_image_2.py edit --api-key <azure-openai-api-key> --base-url <azure-openai-base-url> --image my.jpg --mask my-mask-gpt.png --prompt "fill naturally"
```