from fastapi import FastAPI, HTTPException
import requests

from authorizations.src.authorization_services import todoist
from authorizations.src.hackathon_utils import (
    save_authorization_data_and_return_response,
)
from authorizations.src.settings import (
    base_hackathon_settings,
    todoist_auth_settings,
    github_auth_settings
)
from team_actions.src.actions.GitHub.actions import authorization_data

app = FastAPI()

# Проверка настроек Telegram
assert (
    base_hackathon_settings.user_token_from_tg_bot != ""
), "Укажите Telegram токен в settings.py"

# Проверка настроек Todoist
assert (
    todoist_auth_settings.todoist_client_id != ""
), "Укажите Todoist Client ID в settings.py"
assert (
    todoist_auth_settings.todoist_client_secret != ""
), "Укажите Todoist Client Secret в settings.py"

# Проверка настроек GitHub
assert (
    github_auth_settings.github_client_id != ""
), "Укажите GitHub Client ID в settings.py"
assert (
    github_auth_settings.github_client_secret != ""
), "Укажите GitHub Client Secret в settings.py"

# Эндпоинты для Todoist
@app.get("/todoist/authorize")
def authorize_in_todoist():
    return {"url": todoist.authorize()}


@app.get("/todoist/get-token", include_in_schema=False)
def get_todoist_token(
    code: str = None,
    state: str = None,
    error: str = None,
):
    if error == "invalid_application_status":
        raise HTTPException(status_code=500, detail="Invalid application status")
    elif error == "invalid_scope":
        raise HTTPException(status_code=400, detail="Invalid scope")
    elif error == "access_denied":
        raise HTTPException(status_code=403, detail="User denied authorization")

    authorization_token = todoist.callback(code, state, error)
    return save_authorization_data_and_return_response(
        authorization_token, system_name="Todoist"
    )

# Эндпоинты для GitHub
@app.get("/github/authorize")
def authorize_in_github():
    auth_url = (
        f"https://github.com/login/oauth/authorize?"
        f"client_id={github_auth_settings.github_client_id}&"
        f"redirect_uri={github_auth_settings.github_redirect_url}"
    )
    return {"url": auth_url}

@app.get("/github/get-token", include_in_schema=False)
def get_github_token(code: str = None, error: str = None):
    if error == "access_denied":
        raise HTTPException(status_code=403, detail="User denied authorization")
    elif not code:
        raise HTTPException(status_code=400, detail="Authorization code is missing")

    # Обмен кода на токен
    response = requests.post(
        "https://github.com/login/oauth/access_token",
        headers={"Accept": "application/json"},
        data={
            "client_id": github_auth_settings.github_client_id,
            "client_secret": github_auth_settings.github_client_secret,
            "code": code,
        },
    )
    response.raise_for_status()
    auth_data = response.json()

    # Отладочный вывод для проверки данных от GitHub
    print("Auth Data from GitHub:", auth_data)

    # Сохранение данных авторизации
    save_response = save_authorization_data_and_return_response(auth_data, system_name="GitHub")

    # Проверяем, что данные сохранены
    print("Authorization Data after saving:", authorization_data)

    return save_response

# Пример временного вызова create_issue для тестирования
from team_actions.src.actions.GitHub.actions import create_issue

