import unittest
import azure.functions as func
from requests.structures import CaseInsensitiveDict
import os
import json

from UpdateProtocolEnrollment import main  # import the method we want to test
from SharedFunctions.set_environment_variables import set_variables
# Note how the class name starts with Test

URL = "crowndb/protocol_enrollment/quu"

BODY = {
    "code": "QUU",
    "protocols": {
        "sensor_data": 1,
        "bulk_density": 0,
        "corn_disease": None,
        "farm_history": 0,
        "soil_texture": 1,
        "gps_locations": 0,
        "soil_nitrogen": 0,
        "yield_monitor": None,
        "decomp_biomass": -999,
        "cash_crop_yield": 1,
        "in_field_biomass": -999,
        "weed_visual_rating": None,
        "weed_quadrat_photos_beta": 1
    }
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
            route_params={'code': 'QUU'},
            body=json.dumps(BODY).encode(),
            headers=HEADERS
        )

        response = main(request)
        json_response = json.loads(response.get_body())

        print(json_response)

        assert response.status_code == 201
        assert json_response.get("status") == "success"
        assert "QUU" in json_response.get("details")

    def test_invalid_github_user(self):
        request = func.HttpRequest(
            method='POST',
            url=URL,
            route_params={'code': 'oansddasd'},
            body=json.dumps(BODY).encode(),
            headers=HEADERS
        )

        response = main(request)
        json_response = json.loads(response.get_body())
        print(json_response)

        assert response.status_code == 400
        assert "failed to update protocol enrollment" in json_response["details"]

    def test_no_query_params(self):
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
        assert "missing query params" in json_response["details"]

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
