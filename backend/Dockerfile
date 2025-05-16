# 使用官方 Python 作为基础镜像
FROM python:3.9

# 设置工作目录
WORKDIR /app

# 复制requirements.txt文件
COPY requirements.txt /app/

# 安装项目依赖
RUN pip install --no-cache-dir -r requirements.txt

# 将当前目录内容复制到容器的 /app 目录
COPY . /app

# 设置 PYTHONPATH 环境变量
ENV PYTHONPATH=/app

# 暴露端口
EXPOSE 8000

# 设置默认启动命令
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]





