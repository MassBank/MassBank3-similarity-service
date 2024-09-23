import os

import connexion
import logging

from similarity_service import encoder
from waitress import serve

VERBOSE = os.environ.get('VERBOSE', "false")

app = connexion.App(__name__, specification_dir='..')
app.app.json_encoder = encoder.JSONEncoder
app.add_api('openapi.yaml',
            arguments={'title': 'Similarity score api for MassBank3'},
            pythonic_params=True)



def serve_app():
    if VERBOSE == "true":
        from paste.translogger import TransLogger
        logging.getLogger('waitress').setLevel(logging.INFO)
        serve(TransLogger(app, setup_console_handler=False), listen='*:8080')
    else:
        serve(app, listen='*:8080')
