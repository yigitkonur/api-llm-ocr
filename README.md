LLM-powered PDF to markdown. uses vision models to actually read your documents — tables, headers, mixed layouts — and outputs clean, structured markdown. not traditional OCR.

```bash
curl -X POST "http://localhost:8000/ocr" -F "file=@document.pdf"
```

[![python](https://img.shields.io/badge/python-3.8+-93450a.svg?style=flat-square)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.100+-93450a.svg?style=flat-square)](https://fastapi.tiangolo.com/)
[![license](https://img.shields.io/badge/license-AGPL_v3-grey.svg?style=flat-square)](https://www.gnu.org/licenses/agpl-3.0)

---

## demo

https://github.com/user-attachments/assets/6b39f3ea-248e-4c29-ac2e-b57de64d5d65

NASA Apollo 17 flight docs — mixed orientations, messy layouts — converted to structured markdown.

---

## what it does

- **vision model OCR** — understands context, not just character shapes
- **parallel processing** — 50-page PDF in seconds, not minutes
- **table preservation** — detected and formatted as proper markdown tables
- **smart batching** — configurable pages-per-request for speed vs accuracy tradeoff
- **retry with backoff** — handles rate limits and timeouts without crashing
- **flexible input** — file upload or URL, your choice
- **image descriptions** — non-text elements get `[Image: description]` annotations

## cost

using OpenAI as an example (~1,500 tokens/page average):

| model | cost per 1,000 pages |
|:---|:---|
| GPT-4o | ~$15 |
| GPT-4o mini | ~$8 |
| batch API | ~$4 |

works with any OpenAI-compatible vision API. swap the endpoint and model in config.

## install

```bash
git clone https://github.com/yigitkonur/swift-ocr-llm-powered-pdf-to-markdown.git
cd swift-ocr-llm-powered-pdf-to-markdown

python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### configure

create a `.env` file:

```env
# required
OPENAI_API_KEY=your_api_key
AZURE_OPENAI_ENDPOINT=https://your-resource.openai.azure.com/
OPENAI_DEPLOYMENT_ID=your_vision_model_deployment

# optional
OPENAI_API_VERSION=gpt-4o
BATCH_SIZE=1
MAX_CONCURRENT_OCR_REQUESTS=5
MAX_CONCURRENT_PDF_CONVERSION=4
```

### run

```bash
# pick one
uvicorn main:app --reload
uvicorn swift_ocr.app:app --reload
python -m swift_ocr
python -m swift_ocr --host 0.0.0.0 --port 8080 --workers 4
```

API lives at `http://127.0.0.1:8000`. auto-generated docs at `/docs`.

## usage

### upload a file

```bash
curl -X POST "http://127.0.0.1:8000/ocr" \
  -F "file=@/path/to/document.pdf"
```

### process from URL

```bash
curl -X POST "http://127.0.0.1:8000/ocr" \
  -H "Content-Type: application/json" \
  -d '{"url": "https://example.com/document.pdf"}'
```

### response

```json
{
  "text": "# document title\n\n## section 1\n\nextracted text...",
  "status": "success",
  "pages_processed": 5,
  "processing_time_ms": 1234
}
```

### health check

```bash
curl http://127.0.0.1:8000/health
```

### error codes

| code | meaning |
|:---|:---|
| `200` | success |
| `400` | bad request (no file/URL, or both provided) |
| `422` | validation error |
| `429` | rate limited — retry with backoff |
| `500` | processing error |
| `504` | timeout downloading PDF |

## configuration

| variable | default | description |
|:---|:---|:---|
| `OPENAI_API_KEY` | — | API key |
| `AZURE_OPENAI_ENDPOINT` | — | endpoint URL |
| `OPENAI_DEPLOYMENT_ID` | — | vision model deployment ID |
| `OPENAI_API_VERSION` | `gpt-4o` | API version |
| `BATCH_SIZE` | `1` | pages per OCR request (1-10). higher = faster, less accurate |
| `MAX_CONCURRENT_OCR_REQUESTS` | `5` | parallel OCR calls |
| `MAX_CONCURRENT_PDF_CONVERSION` | `4` | parallel page renders. match your CPU cores |

### tuning

- **high accuracy:** `BATCH_SIZE=1`
- **balanced:** `BATCH_SIZE=5`, `MAX_CONCURRENT_OCR_REQUESTS=10`
- **max throughput:** `BATCH_SIZE=10`, `MAX_CONCURRENT_OCR_REQUESTS=20` (watch rate limits)

## project structure

```
swift_ocr/
  __init__.py           — package init
  __main__.py           — CLI entry point
  app.py                — FastAPI app factory
  config/
    settings.py         — pydantic settings (type-safe config)
  core/
    exceptions.py       — custom exception hierarchy
    logging.py          — structured logging
    retry.py            — exponential backoff
  schemas/
    ocr.py              — pydantic request/response models
  services/
    ocr.py              — vision model OCR service
    pdf.py              — PDF conversion service
  api/
    deps.py             — dependency injection
    exceptions.py       — FastAPI exception handlers
    router.py           — route aggregation
    routes/
      health.py         — health check endpoints
      ocr.py            — OCR endpoints
```

## troubleshooting

| problem | fix |
|:---|:---|
| missing env vars | check `.env` has `OPENAI_API_KEY`, `AZURE_OPENAI_ENDPOINT`, `OPENAI_DEPLOYMENT_ID` |
| 429 rate limits | reduce `MAX_CONCURRENT_OCR_REQUESTS` or `BATCH_SIZE` |
| timeout errors | large PDFs take time — backoff is built in |
| garbled output | make sure your PDF isn't password-protected or corrupted |
| tables misformatted | try `BATCH_SIZE=1` for complex tables |
| failed to init client | verify endpoint format: `https://your-resource.openai.azure.com/` |

## license

AGPL v3 — required by PyMuPDF dependency.

if you want MIT, swap PyMuPDF for `pdf2image` + Poppler. the rest of the code is yours.
