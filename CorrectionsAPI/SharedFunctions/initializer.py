import azure.functions as func
import json

from SharedFunctions import global_vars, authenticator


def get_response(authenticated, auth_response, invalid_params, token_missing, invalid_user):
    # authenticate user based on token
    errors = []
    status_code = 400
    if token_missing:
        errors.append("token missing")
    if invalid_params:
        errors.append("missing query params")
    if invalid_user:
        errors.append("invalid github nickname")
    if not authenticated:
        errors.append(auth_response)
        status_code = 401

    return func.HttpResponse(json.dumps({"status": "error", "details": errors}), headers=global_vars.HEADER, status_code=status_code)


def get_route_params(route_params, req):
    # get route params
    if route_params is not None:
        route_params_obj = {}
        missing_query_params = False
        for param in route_params:
            value = req.route_params.get(param)
            if value is None:
                missing_query_params = True
            route_params_obj[param] = value

        return route_params_obj if not missing_query_params else None


def get_body_params(body_params, req):
    # get body params
    if body_params is not None:
        body_params_obj = {}
        missing_body_params = False
        for param in body_params:
            # get params from body
            try:
                req_body = req.get_json()
            except ValueError:
                body_params_obj[param] = None
                missing_body_params = True
            else:
                body_params_obj[param] = req_body.get(param)

        return body_params_obj if not missing_body_params else None


def get_token(req):
    # get token and set flag if it fails
    try:
        token = req.headers.__http_headers__["authorization"].split(" ")[
            1]
    except Exception:
        token = None

    return token


def initialize(req, route_params=None, body_params=None):
    route_params_obj = get_route_params(
        route_params, req)
    body_params_obj = get_body_params(body_params, req)
    token = get_token(req)

    # authenticate
    if token is not None:
        authenticated, auth_response = authenticator.authenticate(token)
    else:
        authenticated = None
        auth_response = None

    return {
        "route_params_obj": route_params_obj,
        "body_params_obj": body_params_obj,
        "token": token,
        "authenticated": authenticated,
        "auth_response": auth_response,
    }
