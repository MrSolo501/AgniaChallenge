from typing import Annotated, Optional, List, Literal
from pydantic import BaseModel, Field, HttpUrl
from team_actions.src.registration import register_action
import requests

# 1. Определение типов данных и структур данных (Pydantic модели)

# Определяем Type Hints для входных параметров
Id = Annotated[str, Field(pattern="^[0-9]+$")]
RepoName = Annotated[str, Field(description="Repository name, e.g., 'username/repo'")]
IssueTitle = Annotated[str, Field(description="Title of the issue")]
BodyContent = Annotated[Optional[str], Field(description="Content of the issue or pull request body")]
Label = Annotated[str, Field(description="Label associated with the issue or pull request")]

# Дата и время создания в формате ISO 8601
Datetime = Annotated[
    str,
    Field(
        pattern=(
            r"^\d{4}-\d{2}-\d{2}T\d{2}:"
            r"\d{2}:\d{2}(\.\d+)?Z$"
        ),
        description="Datetime in ISO 8601 format"
    )
]

# Модель для пользователя
class User(BaseModel):
    id: Id
    login: str
    url: HttpUrl

# Модель для меток
class LabelModel(BaseModel):
    id: Id
    name: Label
    color: str

# Модель для задачи (issue)
class Issue(BaseModel):
    id: Id
    number: int
    title: IssueTitle
    body: Optional[BodyContent]
    user: User
    labels: List[LabelModel]
    state: Literal["open", "closed"]
    created_at: Datetime
    updated_at: Optional[Datetime]
    closed_at: Optional[Datetime]
    url: HttpUrl

# Модель для пул-реквеста
class PullRequest(BaseModel):
    id: Id
    number: int
    title: str
    body: Optional[BodyContent]
    user: User
    state: Literal["open", "closed"]
    created_at: Datetime
    updated_at: Optional[Datetime]
    closed_at: Optional[Datetime]
    merged_at: Optional[Datetime]
    url: HttpUrl


# 2. Определение функции действия create_issue

authorization_data = {}  # Словарь authorization_data заполняется автоматически после регистрации действий

@register_action(
    system_type="version_control_system",
    include_in_plan=True,
    signature=(
        "(repo: str, title: str, "
        "body: Optional[str] = None, "
        "labels: Optional[List[str]] = None) "
        "-> dict"
    ),
    arguments=["repo", "title", "body", "labels"],
    description="Creates a new issue in the specified GitHub repository.",
)
def create_issue(repo: str, title: str, body: Optional[str] = None, labels: Optional[List[str]] = None) -> dict:
    """
    Создает новый issue в указанном репозитории на GitHub.

    Args:
        repo (str): Полное имя репозитория в формате "owner/repo".
        title (str): Название задачи (issue).
        body (Optional[str]): Описание задачи (опционально).
        labels (Optional[List[str]]): Список меток для задачи (опционально).

    Returns:
        dict: Данные о созданной задаче.
    """
    # Логика функции здесь


    # Получаем токен доступа из authorization_data
    token = authorization_data.get("GitHub", {}).get("access_token")
    if not token:
        raise ValueError("Authorization token for GitHub is missing.")

    # Выполняем запрос для создания нового issue
    response = requests.post(
        f"https://api.github.com/repos/{repo}/issues",
        headers={
            "Authorization": f"Bearer {token}",
            "Accept": "application/vnd.github+json"
        },
        json={
            "title": title,
            "body": body,
            "labels": labels
        }
    )

    # Проверяем успешность запроса и возвращаем данные о задаче
    response.raise_for_status()
    return response.json()

@register_action(
    system_type="version_control_system",
    include_in_plan=True,
    signature="(name: str, description: Optional[str] = None, private: bool = False) -> dict",
    arguments=["name", "description", "private"],
    description="Creates a new repository in the authenticated user's account."
)
def create_repository(name: str, description: Optional[str] = None, private: bool = False) -> dict:
    """
    Создает новый репозиторий в аккаунте пользователя GitHub.

    Args:
        name (str): Название репозитория.
        description (Optional[str]): Описание репозитория (опционально).
        private (bool): Флаг приватности репозитория (по умолчанию публичный).

    Returns:
        dict: Данные о созданном репозитории.
    """
    # Получаем токен доступа из authorization_data
    token = authorization_data.get("GitHub", {}).get("access_token")
    if not token:
        raise ValueError("Authorization token for GitHub is missing.")

    # Выполняем запрос для создания нового репозитория
    response = requests.post(
        "https://api.github.com/user/repos",
        headers={
            "Authorization": f"Bearer {token}",
            "Accept": "application/vnd.github+json"
        },
        json={
            "name": name,
            "description": description,
            "private": private
        }
    )

    # Проверяем успешность запроса и возвращаем данные о репозитории
    response.raise_for_status()
    return response.json()

@register_action(
    system_type="version_control_system",
    include_in_plan=True,
    signature="(repo: str) -> dict",
    arguments=["repo"],
    description="Deletes a specified repository in the GitHub account."
)
def delete_repository(repo: str) -> dict:
    """
    Удаляет указанный репозиторий из аккаунта GitHub.

    Args:
        repo (str): Полное имя репозитория в формате "owner/repo".

    Returns:
        dict: Сообщение о результате операции.
    """
    # Получаем токен доступа из authorization_data
    token = authorization_data.get("GitHub", {}).get("access_token")
    if not token:
        raise ValueError("Authorization token for GitHub is missing.")

    # Выполняем запрос для удаления репозитория
    response = requests.delete(
        f"https://api.github.com/repos/{repo}",
        headers={
            "Authorization": f"Bearer {token}",
            "Accept": "application/vnd.github+json"
        }
    )

    # Проверяем успешность запроса и возвращаем сообщение о результате
    if response.status_code == 204:
        return {"message": "Repository deleted successfully."}
    else:
        response.raise_for_status()
        return {"message": "Failed to delete repository."}

@register_action(
    system_type="version_control_system",
    include_in_plan=True,
    signature="(repo: str, issue_number: int) -> dict",
    arguments=["repo", "issue_number"],
    description="Retrieves information about a specific issue in the specified GitHub repository."
)
def get_issue(repo: str, issue_number: int) -> dict:
    """
    Получает информацию о задаче (issue) в указанном репозитории GitHub.

    Args:
        repo (str): Полное имя репозитория в формате "owner/repo".
        issue_number (int): Номер задачи (issue) в репозитории.

    Returns:
        dict: Данные о задаче, включая название, описание, статус и метки.
    """
    # Получаем токен доступа из authorization_data
    token = authorization_data.get("GitHub", {}).get("access_token")
    if not token:
        raise ValueError("Authorization token for GitHub is missing.")

    # Выполняем запрос для получения информации о задаче
    response = requests.get(
        f"https://api.github.com/repos/{repo}/issues/{issue_number}",
        headers={
            "Authorization": f"Bearer {token}",
            "Accept": "application/vnd.github+json"
        }
    )

    # Проверяем успешность запроса и возвращаем данные о задаче
    response.raise_for_status()
    return response.json()

@register_action(
    system_type="version_control_system",
    include_in_plan=True,
    signature="(repo: str, issue_number: int, title: Optional[str] = None, body: Optional[str] = None, state: Optional[str] = None, assignees: Optional[List[str]] = None) -> dict",
    arguments=["repo", "issue_number", "title", "body", "state", "assignees"],
    description="Updates an issue in the specified GitHub repository, including title, description, status, and assignees."
)
def update_issue(repo: str, issue_number: int, title: Optional[str] = None, body: Optional[str] = None, state: Optional[str] = None, assignees: Optional[List[str]] = None) -> dict:
    """
    Редактирует информацию о задаче (issue) в указанном репозитории GitHub.

    Args:
        repo (str): Полное имя репозитория в формате "owner/repo".
        issue_number (int): Номер задачи (issue) в репозитории.
        title (Optional[str]): Новый заголовок задачи.
        body (Optional[str]): Новое описание задачи.
        state (Optional[str]): Новый статус задачи ('open' или 'closed').
        assignees (Optional[List[str]]): Список логинов пользователей GitHub для добавления или удаления исполнителей.

    Returns:
        dict: Обновлённые данные о задаче.
    """
    # Получаем токен доступа из authorization_data
    token = authorization_data.get("GitHub", {}).get("access_token")
    if not token:
        raise ValueError("Authorization token for GitHub is missing.")

    # Подготовка данных для обновления
    data = {
        "title": title,
        "body": body,
        "state": state,
        "assignees": assignees
    }
    # Удаляем ключи с None значениями
    data = {k: v for k, v in data.items() if v is not None}

    # Выполняем запрос для обновления информации о задаче
    response = requests.patch(
        f"https://api.github.com/repos/Fugaret/{repo}/issues/{issue_number}",
        headers={
            "Authorization": f"Bearer {token}",
            "Accept": "application/vnd.github+json"
        },
        json=data
    )

    # Проверяем успешность запроса и возвращаем данные о задаче
    response.raise_for_status()
    return response.json()

@register_action(
    system_type="version_control_system",
    include_in_plan=True,
    signature="(repo: str, issue_number: int) -> dict",
    arguments=["repo", "issue_number"],
    description="Closes an issue in the specified GitHub repository."
)
def close_issue(repo: str, issue_number: int) -> dict:
    """
    Закрывает задачу (issue) в указанном репозитории GitHub, изменяя её статус на 'closed'.

    Args:
        repo (str): Полное имя репозитория в формате "owner/repo".
        issue_number (int): Номер задачи (issue) в репозитории.

    Returns:
        dict: Обновлённые данные о задаче, подтверждающие её закрытие.
    """
    # Получаем токен доступа из authorization_data
    token = authorization_data.get("GitHub", {}).get("access_token")
    if not token:
        raise ValueError("Authorization token for GitHub is missing.")

    # Выполняем запрос для закрытия задачи
    response = requests.patch(
        f"https://api.github.com/repos/Fugaret/{repo}/issues/{issue_number}",
        headers={
            "Authorization": f"Bearer {token}",
            "Accept": "application/vnd.github+json"
        },
        json={"state": "closed"}
    )

    # Проверяем успешность запроса и возвращаем данные о задаче
    response.raise_for_status()
    return response.json()

@register_action(
    system_type="version_control_system",
    include_in_plan=True,
    signature="(repo: str, state: Optional[str] = None, labels: Optional[List[str]] = None, assignee: Optional[str] = None) -> list",
    arguments=["repo", "state", "labels", "assignee"],
    description="Retrieves a list of issues from the specified GitHub repository, filtered by state, labels, and assignee."
)
def list_issues(repo: str, state: Optional[str] = None, labels: Optional[List[str]] = None, assignee: Optional[str] = None) -> list:
    """
    Получает список задач (issues) в указанном репозитории GitHub, с возможностью фильтрации по статусу, меткам и исполнителю.

    Args:
        repo (str): Полное имя репозитория в формате "owner/repo".
        state (Optional[str]): Фильтр по статусу задачи ('open', 'closed' или 'all').
        labels (Optional[List[str]]): Список меток для фильтрации.
        assignee (Optional[str]): Логин исполнителя для фильтрации.

    Returns:
        list: Список задач, соответствующих указанным фильтрам.
    """
    # Получаем токен доступа из authorization_data
    token = authorization_data.get("GitHub", {}).get("access_token")
    if not token:
        raise ValueError("Authorization token for GitHub is missing.")

    # Подготовка параметров запроса
    params = {
        "state": state or "open",
        "labels": ",".join(labels) if labels else None,
        "assignee": assignee
    }
    # Удаляем ключи с None значениями
    params = {k: v for k, v in params.items() if v is not None}

    # Выполняем запрос для получения списка задач
    response = requests.get(
        f"https://api.github.com/repos/{repo}/issues",
        headers={
            "Authorization": f"Bearer {token}",
            "Accept": "application/vnd.github+json"
        },
        params=params
    )

    # Проверяем успешность запроса и возвращаем список задач
    response.raise_for_status()
    return response.json()

@register_action(
    system_type="version_control_system",
    include_in_plan=True,
    signature="(repo: str) -> dict",
    arguments=["repo"],
    description="Retrieves information about a specific GitHub repository."
)
def get_repository_info(repo: str) -> dict:
    """
    Получает информацию о указанном репозитории GitHub.

    Args:
        repo (str): Полное имя репозитория в формате "owner/repo".

    Returns:
        dict: Данные о репозитории, включая описание, количество звёзд, форков и статус приватности.
    """
    # Получаем токен доступа из authorization_data
    token = authorization_data.get("GitHub", {}).get("access_token")
    if not token:
        raise ValueError("Authorization token for GitHub is missing.")

    # Выполняем запрос для получения информации о репозитории
    response = requests.get(
        f"https://api.github.com/repos/Fugaret/{repo}",
        headers={
            "Authorization": f"Bearer {token}",
            "Accept": "application/vnd.github+json"
        }
    )

    # Проверяем успешность запроса и возвращаем данные о репозитории
    response.raise_for_status()
    return response.json()

@register_action(
    system_type="version_control_system",
    include_in_plan=True,
    signature="(repo: str) -> dict",
    arguments=["repo"],
    description="Stars a specified GitHub repository for the authenticated user."
)
def star_repository(repo: str) -> dict:
    """
    Добавляет звезду к указанному репозиторию GitHub от имени аутентифицированного пользователя.

    Args:
        repo (str): Полное имя репозитория в формате "owner/repo".

    Returns:
        dict: Сообщение о результате операции.
    """
    # Получаем токен доступа из authorization_data
    token = authorization_data.get("GitHub", {}).get("access_token")
    if not token:
        raise ValueError("Authorization token for GitHub is missing.")

    # Выполняем запрос для добавления звезды к репозиторию
    response = requests.put(
        f"https://api.github.com/user/starred/{repo}",
        headers={
            "Authorization": f"Bearer {token}",
            "Accept": "application/vnd.github+json"
        }
    )

    # Проверяем успешность запроса и возвращаем сообщение о результате
    if response.status_code == 204:
        return {"message": "Repository starred successfully."}
    else:
        response.raise_for_status()
        return {"message": "Failed to star repository."}
@register_action(
    system_type="version_control_system",
    include_in_plan=True,
    signature="(repo: str) -> dict",
    arguments=["repo"],
    description="Removes a star from a specified GitHub repository for the authenticated user."
)
def unstar_repository(repo: str) -> dict:
    """
    Убирает звезду с указанного репозитория GitHub от имени аутентифицированного пользователя.

    Args:
        repo (str): Полное имя репозитория в формате "owner/repo".

    Returns:
        dict: Сообщение о результате операции.
    """
    # Получаем токен доступа из authorization_data
    token = authorization_data.get("GitHub", {}).get("access_token")
    if not token:
        raise ValueError("Authorization token for GitHub is missing.")

    # Выполняем запрос для удаления звезды с репозитория
    response = requests.delete(
        f"https://api.github.com/user/starred/{repo}",
        headers={
            "Authorization": f"Bearer {token}",
            "Accept": "application/vnd.github+json"
        }
    )

    # Проверяем успешность запроса и возвращаем сообщение о результате
    if response.status_code == 204:
        return {"message": "Repository unstarred successfully."}
    else:
        response.raise_for_status()
        return {"message": "Failed to unstar repository."}

@register_action(
    system_type="version_control_system",
    include_in_plan=True,
    signature="(repo: str) -> list",
    arguments=["repo"],
    description="Retrieves a list of all branches in the specified GitHub repository."
)
def list_branches(repo: str) -> list:
    """
    Получает список всех веток в указанном репозитории GitHub.

    Args:
        repo (str): Полное имя репозитория в формате "owner/repo".

    Returns:
        list: Список веток в репозитории.
    """
    # Получаем токен доступа из authorization_data
    token = authorization_data.get("GitHub", {}).get("access_token")
    if not token:
        raise ValueError("Authorization token for GitHub is missing.")

    # Выполняем запрос для получения списка веток
    response = requests.get(
        f"https://api.github.com/repos/{repo}/branches",
        headers={
            "Authorization": f"Bearer {token}",
            "Accept": "application/vnd.github+json"
        }
    )

    # Проверяем успешность запроса и возвращаем список веток
    response.raise_for_status()
    return response.json()

@register_action(
    system_type="version_control_system",
    include_in_plan=True,
    signature="(repo: str, branch_name: str, commit_sha: str) -> dict",
    arguments=["repo", "branch_name", "commit_sha"],
    description="Creates a new branch in the specified GitHub repository from the given commit SHA."
)
def create_branch(repo: str, branch_name: str, commit_sha: str) -> dict:
    """
    Создаёт новую ветку в указанном репозитории GitHub от заданного коммита.

    Args:
        repo (str): Полное имя репозитория в формате "owner/repo".
        branch_name (str): Название новой ветки.
        commit_sha (str): SHA идентификатор коммита, от которого будет создана ветка.

    Returns:
        dict: Данные о созданной ветке.
    """
    # Получаем токен доступа из authorization_data
    token = authorization_data.get("GitHub", {}).get("access_token")
    if not token:
        raise ValueError("Authorization token for GitHub is missing.")

    # Выполняем запрос для создания новой ветки
    response = requests.post(
        f"https://api.github.com/repos/{repo}/git/refs",
        headers={
            "Authorization": f"Bearer {token}",
            "Accept": "application/vnd.github+json"
        },
        json={
            "ref": f"refs/heads/{branch_name}",
            "sha": commit_sha
        }
    )

    # Проверяем успешность запроса и возвращаем данные о ветке
    response.raise_for_status()
    return response.json()
@register_action(
    system_type="version_control_system",
    include_in_plan=True,
    signature="(repo: str, branch_name: str) -> dict",
    arguments=["repo", "branch_name"],
    description="Deletes a specified branch in the GitHub repository."
)
def delete_branch(repo: str, branch_name: str) -> dict:
    """
    Удаляет указанную ветку в репозитории GitHub.

    Args:
        repo (str): Полное имя репозитория в формате "owner/repo".
        branch_name (str): Название ветки, которую нужно удалить.

    Returns:
        dict: Сообщение о результате операции.
    """
    # Получаем токен доступа из authorization_data
    token = authorization_data.get("GitHub", {}).get("access_token")
    if not token:
        raise ValueError("Authorization token for GitHub is missing.")

    # Выполняем запрос для удаления ветки
    response = requests.delete(
        f"https://api.github.com/repos/Fugaret/{repo}/git/refs/heads/{branch_name}",
        headers={
            "Authorization": f"Bearer {token}",
            "Accept": "application/vnd.github+json"
        }
    )

    # Проверяем успешность запроса и возвращаем сообщение о результате
    if response.status_code == 204:
        return {"message": "Branch deleted successfully."}
    else:
        response.raise_for_status()
        return {"message": "Failed to delete branch."}

import base64

@register_action(
    system_type="version_control_system",
    include_in_plan=True,
    signature="(repo: str, file_path: str, branch: Optional[str] = 'main') -> dict",
    arguments=["repo", "file_path", "branch"],
    description="Retrieves the content of a specified file in the GitHub repository."
)
def get_file_content(repo: str, file_path: str, branch: str = "main") -> dict:
    """
    Получает содержимое файла в указанном репозитории GitHub по заданному пути.

    Args:
        repo (str): Полное имя репозитория в формате "owner/repo".
        file_path (str): Путь к файлу в репозитории.
        branch (str): Имя ветки, откуда извлекается файл (по умолчанию 'main').

    Returns:
        dict: Содержимое файла в виде текста.
    """
    # Получаем токен доступа из authorization_data
    token = authorization_data.get("GitHub", {}).get("access_token")
    if not token:
        raise ValueError("Authorization token for GitHub is missing.")

    # Выполняем запрос для получения содержимого файла
    response = requests.get(
        f"https://api.github.com/repos/{repo}/contents/{file_path}",
        headers={
            "Authorization": f"Bearer {token}",
            "Accept": "application/vnd.github+json"
        },
        params={"ref": branch}
    )

    # Проверяем успешность запроса
    response.raise_for_status()
    file_data = response.json()

    # Декодируем содержимое файла из base64
    file_content = base64.b64decode(file_data['content']).decode('utf-8')

    return {"file_content": file_content}

@register_action(
    system_type="version_control_system",
    include_in_plan=True,
    signature="(repo: str, file_path: str, content: str, branch: Optional[str] = 'main', message: Optional[str] = 'Create new file') -> dict",
    arguments=["repo", "file_path", "content", "branch", "message"],
    description="Creates a new file in the specified GitHub repository with the provided content."
)
def create_file(repo: str, file_path: str, content: str, branch: str = "main", message: str = "Create new file") -> dict:
    """
    Создаёт новый файл с указанным содержимым в репозитории GitHub.

    Args:
        repo (str): Полное имя репозитория в формате "owner/repo".
        file_path (str): Путь к создаваемому файлу в репозитории.
        content (str): Содержимое файла в виде строки.
        branch (str): Имя ветки, куда будет добавлен файл (по умолчанию 'main').
        message (str): Сообщение коммита для создания файла (по умолчанию 'Create new file').

    Returns:
        dict: Данные о созданном файле.
    """
    # Получаем токен доступа из authorization_data
    token = authorization_data.get("GitHub", {}).get("access_token")
    if not token:
        raise ValueError("Authorization token for GitHub is missing.")

    # Кодируем содержимое файла в base64
    encoded_content = base64.b64encode(content.encode('utf-8')).decode('utf-8')

    # Выполняем запрос для создания файла
    response = requests.put(
        f"https://api.github.com/repos/{repo}/contents/{file_path}",
        headers={
            "Authorization": f"Bearer {token}",
            "Accept": "application/vnd.github+json"
        },
        json={
            "message": message,
            "content": encoded_content,
            "branch": branch
        }
    )

    # Проверяем успешность запроса и возвращаем данные о созданном файле
    response.raise_for_status()
    return response.json()
import base64

@register_action(
    system_type="version_control_system",
    include_in_plan=True,
    signature="(repo: str, file_path: str, content: str, branch: Optional[str] = 'main', message: Optional[str] = 'Update file') -> dict",
    arguments=["repo", "file_path", "content", "branch", "message"],
    description="Updates the content of a specified file in the GitHub repository."
)
def update_file(repo: str, file_path: str, content: str, branch: str = "main", message: str = "Update file") -> dict:
    """
    Обновляет содержимое указанного файла в репозитории GitHub.

    Args:
        repo (str): Полное имя репозитория в формате "owner/repo".
        file_path (str): Путь к файлу в репозитории.
        content (str): Новое содержимое файла в виде строки.
        branch (str): Имя ветки, в которой обновляется файл (по умолчанию 'main').
        message (str): Сообщение коммита для обновления файла (по умолчанию 'Update file').

    Returns:
        dict: Данные об обновлённом файле.
    """
    # Получаем токен доступа из authorization_data
    token = authorization_data.get("GitHub", {}).get("access_token")
    if not token:
        raise ValueError("Authorization token for GitHub is missing.")

    # Получаем текущий SHA файла
    get_response = requests.get(
        f"https://api.github.com/repos/{repo}/contents/{file_path}",
        headers={
            "Authorization": f"Bearer {token}",
            "Accept": "application/vnd.github+json"
        },
        params={"ref": branch}
    )
    get_response.raise_for_status()
    file_data = get_response.json()
    file_sha = file_data["sha"]

    # Кодируем новое содержимое файла в base64
    encoded_content = base64.b64encode(content.encode('utf-8')).decode('utf-8')

    # Выполняем запрос для обновления содержимого файла
    response = requests.put(
        f"https://api.github.com/repos/{repo}/contents/{file_path}",
        headers={
            "Authorization": f"Bearer {token}",
            "Accept": "application/vnd.github+json"
        },
        json={
            "message": message,
            "content": encoded_content,
            "sha": file_sha,
            "branch": branch
        }
    )

    # Проверяем успешность запроса и возвращаем данные об обновлённом файле
    response.raise_for_status()
    return response.json()


@register_action(
    system_type="version_control_system",
    include_in_plan=True,
    signature="(repo: str, file_path: str, branch: Optional[str] = 'main', message: Optional[str] = 'Delete file') -> dict",
    arguments=["repo", "file_path", "branch", "message"],
    description="Deletes a specified file from the GitHub repository."
)
def delete_file(repo: str, file_path: str, branch: str = "main", message: str = "Delete file") -> dict:
    """
    Удаляет указанный файл из репозитория GitHub.

    Args:
        repo (str): Полное имя репозитория в формате "owner/repo".
        file_path (str): Путь к файлу в репозитории.
        branch (str): Имя ветки, из которой удаляется файл (по умолчанию 'main').
        message (str): Сообщение коммита для удаления файла (по умолчанию 'Delete file').

    Returns:
        dict: Данные об удалённом файле.
    """
    # Получаем токен доступа из authorization_data
    token = authorization_data.get("GitHub", {}).get("access_token")
    if not token:
        raise ValueError("Authorization token for GitHub is missing.")

    # Получаем текущий SHA файла
    get_response = requests.get(
        f"https://api.github.com/repos/{repo}/contents/{file_path}",
        headers={
            "Authorization": f"Bearer {token}",
            "Accept": "application/vnd.github+json"
        },
        params={"ref": branch}
    )
    get_response.raise_for_status()
    file_data = get_response.json()
    file_sha = file_data["sha"]

    # Выполняем запрос для удаления файла
    response = requests.delete(
        f"https://api.github.com/repos/{repo}/contents/{file_path}",
        headers={
            "Authorization": f"Bearer {token}",
            "Accept": "application/vnd.github+json"
        },
        json={
            "message": message,
            "sha": file_sha,
            "branch": branch
        }
    )

    # Проверяем успешность запроса и возвращаем данные об удалении файла
    response.raise_for_status()
    return {"message": "File deleted successfully."}

@register_action(
    system_type="version_control_system",
    include_in_plan=True,
    signature="(repo: str, title: str, head: str, base: str, body: Optional[str] = '') -> dict",
    arguments=["repo", "title", "head", "base", "body"],
    description="Creates a new pull request between specified branches in the GitHub repository."
)
def create_pull_request(repo: str, title: str, head: str, base: str, body: str = "") -> dict:
    """
    Создаёт новый pull request между указанными ветками в репозитории GitHub.

    Args:
        repo (str): Полное имя репозитория в формате "owner/repo".
        title (str): Заголовок pull request.
        head (str): Ветка-источник (откуда делать изменения).
        base (str): Ветка-назначение (куда вносить изменения).
        body (str): Описание pull request (опционально).

    Returns:
        dict: Данные о созданном pull request.
    """
    # Получаем токен доступа из authorization_data
    token = authorization_data.get("GitHub", {}).get("access_token")
    if not token:
        raise ValueError("Authorization token for GitHub is missing.")

    # Выполняем запрос для создания pull request
    response = requests.post(
        f"https://api.github.com/repos/{repo}/pulls",
        headers={
            "Authorization": f"Bearer {token}",
            "Accept": "application/vnd.github+json"
        },
        json={
            "title": title,
            "head": head,
            "base": base,
            "body": body
        }
    )

    # Проверяем успешность запроса и возвращаем данные о pull request
    response.raise_for_status()
    return response.json()

@register_action(
    system_type="version_control_system",
    include_in_plan=True,
    signature="(repo: str, state: Optional[str] = 'open') -> list",
    arguments=["repo", "state"],
    description="Retrieves a list of pull requests from the specified GitHub repository, with optional filtering by status."
)
def list_pull_requests(repo: str, state: str = "open") -> list:
    """
    Получает список pull requests в указанном репозитории GitHub с возможностью фильтрации по статусу.

    Args:
        repo (str): Полное имя репозитория в формате "owner/repo".
        state (str): Фильтр по статусу pull requests ('open', 'closed' или 'all').

    Returns:
        list: Список pull requests, соответствующих указанным фильтрам.
    """
    # Получаем токен доступа из authorization_data
    token = authorization_data.get("GitHub", {}).get("access_token")
    if not token:
        raise ValueError("Authorization token for GitHub is missing.")

    # Подготовка параметров запроса
    params = {
        "state": state
    }

    # Выполняем запрос для получения списка pull requests
    response = requests.get(
        f"https://api.github.com/repos/{repo}/pulls",
        headers={
            "Authorization": f"Bearer {token}",
            "Accept": "application/vnd.github+json"
        },
        params=params
    )

    # Проверяем успешность запроса и возвращаем список pull requests
    response.raise_for_status()
    return response.json()
@register_action(
    system_type="version_control_system",
    include_in_plan=True,
    signature="(repo: str, pull_number: int, commit_message: Optional[str] = 'Merging pull request') -> dict",
    arguments=["repo", "pull_number", "commit_message"],
    description="Merges a specified pull request in the GitHub repository."
)
def merge_pull_request(repo: str, pull_number: int, commit_message: str = "Merging pull request") -> dict:
    """
    Принимает (мерджит) указанный pull request в репозитории GitHub.

    Args:
        repo (str): Полное имя репозитория в формате "owner/repo".
        pull_number (int): Номер pull request, который нужно принять.
        commit_message (str): Сообщение для коммита слияния (опционально).

    Returns:
        dict: Данные о выполненном слиянии pull request.
    """
    # Получаем токен доступа из authorization_data
    token = authorization_data.get("GitHub", {}).get("access_token")
    if not token:
        raise ValueError("Authorization token for GitHub is missing.")

    # Выполняем запрос для принятия pull request
    response = requests.put(
        f"https://api.github.com/repos/{repo}/pulls/{pull_number}/merge",
        headers={
            "Authorization": f"Bearer {token}",
            "Accept": "application/vnd.github+json"
        },
        json={
            "commit_message": commit_message
        }
    )

    # Проверяем успешность запроса и возвращаем данные о слиянии
    response.raise_for_status()
    return response.json()
@register_action(
    system_type="version_control_system",
    include_in_plan=True,
    signature="(repo: str, pull_number: int) -> dict",
    arguments=["repo", "pull_number"],
    description="Closes a specified pull request in the GitHub repository without merging."
)
def close_pull_request(repo: str, pull_number: int) -> dict:
    """
    Закрывает указанный pull request в репозитории GitHub без слияния.

    Args:
        repo (str): Полное имя репозитория в формате "owner/repo".
        pull_number (int): Номер pull request, который нужно закрыть.

    Returns:
        dict: Данные о закрытом pull request.
    """
    # Получаем токен доступа из authorization_data
    token = authorization_data.get("GitHub", {}).get("access_token")
    if not token:
        raise ValueError("Authorization token for GitHub is missing.")


    # Выполняем запрос для закрытия pull request
    response = requests.patch(
        f"https://api.github.com/repos/{repo}/pulls/{pull_number}",
        headers={
            "Authorization": f"Bearer {token}",
            "Accept": "application/vnd.github+json"
        },
        json={
            "state": "closed"
        }
    )

    # Проверяем успешность запроса и возвращаем данные о закрытии pull request
    response.raise_for_status()
    return response.json()
