FROM python:3.12-slim
WORKDIR /script
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY resource-check.py .

COPY entrypoint.sh .
RUN chmod +x /script/entrypoint.sh

ENTRYPOINT ["python", "/script/resource-check.py"]