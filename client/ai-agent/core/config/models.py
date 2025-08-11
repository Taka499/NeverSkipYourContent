# core/config/models
import base64
import json
import os
from typing import Any, Tuple, Callable
import boto3
from botocore.exceptions import ClientError, NoCredentialsError, NoRegionError
from pydantic_settings import BaseSettings, SettingsConfigDict

from .models import CombinedCoreSettings


SettingsSourceCallable = Callable[[BaseSettings], dict[str, Any]]


class SecretsManagerSource:
    """
    A custom settings source for Pydantic that retrieves settings from AWS Secrets Manager
    """

    def __init__(self, secret_name: str, region_name: str = "ap-northeast-1"):
        self.secret_name = secret_name
        self.region_name = region_name
        self.client = boto3.client("secretsmanager", region_name=region_name)

    def __call__(self, settings: BaseSettings) -> dict:
        try:
            response = self.client.get_secret_value(SecretId=self.secret_name)
        except (ClientError, NoCredentialsError, NoRegionError) as e:
            raise ValueError(f"Failed to retrieve secret {self.secret_name}: {e}")

        secret: bytes | str | None = response.get("SecretString")
        # If SecretString is None, try SecretBinary
        if secret is None and (b64 := response.get("SecretBinary")) is not None:
            try:
                secret = base64.b64decode(b64)
            except Exception as e:
                raise ValueError(
                    f"Failed to decode base64 from secret {self.secret_name}: {e}"
                )

        if secret is None:
            raise ValueError(f"Secret {self.secret_name} not found or empty.")

        try:
            if isinstance(secret, (bytes, bytearray)):
                return json.loads(secret.decode("utf-8"))
            return json.loads(secret)
        except (UnicodeDecodeError, json.JSONDecodeError) as e:
            raise ValueError(
                f"Failed to parse JSON from secret {self.secret_name}: {e}"
            )


class LocalAppSettings(CombinedCoreSettings):
    """
    Local application settings, loaded from environment variables or a local .env file.
    """

    model_config = SettingsConfigDict(
        env_file=".env", env_file_encoding="utf-8", extra="ignore"
    )


class AWSAppSettings(CombinedCoreSettings):
    """
    AWS application settings, loaded from AWS Secrets Manager.
    AWS settings prioritized from AWS Secrets Manager, then init/env/.env.
    `APP_SECRET_NAME` and `AWS_REGION` (or `AWS_DEFAULT_REGION`) can control the secret lookup.
    """

    @classmethod
    def settings_customise_sources(
        cls,
        settings_cls,
        init_settings: SettingsSourceCallable,
        env_settings: SettingsSourceCallable,
        dotenv_settings: SettingsSourceCallable,
        file_secret_settings: SettingsSourceCallable,
    ) -> Tuple[SettingsSourceCallable, ...]:
        """Prioritize AWS Secrets Manager settings"""
        # Read env directly to avoid instantiating settings inside the hook
        secret_name = os.getenv("APP_SECRET_NAME", "my_secret")
        region = (
            os.getenv("AWS_REGION")
            or os.getenv("AWS_DEFAULT_REGION")
            or "ap-northeast-1"
        )

        return (
            SecretsManagerSource(
                secret_name=secret_name,
                region_name=region,
            ),
            init_settings,
            env_settings,
            dotenv_settings,
            file_secret_settings,
        )
