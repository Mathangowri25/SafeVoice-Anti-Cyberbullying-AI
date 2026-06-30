# SafeVoice — Multilingual Anti-Cyberbullying AI

SafeVoice is an AI-powered platform that detects cyberbullying, harassment, and toxic content in real time across social media and chat platforms — with full support for **Tamil**, **Hindi**, and **English**, including code-switched and mixed-language text.

37% of young people experience cyberbullying, yet most moderation tools fail to catch regional-language abuse. SafeVoice closes that gap with a fine-tuned multilingual transformer model, a real-time classification API, and dashboards for guardians and moderators.

## Features

- Multilingual toxicity detection — Tamil, Hindi, English, and mixed/code-switched text
- Severity classification across four levels: safe, mild toxic, hate speech, severe
- Real-time REST API built with FastAPI
- Guardian dashboard with live incident feed and severity breakdown
- Moderator panel with bulk review and CSV export
- Automated email alerts when severity crosses a configurable threshold
- Data pipeline covering YouTube, Instagram, WhatsApp, and Telegram

## Tech stack

**AI / ML**
MuRIL (`google/muril-base-cased`), PyTorch, HuggingFace Transformers, Scikit-learn

**Backend**
Python, FastAPI, PostgreSQL, SQLAlchemy, Redis

**Frontend**
React, Tailwind CSS, Vite

**Data collection**
youtube-comment-downloader, Instaloader, Telethon, WhatsApp chat export

## Architecture

```
Data sources (YouTube, Instagram, WhatsApp, Telegram)
        │
        ▼
Data cleaning & preprocessing (language detection, tokenization)
        │
        ▼
MuRIL fine-tuned classifier (severity 0–3)
        │
        ▼
FastAPI backend (/classify endpoint, alert engine, incident logging)
        │
        ▼
React dashboard (guardian portal, moderator panel, live classify test)
```

## Project structure

```
safevoice/
├── backend/                  FastAPI server and model serving
│   ├── main.py
│   ├── classifier.py
│   ├── model_loader.py
│   ├── alert_engine.py
│   ├── database.py
│   └── models.py
│
├── safevoice-frontend/       React dashboard
│   └── src/
│       ├── api/
│       ├── pages/
│       └── components/
│
├── scripts/                  Data collection, training, evaluation
│   ├── scrape_youtube.py
│   ├── scrape_instagram.py
│   ├── parse_whatsapp.py
│   ├── scrape_telegram.py
│   ├── build_seed_dataset.py
│   ├── retrain_full.py
│   └── verify_all_labels.py
│
├── data/                     Raw, processed, and labeled datasets
├── models/                   Trained MuRIL weights
└── README.md
```

## Getting started

### Prerequisites

- Python 3.9+
- Node.js 18+
- PostgreSQL
- (Optional) CUDA-enabled GPU for faster training

### Backend setup

```bash
cd backend
pip install -r requirements.txt
uvicorn main:app --reload --port 8000
```

API will be available at `http://localhost:8000`. Interactive docs at `http://localhost:8000/docs`.

### Frontend setup

```bash
cd safevoice-frontend
npm install
npm run dev
```

Dashboard will be available at `http://localhost:5173`.

### Training the model

```bash
python scripts/build_seed_dataset.py
python scripts/retrain_full.py
python scripts/verify_all_labels.py
```

## API example

```bash
curl -X POST "http://localhost:8000/classify" \
  -H "Content-Type: application/json" \
  -d '{"text": "I will find you and hurt you", "platform": "youtube"}'
```

```json
{
  "text": "I will find you and hurt you",
  "label": "severe",
  "severity": 3,
  "confidence": 94.7,
  "scores": {
    "safe": 0.8,
    "mild_toxic": 1.2,
    "hate_speech": 3.3,
    "severe": 94.7
  },
  "alert_sent": true
}
```

## Severity levels

| Level | Label | Description |
|---|---|---|
| 0 | Safe | Normal, non-toxic content |
| 1 | Mild toxic | Rude or mildly offensive language |
| 2 | Hate speech | Targeted insults, slurs, or discriminatory language |
| 3 | Severe | Threats or content requiring immediate action |

## Roadmap

- [ ] Chrome extension for real-time browser-level detection
- [ ] Mobile app for guardians
- [ ] Expand language support to Telugu and Malayalam
- [ ] Docker deployment and CI/CD pipeline
- [ ] Continuous retraining loop from moderator feedback

## Disclaimer

SafeVoice is built for educational and research purposes around AI safety and content moderation. Data collection scripts are intended for use with publicly available data only, in line with each platform's terms of service. Always obtain appropriate consent when monitoring chats involving minors.

## License

MIT License

## Author

Mathan
[GitHub](https://github.com/Mathangowri25) · [LinkedIn](https://linkedin.com/in/mathan-m-5141a527b)
