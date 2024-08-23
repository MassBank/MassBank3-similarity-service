FROM maven:3.9-eclipse-temurin-21
RUN apt-get update && apt-get install -y --no-install-recommends jq && rm -rf /var/lib/apt/lists/*

COPY generate.sh config-openapi.yaml openapi.yaml /usr/src/app/

WORKDIR /usr/src/app
RUN bash generate.sh

FROM python:3.12-slim-bookworm
WORKDIR /usr/src/app
COPY requirements.txt /usr/src/app/
RUN pip3 install --root-user-action=ignore --upgrade pip && pip3 install --root-user-action=ignore --no-cache-dir -r requirements.txt

COPY --from=0 /usr/src/app/openapi.yaml /usr/src/app/openapi.yaml
COPY --from=0 /usr/src/app/gen /usr/src/app/gen
COPY similarity_service_impl /usr/src/app/similarity_service_impl

ENV PYTHONPATH=/usr/src/app/gen

EXPOSE 8080/tcp
ENTRYPOINT ["/usr/local/bin/waitress-serve"]
CMD ["--port=8080", "similarity_service_impl.app:app"]