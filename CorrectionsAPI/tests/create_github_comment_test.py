import unittest
import azure.functions as func
from requests.structures import CaseInsensitiveDict
import os
import json

from CreateGithubComment import main  # import the method we want to test
from SharedFunctions.set_environment_variables import set_variables
# Note how the class name starts with Test

URL = "precision-sustainable-ag/repos/data_corrections/comments/mikahpinegar/495"

set_variables()
token = os.environ["USER_TOKEN"]

HEADERS = CaseInsensitiveDict()
HEADERS["Accept"] = "application/json"
HEADERS["Authorization"] = "Bearer {}".format(token)

invalid_token = os.environ["EXPIRED_USER_TOKEN"]

EXPIRED_HEADERS = CaseInsensitiveDict()
EXPIRED_HEADERS["Accept"] = "application/json"
EXPIRED_HEADERS["Authorization"] = "Bearer {}".format(invalid_token)

COMMENT = "testing comment"


class TestCreateGithubComment(unittest.TestCase):
    def test_good_response(self):
        request = func.HttpRequest(
            method='POST',
            url=URL,
            route_params={'user': 'mikahpinegar', "number": "495"},
            body=json.dumps({
                "comment": COMMENT
            }).encode(),
            headers=HEADERS
        )

        response = main(request)
        json_response = json.loads(response.get_body())

        print(json_response)

        assert response.status_code == 201
        assert json_response.get("status") == "success"
        assert "#495" in json_response.get("details")

    def test_invalid_github_user(self):
        request = func.HttpRequest(
            method='POST',
            url=URL,
            route_params={'user': 'oansddasd', "number": "495"},
            body=json.dumps({
                "comment": COMMENT
            }).encode(),
            headers=HEADERS
        )

        response = main(request)
        json_response = json.loads(response.get_body())
        print(json_response)

        assert response.status_code == 400
        assert "invalid github nickname" in json_response["details"]

    def test_invalid_issue_number(self):
        request = func.HttpRequest(
            method='POST',
            url=URL,
            route_params={'user': 'mikahpinegar', "number": "100000"},
            body=json.dumps({
                "comment": COMMENT
            }).encode(),
            headers=HEADERS
        )

        response = main(request)
        json_response = json.loads(response.get_body())
        print(json_response)

        assert response.status_code == 400
        assert "could not create comment" in json_response["details"]

    def test_no_query_params(self):
        request = func.HttpRequest(
            method='POST',
            url=URL,
            body=json.dumps({
                "comment": COMMENT
            }).encode(),
            headers=HEADERS
        )

        response = main(request)
        json_response = json.loads(response.get_body())
        print(json_response)

        assert response.status_code == 400
        assert "missing query params" in json_response["details"]

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
            body=json.dumps({
                "comment": COMMENT
            }).encode(),
        )

        response = main(request)
        json_response = json.loads(response.get_body())
        print(json_response)

        assert response.status_code == 401
        assert "token missing" in json_response["details"]

    def test_expired_token(self):
        request = func.HttpRequest(
            method='POST',
            route_params={'user': 'mikahpinegar'},
            url=URL,
            body=json.dumps({
                "comment": COMMENT
            }).encode(),
            headers=EXPIRED_HEADERS
        )

        response = main(request)
        json_response = json.loads(response.get_body())
        print(json_response)

        assert response.status_code == 401
        assert "token_expired" in str(json_response["details"])
