# ---------------- BASE IMAGE ----------------
FROM python:3.10-slim

# ---------------- SYSTEM DEPS ----------------
RUN apt-get update && apt-get install -y \
    ffmpeg \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# ---------------- WORKDIR ----------------
WORKDIR /app

# ---------------- INSTALL PYTHON DEPS ----------------
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# ---------------- COPY APP CODE ----------------
COPY . .

# ---------------- STREAMLIT CONFIG ----------------
ENV STREAMLIT_SERVER_PORT=8080
ENV STREAMLIT_SERVER_ADDRESS=0.0.0.0
ENV STREAMLIT_BROWSER_GATHER_USAGE_STATS=false

# ---------------- EXPOSE PORT ----------------
EXPOSE 8080

# ---------------- START APP ----------------
CMD ["streamlit", "run", "app.py", "--server.port=8080", "--server.address=0.0.0.0"]
