# --- Stage 1: Build and Install Dependencies ---
FROM python:3.11-slim AS builder

WORKDIR /app
    
# Install system build dependencies if any packages require compilation
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Copy only requirements to leverage Docker cache
COPY requirements.txt .

# Install dependencies into a user deployment folder
RUN pip install --no-cache-dir --user -r requirements.txt


# --- Stage 2: Final Lightweight Runtime ---
FROM python:3.11-slim AS runtime

WORKDIR /app

# Prevent Python from writing .pyc files and enable unbuffered logging
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Copy installed dependencies from the builder stage
COPY --from=builder /root/.local /root/.local
ENV PATH=/root/.local/bin:$PATH

# Copy application source code
COPY server.py .
COPY rag_code.py .

# FastMCP default port is 8000
EXPOSE 8000

# Run the MCP Server
CMD ["python", "server.py"]