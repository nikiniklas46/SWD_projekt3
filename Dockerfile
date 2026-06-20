FROM python:3.12-slim

WORKDIR /app

COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

COPY Source/ ./Source/
COPY tests/ ./tests/
COPY data/ ./data/
COPY documentation/ ./documentation/
COPY .streamlit/ ./.streamlit/

ENV PYTHONPATH=/app

EXPOSE 5000
EXPOSE 8501

CMD ["python", "Source/server.py"]