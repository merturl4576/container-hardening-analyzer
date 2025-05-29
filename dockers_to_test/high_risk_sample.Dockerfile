FROM alpine:latest
ENV ROOT_PASS=toor
ADD . /
RUN apt-get update && apt-get install -y netcat curl
EXPOSE 80
USER root
CMD ["sh"]
