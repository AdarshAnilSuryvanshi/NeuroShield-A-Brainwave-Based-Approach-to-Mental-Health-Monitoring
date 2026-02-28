# EEG-Based Depression Detection — Full-Stack Documentation (React + Django)

This document explains **A to Z** of the project in **simple, step-by-step English** so that any outsider (faculty / recruiter / teammate) can understand:
- what data you used,
- what preprocessing you did,
- how you trained the model,
- how the API will work in production,
- how React + Django + Database will be connected,
- how to handle wrong/corrupted inputs safely,
- and how to deploy like a real system.

---

## 1) Project Summary (What problem we solve)

Depression (MDD) detection normally needs clinical assessment.  
This project builds a **machine learning system** that analyzes **EEG signals** (brain electrical activity) and predicts:

- **0 = Healthy**
- **1 = MDD (Depression)**

Important note: This system is a **decision-support tool**, not a final medical diagnosis.

---

## 2) Dataset (What raw data looks like)

### 2.1 Per patient files
Each patient has **3 EEG sessions** (3 files):
1) **EC** = Eyes Closed  
2) **EO** = Eyes Open  
3) **Task** = Task-based recording  

So if you have 60 patients → total files ≈ 60 × 3 = **180 EDF files**.

### 2.2 What is inside one EDF file?
An EDF file stores EEG signals:
- **X-axis (columns / features):** EEG channels (pins on the head)
- **Y-axis (rows):** time samples (signal values over time)

In your data, most files have **~19 channels**, but some can have 20/21/23 channels.

---

## 3) Your End-to-End Pipeline (What you already did)

### 3.1 High-level steps
You followed this flow:

1) **Load raw EDF**
2) **Filter noise** (band-pass)
3) **Create epochs** (split into time windows)
4) **Reject artifacts** (remove noisy epochs)
5) **Convert to NumPy arrays**
6) **Prepare final training inputs** (`groups.npy`, `y_labels_epochs.npy`)
7) **Train ML model** and save it (`.pkl` / `.joblib`)
8) **Use saved model inside API** to predict for new uploads

---

## 4) Training Pipeline (Model Side) — Step by Step

### Step 1 — Load EDF files
**Goal:** Convert EDF → a clean signal matrix.

Tooling:
- `mne` (industry standard EEG Python library)

Output:
- `raw_signals` as NumPy array: `(channels, samples)`

---

### Step 2 — Filter noise (Band-pass)
**What you do:** keep only useful EEG frequencies.

Typical setting:
- **0.5 Hz to 45 Hz**

**Why:**
- remove DC drift (very low freq)
- remove high frequency noise (muscle / device noise)

---

### Step 3 — Create epochs (time segments)
**What you do:** split continuous signal into fixed windows.

In your approach:
- create **10 epochs**
- each epoch is **0.5 seconds**

So each epoch becomes:
- `(channels, samples_in_epoch)`

**Why epoching is important:**
- makes the dataset larger (more training samples)
- reduces effect of one noisy long recording
- makes features more stable

---

### Step 4 — Automatic artifact rejection
**What you do:** remove epochs which are too noisy.

Rule:
- remove epoch if amplitude exceeds a threshold (example: **150 µV**)

**Why:**
- EEG has eye blinks, movement, electrode issues
- noisy epochs can ruin ML training

---

### Step 5 — Standardize channel count (padding)
Problem:
- Some files have 19 channels, some 21/23.

Solution:
- convert all to a fixed channel count (example: **23**)
- if missing channels → pad zeros

**Why:**
- ML models need consistent input shape

---

### Step 6 — Feature extraction (PSD band powers)
Instead of feeding raw EEG directly to classical ML, you compute frequency features.

Method:
- **Welch PSD** per epoch, per channel
- compute average power in bands:
  - Delta (0.5–4)
  - Theta (4–8)
  - Alpha (8–12)
  - Beta (12–30)

Final features (example):
- `(epoch, channel, band)` → flattened to 1D vector per epoch

**Why:**
- PSD band powers are stable and meaningful for brain activity

---

### Step 7 — Labels and Groups (very important)
You created:
- `y_labels_epochs.npy`: labels for each epoch (0/1)
- `groups.npy`: subject ID per epoch (so epochs from same subject are grouped)

**Why groups are critical:**
If you randomly split epochs, the same subject can appear in both train and test → **data leakage**.

Correct approach:
- **Group K-Fold** or **Stratified Group K-Fold**
- subjects are separated between train/test folds

---

### Step 8 — Train ML models
You tested multiple models, and Random Forest performed best.

You save:
- model file: `rf_model.joblib`
- scaler (if used)
- pipeline metadata (feature list, version, accuracy)

---

## 5) Inference Pipeline (API Side) — Step by Step

API pipeline is the SAME until feature creation.

### Key difference:
- **Training pipeline:** trains model
- **API pipeline:** loads the saved model and predicts

---

## 6) Full-Stack System Design (React + Django + DB)

### 6.1 Why we need a database
We must store:
- uploaded EDF file info
- case status (processing / done / failed)
- final prediction + probability
- report PDF
- model version used
- audit log (who uploaded, when)

Recommended DB:
- **PostgreSQL**
- add **pgvector** for later AI agent / semantic search

---

### 6.2 Architecture (simple view)

```mermaid
flowchart LR
  A[React Frontend] -->|Upload EDF| B[Django REST API]
  B -->|Save file metadata| C[(PostgreSQL)]
  B -->|Queue heavy preprocessing| D[Celery Worker]
  D -->|Read EDF + preprocess + features| D
  D -->|Load saved model + predict| E[ML Model (.joblib)]
  D -->|Save prediction + report| C
  A -->|Check status| B
  B -->|Return result + report| A
```

**Why Celery is needed:**  
EDF processing can be heavy; don’t block the API request thread.

---

## 7) Backend (Django) — What to Build

### 7.1 Database tables (models)

**User**
- role: admin / researcher / clinician

**Case**
- id
- created_by
- status: UPLOADED / PROCESSING / DONE / FAILED
- session_type: EC (current MVP)
- predicted_label
- probability_mdd
- created_at

**EEGFile**
- case_id
- original_name
- file_path
- file_hash
- size_bytes

**Prediction**
- case_id
- model_version
- raw_probabilities (optional)
- created_at

**Report**
- case_id
- report_text
- pdf_path
- embedding_vector (pgvector, optional for later)

---

### 7.2 API endpoints (MVP)

1) `POST /api/auth/login`
2) `POST /api/cases/`  → create case + upload EDF file(s)
3) `POST /api/cases/{id}/process` → start processing job
4) `GET /api/cases/{id}/status` → progress
5) `GET /api/cases/{id}` → final output
6) `GET /api/cases/{id}/report` → download report

---

## 8) Frontend (React) — What to Build

Pages:
1) Login
2) Upload EDF
3) Cases dashboard (list of all cases)
4) Case details page:
   - label + probability
   - charts
   - download report button
5) Model info page (accuracy, CV method, model version)

---

## 9) Critical Situations (Wrong / Corrupted / Rubbish Input)

This is how we handle it safely:

### 9.1 Frontend validation
- accept only `.edf`
- size limit
- show warning for invalid input

### 9.2 Backend validation (must-have)
Even if frontend fails, backend protects:

- try to read file with MNE:
  - if fails → reject: `400 Invalid EDF`
- check channels:
  - if missing required channels → pad zeros OR reject
- check epochs after artifact rejection:
  - if too few epochs remain → mark case FAILED and explain
- if user uploads PDF / image:
  - reject immediately

### 9.3 Safe responses
Return clear error messages like:
- `INVALID_FILE_TYPE`
- `EDF_READ_FAILED`
- `INSUFFICIENT_CLEAN_EPOCHS`
- `PROCESSING_ERROR`

---

## 10) Visuals / Charts (from your current saved arrays)

In your current processed dataset:
- Total epoch samples: **3801**
- Healthy epochs (0): **1969**
- MDD epochs (1): **1832**
- Total unique subject groups: **58**

(Charts are provided separately as images.)

---

## 11) Step-by-Step Build Plan (When to do what)

### Week 1 — Make ML code production-ready
- move notebook code into python modules:
  - `preprocess.py`
  - `features.py`
  - `predict.py`
- export model artifacts:
  - `model.joblib`
  - `meta.json`

### Week 2 — Django backend + DB
- create models + migrations
- upload endpoint
- Celery task to process EDF and run prediction

### Week 3 — React frontend
- upload page + dashboard + case details
- status polling

### Week 4 — Reports + charts
- generate PDF report
- show PSD band charts in UI

### Week 5 — Hardening
- test cases
- logging
- input validation
- performance improvements

### Week 6 — Deployment
- Docker compose: backend + worker + redis + postgres
- deploy to cloud (Render/Railway/AWS)

---

## 12) Future Upgrade (Project-only AI Agent)
Later, you can add a restricted agent:
- it answers only from:
  - your reports
  - your documentation
  - your case history
- embeddings stored in pgvector
- if no relevant context found → it refuses (project-only knowledge)

---

# End
If you want, next I can generate:
1) Django DB schema SQL
2) DRF serializers + views skeleton
3) Celery task code template
4) React pages skeleton
