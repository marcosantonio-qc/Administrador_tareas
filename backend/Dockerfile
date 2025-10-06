FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    DEBIAN_FRONTEND=noninteractive

# Install MS SQL ODBC Driver 18 and tools
RUN apt-get update && apt-get install -y curl gnupg2 apt-transport-https ca-certificates && \
    curl https://packages.microsoft.com/keys/microsoft.asc | gpg --dearmor > /etc/apt/trusted.gpg.d/microsoft.gpg && \
    . /etc/os-release && \
    echo "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/trusted.gpg.d/microsoft.gpg] https://packages.microsoft.com/debian/$(. /etc/os-release && echo $VERSION_ID)/prod $(. /etc/os-release && echo $VERSION_CODENAME) main" > /etc/apt/sources.list.d/mssql-release.list && \
    apt-get update && ACCEPT_EULA=Y apt-get install -y msodbcsql18 mssql-tools18 unixodbc-dev build-essential && \
    echo 'export PATH="$PATH:/opt/mssql-tools18/bin"' >> /etc/profile && \
    ln -s /opt/mssql-tools18/bin/sqlcmd /usr/local/bin/sqlcmd && \
    ln -s /opt/mssql-tools18/bin/bcp /usr/local/bin/bcp && \
    rm -rf /var/lib/apt/lists/*

WORKDIR /app
COPY requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir -r /app/requirements.txt

COPY app /app/app

EXPOSE 8000
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
