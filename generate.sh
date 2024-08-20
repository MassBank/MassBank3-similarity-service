#!/usr/bin/env bash
SCRIPT_DIR=$( cd -- "$( dirname -- "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )
mkdir -p ${SCRIPT_DIR}/openapi-generator
OPENAPI_GENERATOR=${SCRIPT_DIR}/openapi-generator/openapi-generator-cli.sh
#export OPENAPI_GENERATOR_VERSION=7.8.0
curl https://raw.githubusercontent.com/OpenAPITools/openapi-generator/master/bin/utils/openapi-generator-cli.sh > ${OPENAPI_GENERATOR}
chmod +x ${OPENAPI_GENERATOR}
${OPENAPI_GENERATOR} generate -c ${SCRIPT_DIR}/config-openapi.yaml
