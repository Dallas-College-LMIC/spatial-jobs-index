"""Configuration classes for external services"""

import os
from pydantic import BaseModel


class LightcastConfig(BaseModel):
    """Configuration for Lightcast API credentials"""
    username: str
    password: str

    @classmethod
    def from_env(cls) -> "LightcastConfig":
        """Create Lightcast config from environment variables"""
        required_vars = ["LCAPI_USER", "LCAPI_PASS"]
        missing_vars = []

        for var in required_vars:
            if not os.getenv(var):
                missing_vars.append(var)

        if missing_vars:
            raise RuntimeError(
                f"Missing required Lightcast environment variables: {', '.join(missing_vars)}"
            )

        return cls(
            username=os.getenv("LCAPI_USER", ""),  # MyPy: provide default to ensure str
            password=os.getenv("LCAPI_PASS", ""),  # MyPy: provide default to ensure str
        )