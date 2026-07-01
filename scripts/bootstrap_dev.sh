#!/usr/bin/env bash

set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT_DIR"

VENV_DIR="venv"
RUN_TESTS=1
START_APP=0
USE_SQLITE=1
APP_HOST="0.0.0.0"
APP_PORT=8000

find_free_port() {
  local start_port="$1"
  local end_port="$2"
  local port

  for ((port=start_port; port<=end_port; port++)); do
    if ! lsof -i TCP:"$port" -sTCP:LISTEN -t >/dev/null 2>&1; then
      echo "$port"
      return 0
    fi
  done

  return 1
}

usage() {
  cat <<'EOF'
Usage: scripts/bootstrap_dev.sh [options]

Options:
  --no-tests       Skip running tests at the end
  --run-app        Start API after setup completes
  --postgres       Keep existing DATABASE_URL; do not force sqlite default
  -h, --help       Show this help message

Run behavior for --run-app:
  - If port 8000 is used by this project's uvicorn process, it is restarted.
  - If port 8000 is used by another process, a free port in 8001-8100 is used.

Examples:
  scripts/bootstrap_dev.sh
  scripts/bootstrap_dev.sh --run-app
  scripts/bootstrap_dev.sh --postgres --no-tests
EOF
}

for arg in "$@"; do
  case "$arg" in
    --no-tests)
      RUN_TESTS=0
      ;;
    --run-app)
      START_APP=1
      ;;
    --postgres)
      USE_SQLITE=0
      ;;
    -h|--help)
      usage
      exit 0
      ;;
    *)
      echo "Unknown option: $arg"
      usage
      exit 1
      ;;
  esac
done

echo "[1/7] Creating virtual environment if needed..."
if [[ ! -d "$VENV_DIR" ]]; then
  python -m venv "$VENV_DIR"
fi

echo "[2/7] Activating virtual environment..."
source "$VENV_DIR/bin/activate"

echo "[3/7] Installing dependencies..."
python -m pip install --upgrade pip
pip install -r requirements.txt
pip install -r requirements-dev.txt

echo "[4/7] Ensuring .env exists..."
if [[ ! -f .env ]]; then
  cp .env.example .env
fi

echo "[5/7] Applying safe local defaults (non-destructive)..."
if [[ "$USE_SQLITE" -eq 1 ]] && ! grep -q '^DATABASE_URL=' .env; then
  echo "DATABASE_URL=sqlite:///./local_dev.db" >> .env
fi

if ! grep -q '^SECRET_KEY=' .env; then
  echo "SECRET_KEY=dev-secret-key" >> .env
fi

if ! grep -q '^JWT_SECRET_KEY=' .env; then
  echo "JWT_SECRET_KEY=dev-jwt-secret" >> .env
fi

if ! grep -q '^OPENAI_API_KEY=' .env; then
  echo "OPENAI_API_KEY=sk-local-placeholder" >> .env
fi

echo "[6/7] Running tests..."
if [[ "$RUN_TESTS" -eq 1 ]]; then
  python -m pytest
else
  echo "Skipped tests (--no-tests)."
fi

echo "[7/7] Setup complete."
echo "Next commands:"
echo "  source venv/bin/activate"
echo "  python -m uvicorn src.main:app --host 0.0.0.0 --port 8000 --reload"

if [[ "$START_APP" -eq 1 ]]; then
  echo "Starting application..."

  if [[ "$USE_SQLITE" -eq 1 ]]; then
    export DATABASE_URL="sqlite:///./local_dev.db"
    echo "Using SQLite runtime database: $DATABASE_URL"
  fi

  existing_pid=""
  if lsof -i TCP:"$APP_PORT" -sTCP:LISTEN -t >/dev/null 2>&1; then
    existing_pid="$(lsof -i TCP:"$APP_PORT" -sTCP:LISTEN -t | head -n 1)"
  fi

  if [[ -n "$existing_pid" ]]; then
    existing_cmd="$(ps -p "$existing_pid" -o args= || true)"

    if [[ "$existing_cmd" == *"uvicorn"* ]] && [[ "$existing_cmd" == *"src.main:app"* ]]; then
      echo "Port $APP_PORT is used by existing project server (PID $existing_pid). Restarting it..."
      kill "$existing_pid"
      for _ in {1..20}; do
        if ! lsof -i TCP:"$APP_PORT" -sTCP:LISTEN -t >/dev/null 2>&1; then
          break
        fi
        sleep 0.2
      done
    else
      echo "Port $APP_PORT is occupied by a different process (PID $existing_pid)."
      free_port="$(find_free_port 8001 8100 || true)"
      if [[ -z "$free_port" ]]; then
        echo "Could not find a free port in range 8001-8100."
        exit 1
      fi
      APP_PORT="$free_port"
      echo "Using fallback port $APP_PORT."
    fi
  fi

  exec python -m uvicorn src.main:app --host "$APP_HOST" --port "$APP_PORT" --reload
fi
