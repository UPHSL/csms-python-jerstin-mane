
"""Configuration settings for the CSMS Flask application."""

import os

from csms.database import DEFAULT_DATABASE_PATH


class BaseConfig:
    """Settings shared by all application environments."""

    APP_NAME = "Community Services Management System"
    APP_VERSION = "0.1.0"
    CURRENT_SPRINT = "Sprint 0 - Developer Onboarding"

    DATABASE_PATH = DEFAULT_DATABASE_PATH

    SECRET_KEY = os.environ.get(
        "CSMS_SECRET_KEY",
        "development-only-secret-key",
    )


class DevelopmentConfig(BaseConfig):
    """Local development configuration."""

    DEBUG = True


class TestingConfig(BaseConfig):
    """Automated testing configuration."""

    TESTING = True
    DEBUG = False
    SECRET_KEY = "testing-secret-key"
