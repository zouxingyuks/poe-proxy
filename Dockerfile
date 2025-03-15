FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# 设置默认端口
ENV PORT=8080

EXPOSE 8080

CMD ["python", "app.py"]