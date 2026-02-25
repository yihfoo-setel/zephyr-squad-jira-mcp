# Installation for MCP client
## Cursor
Install uv:
`pip install uv`

In your Cursor MCP config (.cursor/mcp.json), use uvx with --from pointing to the Git repo. Make sure you have a ssh key configured in your Github Account for host `git@github.com`:

```json
{
  "mcpServers": {
    "zephyr-squad-jira-mcp": {
      "command": "uvx",
      "args": [
        "--from",
        "git+ssh://git@github.com/yihfoo-setel/zephyr-squad-jira-mcp.git",
        "zephyr-squad-jira-mcp"
      ],
      "env": {
        "ZEPHYR_ACCESS_KEY": "...",
        "ZEPHYR_SECRET_KEY": "...",
        "ZEPHYR_USERNAME": "...",
        "JIRA_BASE_URL": "...",
        "JIRA_USER_ID": "...",
        "JIRA_ACCESS_TOKEN": "..."
      }
    }
  }
}
```

For more targeted installs, append @ref to target a specific version:
- Branch: git+ssh://git@github.com/yihfoo-setel/zephyr-squad-jira-mcp.git@main
- Tag: git+ssh://git@github.com/yihfoo-setel/zephyr-squad-jira-mcp.git@v0.1.0
- Commit: git+ssh://git@github.com/yihfoo-setel/zephyr-squad-jira-mcp.git@abc1234

# Development
Since this is a Poetry package, changes require rebuilding the dist/ folder. Run this from the repo root (where `pyproject.toml` lives). Dependencies listed in pyproject.toml would be installed:
`poetry build`

If you want a clean rebuild, you can delete the dist/ folder first.

Now push the package to the Github repo

Next, reinstall this MCP package by restarting the MCP. Assuming the MCP client is pointing to the change branch, it would reload with the latest changes. For example:

`git+ssh://git@github.com/yihfoo-setel/zephyr-squad-jira-mcp.git@change-branch-name`


# Examples to trigger tools set up
Example command to list all available `@mcp.tool`: `Get list of tools using zephyr_squad_jira MCP `

To call tools, use natural language. Given this example tool:

```
add - Adds two numbers
Parameters: a (integer, required), b (integer, required)
```

Call with: `Call the 'add' tool with the arguments [1,2]`

It would return '3'
