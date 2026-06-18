---
title: AGL Chatbot
emoji: 🚢
colorFrom: blue
colorTo: indigo
sdk: gradio
sdk_version: 6.14.0
app_file: app.py
pinned: false
license: mit
---

# AGL Chatbot

Assistant virtuel pour **Africa Global Logistics (AGL)**.  
Répond aux questions sur les services, la logistique et les activités d'AGL.

## Variables d'environnement requises

| Variable | Description |
|---|---|
| `GOOGLE_API_KEY` | Clé API Google Gemini |
| `QDRANT_URL` | URL du cluster Qdrant Cloud |
| `QDRANT_API_KEY` | Clé API Qdrant Cloud |
| `QDRANT_COLLECTION` | Nom de la collection (défaut: `agl_website`) |
