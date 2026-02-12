# Backend Testing Guide

Local quick test (no venv):

```bash
# Run tests using system Python (adds `backend` to PYTHONPATH)
PYTHONPATH=backend python3 -m pytest -q
```

Create a proper venv and install dependencies:

```bash
sudo apt update && sudo apt install python3.12-venv -y
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip setuptools wheel
python -m pip install -r backend/requirements.txt
pytest -q
```

Run tests inside Docker (recommended for CI-like environment):

```bash
docker build -t future-backend:dev backend
docker run --rm future-backend:dev sh -c "cd backend && PYTHONPATH=. pytest -q"
```

Notes:
- If Docker isn't available locally, use the GitHub Actions workflow `.github/workflows/ci.yml` which builds the same image and runs tests in CI.
- The project pins `pydantic==2.x` and `pydantic-settings`; ensure those are installed in your venv.
