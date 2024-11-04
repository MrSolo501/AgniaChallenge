from pydantic_settings import BaseSettings

# Основные настройки для хакатона
class BaseHackathonSettings(BaseSettings):
    user_token_from_tg_bot: str = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyX2lkIjoiN2YwNWQxOTAtM2JiNy00OGYzLThhNDAtMzcyODg0MGQwYWFiIiwiZXhwIjoxNzMwNzM1MDMyLjkwMTc5MSwiaXNzIjoiYmFja2VuZDphY2Nlc3MtdG9rZW4ifQ.rCLz_CaJ_f2Q5un_gRvjF5o1VLHXE2uFavLswUI8Aek"
    save_auth_data_endpoint: str = "https://aes-agniachallenge-case.olymp.innopolis.university/save-authorization-data"

# Настройки для авторизации Todoist
class TodoistAuthSettings(BaseSettings):
    todoist_oauth_api_url: str = "https://todoist.com/oauth/authorize/"
    todoist_token_exchange_api_url: str = "https://todoist.com/oauth/access_token/"
    todoist_redirect_url: str = "http://localhost:9000/todoist/authorize"
    todoist_client_id: str = "6e0e6fa0d2be4b86b35ea3dce3332f0a"
    todoist_scope: str = "task:add,data:read,data:read_write,data:delete"
    todoist_state: str = "some_secret_state"
    todoist_client_secret: str = "0c671f9a498347cab38c058fb636423b"

# Настройки для авторизации GitHub
class GitHubAuthSettings(BaseSettings):
    github_oauth_api_url: str = "https://github.com/login/oauth/authorize"
    github_token_exchange_api_url: str = "https://github.com/login/oauth/access_token"
    github_redirect_url: str = "http://localhost:9000/github/get-token"  # URL для обработки токена GitHub
    github_client_id: str = "Ov23lisPeRlq03n5th3d"  # Укажите свой GitHub Client ID
    github_client_secret: str = "839c201a8c8d8dc53bf344a1a40d222b7f80fcfa"  # Укажите свой GitHub Client Secret
    github_scope: str = "repo,user"  # Пример scopes: доступ к репозиториям и пользователю
    github_state: str = "some_secret_state_for_github"

# Инициализация настроек
base_hackathon_settings = BaseHackathonSettings()
todoist_auth_settings = TodoistAuthSettings()
github_auth_settings = GitHubAuthSettings()
