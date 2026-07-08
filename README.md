# lab-azure-handbook-gpt-image-2

gpt-image-2 이미지 생성/편집과, Imagen 3 · Gemini 마스크를 gpt-image-2 규격으로 변환하는 최소 예제.

## 설치

```bash
pip install -r requirements.txt
```

API 키/엔드포인트는 환경변수 없이 `--api-key`, `--base-url` 인자로 넘긴다. 테스트 이미지 `000122.jpg`(원본), `000122-mask.png`(Imagen 스타일, 흰색=편집) 포함.

## 1. 이미지 생성 · 편집 — `gpt_image_2.py`

```bash
python gpt_image_2.py --api-key sk-...                                    # generate
python gpt_image_2.py generate --api-key sk-... --prompt "a red sports car"
python gpt_image_2.py edit --api-key sk-...                               # 000122.jpg + 000122-mask.png
python gpt_image_2.py edit --api-key sk-... --image my.jpg --mask my-mask.png --prompt "fill naturally"

# Azure OpenAI: --base-url 로 엔드포인트 지정
python gpt_image_2.py --api-key <azure-key> \
    --base-url https://<resource>.openai.azure.com/openai/v1/
```

`edit` 는 넘긴 Imagen/Gemini 마스크를 자동으로 gpt-image-2 규격으로 변환한 뒤 편집한다.

## 2. 마스크 변환 — `convert_mask.py`

마스크 규칙이 서로 다르다.

| API | 편집 대상 영역 | 포맷 |
|-----|----------------|------|
| Imagen 3 / Gemini | **흰색(255)** | grayscale PNG |
| gpt-image-2 | **투명(alpha=0)** | RGBA PNG |

`edit` 전에 변환한다. 단독 실행도 가능하다.

```bash
python convert_mask.py                                  # 000122-mask.png 변환
python convert_mask.py my-mask.png --out my-mask-gpt.png --threshold 128
```

라이브러리로도 사용 가능:

```python
from convert_mask import convert_mask
convert_mask("mask_imagen.png", "mask-gpt.png")   # 흰색=편집 -> 투명=편집
```
