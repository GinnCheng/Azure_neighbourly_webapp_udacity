FROM python:3.11-slim

# 设置工作目录
WORKDIR /app

# 复制依赖
COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

# 复制代码
COPY neighbourlydash.py .

# Dash 默认监听 8050，我们统一用 8051
EXPOSE 8051

# 用 gunicorn 跑 Dash（比 python xxx.py 稳定）
CMD ["gunicorn", "-b", "0.0.0.0:8051", "neighbourlydash:server"]
