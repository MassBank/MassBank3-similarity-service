import logging
import os
from datetime import datetime

import connexion
import numpy
from flask import jsonify
from matchms import calculate_scores, set_matchms_logger_level, Spectrum
from matchms.filtering import normalize_intensities
from matchms.similarity import CosineGreedy
from matchms.importing import load_from_msp

import os.path

from similarity_service.models import SimilarityScore
from similarity_service.models.similarity_calculation import SimilarityCalculation  # noqa: E501
from similarity_service.models.similarity_score_list import SimilarityScoreList  # noqa: E501

# Environment variables
MSP = os.environ.get('MSP', "./MassBank_NIST.msp")

# Global variables for in-memory data
timestamp = datetime.fromisoformat('2010-01-01')
spectra = []

# Global setting
logging.basicConfig(level="INFO")
set_matchms_logger_level("ERROR")

def load_spectra():
    """load all spectra from the given msp file"""
    global timestamp, MSP, spectra
    file_timestamp = datetime.fromtimestamp(os.path.getmtime(MSP))
    timestamp_diff = file_timestamp - timestamp
    if timestamp_diff.total_seconds() > 0:
        spectra = list(load_from_msp(MSP))
        timestamp = file_timestamp

def similarity_post(similarity_calculation):  # noqa: E501
    """Create a new similarity calculation.

     # noqa: E501

    :param similarity_calculation: a similarity job
    :type similarity_calculation: dict | bytes

    :rtype: Union[SimilarityScoreList, Tuple[SimilarityScoreList, int], Tuple[SimilarityScoreList, int, Dict[str, str]]
    """
    if connexion.request.is_json:
        request = SimilarityCalculation.from_dict(similarity_calculation)

        # try:
        load_spectra()
        # except psycopg.DatabaseError as e:
        #     return connexion.problem(
        #         title="Database Error",
        #         detail=str(e),
        #         status=500,
        #     )

        mz, intensities = zip(*[(peak.mz, peak.intensity) for peak in request.peak_list])

        try:
            query = normalize_intensities(Spectrum(mz=numpy.array(mz), intensities=numpy.array(intensities)))
        except AssertionError as e:
            return connexion.problem(
                title="AssertionError",
                detail=str(e),
                status=400,
            )

        references = spectra
        if request.reference_spectra_list:
            references = [s for s in references if s.metadata['spectrum_id'] in request.reference_spectra_list]

        scores = calculate_scores(references, [query], CosineGreedy())
        matches = scores.scores_by_query(query, 'CosineGreedy_score', sort=True)
        match_list = SimilarityScoreList(
            [SimilarityScore(match[0].metadata['spectrum_id'], match[1][0]) for match in matches])

        return match_list


def version_get():  # noqa: E501
    """Get the version string of the implementation.

     # noqa: E501


    :rtype: Union[str, Tuple[str, int], Tuple[str, int, Dict[str, str]]
    """
    return 'similarity similarity 0.1.0'


def handle_psycopg_database_error(error):
    response = jsonify(error.to_dict())
    response.status_code = error.status_code
    return response
