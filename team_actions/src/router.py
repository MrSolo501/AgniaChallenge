from team_actions.src.utils.action_router import ActionRouter

# Import actions module for existing systems
from team_actions.src.actions.Todoist import actions as todoist_actions

# Import actions module for new system GitHub
from team_actions.src.actions.GitHub import actions as github_actions

# Register actions modules in the router
ActionRouter.add_actions_for_module(todoist_actions)
ActionRouter.add_actions_for_module(github_actions)  # Register GitHub actions

# Keep it as is
action_router = ActionRouter()
