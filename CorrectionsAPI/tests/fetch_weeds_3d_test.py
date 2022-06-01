import unittest
import azure.functions as func
from requests.structures import CaseInsensitiveDict
import os
import json

from FetchWeeeds3D import main  # import the method we want to test
from unittest import mock
from SharedFunctions.set_environment_variables import set_variables
# Note how the class name starts with Test

CODES = ["DET", "ABCDE"]

URL = 'weeds3d/videos'

set_variables()
token = os.environ["USER_TOKEN"]

HEADERS = CaseInsensitiveDict()
HEADERS["Accept"] = "application/json"
HEADERS["Authorization"] = "Bearer {}".format(token)

invalid_token = os.environ["EXPIRED_USER_TOKEN"]

EXPIRED_HEADERS = CaseInsensitiveDict()
EXPIRED_HEADERS["Accept"] = "application/json"
EXPIRED_HEADERS["Authorization"] = "Bearer {}".format(invalid_token)


class TestAddToTechnicians(unittest.TestCase):
    def test_good_response(self):
        request = func.HttpRequest(
            method='POST',
            url=URL,
            body=json.dumps({'codes': CODES}).encode(),
            headers=HEADERS
        )

        response = main(request)
        json_response = json.loads(response.get_body())

        print(json_response)

        assert response.status_code == 201
        assert json_response["status"] == "success"
        assert len(json_response["files"]) > 0

    def test_bad_invalid_code(self):
        request = func.HttpRequest(
            method='POST',
            url=URL,
            body=json.dumps({'codes': ['XYZ']}).encode(),
            headers=HEADERS
        )

        response = main(request)
        json_response = json.loads(response.get_body())
        print(json_response)

        assert response.status_code == 400
        assert "no files" in json_response["details"]

    def test_no_body_params(self):
        request = func.HttpRequest(
            method='POST',
            body=None,
            url=URL,
            headers=HEADERS
        )

        response = main(request)
        json_response = json.loads(response.get_body())
        print(json_response)

        assert response.status_code == 500

    def test_no_token(self):
        request = func.HttpRequest(
            method='POST',
            body=json.dumps({'code': CODES}).encode(),
            url=URL,
        )

        response = main(request)
        json_response = json.loads(response.get_body())
        print(json_response)

        assert response.status_code == 401
        assert "token missing" in json_response["details"]

    def test_expired_token(self):
        request = func.HttpRequest(
            method='POST',
            body=json.dumps({'code': CODES}).encode(),
            url=URL,
            headers=EXPIRED_HEADERS
        )

        response = main(request)
        json_response = json.loads(response.get_body())
        print(json_response)

        assert response.status_code == 401
        assert "token_expired" in str(json_response["details"])
