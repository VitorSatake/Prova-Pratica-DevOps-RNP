FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt
COPY ping_agent.py ./
EXPOSE 8000
CMD ["python","ping_agent.py"]