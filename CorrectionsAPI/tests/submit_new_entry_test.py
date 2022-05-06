import unittest
import azure.functions as func
from requests.structures import CaseInsensitiveDict
import os
import json

from SubmitNewEntry import main  # import the method we want to test
from SharedFunctions.set_environment_variables import set_variables
# Note how the class name starts with Test

URL = "tech-dashboard/kobo"

BODY = {
    "data": "test data from python_api",
    "asset_name": "psa biomass",
    "id": 152198403,
    "xform_id_string": "test xform",
    "uid": 2430
}

# Arrange
set_variables()
token = os.environ["USER_TOKEN"]

HEADERS = CaseInsensitiveDict()
HEADERS["Accept"] = "application/json"
HEADERS["Authorization"] = "Bearer {}".format(token)

invalid_token = os.environ["EXPIRED_USER_TOKEN"]

EXPIRED_HEADERS = CaseInsensitiveDict()
EXPIRED_HEADERS["Accept"] = "application/json"
EXPIRED_HEADERS["Authorization"] = "Bearer {}".format(invalid_token)


class TestCreateGithubIssue(unittest.TestCase):
    def test_good_response(self):
        request = func.HttpRequest(
            method='POST',
            url=URL,
            body=json.dumps(BODY).encode(),
            headers=HEADERS
        )

        response = main(request)
        json_response = json.loads(response.get_body())

        print(json_response)

        assert response.status_code == 201
        assert json_response.get("status") == "success"
        assert "152198403" in json_response.get("details")
        assert "psa biomass" in json_response.get("details")
        assert "test data" in json_response.get("details")
        assert "test xform" in json_response.get("details")

    def test_invalid_uid(self):
        BODY["uid"] = 1000000
        request = func.HttpRequest(
            method='POST',
            url=URL,
            body=json.dumps(BODY).encode(),
            headers=HEADERS
        )

        response = main(request)
        json_response = json.loads(response.get_body())
        print(json_response)

        assert response.status_code == 400
        assert "failed to set resolved" in json_response["details"]

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
            url=URL,
            body=json.dumps(BODY).encode(),
        )

        response = main(request)
        json_response = json.loads(response.get_body())
        print(json_response)

        assert response.status_code == 401
        assert "token missing" in json_response["details"]

    def test_expired_token(self):
        request = func.HttpRequest(
            method='POST',
            route_params={'code': 'QUU'},
            url=URL,
            body=json.dumps(BODY).encode(),
            headers=EXPIRED_HEADERS
        )

        response = main(request)
        json_response = json.loads(response.get_body())
        print(json_response)

        assert response.status_code == 401
        assert "token_expired" in str(json_response["details"])
