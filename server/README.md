---
title: MediSync API
emoji: ⚕
colorFrom: blue
colorTo: green
sdk: docker
app_port: 7860
pinned: false
---

MediSync FastAPI backend — AI-powered healthcare middleware connecting Doctors, Hospitals, Insurers, and Patients.

## Required Space secrets
- `MONGODB_URI` — MongoDB Atlas SRV connection string
- `JWT_SECRET` — random 32+ char string
- `GEMINI_API_KEY` — Google AI Studio key
- `LLM_PROVIDER` — set to `gemini`
- `CORS_ORIGINS` — comma-separated list of allowed frontend origins (e.g. `https://medisync.vercel.app`)
