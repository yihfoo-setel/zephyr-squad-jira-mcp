import os
import requests

# Constants
JIRA_BASE_URL = os.environ.get("JIRA_BASE_URL")
JIRA_USER_ID = os.environ.get("JIRA_USER_ID")
JIRA_ACCESS_TOKEN = os.environ.get("JIRA_ACCESS_TOKEN")


def resolve_issue_id(issue_key: str) -> str:
    """Resolve a Jira issue key (e.g. TR-1994) to its numeric issue ID via the Jira REST API."""
    url = f"{JIRA_BASE_URL}/issue/{issue_key}?fields=id"
    headers = {
        "Authorization": f"Basic {JIRA_ACCESS_TOKEN}",
        "Accept": "application/json",
    }

    response = requests.get(url=url, headers=headers)
    response.raise_for_status()
    numeric_id = response.json()["id"]
    return numeric_id
