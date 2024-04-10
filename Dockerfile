FROM python:3.12-slim
WORKDIR /script
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY resource-check.py .

CMD ["python", "script.py", "/input.yaml"]  