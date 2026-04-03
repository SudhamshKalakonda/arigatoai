# ArigatoAI — AI Tax Assistant for CA Firms

> A 24/7 AI-powered chatbot that answers client tax and compliance questions instantly. Built with RAG pipeline, deployed on Render + Vercel.

![ArigatoAI Demo](https://arigatoai-six.vercel.app/chat)

## Live Demo

- **Chat:** https://arigatoai-six.vercel.app/chat
- **Admin:** https://arigatoai-six.vercel.app
- **API:** https://arigatoai-backend.onrender.com/docs

---

## The Problem

CA firms receive the same tax questions hundreds of times daily.
Staff wastes hours answering repetitive queries about ITR deadlines,
GST rates, TDS rules, and EPF compliance instead of focusing on
actual CA work.

## The Solution

ArigatoAI is an AI assistant that:

- Scrapes 6 Indian government tax portals automatically
- Indexes all content in Pinecone vector database
- Answers questions instantly using RAG + Groq Llama 3.3 70B
- Updates its knowledge base every Monday automatically
- Embeds on any website with a single line of code

---

## Tech Stack

| Layer       | Technology                          |
| ----------- | ----------------------------------- |
| Backend     | Python, FastAPI                     |
| Frontend    | Next.js, TypeScript, Tailwind CSS   |
| Vector DB   | Pinecone                            |
| Embeddings  | OpenAI text-embedding-3-small       |
| LLM         | Groq (Llama 3.3 70B)                |
| Scraping    | Scrapy                              |
| PDF Parsing | PyMuPDF, pdfplumber                 |
| Scheduler   | APScheduler                         |
| Deployment  | Render (backend), Vercel (frontend) |

---

## Architecture

```
Client Question
      ↓
OpenAI Embeddings
      ↓
Pinecone Vector Search (top 5 chunks)
      ↓
Groq Llama 3.3 70B (answer generation)
      ↓
Response with sources + confidence score
```

---

## Features

- **RAG Pipeline** — semantic search over 2500+ indexed chunks
- **PDF Upload** — upload any tax document, indexed instantly
- **Embeddable Widget** — one line script tag for any website
- **Admin Dashboard** — manage documents, view conversations
- **Auto Updates** — re-scrapes government portals every Monday
- **Dedicated Chat Page** — for internal team use

---

## Getting Started

### Prerequisites

- Python 3.11+
- Node.js 18+
- Pinecone account
- OpenAI API key
- Groq API key

### Backend Setup

```bash
git clone https://github.com/SudhamshKalakonda/arigatoai
cd arigatoai/backend

# Create virtual environment
conda create -n arigatoai python=3.11
conda activate arigatoai

# Install dependencies
pip install -r requirements.txt

# Set environment variables
cp .env.example .env
# Add your API keys to .env

# Run the server
PYTHONPATH=. uvicorn api.main:app --reload --port 8000
```

### Dashboard Setup

```bash
cd arigatoai/dashboard
npm install
npm run dev
```

### Environment Variables

```env
OPENAI_API_KEY=sk-...
PINECONE_API_KEY=pcsk-...
PINECONE_INDEX_NAME=arigato-chatbot
GROQ_API_KEY=gsk-...
```

### Embed on any website

```html
<script src="https://arigatoai-backend.onrender.com/widget.js?key=arigato"></script>
```

---

## Project Structure

```
arigatoai/
├── backend/
│   ├── api/
│   │   ├── main.py          # FastAPI app
│   │   ├── rag.py           # RAG pipeline
│   │   └── routes/
│   │       └── ask.py       # API endpoints
│   └── pipeline/
│       ├── embedder.py      # OpenAI embeddings
│       ├── chunker.py       # Text chunking
│       ├── pinecone_client.py # Vector DB
│       ├── pdf_parser.py    # PDF processing
│       ├── scheduler.py     # Auto updates
│       └── spiders/         # Scrapy spiders
├── dashboard/               # Next.js admin
└── widget/                  # Embeddable widget
```

---

## Built By

**Sudhamsh Kalakonda**

- GitHub: [@SudhamshKalakonda](https://github.com/SudhamshKalakonda)
- LinkedIn: [Add your LinkedIn]

Built for Arigato Consultancy Services Pvt. Ltd., Hyderabad.

---

## License

MIT
# Logo updated
