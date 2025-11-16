FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt
COPY http_agent.py ./
EXPOSE 8001
CMD ["python","http_agent.py"]