import logging
import os
import threading
from datetime import datetime

import connexion
import numpy
from matchms import calculate_scores, set_matchms_logger_level, Spectrum
from matchms.filtering import normalize_intensities
from matchms.importing import load_from_msp
from matchms.similarity import CosineGreedy

from similarity_service.models import SimilarityScore
from similarity_service.models.similarity_calculation import SimilarityCalculation  # noqa: E501
from similarity_service.models.similarity_score_list import SimilarityScoreList  # noqa: E501

# Environment variables
MSP = os.environ.get('MSP', "./MassBank_NIST.msp")
VERBOSE = os.environ.get('VERBOSE', "false")

# Global variables for in-memory data
timestamp = datetime.fromisoformat('2010-01-01')
spectra = []

# Lock for thread safety
lock = threading.Lock()

# set log level
set_matchms_logger_level("ERROR")

logger = logging.getLogger('similarity_service_impl_controller')
print(__name__)
if VERBOSE == "true":
    logger.setLevel(logging.DEBUG)

def load_spectra():
    """load all spectra from the given msp file"""
    global timestamp, MSP, spectra
    with lock:
        file_timestamp = datetime.fromtimestamp(os.path.getmtime(MSP))
        logger.debug("In-memory timestamp of reference spectra: %s", timestamp)
        logger.debug("Reference spectra data file timestamp: %s", file_timestamp)
        timestamp_diff = file_timestamp - timestamp
        if timestamp_diff.total_seconds() > 0:
            logger.info("Reference spectra data file timestamp is %s newer. Reloading...", timestamp_diff)
            spectra = list(load_from_msp(MSP))
            timestamp = file_timestamp
            logger.info("Finished. Loaded %s spectra from the data file.", len(spectra))



def similarity_post(similarity_calculation):  # noqa: E501
    """Create a new similarity calculation.

     # noqa: E501

    :param similarity_calculation: a similarity job
    :type similarity_calculation: dict | bytes

    :rtype: Union[SimilarityScoreList, Tuple[SimilarityScoreList, int], Tuple[SimilarityScoreList, int, Dict[str, str]]
    """
    if connexion.request.is_json:
        request = SimilarityCalculation.from_dict(similarity_calculation)

        load_spectra()

        mz, intensities = zip(*[(peak.mz, peak.intensity) for peak in request.peak_list])
        logger.debug("Got spectra: %s", request.peak_list)

        try:
            query = normalize_intensities(Spectrum(mz=numpy.array(mz), intensities=numpy.array(intensities)))
        except AssertionError as e:
            return connexion.problem(
                title="AssertionError",
                detail=str(e),
                status=400,
            )

        logger.debug("Got %s reference spectra.", len(request.reference_spectra_list))
        references = spectra
        if request.reference_spectra_list:
            references = [s for s in references if s.metadata['spectrum_id'] in request.reference_spectra_list]
        logger.debug("Use %s for calculation.", len(references))

        scores = calculate_scores(references, [query], CosineGreedy())
        matches = scores.scores_by_query(query, 'CosineGreedy_score', sort=True)
        match_list = SimilarityScoreList(
            [SimilarityScore(match[0].metadata['spectrum_id'], match[1][0]) for match in matches])

        logger.debug("Calculated scores for %s similar spectra.", len(match_list.similarity_score_list))
        return match_list


def version_get():  # noqa: E501
    """Get the version string of the implementation.

     # noqa: E501


    :rtype: Union[str, Tuple[str, int], Tuple[str, int, Dict[str, str]]
    """
    return 'similarity service 0.1'



