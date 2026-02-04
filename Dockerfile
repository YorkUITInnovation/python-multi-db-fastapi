# syntax=docker/dockerfile:1
# Use Ubuntu 24.04 LTS as base image for better package compatibility
# Platform: linux/amd64 (x86_64) only - required for Oracle Instant Client
FROM --platform=linux/amd64 ubuntu:24.04

# Set working directory
WORKDIR /app

# Install Python 3.12 and system dependencies required for database drivers
RUN apt-get update && apt-get install -y \
    # Python 3.12 and pip
    python3.12 \
    python3.12-venv \
    python3-pip \
    # For Oracle Instant Client
    wget \
    unzip \
    libaio1t64 \
    libnsl2 \
    # For SQL Server ODBC driver
    curl \
    gnupg \
    apt-transport-https \
    # For PostgreSQL
    libpq-dev \
    # For MySQL
    default-libmysqlclient-dev \
    pkg-config \
    # Build essentials
    gcc \
    g++ \
    && rm -rf /var/lib/apt/lists/* \
    # Create symlink for Oracle Instant Client compatibility (libaio.so.1 -> libaio.so.1t64)
    && ln -s /usr/lib/x86_64-linux-gnu/libaio.so.1t64 /usr/lib/x86_64-linux-gnu/libaio.so.1 \
    && ldconfig

# Set Python 3.12 as default python3
RUN update-alternatives --install /usr/bin/python3 python3 /usr/bin/python3.12 1 \
    && update-alternatives --install /usr/bin/python python /usr/bin/python3.12 1

# Install Microsoft ODBC Driver 18 for SQL Server (Ubuntu 24.04)
RUN curl https://packages.microsoft.com/keys/microsoft.asc | gpg --dearmor -o /usr/share/keyrings/microsoft-prod.gpg \
    && curl https://packages.microsoft.com/config/ubuntu/24.04/prod.list > /etc/apt/sources.list.d/mssql-release.list \
    && apt-get update \
    && ACCEPT_EULA=Y apt-get install -y msodbcsql18 \
    && rm -rf /var/lib/apt/lists/*

# Install Oracle Instant Client
ENV ORACLE_CLIENT_VERSION=21_15
RUN wget -q https://download.oracle.com/otn_software/linux/instantclient/2115000/instantclient-basiclite-linux.x64-21.15.0.0.0dbru.zip -O /tmp/instantclient.zip \
    && unzip -q /tmp/instantclient.zip -d /opt/oracle \
    && rm /tmp/instantclient.zip \
    && echo /opt/oracle/instantclient_21_15 > /etc/ld.so.conf.d/oracle-instantclient.conf \
    && ldconfig \
    && echo "Verifying Oracle Instant Client installation:" \
    && ls -la /opt/oracle/instantclient_21_15/ | head -15 \
    && echo "Verifying libaio.so.1 symlink:" \
    && ls -la /usr/lib/x86_64-linux-gnu/libaio.so* \
    && echo "Oracle Instant Client installed successfully"

# Set Oracle Instant Client environment variable
ENV ORACLE_CLIENT_LIB=/opt/oracle/instantclient_21_15
ENV LD_LIBRARY_PATH=/opt/oracle/instantclient_21_15:${LD_LIBRARY_PATH}

# Copy requirements file
COPY requirements.txt .

# Install Python dependencies
RUN pip install --break-system-packages --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Create a non-root user to run the application
RUN useradd -m appuser && chown -R appuser:appuser /app
USER appuser

# Expose port 8082
EXPOSE 8082

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python -c "import requests; requests.get('http://localhost:8082/health')" || exit 1

# Run the application
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8082", "--workers", "4"]

