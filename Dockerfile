FROM python:3.12-slim
WORKDIR /script
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY resource-check.py .

CMD ["python", "resource-check.py", "/input.yaml"]  