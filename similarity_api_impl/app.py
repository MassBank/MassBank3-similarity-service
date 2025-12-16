import os
import sys

# Add the 'gen' directory to the PYTHONPATH
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../gen'))

import connexion
from flask_cors import CORS
import logging
import threading
from similarity_api import encoder
from waitress import serve
from flask import redirect,request
from similarity_api_impl.spectra_loader import spectra_loader

VERBOSE = os.environ.get('VERBOSE', "false")
CONTEXT_PATH = os.environ.get('CONTEXT_PATH', '')
logging.basicConfig(
    format='%(asctime)s %(name)s %(levelname)-8s %(message)s',
    level=logging.INFO,
    datefmt='%Y-%m-%d %H:%M:%S')

app = connexion.App(__name__, specification_dir='..')
app.app.json_encoder = encoder.JSONEncoder
app.add_api('openapi.yaml',
            base_path=CONTEXT_PATH,
            arguments={'title': 'Similarity score api for MassBank'},
            pythonic_params=True)
CORS(app.app)

# Create and start a thread to run spectra_loader.load_spectra()
init_thread = threading.Thread(target=spectra_loader.load_spectra)
init_thread.start()
# Enable verbose logging if set
@app.app.before_request
def log_request_info():
    if VERBOSE == "true":
        logging.getLogger('waitress').setLevel(logging.DEBUG)
        app.app.logger.info(f"{request.method} {request.path} from {request.remote_addr}")


@app.app.route(f'{CONTEXT_PATH}/')
def index():
    return redirect(f'{CONTEXT_PATH}/ui/')


def serve_app():
    serve(app, threads=1, listen='*:8080')
