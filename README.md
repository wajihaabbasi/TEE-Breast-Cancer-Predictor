# Breast Cancer Predictor (Confidential AI PoC)

A two-container ML app: a **FastAPI backend** serving a logistic regression model trained on the Wisconsin Diagnostic Breast Cancer (WDBC) dataset, and a **Gradio frontend** that calls it over HTTP. The same Docker Compose setup can be deployed into a TEE-backed confidential VM using **dstack on Phala Cloud**, where remote attestation can be inspected.

> **Not a medical device.** This was built for a thesis proof of concept using a public benchmark dataset, and SHOULD NOT be used for medical diagnosis.

---

## Table of contents

1. [Project layout](#1-project-layout)
2. [Prerequisites](#2-prerequisites)
3. [Run locally with Python (no Docker)](#3-run-locally-with-python-no-docker)
4. [Run locally with Docker Compose](#4-run-locally-with-docker-compose)
5. [Deploy to Phala Cloud (confidential VM)](#5-deploy-to-phala-cloud-confidential-vm)
6. [Viewing the attestation](#6-viewing-the-attestation)
7. [Troubleshooting](#9-troubleshooting)

---

## 1. Project layout

```
Breast_Cancer_Predictor/
├── venv/                       # Python virtual environment (not committed)
├── Backend/
│   ├── data/data.csv           # WDBC dataset
│   ├── app/
│   │   ├── main.py             # FastAPI routes
│   │   ├── model.py            # loads model + predict()
│   │   ├── model.pkl           # trained model   (created by train.py)
│   │   ├── scaler.pkl          # fitted scaler   (created by train.py)
│   │   └── feature_names.pkl   # feature order   (created by train.py)
│   ├── train.py
│   ├── requirements.txt
│   └── Dockerfile
├── Frontend/
│   ├── gradio_app.py
│   ├── requirements.txt
│   └── Dockerfile
├── docker-compose.yml          # local: builds images from source
├── docker-compose.phala.yml    # cloud: pulls pre-built images from Docker Hub
└── .gitignore
```

---

## 2. Prerequisites

| Needed for | Tool |
|---|---|
| Everything | Python 3.10+ (3.12 recommended), Git |
| Docker sections | Docker Engine + Compose plugin (`docker compose version` should work) |
| Phala deployment | A [Phala Cloud](https://cloud.phala.network) account, a Docker Hub account, Node.js v.18+ |

---

## 3. Run locally with Python (no Docker)

Good for quick development. You need two terminals.

### 3.1 Create and activate the virtual environment

From the project root:

```bash
cd ~/Thesis/Breast_Cancer_Predictor
python3 -m venv venv
source venv/bin/activate          # Windows PowerShell: venv\Scripts\Activate.ps1
```

```bash
echo $VIRTUAL_ENV
```
### 3.2 Install backend dependencies and train the model

```bash
cd Backend
pip install -r requirements.txt
python3 train.py
```

You should see an accuracy of about 0.96 and the message that the model, scaler and feature names were saved into `app/`.

### 3.3 Start the backend (terminal 1)

```bash
python3 -m uvicorn app.main:app --reload
```

Open <http://127.0.0.1:8000/docs> to see the interactive API docs. `GET /health` should return `{"status":"ok"}`.

### 3.4 Start the frontend (terminal 2)

```bash
cd ~/Thesis/Breast_Cancer_Predictor
source venv/bin/activate
cd Frontend
pip install -r requirements.txt
python3 gradio_app.py
```

Open <http://127.0.0.1:7860>, enter 30 values (copy a row from `Backend/data/data.csv`, skipping `id` and `diagnosis`) and submit. You should get a diagnosis and a malignancy probability.

---

## 4. Run locally with Docker Compose

From the project root, with the model files already created (step 3.2):

```bash
docker compose up --build
```

Wait until you see both lines:

```
breast-cancer-backend   | Uvicorn running on http://0.0.0.0:8000
breast-cancer-frontend  | Running on local URL:  http://0.0.0.0:7860
```

Then open:

- <http://127.0.0.1:7860>: the Gradio UI
- <http://127.0.0.1:8000/docs>: the backend API docs

Inside Docker the frontend reaches the backend by service name (`BACKEND_URL=http://backend:8000`, set in `docker-compose.yml`). Stop with `Ctrl+C`, then `docker compose down`.

> **Do not mount `/var/run/dstack.sock` in the local `docker-compose.yml`.** That socket only exists inside a dstack confidential VM. Locally, Docker would create an empty folder in its place.

---

## 5. Deploy to Phala Cloud (confidential VM)

### 5.1 Log in to Docker Hub

```bash
docker login
```

### 5.2 Build and push both images

Replace `YOURUSER` with your Docker Hub username:

```bash
cd ~/Thesis/Breast_Cancer_Predictor
docker build -t YOURUSER/bc-backend:latest  ./Backend
docker build -t YOURUSER/bc-frontend:latest ./Frontend
docker push YOURUSER/bc-backend:latest
docker push YOURUSER/bc-frontend:latest
```

Re-run these two build + push steps every time you change code.

### 5.3 Check `docker-compose.phala.yml`

```yaml
services:
  backend:
    image: YOURUSER/bc-backend:latest
    container_name: breast-cancer-backend
    ports:
      - "8000:8000"
    volumes:
      - /var/run/dstack.sock:/var/run/dstack.sock

  frontend:
    image: YOURUSER/bc-frontend:latest
    container_name: breast-cancer-frontend
    ports:
      - "7860:7860"
    environment:
      - BACKEND_URL=http://backend:8000
    depends_on:
      - backend
```
### 5.4 Install the CLI, log in, deploy

```bash
npm install -g phala
phala auth login
phala deploy -c docker-compose.phala.yml -n breast-cancer-predictor --wait
```

`--wait` blocks until the confidential VM is up. Check status any time:

```bash
phala cvms list
phala cvms get breast-cancer-predictor
```

### 5.5 Find the app's public address

To find the app's public URL, open the CVM in the Phala Cloud dashboard and look at its network/endpoints details, or run `phala cvms get breast-cancer-predictor --json` and look for endpoint or URL fields. Phala generates one address per exposed port, so there should be one for 7860 (Gradio) and one for 8000 (API).

---

## 6. Viewing the attestation

Remote attestation is the hardware-signed proof of what is running inside the confidential VM. There are two ways to view it:

### O1: Phala CLI

```bash
phala cvms attestation breast-cancer-predictor
```

This prints an attestation summary. For the full raw data (quote, event log, and so on):

```bash
phala cvms attestation breast-cancer-predictor --json
```

> Per Phala's docs this command is marked *unstable* and may change between CLI versions. If it errors, run `phala cvms --help` to see the current subcommands.

### 02: Phala Cloud dashboard

Open your CVM in the dashboard at <https://cloud.phala.network> and use its attestation view. 

### What to look for

- A **TDX quote**: the hardware-signed statement from the CPU.
- **Measurement registers (RTMRs)**: hashes covering the boot chain and your deployed compose configuration. If the app were altered, these values would change.
- An **event log** that lets a verifier recompute those measurements.

---

## 7. Troubleshooting

| Symptom | Likely cause and fix |
|---|---|
| `ModuleNotFoundError: No module named 'joblib'` | Wrong or inactive venv. Run `echo $VIRTUAL_ENV`; it must point inside this project. If it does not, `deactivate`, then `source venv/bin/activate` from the project root. If the venv was copied from another project, delete it and recreate with `python3 -m venv venv`. |
| `uvicorn` traces show `/usr/lib/python3/dist-packages/...` | A system uvicorn is being used. Run `python3 -m uvicorn app.main:app` instead. |
| `permission denied ... /var/run/docker.sock` | Add yourself to the docker group: `sudo usermod -aG docker $USER`, then log out and back in. |
| `docker compose: unknown command` | Compose V2 plugin missing. Install `docker-compose-plugin` from Docker's official apt repository. |
| Frontend container exits: `can't open file '/app/gradio_app.py'` | Filename or case mismatch with the Dockerfile `CMD`. Check the exact filename. |
| Gradio shows `Error contacting backend` | Backend not running, or wrong `BACKEND_URL`. Locally it defaults to `http://127.0.0.1:8000`; in Docker it must be `http://backend:8000`. |
| Phala deploy: `422 ... while parsing a block mapping` | YAML indentation error in the compose file. Use spaces only, 2 per level; check with `cat -A docker-compose.phala.yml`. |
| Phala link opens the dashboard, not the app | That link is the management page. See step 5.5 for the app's public endpoint. |
| `/attestation` returns 503 locally | Expected outside a dstack CVM. It works only inside a confidential VM (or against the dstack simulator via `DSTACK_ENDPOINT`). |

---

## References

- Phala Cloud CLI: `phala cvms attestation` reference, <https://docs.phala.com/phala-cloud/phala-cloud-cli/cvms/attestation>
- Phala Cloud: Get Attestation guide, <https://docs.phala.com/phala-cloud/attestation/get-attestation>
- dstack SDK for Python, <https://pypi.org/project/dstack-sdk/>
- Wolberg, W. H., Street, W. N., & Mangasarian, O. L. (1995). *Breast Cancer Wisconsin (Diagnostic) Data Set*. UCI Machine Learning Repository. https://doi.org/10.24432/C5DW2B
