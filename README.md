# 🎙️ Voice2Product AI

### Don't type the product. Just speak it.

Built for **AssemblyAI's "Hack into Dictation" Voice Hackathon Week**.

```
🎙️ Speak
      ↓
⚡ AssemblyAI Dictation API
      ↓
📝 Clean Transcript
      ↓
🤖 4 AI Agents  (Discovery → Standardization → Enrichment → Trust)
      ↓
🔍 Evidence
      ↓
🛡️ Trust Score
      ↓
📦 Structured, Traceable Product Intelligence
```

## What it does

Say a product out loud — *"Part number X200, brand ABC Industries, industrial
centrifugal pump"* — and Voice2Product AI turns your voice directly into a
rich, structured, evidence-backed product record. No typing required.

1. **You speak** into the browser mic.
2. **AssemblyAI's Dictation API** (`dictation.assemblyai.com`) transcribes it
   in under a second, with filler words removed and punctuation applied.
3. **Gemini parses** that clean transcript into structured intake fields —
   part number, brand, description — without inventing anything that wasn't
   actually said.
4. Those fields feed straight into an **unmodified 4-agent AI pipeline**
   (Discovery, Standardization, Enrichment, Trust/Validation) that extracts
   specs from any attached datasheet/image, enriches the record with
   RAG-grounded context, and validates every value with a confidence score
   and cited evidence.
5. You get a fully traceable product intelligence record — exportable as
   JSON, or as an industrial-catalog-ready XLSX/CSV.

Manual typing still works too — voice is an additional front door, not a
replacement for the existing input form.

## Why this matters

Dictation is becoming the default input method everywhere. For industrial
commerce specifically, that means a field technician, warehouse worker, or
procurement agent can log a product **hands-free**, on the floor, without
sitting down at a keyboard — and still get the same evidence-first,
validated intelligence record as if they'd typed it all in carefully.

## Architecture

This project is a voice-first front door bolted onto a working, previously
deployed 4-agent product intelligence platform — not a rebuild. The core
agents, RAG enrichment, trust/validation layer, and export pipeline are
unchanged; only the input path is new.

```
agents/                  # unchanged 4-agent pipeline
models/                  # unchanged shared Pydantic state
services/
  ├── voice_service.py   # NEW — AssemblyAI Dictation + Gemini field parsing
  ├── llm_service.py      # Gemini/OpenAI/mock, swappable via .env
  ├── pdf_service.py
  ├── vision_service.py
  ├── rag_service.py
  ├── validation_service.py
  └── export_service.py
app/streamlit_app.py     # voice recorder added to the existing dashboard
orchestrator.py           # unchanged LangGraph workflow
```

## Tech stack

- **Voice:** AssemblyAI Dictation API (`dictation.assemblyai.com/v1/transcribe/live`)
- **AI reasoning:** Google Gemini (swappable via `MODEL_PROVIDER` env var)
- **Orchestration:** LangGraph (4-agent workflow)
- **Document intelligence:** PyMuPDF
- **RAG:** local retrieval over a curated knowledge base
- **Structured data:** Pydantic
- **Frontend:** Streamlit
- **Backend:** FastAPI (existing REST endpoints, unchanged)

## Setup

```bash
python -m venv venv
source venv/bin/activate   # Windows: venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env
```

Fill in `.env`:
```
MODEL_PROVIDER=gemini
GEMINI_API_KEY=your_gemini_key
MODEL_NAME=gemini-flash-latest
ASSEMBLYAI_API_KEY=your_assemblyai_key
```

Run it:
```bash
streamlit run app/streamlit_app.py
```

## Try it

1. Click the microphone recorder in the sidebar.
2. Say something like: *"Part number X200, brand ABC Industries, industrial
   centrifugal pump."*
3. Click **⚡ Transcribe & Fill** — watch the fields populate from your voice.
4. Optionally attach a datasheet PDF or product photo.
5. Click **🚀 Generate Product Intelligence** and watch the 4-agent pipeline
   run, producing specs with page-level evidence, AI-enriched applications,
   a trust score, and flagged items for human review.
6. Export as JSON, or as an industrial-catalog-ready XLSX/CSV.

## Links

- **Live prototype:** _add your deployed Streamlit Cloud URL here_
- **GitHub:** https://github.com/DK-4/voice2product-ai

## Built on

This voice-first experience sits on top of an existing, independently
deployed multi-agent product intelligence platform (originally built for the
UniHack "AI-Powered Product Intelligence for Industrial Commerce" challenge),
adapted here around AssemblyAI's Dictation API as the primary input method.