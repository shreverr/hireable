from __future__ import annotations

"""Custom Portia tool: Interact with the alfa-leetcode-api to get LeetCode user profile and skill statistics."""

from typing import Any, Optional, Dict
import requests
from pydantic import BaseModel, Field, validator

from portia.tool import Tool, ToolRunContext, ToolHardError


class LeetCodeAPISchema(BaseModel):
    """Inputs for LeetCodeAPI tool."""

    action: str = Field(
        ...,
        description=(
            "The action to perform. Available actions: "
            "'user_profile' - Get complete user profile data, "
            "'skill_stats' - Get user's skill-based statistics"
        )
    )

    username: str = Field(
        ...,
        description="LeetCode username (required)"
    )

    @validator('action')
    def validate_action(cls, v):
        valid_actions = {'user_profile', 'skill_stats'}
        if v not in valid_actions:
            raise ValueError(
                f"Invalid action. Must be one of: {valid_actions}")
        return v


class LeetCodeAPITool(Tool[Dict[str, Any]]):
    """Tool to interact with the alfa-leetcode-api for LeetCode user data."""

    id: str = "leetcode_api_tool"
    name: str = "LeetCode API Tool"
    base_url: str = "https://alfa-leetcode-api-wxt7.onrender.com"
    description: str = (
        "Get LeetCode user profile and skill statistics through the alfa-leetcode-api. "
        "Provides comprehensive user data and detailed skill breakdowns."
    )
    args_schema: type[BaseModel] = LeetCodeAPISchema
    output_schema: tuple[str, str] = (
        "Dict[str, Any]", "JSON response from the LeetCode API")

    def _make_request(self, endpoint: str) -> Dict[str, Any]:
        """Make HTTP request to the API."""
        url = f"{self.base_url}{endpoint}"

        try:
            response = requests.get(url)
            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            raise ToolHardError(f"Failed to fetch data from LeetCode API: {e}")
        except ValueError as e:
            raise ToolHardError(f"Failed to parse JSON response: {e}")

    def _build_endpoint(self, action: str, username: str) -> str:
        """Build the API endpoint based on the action."""
        if action == 'user_profile':
            return f"/userProfile/{username}"
        elif action == 'skill_stats':
            return f"/skillStats/{username}"
        else:
            raise ToolHardError(f"Unknown action: {action}")

    def run(self, context: ToolRunContext, action: str, username: str) -> Dict[str, Any]:
        """Execute the LeetCode API request."""

        # Build endpoint
        endpoint = self._build_endpoint(action, username)

        # Make the request
        try:
            result = self._make_request(endpoint)

            # Add metadata about the request
            result['_metadata'] = {
                'action': action,
                'username': username,
                'endpoint': endpoint,
                'base_url': self.base_url
            }

            return result

        except Exception as e:
            raise ToolHardError(f"Error executing LeetCode API request: {e}")


# Usage examples and helper functions
def get_user_profile(context: ToolRunContext, username: str) -> Dict[str, Any]:
    """Helper function to get a user's complete profile."""
    tool = LeetCodeAPITool()
    return tool.run(context, action='user_profile', username=username)


def get_skill_stats(context: ToolRunContext, username: str) -> Dict[str, Any]:
    """Helper function to get user's skill-based statistics."""
    tool = LeetCodeAPITool()
    return tool.run(context, action='skill_stats', username=username)
