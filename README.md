# Face Intelligence

Local-first face analysis for development and controlled demonstrations.
The project combines a React dashboard with a FastAPI backend and ONNX Runtime
models for face detection, recognition, expression classification, and
approximate age and gender estimation.

> This project is designed to run on your own computer. It does not require
> API keys, cloud credentials, telemetry, or a deployment service.

## What it can do

- Analyze uploaded images and videos.
- Detect faces and return five facial landmarks.
- Match faces against an explicitly enrolled local gallery.
- Classify visible facial expressions with uncertainty information.
- Estimate age and gender using an ensemble of models.
- Analyze webcam frames over a local WebSocket connection.
- Track faces between detector frames to reduce repeated inference cost.
- Enroll and delete identities with an explicit consent confirmation step.
- Store local biometric data under the project data directory.

The analysis options are independent. Recognition and age estimation can be
disabled when they are not needed; expression analysis is enabled by default
in the dashboard.

## Important limitations

Face recognition, expression labels, and age or gender estimates are
probabilistic outputs. They are not identity proof, emotion measurements,
verified age, or suitable inputs for decisions about employment, eligibility,
law enforcement, access control, or other high-impact situations.

Use only images and video that you have permission to process. Enrollment must
be deliberate and consent-based. The system never searches the internet or
tries to identify an unknown person from an external database.

## Architecture

```text
React + Vite dashboard
        |
        | REST API and WebSocket
        v
FastAPI backend
        |
        +-- SCRFD       face detection and five-point alignment
        +-- ArcFace    face embeddings and gallery matching
        +-- HSEmotion  expression classification
        +-- FairFace   age and gender ensemble
        |
        v
Local models and local data directory
```

### Main components

| Component | Location | Purpose |
| --- | --- | --- |
| Frontend | `frontend/` | React dashboard and webcam client |
| API entry point | `backend/app/main.py` | FastAPI application |
| REST routes | `backend/app/api/routes.py` | Health, analysis, and gallery endpoints |
| WebSocket route | `backend/app/api/ws.py` | Live webcam analysis |
| Pipeline | `backend/app/services/pipeline.py` | Detection and optional analysis stages |
| Model services | `backend/app/services/` | Detection, recognition, expression, age, and tracking |
| Local models | `models/` | ONNX model files and manifest |
| Local data | `data/` | Embeddings, temporary uploads, and optional retained images |
| Tests | `backend/tests/` | Backend unit, integration, and API tests |

## Requirements

- Windows, macOS, or Linux
- Python 3.12 or newer
- Node.js and npm
- CPU with enough memory for the selected ONNX models
- A browser with webcam support for the webcam tab

The backend uses CPU execution by default and can use OpenVINO when the
provider is available.

## Quick start on Windows

Run each service in a separate PowerShell terminal.

### 1. Create the backend environment

From the repository root:

```powershell
python -m venv backend\.venv
backend\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
python -m pip install -r backend\requirements.txt
```

If PowerShell blocks activation, use the environment's executable directly:

```powershell
backend\.venv\Scripts\python.exe -m pip install -r backend\requirements.txt
```

### 2. Prepare model files

Model files are not included in the repository. If the `models/` directory
does not contain the files expected by the backend, run the provisioning
script:

```powershell
backend\.venv\Scripts\python.exe backend\scripts\download_models.py
```

The provisioning script downloads the required upstream weights, quantizes
the models where applicable, verifies their hashes, and writes them under
`models/`. It may require the script-only `uniface` package:

```powershell
backend\.venv\Scripts\python.exe -m pip install uniface
```

Do not run the downloader if the required model files are already present.
The first model-status request can take longer while models are loaded.

### 3. Start the backend

From the repository root:

```powershell
$env:PYTHONPATH = (Resolve-Path .\backend).Path
backend\.venv\Scripts\python.exe -m uvicorn app.main:app --reload --port 8000
```

The backend is available at:

- API root: <http://127.0.0.1:8000/>
- Health: <http://127.0.0.1:8000/health>
- Readiness: <http://127.0.0.1:8000/ready>
- Interactive API documentation: <http://127.0.0.1:8000/docs>

### 4. Start the frontend

In another PowerShell terminal:

```powershell
cd frontend
npm install
npm run dev
```

Open <http://127.0.0.1:5173/>.

The Vite development server proxies `/api`, `/health`, and `/ws` to the
backend at `127.0.0.1:8000`. No `VITE_API_KEY` or other frontend secret is
needed.

## Using the dashboard

### Analyze

1. Select the Analyze tab.
2. Upload a supported image or video.
3. Choose recognition, expression, and age options.
4. Review the returned boxes, landmarks, labels, and uncertainty notes.

Supported image extensions are `.jpg`, `.jpeg`, `.png`, `.bmp`, and `.webp`.
Supported video extensions are `.mp4`, `.avi`, `.mov`, and `.mkv`.

### Webcam

1. Select the Webcam tab.
2. Choose the analysis options.
3. Click Start webcam and approve the browser's camera prompt.
4. Click Stop webcam to release the camera and close the WebSocket.

The camera is not requested on page load. Frames are sent only after the user
starts the webcam session.

### Enroll

1. Select the Enroll tab.
2. Provide a name and a photo containing exactly one face.
3. Confirm that the person consented to enrollment.
4. Use the enrolled list to review or delete local entries.

Enrollment stores an embedding rather than the original image by default.

## Local API overview

The API is intentionally open for local development; it does not require API
keys or cloud credentials.

| Method | Path | Purpose |
| --- | --- | --- |
| `GET` | `/health` | Basic health check |
| `GET` | `/ready` | Check model and runtime readiness |
| `GET` | `/api/models/status` | Check which models are loaded |
| `POST` | `/api/analyze/image` | Analyze one uploaded image |
| `POST` | `/api/analyze/video` | Analyze an uploaded video |
| `POST` | `/api/faces/enroll` | Enroll one consented face |
| `GET` | `/api/faces` | List enrolled faces |
| `DELETE` | `/api/faces/{face_id}` | Delete an enrolled face |
| `POST` | `/api/faces/{face_id}/withdraw-consent` | Delete data after consent withdrawal |
| `WebSocket` | `/ws/analyze` | Analyze webcam JPEG frames |
| `GET` | `/ws/stats` | Inspect active local WebSocket connections |

For request schemas and response examples, use the generated documentation at
<http://127.0.0.1:8000/docs>.

## Data and privacy

By default, the application writes local data under `data/`:

```text
data/
├── embeddings/index.json   enrolled face embeddings
├── gallery/                optional retained enrollment images
└── tmp_uploads/            temporary request files
```

Uploaded files are temporary and are cleaned up after request processing.
Enrollment images are not retained unless `retain_enrollment_images` is
enabled in the backend settings. Enrolled embeddings can be removed with the
delete or withdraw-consent endpoints.

For the full consent, retention, and responsible-use discussion, read
[docs/PRIVACY.md](docs/PRIVACY.md).

## Configuration

Settings are loaded from environment variables and an optional `.env` file.
Useful local settings include:

| Variable | Default | Purpose |
| --- | --- | --- |
| `FACE_DATA_DIR` | `data/` | Change the local data directory |
| `CORS_ORIGINS` | `localhost:5173,127.0.0.1:5173` | Allowed browser origins |
| `DEBUG` | `false` | Include more diagnostic details in development |
| `RATE_LIMIT_ENABLED` | `true` | Enable request rate limiting |
| `RATE_LIMIT_RPM` | `60` | Requests per minute |
| `MAX_UPLOAD_SIZE_MB` | `25` | Maximum upload size |

Encryption settings are optional for local development. If configured,
`FACE_ENCRYPTION_KEY` and `FACE_ENCRYPTION_SALT` protect stored biometric
data. Never commit secret values to the repository.

## Testing and validation

From the repository root:

```powershell
$env:PYTHONPATH = (Resolve-Path .\backend).Path
backend\.venv\Scripts\python.exe -m pytest backend\tests -q
```

Build the frontend:

```powershell
cd frontend
npm run build
```

Compile-check the backend:

```powershell
cd ..
backend\.venv\Scripts\python.exe -m compileall -q backend\app
```

The automated tests use synthetic images for deterministic plumbing and
validation checks. They do not replace evaluation with real, consented faces.
Add real images only when you have the right to use them.

## Troubleshooting

### `Could not import module "main"`

The entry point is inside the `app` package. Start Uvicorn from the repository
root with:

```powershell
$env:PYTHONPATH = (Resolve-Path .\backend).Path
backend\.venv\Scripts\python.exe -m uvicorn app.main:app --reload --port 8000
```

### `No module named app`

Set `PYTHONPATH` to the backend directory, or run the command from the
repository root exactly as shown above.

### `This is taking a little longer than usual`

The first model load can take several seconds, especially when
`/api/models/status` or `/ready` initializes all model services. Wait for the
backend terminal to finish loading, then refresh the dashboard. The frontend
does not need an API key.

### The webcam does not start

Use `http://127.0.0.1:5173` or `http://localhost:5173`, allow camera access in
the browser, and make sure the backend is running on port `8000`. Stop any
previous webcam session before starting another one.

### Models are missing

Run `backend\scripts\download_models.py` and check the backend logs. Model
assets are intentionally kept outside source control because of their size
and upstream licensing.

More troubleshooting notes are available in
[docs/TROUBLESHOOTING.md](docs/TROUBLESHOOTING.md).

## Documentation

- [Privacy, consent, and retention](docs/PRIVACY.md)
- [Architecture](docs/ARCHITECTURE.md)
- [Model cards](docs/MODEL_CARDS.md)
- [OpenCV fundamentals](docs/OPENCV_FUNDAMENTALS.md)
- [Troubleshooting](docs/TROUBLESHOOTING.md)

## Responsible use

This software is for local research, development, and controlled
demonstrations. Obtain appropriate consent, explain what is processed, keep
the data local, and delete biometric data when it is no longer needed.

Do not use the outputs as the sole basis for identity, emotion, age,
eligibility, employment, legal, medical, financial, or safety decisions.
