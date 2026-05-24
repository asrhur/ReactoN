# ReactoN Installation Guide

This document outlines the step-by-step setup procedure to establish a local engineering and testing environment for the **ReactoN** computational platform.

---

## 📋 System Requirements
- **Operating System:** Windows, macOS, or Linux.
- **Python Version:** $\ge 3.9$ (Python 3.10 or 3.11 recommended).
- **Git:** Installed and available on your system path.

---

## 🛠️ Step-by-Step Installation

### Step 1: Clone the Repository
Clone the private development repository from GitHub:
```bash
git clone https://github.com/asrhur/ReactoN.git
cd ReactoN
```

### Step 2: Establish Virtual Environment
Creating a virtual environment ensures isolated dependency management:
```bash
# On Windows
python -m venv venv
venv\Scripts\activate

# On macOS/Linux
python3 -m venv venv
source venv/bin/activate
```

### Step 3: Install Package Dependencies
Install pinned packaging, scientific, and testing dependencies from `requirements.txt`:
```bash
pip install -r requirements.txt
```

### Step 4: Install in Development Mode
Install the package locally in editable (`-e`) development mode to enable direct importing:
```bash
pip install -e .
```

---

## 🧪 Verifying the Installation

To verify that the scientific packages and API layers are operating correctly, run the full test suite:
```bash
pytest --cov=reacton tests/ -v
```

All unit and integration tests should pass successfully.

---

## 📡 Running the Automation API Server
Start the local FastAPI service:
```bash
uvicorn reacton.api.server:app --host 127.0.0.1 --port 8000 --reload
```
Open your browser and navigate to [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs) to access the interactive OpenAPI documentation panel.
