import unittest
import os
from flask import json
from similarity_service.models import Peak, SimilarityCalculation
from similarity_service.test import BaseTestCase

#set MSP to the test data
os.environ["MSP"] = os.path.join(os.path.dirname(__file__), 'test_data.msp')

class TestSimilarityServiceImplController(BaseTestCase):

    def setUp(self):
        self.headers = {
            'Accept': 'application/json',
            'Content-Type': 'application/json',
        }

    def test_similarity_post_with_reference_spectra_list(self):
        """Test case for similarity_post with a reference spectra list
        """
        similarity_calculation = SimilarityCalculation(
            peak_list=[
                Peak(mz=147.063, intensity=121.684),
                Peak(mz=303.050, intensity=10000.000),
                Peak(mz=449.108, intensity=657.368),
                Peak(mz=465.102, intensity=5884.210),
                Peak(mz=611.161, intensity=6700.000)],
            reference_spectra_list=[
                "MSBNK-IPB_Halle-PB001341",
                "MSBNK-IPB_Halle-PB001342",
                "MSBNK-IPB_Halle-PB001343",
                "MSBNK-IPB_Halle-PB006202",
                "MSBNK-IPB_Halle-PB006203"],
            similarity_fn="cosine")
        response = self.client.open(
            '/similarity',
            method='POST',
            headers=self.headers,
            data=json.dumps(similarity_calculation),
            content_type='application/json')
        self.assert200(response,
                       'Response body is : ' + response.data.decode('utf-8'))
        self.assertEqual(
            first=response.json,
            second={'similarity_score_list': [
                {'accession': 'MSBNK-IPB_Halle-PB001341', 'similarity_score': 0.9999987337877411},
                {'accession': 'MSBNK-IPB_Halle-PB001342', 'similarity_score': 0.9997024900194288},
                {'accession': 'MSBNK-IPB_Halle-PB006202', 'similarity_score': 0.7797803260380126},
                {'accession': 'MSBNK-IPB_Halle-PB001343', 'similarity_score': 0.7453832548137632},
                {'accession': 'MSBNK-IPB_Halle-PB006203', 'similarity_score': 0.7448505386345436}
            ]})

    def test_similarity_post_with_empty_reference_spectra_list(self):
        """Test case for similarity_post with an empty reference spectra list
        """
        similarity_calculation = SimilarityCalculation(
            peak_list=[
                Peak(mz=147.063, intensity=121.684),
                Peak(mz=303.050, intensity=10000.000),
                Peak(mz=449.108, intensity=657.368),
                Peak(mz=465.102, intensity=5884.210),
                Peak(mz=611.161, intensity=6700.000)],
            reference_spectra_list=[],
            similarity_fn="cosine")
        response = self.client.open(
            '/similarity',
            method='POST',
            headers=self.headers,
            data=json.dumps(similarity_calculation),
            content_type='application/json')
        self.assert200(response,
                       'Response body is : ' + response.data.decode('utf-8'))
        self.assertEqual(
            first=response.json['similarity_score_list'][0:5],
            second=[
                {'accession': 'MSBNK-IPB_Halle-PB001341', 'similarity_score': 0.9999987337877411},
                {'accession': 'MSBNK-IPB_Halle-PB001342', 'similarity_score': 0.9997024900194288},
                {'accession': 'MSBNK-IPB_Halle-PB006201', 'similarity_score': 0.8742310139566003},
                {'accession': 'MSBNK-IPB_Halle-PB006202', 'similarity_score': 0.7797803260380126},
                {'accession': 'MSBNK-IPB_Halle-PB001343', 'similarity_score': 0.7453832548137632}
            ])
        self.assertTrue(len(response.json['similarity_score_list']) > 5)

    def test_similarity_post_with_only_peaklist(self):
        """Test case for similarity_post with only peaklist given
        """
        similarity_calculation = SimilarityCalculation(
            peak_list=[
                Peak(mz=147.063, intensity=121.684),
                Peak(mz=303.050, intensity=10000.000),
                Peak(mz=449.108, intensity=657.368),
                Peak(mz=465.102, intensity=5884.210),
                Peak(mz=611.161, intensity=6700.000)])
        response = self.client.open(
            '/similarity',
            method='POST',
            headers=self.headers,
            data=json.dumps(similarity_calculation),
            content_type='application/json')
        self.assert200(response,
                       'Response body is : ' + response.data.decode('utf-8'))
        self.assertEqual(
            first=response.json['similarity_score_list'][0:5],
            second=[
                {'accession': 'MSBNK-IPB_Halle-PB001341', 'similarity_score': 0.9999987337877411},
                {'accession': 'MSBNK-IPB_Halle-PB001342', 'similarity_score': 0.9997024900194288},
                {'accession': 'MSBNK-IPB_Halle-PB006201', 'similarity_score': 0.8742310139566003},
                {'accession': 'MSBNK-IPB_Halle-PB006202', 'similarity_score': 0.7797803260380126},
                {'accession': 'MSBNK-IPB_Halle-PB001343', 'similarity_score': 0.7453832548137632}
            ])
        self.assertTrue(len(response.json['similarity_score_list']) > 5)

    def test_version_get(self):
        """Test case for version_get
        """
        response = self.client.open(
            '/version',
            method='GET',
            headers=self.headers)
        self.assert200(response, 'Response body is : ' + response.data.decode('utf-8'))
        self.assertEqual(response.json, 'similarity service 0.1')


if __name__ == '__main__':
    unittest.main()
