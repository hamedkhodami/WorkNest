FROM docker.arvancloud.ir/python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1

ENV PYTHONUNBUFFERED=1

WORKDIR /app

COPY requirements.txt /app/
RUN pip install --upgrade pip && pip3 install -r requirements.txt

COPY src /app/src

EXPOSE 8000

ENTRYPOINT ["python", "src/manage.py"]
CMD ["runserver", "0.0.0.0:8000"]
