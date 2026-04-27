FROM python:3.11-slim

WORKDIR /app

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

COPY requirements.txt ./

RUN python - <<'PY'
from pathlib import Path

path = Path("requirements.txt")
data = path.read_bytes()
if data.startswith(b"\xff\xfe") or data.startswith(b"\xfe\xff"):
    path.write_text(data.decode("utf-16"), encoding="utf-8")
PY

RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

COPY . ./

EXPOSE 8000

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
