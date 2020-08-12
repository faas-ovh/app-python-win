# https://medium.com/@mike.p.moritz/using-docker-compose-to-deploy-a-lightweight-python-rest-api-with-a-job-queue-37e6072a209b
FROM python:3.6-alpine
RUN adduser -D myproj
WORKDIR /home/myproj
COPY requirements.txt requirements.txt
RUN pip install -r requirements.txt
COPY api.py ./
RUN chown -R myproj:myproj ./
USER myproj
CMD uvicorn api:app --host 0.0.0.0 --port 5057
