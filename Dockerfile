FROM python:3.8.19-slim

ENV PYTHONUNBUFFERED True

ENV APP_HOME /app
WORKDIR $APP_HOME
COPY requirements.txt ./
COPY chat_app/ ./chat_app/

ENV PORT 8080
ENV GOOGLE_CLOUD_PROJECT foodie-355420

RUN pip install --no-cache-dir -r requirements.txt

# As an example here we're running the web service with one worker on uvicorn.
CMD exec uvicorn chat_app.main:app --host 0.0.0.0 --port ${PORT} --workers 1