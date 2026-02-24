import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from fastmcp import FastMCP
import logging
import requests
from zephyr.zephyr_squad_token_gen import generate_zephyr_jwt
from jira.jira_const import project_key_list
from jira.jira_service import resolve_issue_id

# Constants
ZEPHYR_ACCESS_KEY = os.environ.get("ZEPHYR_ACCESS_KEY")
JIRA_BASE_URL = os.environ.get(
    "JIRA_BASE_URL"
)  # e.g. https://yourcompany.atlassian.net
JIRA_API_TOKEN = os.environ.get("JIRA_API_TOKEN")

# base config
name = "zephyr_squad_mcp"
logging.basicConfig(
    level=logging.INFO,
    format="%(name)s - %(levelname)s - %(message)s",
    handlers=[logging.StreamHandler()],
)
logger = logging.getLogger(name)

mcp = FastMCP(name=name)


# Tool list
@mcp.tool()
def get_test_steps(issue_key: str) -> list[dict]:
    """Retrieve test steps for a given issue from the Zephyr Squad API.

    Args:
        issue_key: The Jira issue key (e.g. TR-1994).

    Returns:
        A list of test step dicts, each containing 'step', 'result', and 'data' as defined in each ticket
    """
    project_key = issue_key.split("-")[0]
    project_id = project_key_list.get(project_key)
    if not project_id:
        raise ValueError(f"Project ID not found for project key: {project_key}")

    issue_id = resolve_issue_id(issue_key)

    url = f"https://prod-api.zephyr4jiracloud.com/connect/public/rest/api/2.0/teststep/{issue_id}?projectId={project_id}"
    jwt_token = generate_zephyr_jwt(endpoint_url=url, http_method="GET")

    headers = {
        "Content-Type": "application/json",
        "Authorization": f"JWT {jwt_token}",
        "zapiAccessKey": ZEPHYR_ACCESS_KEY,
    }

    response = requests.get(url, headers=headers)
    response.raise_for_status()

    return [
        {"step": ts["step"], "result": ts["result"], "data": ts["data"]}
        for ts in response.json().get("testSteps", [])
    ]


# MCP init
if __name__ == "__main__":
    logger.info(f"Starting MCP Server '{name}'...")
    try:
        mcp.run()
    except Exception as e:
        logger.error(f"Server error: {str(e)}")
        sys.exit(1)
    finally:
        logger.info("Server terminated")
