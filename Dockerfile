FROM python:3.12-slim-buster
WORKDIR /script
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY resources-check.py .
CMD ["python", "script.py", "/input.yaml"]  