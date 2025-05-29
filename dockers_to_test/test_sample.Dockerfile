FROM ubuntu:latest
RUN apt-get update && apt-get install -y python3
USER root
CMD ["python3"]
