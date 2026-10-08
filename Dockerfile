FROM mcr.microsoft.com/playwright/python:v1.55.0-noble
WORKDIR /app
ENV PYTHONUNBUFFERED=1 PIP_NO_CACHE_DIR=1 STREAMLIT_BROWSER_GATHER_USAGE_STATS=false
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
EXPOSE 10000
CMD ["bash", "-lc", "streamlit run app.py --server.address=0.0.0.0 --server.port=${PORT:-10000} --server.headless=true --server.enableCORS=false --server.enableXsrfProtection=false"]
