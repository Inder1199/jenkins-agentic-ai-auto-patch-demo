FROM python:3.11
COPY sample_app/ /app/
WORKDIR /app
RUN pip install -r requirements.txt
CMD ["python", "vulnerable.py"]
