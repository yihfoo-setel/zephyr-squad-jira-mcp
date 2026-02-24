# Installation
pip install -r requirements.txt

# Config for MCP server .py file
Must run from some kind of LLM server e.g. Cursor, Claude. No more starting like a server using SSE protocol as of mid-2025

Sample config in Cursor's ~/.cursor/mcp.json for `local-test` MCP:

```json
{
  "mcpServers": {
    "local-test": {
      "command": "python", // Assuming it's accessible from terminal env.
      "args": ["zephyr_squad_mcp.py"] // Located in root
    }
  }
} 
```

To apply new settings settings in Cursor including code changes to server:
1. Cursor -> Settings -> Cursor settings
2. Tools & MCP
3. Stop-start via the toggle

# Starting the MCP server:
For testing:
`fastmcp run my_server.py:mcp --transport http --port 8000`

This starts MCP server at http://localhost:8080/ i.e. http://127.0.0.1:8080/

Proper way is via LLM client that supports MCP protocol.

Once your server is running with HTTP transport, you can connect to it with any LLM client that supports the MCP protocol e.g. Claude, Cursor, or FastMCP.

# Examples to trigger tools set up
Example command to list all available `@mcp.tool`: `Get list of tools using local-test MCP `

To call it, use natural language. For this following tool:

```
add - Adds two numbers
Parameters: a (integer, required), b (integer, required)
```

Call with: `Call the 'add' tool with the arguments [1,2]`

It would return '3'
