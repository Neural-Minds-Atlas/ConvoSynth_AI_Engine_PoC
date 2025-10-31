# RAG service Dockerfile
FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# TODO: RAG-specific startup command
CMD ["python", "-m", "src.rag_anything.client"]
