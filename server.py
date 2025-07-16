from typing import Any, Optional
import logging
import boto3
from mcp.server.fastmcp import FastMCP
from botocore.exceptions import ClientError
import json
import os

# Initialize logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("bedrock-guardrails-mcp")

# Initialize FastMCP server
mcp = FastMCP("bedrock-guardrails")

# Get AWS credentials and region from environment variables
aws_access_key_id = os.environ.get("AWS_ACCESS_KEY_ID")
aws_secret_access_key = os.environ.get("AWS_SECRET_ACCESS_KEY")
aws_session_token = os.environ.get("AWS_SESSION_TOKEN")
aws_region = os.environ.get("AWS_REGION", "us-east-1")

boto3_kwargs = {"region_name": aws_region}
if aws_access_key_id and aws_secret_access_key:
    boto3_kwargs["aws_access_key_id"] = aws_access_key_id
    boto3_kwargs["aws_secret_access_key"] = aws_secret_access_key
    if aws_session_token:
        boto3_kwargs["aws_session_token"] = aws_session_token

# Initialize boto3 client for Bedrock (update region as needed)
bedrock = boto3.client("bedrock", **boto3_kwargs)

def _filter_none(d):
    """Recursively remove None values from dicts/lists."""
    if isinstance(d, dict):
        return {k: _filter_none(v) for k, v in d.items() if v is not None}
    if isinstance(d, list):
        return [_filter_none(x) for x in d if x is not None]
    return d

@mcp.tool()
def list_guardrails() -> list[dict[str, Any]]:
    """List all Bedrock Guardrails in the AWS account."""
    try:
        paginator = bedrock.get_paginator("list_guardrails")
        guardrails = []
        for page in paginator.paginate():
            guardrails.extend(page.get("guardrailSummaries", []))
        return guardrails
    except ClientError as e:
        logger.error(f"Error listing guardrails: {e}")
        return []

@mcp.tool()
def get_guardrail(guardrail_id: str) -> Optional[dict[str, Any]]:
    """Get details of a specific Bedrock Guardrail by its ID."""
    try:
        response = bedrock.get_guardrail(guardrailIdentifier=guardrail_id)
        return response.get("guardrail")
    except ClientError as e:
        logger.error(f"Error getting guardrail {guardrail_id}: {e}")
        return None

@mcp.tool()
def create_guardrail_full(
    name: str,
    blocked_input_messaging: str,
    blocked_outputs_messaging: str,
    description: Optional[str] = None,
    content_policy_config: Optional[dict] = None,
    contextual_grounding_policy_config: Optional[dict] = None,
    cross_region_config: Optional[dict] = None,
    kms_key_arn: Optional[str] = None,
    sensitive_information_policy_config: Optional[dict] = None,
    tags: Optional[list] = None,
    topic_policy_config: Optional[dict] = None,
    word_policy_config: Optional[dict] = None
) -> dict:
    """Create a Bedrock Guardrail with full policy configuration."""
    try:
        payload = _filter_none({
            "name": name,
            "blockedInputMessaging": blocked_input_messaging,
            "blockedOutputsMessaging": blocked_outputs_messaging,
            "description": description,
            "contentPolicyConfig": content_policy_config,
            "contextualGroundingPolicyConfig": contextual_grounding_policy_config,
            "crossRegionConfig": cross_region_config,
            "kmsKeyId": kms_key_arn,
            "sensitiveInformationPolicyConfig": sensitive_information_policy_config,
            "tags": tags,
            "topicPolicyConfig": topic_policy_config,
            "wordPolicyConfig": word_policy_config
        })
        response = bedrock.create_guardrail(**payload)
        return response
    except ClientError as e:
        logger.error(f"Error creating guardrail: {e}")
        return {"error": str(e)}

@mcp.tool()
def update_guardrail_full(
    guardrail_id: str,
    name: Optional[str] = None,
    blocked_input_messaging: Optional[str] = None,
    blocked_outputs_messaging: Optional[str] = None,
    description: Optional[str] = None,
    content_policy_config: Optional[dict] = None,
    contextual_grounding_policy_config: Optional[dict] = None,
    cross_region_config: Optional[dict] = None,
    kms_key_arn: Optional[str] = None,
    sensitive_information_policy_config: Optional[dict] = None,
    tags: Optional[list] = None,
    topic_policy_config: Optional[dict] = None,
    word_policy_config: Optional[dict] = None
) -> dict:
    """Update a Bedrock Guardrail with full policy configuration."""
    try:
        payload = _filter_none({
            "guardrailIdentifier": guardrail_id,
            "name": name,
            "blockedInputMessaging": blocked_input_messaging,
            "blockedOutputsMessaging": blocked_outputs_messaging,
            "description": description,
            "contentPolicyConfig": content_policy_config,
            "contextualGroundingPolicyConfig": contextual_grounding_policy_config,
            "crossRegionConfig": cross_region_config,
            "kmsKeyId": kms_key_arn,
            "sensitiveInformationPolicyConfig": sensitive_information_policy_config,
            "tags": tags,
            "topicPolicyConfig": topic_policy_config,
            "wordPolicyConfig": word_policy_config
        })
        response = bedrock.update_guardrail(**payload)
        return response
    except ClientError as e:
        logger.error(f"Error updating guardrail {guardrail_id}: {e}")
        return {"error": str(e)}

@mcp.tool()
def export_guardrail_to_terraform(guardrail_id: str, tf_resource_name: str = "bedrock_guardrail") -> str:
    """Export a guardrail's configuration as a Terraform .tf file string using the AWS::Bedrock::Guardrail schema."""
    try:
        resp = bedrock.get_guardrail(guardrailIdentifier=guardrail_id)
        g = resp.get("guardrail")
        if not g:
            return f"No guardrail found for id {guardrail_id}"
        # Map AWS API fields to Terraform/CloudFormation fields
        tf_props = {
            "Type": "AWS::Bedrock::Guardrail",
            "Properties": _filter_none({
                "Name": g.get("name"),
                "Description": g.get("description"),
                "BlockedInputMessaging": g.get("blockedInputMessaging"),
                "BlockedOutputsMessaging": g.get("blockedOutputsMessaging"),
                "ContentPolicyConfig": g.get("contentPolicy"),
                "ContextualGroundingPolicyConfig": g.get("contextualGroundingPolicy"),
                "CrossRegionConfig": g.get("crossRegionConfig"),
                "KmsKeyArn": g.get("kmsKeyArn"),
                "SensitiveInformationPolicyConfig": g.get("sensitiveInformationPolicy"),
                "Tags": g.get("tags"),
                "TopicPolicyConfig": g.get("topicPolicy"),
                "WordPolicyConfig": g.get("wordPolicy")
            })
        }
        # Terraform HCL is similar to JSON for resource blocks
        tf_block = f'resource "awscc_bedrock_guardrail" "{tf_resource_name}" ' + json.dumps(tf_props, indent=2)
        return tf_block
    except ClientError as e:
        logger.error(f"Error exporting guardrail {guardrail_id} to terraform: {e}")
        return f"Error: {e}"

@mcp.tool()
def delete_guardrail(guardrail_id: str) -> bool:
    """Delete a Bedrock Guardrail by its ID."""
    try:
        bedrock.delete_guardrail(guardrailIdentifier=guardrail_id)
        return True
    except ClientError as e:
        logger.error(f"Error deleting guardrail {guardrail_id}: {e}")
        return False

if __name__ == "__main__":
    mcp.run(transport="stdio")
