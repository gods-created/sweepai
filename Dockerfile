FROM python:3.14-slim 

COPY . /app

WORKDIR /app 

EXPOSE 8001

RUN apt-get update
RUN pip install --upgrade --no-cache-dir -r requirements.txt
RUN chmod +x /app/entrypoint.sh 

STOPSIGNAL SIGQUIT

HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 NONE 
ENTRYPOINT [ "/app/entrypoint.sh" ]