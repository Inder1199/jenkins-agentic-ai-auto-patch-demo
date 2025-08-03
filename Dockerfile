FROM python:3.11-slim

# Create non-root user
RUN useradd -m -s /bin/bash appuser

COPY sample_app/ /app/
WORKDIR /app

RUN pip install --no-cache-dir -r requirements.txt

# Switch to non-root user
USER appuser

CMD ["python", "vulnerable.py"]
