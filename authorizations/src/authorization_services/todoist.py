import requests
from fastapi import HTTPException

from authorizations.src.settings import todoist_auth_settings


def authorize():
    authorization_url = (
        f"{todoist_auth_settings.todoist_oauth_api_url}?"
        f"client_id={todoist_auth_settings.todoist_client_id}&"
        f"scope={todoist_auth_settings.todoist_scope}&"
        f"state={todoist_auth_settings.todoist_state}"
    )

    return authorization_url


def callback(code: str = None, state: str = None, error: str = None):
    if state != todoist_auth_settings.todoist_state:
        raise HTTPException(status_code=400, detail="State parameter mismatch")

    token_params = {
        "client_id": todoist_auth_settings.todoist_client_id,
        "client_secret": todoist_auth_settings.todoist_client_secret,
        "code": code,
        "redirect_uri": todoist_auth_settings.todoist_redirect_url,
    }
    try:
        response = requests.post(
            todoist_auth_settings.todoist_token_exchange_api_url, data=token_params
        )
        response.raise_for_status()
        response_data = response.json()

        return response_data["access_token"]
    except requests.HTTPError:
        error_data = response.json()
        # This could happen if the code is used more than once, or if it has expired.
        if error_data.get("error") == "bad_authorization_code":
            raise HTTPException(status_code=400, detail="Bad authorization code")
        # client_id or client_secret parameters are incorrect:
        elif error_data.get("error") == "incorrect_application_credentials":
            raise HTTPException(
                status_code=401, detail="Incorrect application credentials"
            )
        else:
            raise HTTPException(status_code=500, detail="Token exchange failed")
    except requests.RequestException as req_err:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to communicate with Todoist: {str(req_err)}",
        )
