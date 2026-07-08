# lab-azure-handbook-gpt-image-2

gpt-image-2 이미지 생성/편집과, Imagen 3 · Gemini 마스크를 gpt-image-2 규격으로 변환하는 최소 예제.

## 설치

```bash
pip install openai pillow
export OPENAI_API_KEY="sk-..."
# Azure OpenAI 사용 시:
# export OPENAI_BASE_URL="https://<resource>.openai.azure.com/openai/v1/"
```

## 1. 이미지 생성 · 편집 — `gpt_image_2.py`

```python
from gpt_image_2 import generate, edit

generate("A cozy reading nook with warm sunlight")          # -> generated.png
edit("Replace the sky with a starry night",
     "generated.png", "mask_gpt.png")                        # -> edited.png
```

## 2. 마스크 변환 — `convert_mask.py`

마스크 규칙이 서로 다르다.

| API | 편집 대상 영역 | 포맷 |
|-----|----------------|------|
| Imagen 3 / Gemini | **흰색(255)** | grayscale PNG |
| gpt-image-2 | **투명(alpha=0)** | RGBA PNG |

Imagen/Gemini 마스크를 gpt-image-2 `edit`에 넣기 전에 변환한다.

```python
from convert_mask import convert_mask

convert_mask("mask_imagen.png", "mask_gpt.png")   # 흰색=편집 -> 투명=편집
```

## 테스트 이미지로 바로 실행

`000122.jpg`(원본) 과 `000122-mask.png`(Imagen 스타일, 흰색=편집) 포함.

```bash
python gpt_image_2.py
# 1) 000122-mask.png -> 000122-mask-gpt.png (마스크 변환)
# 2) 000122.jpg + 변환 마스크 -> 000122-edited.png (편집)
```
