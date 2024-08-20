# MassBank3-similarity-service
A REST interface wrapping [matchms](https://github.com/matchms/matchms) for MassBank3.

This server was generated by the [OpenAPI Generator](https://openapi-generator.tech) project and uses
the [Connexion](https://github.com/zalando/connexion) library on top of Flask.

## Requirements
Tested on Python 3.12

## Configuration
This microservice is configured with environment variables. The following variables and
default values are used:
```
DB_PORT = 5432
DB_USER = "massbank3"
DB_PASSWORD = "massbank3password"
DB_NAME = "massbank3"
DB_HOST = "localhost"
```

## Usage
To run the server, please generate the server code, install the requirements 
and start the server like this:
```bash
bash generate.sh
pip3 install -r requirements.txt
PYTHONPATH=gen python3 -m cosine_impl
```
You can find the swagger ui at http://localhost:8080/ui/ and the
OpenAPI definition at http://localhost:8080/openapi.json in your browser.

## Running with Docker

To run the server on a Docker container, please execute the following from the root directory:

```bash
# building the image
docker build -t openapi_server .

# starting up a container
docker run -p 8080:8080 openapi_server
```