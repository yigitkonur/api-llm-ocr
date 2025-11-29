<h1 align="center">⚡ Swift OCR ⚡</h1>
<h3 align="center">Stop squinting at PDFs. Start extracting clean markdown.</h3>

<p align="center">
  <strong>
    <em>The LLM-powered OCR engine that turns any PDF into beautifully formatted Markdown. It reads your documents like a human, handles messy layouts, and outputs text your AI can actually understand.</em>
  </strong>
</p>

<p align="center">
  <!-- Package Info -->
  <a href="#"><img alt="python" src="https://img.shields.io/badge/python-3.8+-4D87E6.svg?style=flat-square"></a>
  <a href="#"><img alt="fastapi" src="https://img.shields.io/badge/FastAPI-0.100+-4D87E6.svg?style=flat-square"></a>
  &nbsp;&nbsp;•&nbsp;&nbsp;
  <!-- Features -->
  <a href="https://www.gnu.org/licenses/agpl-3.0"><img alt="license" src="https://img.shields.io/badge/License-AGPL_v3-F9A825.svg?style=flat-square"></a>
  <a href="#"><img alt="platform" src="https://img.shields.io/badge/platform-macOS_|_Linux_|_Windows-2ED573.svg?style=flat-square"></a>
</p>

<p align="center">
  <img alt="gpt-4 vision" src="https://img.shields.io/badge/🧠_GPT--4_Vision-powered_by_OpenAI-2ED573.svg?style=for-the-badge">
  <img alt="markdown output" src="https://img.shields.io/badge/📝_markdown_output-tables,_headers,_lists-2ED573.svg?style=for-the-badge">
</p>

<div align="center">

### 🧭 Quick Navigation

[**⚡ Get Started**](#-get-started-in-60-seconds) •
[**✨ Key Features**](#-feature-breakdown-the-secret-sauce) •
[**🎮 Usage & Examples**](#-usage-fire-and-forget) •
[**💰 Cost Breakdown**](#-cost-breakdown-stupidly-cheap) •
[**⚙️ Configuration**](#️-configuration)

</div>

---

**Swift OCR** is the document processor your AI assistant wishes it had. Stop feeding your LLM screenshots and praying it reads them correctly. This tool acts like a professional transcriber, reading every page of your PDF, intelligently handling tables, headers, and mixed layouts, then packaging everything into perfectly structured Markdown so your AI can actually work with it.

<div align="center">
<table>
<tr>
<td align="center">
<h3>🧠</h3>
<b>GPT-4 Vision</b><br/>
<sub>Human-level reading accuracy</sub>
</td>
<td align="center">
<h3>⚡</h3>
<b>Parallel Processing</b><br/>
<sub>Multi-page PDFs in seconds</sub>
</td>
<td align="center">
<h3>📝</h3>
<b>Clean Markdown</b><br/>
<sub>Tables, headers, lists—all formatted</sub>
</td>
</tr>
</table>
</div>

How it slaps:
- **You:** `curl -X POST "http://localhost:8000/ocr" -F "file=@messy_document.pdf"`
- **Swift OCR:** Converts pages → Sends to GPT-4 Vision → Formats as Markdown
- **You:** Get perfectly structured text with tables, headers, and lists intact.
- **Result:** Your AI finally understands that 50-page contract. ☕

---

## 📹 Demo

https://github.com/user-attachments/assets/6b39f3ea-248e-4c29-ac2e-b57de64d5d65

*Demo video showcasing the conversion of NASA's Apollo 17 flight documents—complete with unorganized, horizontally and vertically oriented pages—into well-structured Markdown format without breaking a sweat.*

---

## 💥 Why This Slaps Other Methods

Manually extracting text from PDFs is a vibe-killer. Swift OCR makes traditional OCR look ancient.

<table align="center">
<tr>
<td align="center"><b>❌ The Old Way (Pain)</b></td>
<td align="center"><b>✅ The Swift OCR Way (Glory)</b></td>
</tr>
<tr>
<td>
<ol>
  <li>Run Tesseract. Get garbled text.</li>
  <li>Tables? What tables? Just random words now.</li>
  <li>Manually fix formatting for 2 hours.</li>
  <li>Feed broken context to your AI.</li>
  <li>Get a useless answer. Cry.</li>
</ol>
</td>
<td>
<ol>
  <li>Upload PDF to Swift OCR.</li>
  <li>Get perfectly formatted Markdown.</li>
  <li>Tables intact. Headers preserved.</li>
  <li>Feed clean context to your AI.</li>
  <li>Get genius-level answers. Go grab a coffee. ☕</li>
</ol>
</td>
</tr>
</table>

We're not just running basic OCR. We're using **GPT-4 Vision** to actually *understand* your documents—handling rotated pages, complex tables, mixed layouts, and even describing images for accessibility.

---

## 💰 Cost Breakdown: Stupidly Cheap

Our solution offers an optimal balance of affordability and accuracy that makes enterprise OCR solutions look like highway robbery.

<div align="center">

| Metric | Value |
|:------:|:------|
| **Avg tokens/page** | ~1,500 (including prompt) |
| **GPT-4o input cost** | $5 per million tokens |
| **GPT-4o output cost** | $15 per million tokens |
| **Cost per 1,000 pages** | **~$15** |

</div>

### 💡 Want It Even Cheaper?

| Optimization | Cost per 1,000 pages |
|:------------:|:--------------------:|
| **GPT-4o (default)** | ~$15 |
| **GPT-4o mini** | ~$8 |
| **Batch API** | ~$4 |

### 🆚 Market Comparison

<div align="center">

| Solution | Cost per 1,000 pages | Tables? | Markdown? |
|:--------:|:-------------------:|:-------:|:---------:|
| **Swift OCR** | **$15** | ✅ Perfect | ✅ Native |
| CloudConvert (PDFTron) | ~$30 | ⚠️ Basic | ❌ No |
| Adobe Acrobat API | ~$50+ | ✅ Good | ❌ No |
| Tesseract (free) | $0 | ❌ Broken | ❌ No |

</div>

> **Bottom line:** Half the cost of competitors, 10x the quality. It's not just about being cheaper—it's about getting output you can actually use.

---

## 🚀 Get Started in 60 Seconds

### Prerequisites

- **Python 3.8+**
- **Azure OpenAI** account (with GPT-4 Vision deployment)

### Installation

```bash
# Clone the repo
git clone https://github.com/yigitkonur/swift-ocr-llm-powered-pdf-to-markdown.git
cd swift-ocr-llm-powered-pdf-to-markdown

# Create virtual environment (recommended)
python3 -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### Configure Environment

Create a `.env` file in the root directory:

```env
# Required
OPENAI_API_KEY=your_openai_api_key
AZURE_OPENAI_ENDPOINT=https://your-resource.openai.azure.com/
OPENAI_DEPLOYMENT_ID=your_gpt4_vision_deployment

# Optional (sensible defaults)
OPENAI_API_VERSION=gpt-4o
BATCH_SIZE=1                        # Images per OCR request (1-10)
MAX_CONCURRENT_OCR_REQUESTS=5       # Parallel OCR calls
MAX_CONCURRENT_PDF_CONVERSION=4     # Parallel page rendering
```

### Run It

```bash
uvicorn main:app --reload
```

🎉 **API is now live at `http://127.0.0.1:8000`**

> **✨ Pro tip:** Check out the auto-generated docs at `http://127.0.0.1:8000/docs`

---

## 🎮 Usage: Fire and Forget

### API Endpoint

**POST** `/ocr`

Accept a PDF file upload OR a URL to a PDF. Returns beautifully formatted Markdown.

### Examples

**Upload a PDF file:**

```bash
curl -X POST "http://127.0.0.1:8000/ocr" \
  -F "file=@/path/to/your/document.pdf"
```

**Process a PDF from URL:**

```bash
curl -X POST "http://127.0.0.1:8000/ocr" \
  -H "Content-Type: application/json" \
  -d '{"url": "https://example.com/document.pdf"}'
```

### Response

```json
{
  "text": "# Document Title\n\n## Section 1\n\nExtracted text with **formatting** preserved...\n\n| Column 1 | Column 2 |\n|----------|----------|\n| Data     | Data     |"
}
```

### Error Codes

| Code | Meaning |
|:----:|:--------|
| `200` | Success—Markdown text returned |
| `400` | Bad request (no file/URL, or both provided) |
| `422` | Validation error |
| `429` | Rate limited—retry with backoff |
| `500` | Processing error |
| `504` | Timeout downloading PDF |

---

## ✨ Feature Breakdown: The Secret Sauce

<div align="center">

| Feature | What It Does | Why You Care |
| :---: | :--- | :--- |
| **🧠 GPT-4 Vision**<br/>`Human-level OCR` | Uses OpenAI's most capable vision model to read documents | Actually understands context, not just character shapes |
| **⚡ Parallel Processing**<br/>`Multiprocessing + async` | Converts PDF pages and calls OCR in parallel | 50-page PDF in seconds, not minutes |
| **📊 Table Preservation**<br/>`Markdown tables` | Detects and formats tables as proper Markdown | Your data stays structured, not flattened to gibberish |
| **🔄 Smart Batching**<br/>`Configurable batch size` | Groups pages to optimize API calls vs accuracy | Balance speed and cost for your use case |
| **🛡️ Retry with Backoff**<br/>`Exponential backoff` | Automatically retries on rate limits and timeouts | Handles API hiccups without crashing |
| **📄 Flexible Input**<br/>`File upload or URL` | Accept PDFs directly or fetch from any URL | Works with your existing workflow |
| **🖼️ Image Descriptions**<br/>`Accessibility-friendly` | Describes non-text elements: `[Image: description]` | Context your AI can actually use |

</div>

---

## ⚙️ Configuration

All settings are managed via environment variables. Tune these for your workload:

<div align="center">

| Variable | Default | Description |
|:---------|:-------:|:------------|
| `OPENAI_API_KEY` | — | Your Azure OpenAI API key |
| `AZURE_OPENAI_ENDPOINT` | — | Your Azure OpenAI endpoint URL |
| `OPENAI_DEPLOYMENT_ID` | — | Your GPT-4 Vision deployment ID |
| `OPENAI_API_VERSION` | `gpt-4o` | API version |
| `BATCH_SIZE` | `1` | Pages per OCR request (1-10). Higher = faster but less accurate |
| `MAX_CONCURRENT_OCR_REQUESTS` | `5` | Parallel OCR calls. Increase for throughput |
| `MAX_CONCURRENT_PDF_CONVERSION` | `4` | Parallel page renders. Match your CPU cores |

</div>

### Performance Tuning Tips

- **High accuracy, slower:** `BATCH_SIZE=1`
- **Balanced:** `BATCH_SIZE=5`, `MAX_CONCURRENT_OCR_REQUESTS=10`
- **Maximum throughput:** `BATCH_SIZE=10`, `MAX_CONCURRENT_OCR_REQUESTS=20` (watch rate limits!)

---

## 🔥 Common Issues & Quick Fixes

<details>
<summary><b>Expand for troubleshooting tips</b></summary>

| Problem | Solution |
| :--- | :--- |
| **"Missing required environment variables"** | Check your `.env` file has all three required variables: `OPENAI_API_KEY`, `AZURE_OPENAI_ENDPOINT`, `OPENAI_DEPLOYMENT_ID` |
| **Rate limit errors (429)** | Reduce `MAX_CONCURRENT_OCR_REQUESTS` or `BATCH_SIZE`. The retry logic will handle temporary limits automatically. |
| **Timeout errors** | Large PDFs take time. The system has exponential backoff built in—give it a moment. |
| **Garbled output** | Make sure your PDF isn't password-protected or corrupted. Try opening it locally first. |
| **Tables not formatting correctly** | Some extremely complex tables may need `BATCH_SIZE=1` for best accuracy. |
| **"Failed to initialize OpenAI client"** | Verify your Azure endpoint URL format: `https://your-resource.openai.azure.com/` |

</details>

---

## 📜 License

This project uses **PyMuPDF** for PDF processing, which requires the **GNU AGPL v3.0** license.

> **Want MIT instead?** Fork this project and swap PyMuPDF for `pdf2image` + Poppler. The rest of the code is yours to use freely.

```
GNU AFFERO GENERAL PUBLIC LICENSE
Version 3, 19 November 2007

Copyright (C) 2024 Yiğit Konur
```

See [LICENSE.md](LICENSE.md) for the full license text.

---

<div align="center">

**Built with 🔥 because manually transcribing PDFs is a soul-crushing waste of time.**

[Report Bug](https://github.com/yigitkonur/swift-ocr-llm-powered-pdf-to-markdown/issues) •
[Request Feature](https://github.com/yigitkonur/swift-ocr-llm-powered-pdf-to-markdown/issues)

</div>
