# core/config/settings.py
from typing import Optional, Type

from .loaders import LocalAppSettings
from .models import CombinedCoreSettings

_settings: Optional[CombinedCoreSettings] = None


def initialize_settings(settings_class: Type[CombinedCoreSettings] = LocalAppSettings):
    """
    Initialize the settings object using the specified settings class.

    This function should be called once at the start of the application to load the settings.

    Args:
        settings_class (Type[CombinedCoreSettings], optional): The settings class to use. Defaults to LocalAppSettings.
    """
    global _settings
    if _settings is not None:
        # avoid re-initializing settings
        return
    _settings = settings_class()


def get_settings() -> CombinedCoreSettings:
    """
    Returns the initialized settings object.

    If the settings have not been initialized, it raises an error.

    Returns:
        CombinedCoreSettings: The initialized settings object.
    """
    if _settings is None:
        raise ValueError(
            "Settings have not been initialized. Call initialize_settings() at the beginning of your application."
        )
    return _settings
