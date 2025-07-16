# Bedrock Guardrails MCP Server

## Description

This MCP server exposes all AWS Bedrock Guardrails management features as tools, allowing you to create, edit, delete, and export guardrails (including all policy types) programmatically or via LLMs like Claude Desktop. It also supports exporting guardrail configurations as Terraform files for infrastructure-as-code workflows.

## Features
- Create, update, delete, and list AWS Bedrock Guardrails
- Full support for all policy types: content, topic, word, sensitive information, contextual grounding, etc.
- Export any guardrail as a Terraform `.tf` file (CloudFormation schema)
- Secure authentication using AWS credentials from environment variables
- Ready for integration with Claude Desktop or any MCP-compatible client

## Prerequisites
- Python 3.12+
- [uv](https://astral.sh/uv/) package manager
- AWS account with Bedrock Guardrails permissions
- AWS credentials set in your environment (see below)

## Setup
1. **Clone the repository**
2. **Install dependencies:**
   ```bash
   uv venv
   source .venv/bin/activate
   uv pip install -r requirements.txt  # or use pyproject.toml with uv
   ```
3. **Set AWS credentials in your environment:**
   ```bash
   export AWS_ACCESS_KEY_ID=your-access-key
   export AWS_SECRET_ACCESS_KEY=your-secret-key
   export AWS_SESSION_TOKEN=your-session-token  # if using temporary credentials
   export AWS_REGION=us-east-1  # or your preferred region
   ```
   > **Security Note:** Never commit your credentials to source control. Use environment variables or a secure credentials manager.

4. **Run the server:**
   ```bash
   uv run server.py
   ```

## Claude Desktop Integration
To use this server as a tool in Claude Desktop, add the following to your `claude_desktop_config.json`:

```json
{
  "mcpServers": {
    "BedrockGuardrailsMCP": {
      "command": "uv",
      "args": [
        "--directory",
        "/Users/haji/mcp-servers/bedrock-guardrails-mcp",
        "run",
        "server.py"
      ]
    }
  }
}
```
- Replace the directory path with your actual project location.
- Restart Claude Desktop after updating the config.

## Example Usage
- **Create a guardrail with full policy config:**
  Use the `create_guardrail_full` tool, passing all required and optional policy configs as dictionaries.
- **Update a guardrail:**
  Use `update_guardrail_full` with the guardrail ID and any fields to update.
- **Export to Terraform:**
  Use `export_guardrail_to_terraform(guardrail_id)` to get a `.tf` resource block for your guardrail.



## Screenshots 

<img width="687" height="651" alt="image" src="https://github.com/user-attachments/assets/5d8481f4-6982-4c2d-9ad8-a86302e71db2" />


<img width="1000" height="755" alt="image" src="https://github.com/user-attachments/assets/15167480-c21d-41bb-a8c3-2408e5e1da60" />


## Impact & Use Cases
- **Enterprise LLM Safety:** Centrally manage and automate Bedrock Guardrails for all your generative AI applications.
- **DevOps & IaC:** Export guardrails to Terraform for version control, reproducibility, and CI/CD integration.
- **LLM Tooling:** Enable LLMs (like Claude) to programmatically manage safety policies, audit, and remediate risks.

## Security
- Credentials are only read from environment variables and never stored in code or logs.
- All AWS API calls are made using the official `boto3` SDK.

## License
See LICENSE file.
