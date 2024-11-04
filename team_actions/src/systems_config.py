from typing import Dict, Any
from team_actions.src.registration import fetch_available_actions

# Основной словарь с конфигурацией и описанием доступных систем
systems_info: Dict[str, Any] = {
    "task_tracker": {
        "description": "Manages tasks, issues, and projects (e.g., Todoist, TeamFlame).",
        "systems": {
            "TeamFlame": (
                "TeamFlame is a task tracking system where spaces hold projects, "
                "projects contain Kanban boards, and boards manage tasks across columns "
                "like 'To Do', 'In Progress' and 'Done'. Tasks have statuses such as epic, "
                "bug, etc., ensuring efficient organization and workflow control."
            ),
            "Todoist": (
                "Todoist is a task management app that organizes tasks into projects, "
                "allows setting due dates, priorities, and creating sub-tasks. It supports "
                "collaboration, custom filters, reminders, and tracks productivity across devices."
            ),
        },
    },
    "version_control_system": {
        "description": "Tracks code changes, versions, and issues (e.g., GitHub, GitFlame).",
        "systems": {
            "GitFlame": (
                "GitFlame is a version control and collaboration tool that integrates "
                "Git repositories with task management."
            ),
            "GitHub": (
                "GitHub is a version control and collaboration platform that supports "
                "Git repositories, issue tracking, pull requests, and project management "
                "for software development."
            ),
        },
    },
}

# Список доступных действий, получаемых из системы регистрации
available_actions: Dict[str, Any] = fetch_available_actions()
