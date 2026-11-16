# 🎯 Face Intelligence System — Local-First AI Vision

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.12+](https://img.shields.io/badge/python-3.12+-blue.svg)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.100+-green.svg)](https://fastapi.tiangolo.com/)
[![React 18](https://img.shields.io/badge/React-18-violet.svg)](https://reactjs.org/)
[![ONNX Runtime](https://img.shields.io/badge/ONNX_Runtime-latest-orange.svg)](https://onnxruntime.ai/)
[![OpenCV](https://img.shields.io/badge/OpenCV-4.8+-red.svg)](https://opencv.org/)

<div align="center">
  <p><strong>A local-first, CPU-only face analysis system</strong></p>
  <p>No API keys • No cloud calls • No telemetry • Zero cost to run</p>
</div>

---

## 📊 What This Project Does

| Capability | Description | Model Used |
|------------|-------------|------------|
| **Face Detection** | Find faces + 5 landmarks | SCRFD-10G INT8 (~4.3 MB) |
| **Face Recognition** | Match against local gallery | ArcFace-R50 INT8 (~42 MB) |
| **Expression Classification** | 8 emotion categories | HSEmotion ENet-B0 (~4 MB) |
| **Age & Gender Estimation** | Approximate demographics | GenderAge + FairFace ensemble (~22 MB) |
| **Video Tracking** | Persistent IDs across frames | IoU + Lucas-Kanade optical flow |

**Total model footprint: ≈ 70 MB of INT8-quantized ONNX weights.**

---

<details>
<summary>🖼️ <strong>Click to expand: Architecture Diagram</strong></summary>

```text
┌─────────────────────────────────────────────────────────────────────────────┐
│                         FRONTEND (React + Vite)                             │
│                           Port 5173                                         │
│   ┌─────────────┐   ┌─────────────┐   ┌─────────────┐                     │
│   │  Analyze    │   │   Webcam    │   │   Enroll    │                     │
│   │  Upload     │   │   Live      │   │  Consent    │                     │
│   └──────┬──────┘   └──────┬──────┘   └──────┬──────┘                     │
│          │                 │                  │                             │
│          └─────────────────┴──────────────────┘                             │
│                            │                                                │
│                        REST/WebSocket                                       │
└────────────────────────────┼────────────────────────────────────────────────┘
                             │ HTTP / WebSocket
                             ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                          BACKEND (FastAPI)                                  │
│                           Port 8000                                         │
│   ┌─────────────────────────────────────────────────────────────────────┐   │
│   │                        Pipeline Orchestrator                         │   │
│   │   detect → align → embed → [recognition / expression / age-gender]  │   │
│   └─────────────────────────────────────────────────────────────────────┘   │
│                              │                                              │
│          ┌───────────────────┼───────────────────┐                          │
│          ▼                   ▼                   ▼                          │
│   ┌─────────────┐   ┌─────────────┐   ┌─────────────┐                       │
│   │  Security   │   │   Logging   │   │ Validation  │                       │
│   │ AES-256-GCM │   │ Structured  │   │ Uploads     │                       │
│   │ Consent Gate│   │ JSON Logs   │   │ Rate Limit  │                       │
│   └─────────────┘   └─────────────┘   └─────────────┘                       │
└────────────────────────────┼────────────────────────────────────────────────┘
                             │ ONNX Runtime (CPU/OpenVINO)
                             ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                           LOCAL MODELS (ONNX)                               │
│   ┌──────────────┐ ┌──────────────┐ ┌──────────────┐ ┌──────────────────┐  │
│   │  SCRFD-10G   │ │ ArcFace-R50  │ │ HSEmotion    │ │ GenderAge        │  │
│   │ ~4.3 MB INT8 │ │ ~42 MB INT8  │ │ ~4 MB INT8   │ │ ~1.3 MB FP32     │  │
│   │ Detect + 5pt │ │ 512-D emb'd  │ │ 8 classes    │ │ Age + gender log │  │
│   └──────────────┘ └──────────────┘ └──────────────┘ └──────────────────┘  │
│   ┌──────────────────────────────────────────────────────────────────────┐  │
│   │                      FairFace (Age/Gender)                           │  │
│   │                      ~21 MB INT8 / 224×224 input                     │  │
│   └──────────────────────────────────────────────────────────────────────┘  │
└────────────────────────────┼────────────────────────────────────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                            LOCAL DATA (./data/)                             │
│   ├── embeddings/index.json     Enrolled face embeddings + consent         │
│   ├── gallery/                  Optional retained enrollment images        │
│   └── tmp_uploads/              Auto-deleted after each request            │
└─────────────────────────────────────────────────────────────────────────────┘
```
</details>

---

## 🚀 Quick Start (Windows — Copy & Paste)

### Prerequisites
- Python 3.12+
- Node.js 20+
- A browser with webcam support

### Step 1: Backend Setup

```powershell
# Open PowerShell — navigate to repo root
cd "d:\Opne CV\face-intelligence\face-intelligence"

# Create virtual environment
python -m venv backend\.venv
.\backend\.venv\Scripts\Activate.ps1

# Install dependencies
python -m pip install --upgrade pip
python -m pip install -r backend\requirements.txt

# Download & quantize models (one-time, takes a few minutes)
.\backend\.venv\Scripts\python.exe backend\scripts\download_models.py
```

### Step 2: Start Backend

```powershell
$env:PYTHONPATH = (Resolve-Path .\backend).Path
.\backend\.venv\Scripts\python.exe -m uvicorn app.main:app --reload --port 8000
```

✅ Verify: Open <http://127.0.0.1:8000/health> → should return `{"status":"ok"}`  
✅ API docs: <http://127.0.0.1:8000/docs>

### Step 3: Start Frontend

```powershell
cd frontend
npm install
npm run dev
```

✅ Dashboard: <http://127.0.0.1:5173/>

---

## 🎮 Using the Dashboard

### Tab 1: Analyze
1. Click **Upload** → pick an image or video
2. Toggle on/off: **Recognition**, **Expression**, **Age**
3. View results: bounding boxes, landmarks, labels, confidence scores

### Tab 2: Webcam
1. Click **Start Webcam** → approve camera access
2. Watch real-time analysis with smooth label tracking
3. Click **Stop Webcam** when done

### Tab 3: Enroll
1. Upload a photo with **exactly one face**
2. Enter a name for this person
3. ✅ Check the **consent confirmation** box (required!)
4. Submit → face saved to your local gallery

---

<details>
<summary>📁 <strong>Click to expand: Complete File Map</strong></summary>

### Backend (`backend/app/`)

| File | Purpose |
|------|---------|
| `main.py` | FastAPI entry point — middleware, lifespan, routes |
| `api/routes.py` | REST endpoints: health, analyze, enroll, delete |
| `api/ws.py` | WebSocket endpoint for live webcam streaming |
| `services/pipeline.py` | ⭐ Core orchestrator — detection → alignment → analysis |
| `services/detection.py` | SCRFD-10G face detector + 5-point landmarks |
| `services/recognition.py` | ArcFace-R50 embedding + cosine matching |
| `services/expressions.py` | HSEmotion expression classifier (8 classes) |
| `services/age_estimation.py` | Two-model age/gender ensemble |
| `services/tracking.py` | FaceTracker — IoU matching + optical flow + EMA smoothing |
| `core/onnx_runtime.py` | Model loading, INT8 quantization, batch tensors |
| `core/config.py` | All settings (thresholds, paths, consent rules) |
| `security/crypto.py` | AES-256-GCM encryption for embeddings |
| `security/auth.py` | API key authentication + role-based access |
| `security/validation.py` | Upload validation + decompression-bomb protection |
| `schemas/models.py` | Pydantic response models |

### Frontend (`frontend/src/`)

| File | Purpose |
|------|---------|
| `App.tsx` | Root component |
| `pages/Dashboard.tsx` | Main dashboard with tabs |
| `services/api.ts` | REST API client |
| `services/webcam.ts` | WebSocket webcam stream handler |
| `components/*.tsx` | UI components (canvas, panels, dialogs) |
| `types/api.ts` | TypeScript interfaces for API responses |

### Other

| Path | Purpose |
|------|---------|
| `models/*.onnx` | ONNX model files (~70 MB total) |
| `data/` | Local storage for embeddings and uploads |
| `docs/` | Architecture, model cards, privacy, troubleshooting |
| `tests/` | Unit and integration tests |

</details>

---

<details>
<summary>📐 <strong>Click to expand: Analysis Pipeline (Step-by-Step)</strong></summary>

Each image/frame goes through these stages:

```
INPUT IMAGE
    │
    ▼
┌──────────────────┐
│ 1. DETECTION     │ ← SCRFD-10G runs on full frame
│    (30–50 ms)    │    Outputs: [x,y,w,h] + 5 landmarks
└────────┬─────────┘
         │
         ▼
┌──────────────────┐
│ 2. ALIGNMENT     │ ← Umeyama similarity transform
│    (10–15 ms)    │    Warps to canonical 112×112 crop
└────────┬─────────┘
         │
         ▼
┌──────────────────┐
│ 3. EMBEDDING     │ ← ArcFace-R50 extracts 512-D vector
│    (40–60 ms)    │    (runs only if recognition enabled)
└────────┬─────────┘
         │
    ┌────┴────┬────────────┐
    ▼         ▼            ▼
┌────────┐ ┌────────┐ ┌──────────────┐
│RECOGN. │ │EXPR.   │ │AGE/GENDER    │
│Cosine  │ │HSEmot. │ │GenderAge +   │
│vs gallery│ │8-class │ │FairFace      │
└───┬────┘ └───┬────┘ └──────┬───────┘
    │          │             │
    └──────────┴─────────────┘
               │
               ▼
        ┌──────────────┐
        │ 4. TRACKING  │ ← Joins prev frame tracks
        │  (video only)│    EMA smooths labels
        └──────┬───────┘
               │
               ▼
        ┌──────────────┐
        │ OUTPUT JSON  │ ← Boxes, identities,
        │ + latency    │    expressions, age
        └──────────────┘
```

**Key optimizations:**
- Frame skipping: Full detection every 3rd frame, optical flow in between
- Batch inference: Multiple faces processed in single ONNX forward pass
- Lazy loading: Models load on first use, cached for subsequent calls
- EMA smoothing: Expression/age values blend across frames to prevent flicker

</details>

---

## 🔧 API Endpoints

### Public (no auth required)

| Method | Path | Description |
|--------|------|-------------|
| `GET` | `/health` | Basic health check |
| `GET` | `/ready` | Model loading status |
| `GET` | `/api/models/status` | Which models are loaded |

### Protected (POST/DELETE)

| Method | Path | Description |
|--------|------|-------------|
| `POST` | `/api/analyze/image` | Analyze uploaded image |
| `POST` | `/api/analyze/video` | Analyze uploaded video |
| `POST` | `/api/faces/enroll` | Enroll a face (requires consent) |
| `GET` | `/api/faces` | List enrolled faces |
| `DELETE` | `/api/faces/{id}` | Delete enrolled face |
| `POST` | `/api/faces/{id}/withdraw-consent` | Remove data after consent withdrawal |

### WebSocket

| Endpoint | Description |
|----------|-------------|
| `ws://127.0.0.1:8000/ws/analyze` | Live webcam frame analysis |
| `GET ws://127.0.0.1:8000/ws/stats` | Active connection stats |

> 📖 Full interactive docs at <http://127.0.0.1:8000/docs>

---

## 📦 Model Reference

| Model | File | Size (INT8) | Benchmark | Purpose |
|-------|------|-------------|-----------|---------|
| **SCRFD-10G** | `scrfd_10g_bnkps_int8.onnx` | ~4.3 MB | 95.16% WiderFace Hard | Face detection + 5 landmarks |
| **ArcFace-R50** | `w600k_r50_int8.onnx` | ~42 MB | 99.8% LFW / 96% IJB-C | 512-D face embeddings |
| **HSEmotion** | `hsemotion_enet_b0_8_int8.onnx` | ~4.0 MB | 86.9% RAF-DB | 8-class expression |
| **GenderAge** | `genderage.onnx` | ~1.3 MB | Continuous 0–100 | Age + gender logits |
| **FairFace** | `fairface_int8.onnx` | ~21 MB | 9-bucket classifier | Second age estimate |

All models run on **CPU** via ONNX Runtime. INT8 quantization reduces size ~4× with <0.1% accuracy loss.

---

## 🛡️ Privacy & Consent

This system is designed for **local-first** operation:

- ✅ **No internet calls** — all inference happens on your machine
- ✅ **Consent required** — enrollment needs explicit `consent_confirmed=true`
- ✅ **Embeddings stored locally** — under `./data/embeddings/index.json`
- ✅ **Optional encryption** — enable AES-256-GCM via env variables
- ✅ **Withdraw consent** — delete any enrollment with one API call

### Data Locations

```
./data/
├── embeddings/index.json   ← Enrolled faces (name, embedding hash, consent)
├── gallery/                ← Optional kept images (off by default)
└── tmp_uploads/            ← Temporary upload files (auto-deleted)
```

### Encryption (Optional)

To encrypt biometric data at rest, set these environment variables:

```bash
FACE_ENCRYPTION_KEY=<base64-encoded-32-byte-key>
FACE_ENCRYPTION_SALT=<base64-encoded-32-byte-salt>
```

Generate secure keys:
```bash
python -c "import secrets,base64;print(base64.b64encode(secrets.token_bytes(32)).decode())"
```

> ⚠️ **Never commit these keys to version control!**

---

## ⚙️ Configuration

Settings are loaded from `.env` file or environment variables:

| Variable | Default | Purpose |
|----------|---------|---------|
| `FACE_DATA_DIR` | `data/` | Change local data directory |
| `CORS_ORIGINS` | `localhost:5173,127.0.0.1:5173` | Allowed browser origins |
| `DEBUG` | `false` | Enable verbose diagnostics |
| `RATE_LIMIT_ENABLED` | `true` | Enable rate limiting |
| `RATE_LIMIT_RPM` | `60` | Requests per minute limit |
| `MAX_UPLOAD_SIZE_MB` | `25` | Maximum upload size |
| `REC ognITION_DISTANCE_THRESHOLD` | `0.68` | Cosine distance cutoff |

See [`backend/app/core/config.py`](backend/app/core/config.py) for the complete list.

---

## 🧪 Testing

Run the test suite from the repository root:

```powershell
$env:PYTHONPATH = (Resolve-Path .\backend).Path
.\backend\.venv\Scripts\python.exe -m pytest backend\tests -q

# Build frontend
cd frontend
npm run build
```

Tests use synthetic images to verify pipeline plumbing — not accuracy on real photos.

---

## ❓ Common Issues & Fixes

<details>
<summary><strong>Could not import module "main"</strong></summary>

Ensure you're running from the **repository root**, not inside `backend/`:

```powershell
# WRONG — running from inside backend/
.\backend\.venv\Scripts\python.exe -m uvicorn main:app

# RIGHT — running from repo root with PYTHONPATH set
$env:PYTHONPATH = (Resolve-Path .\backend).Path
.\backend\.venv\Scripts\python.exe -m uvicorn app.main:app
```
</details>

<details>
<summary><strong>Models are missing</strong></summary>

Download and prepare models:
```powershell
.\backend\.venv\Scripts\python.exe backend\scripts\download_models.py
```
The `models/` folder is intentionally excluded from git due to size/license constraints.

</details>

<details>
<summary><strong>Webcam won't start</strong></summary>

1. Use `http://127.0.0.1:5173` (not `localhost` — some browsers block cameras on non-HTTPS localhost)
2. Ensure no other app is using your camera
3. Stop any previous webcam session first
4. Grant camera permission when prompted

</details>

<details>
<summary><strong>"Unknown" instead of recognized name</strong></summary>

Check these common issues:
1. **Alignment mismatch** — enrollment and query must use the same preprocessing
2. **Threshold too strict** — try lowering `recognition_distance_threshold` in config
3. **Different lighting/pose** — enrolling in good lighting helps
4. **Not enough gallery matches** — recognize requires at least one enrolled face

</details>

---

## 🎤 Top 10 Questions (Hackathon Edition)

<details>
<summary><strong>Q1: Do I need a GPU?</strong></summary>
<strong>A:</strong> No! Everything runs on CPU. The INT8 models are small (~70 MB total) and ONNX Runtime uses AVX vectorization. Expect ~1–1.2 seconds per image on a laptop CPU.
</details>

<details>
<summary><strong>Q2: Is this free with no API keys?</strong></summary>
<strong>A:</strong> Yes! All models are downloaded once and run locally. No monthly fees, no quotas, no telemetry.
</details>

<details>
<summary><strong>Q3: How does face recognition actually work?</strong></summary>
<strong>A:</strong> 
1. SCRFD finds the face + 5 landmarks
2. Alignment warps it to a canonical 112×112 template
3. ArcFace extracts a 512-D "fingerprint" vector
4. Cosine distance compared against all enrolled vectors
5. If nearest neighbor is within 0.68 threshold → match, else "Unknown"
</details>

<details>
<summary><strong>Q4: Why does it sometimes say "Unknown" for people I enrolled?</strong></summary>
<strong>A:</strong> Usually caused by: different lighting, angle changes, glasses/hats added, or the enrollment photo was poor quality. Try re-enrolling with a clearer front-facing photo.
</details>

<details>
<summary><strong>Q5: Can I use this for attendance tracking?</strong></summary>
<strong>A:</strong> Not as a sole decision maker. The outputs are probabilistic and can produce false positives/negatives. Always include human oversight for high-stakes decisions.
</details>

<details>
<summary><strong>Q6: Where is my data stored?</strong></summary>
<strong>A:</strong> Locally in `./data/`. Embeddings are stored as JSON (optionally encrypted). No data leaves your machine unless you explicitly share the JSON file.
</details>

<details>
<summary><strong>Q7: How accurate is age estimation?</strong></summary>
<strong>A:</strong> It's an ensemble of two models. The system reports both the estimated age AND an uncertainty band based on how much the models disagree. Treat it as approximate, never as verified.
</details>

<details>
<summary><strong>Q8: Why are expressions sometimes wrong?</strong></summary>
<strong>A:</strong> HSEmotion classifies visible facial configurations, not internal emotional states. Masks, side profiles, low light, and micro-expressions reduce accuracy. Results below 0.22 confidence are reported as "uncertain".
</details>

<details>
<summary><strong>Q9: What happens if I withdraw consent?</strong></summary>
<strong>A:</strong> Call `POST /api/faces/{id}/withdraw-consent`. The embedding is permanently deleted from the index. Any kept enrollment image is also removed. This action cannot be undone.
</details>

<details>
<summary><strong>Q10: What breaks this project?</strong></summary>
<strong>A:</strong> Most common issues:
- BGR vs RGB confusion (the #1 silent bug)
- Wrong normalization (check each model's requirements)
- Missing consent field during enrollment
- Decompression bomb attacks (mitigated by size checks)
- Models not provisioned before first use
</details>

---

## 🏗️ Key Technical Decisions

| Decision | Rationale |
|----------|-----------|
| **CPU-only** | Runs anywhere — no GPU dependency |
| **ONNX format** | Framework-agnostic, portable across platforms |
| **INT8 quantization** | 4× smaller, faster on CPU, minimal accuracy loss |
| **Lazy model loading** | Don't pay startup cost if user doesn't use a feature |
| **Ensemble age estimation** | Two independent models catch each other's errors |
| **Consent gate** | Ethical requirement for biometric data |
| **Local-first** | Privacy by design, works offline |

---

## 📚 Documentation

- [Model Cards](docs/MODEL_CARDS.md) — Accuracy benchmarks & caveats
- [Architecture](docs/ARCHITECTURE.md) — Detailed system design
- [Privacy Policy](docs/PRIVACY.md) — Data handling & consent
- [OpenCV Fundamentals](docs/OPENCV_FUNDAMENTALS.md) — Concepts explained
- [Troubleshooting](docs/TROUBLESHOOTING.md) — Extended debug guide

---

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feat/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feat/amazing-feature`)
5. Open a Pull Request

Please read [docs/PRIVACY.md](docs/PRIVACY.md) before adding new data-handling features.

---

## ⚖️ Responsible Use

This software is for **local research, development, and controlled demonstrations**. 

- Obtain appropriate consent before processing anyone's image
- Explain what analysis is being performed
- Keep biometric data local and delete when no longer needed
- Do NOT use outputs as the sole basis for:
  - Identity verification
  - Employment decisions
  - Access control
  - Law enforcement actions
  - Medical diagnoses

Face recognition, expression classification, and age estimation are **probabilistic estimates** — not ground truth.

---

## 📜 License

MIT License — see [LICENSE](LICENSE) for details.

---

<div align="center">

**Built with ❤️ for local AI development**

Questions? Open an issue or check the API docs at <http://127.0.0.1:8000/docs>

</div>
