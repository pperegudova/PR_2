"""Модуль для загрузки и валидации YAML-конфигурации."""

import yaml
import os
import sys

MIN_DEPTH = 1
REQUIRED_KEYS = [
    "package_name", "source_path", "test_mode",
    "ascii_tree", "max_depth", "filter_substring"
]


class ConfigError(Exception):
    """Пользовательское исключение для ошибок конфигурации."""
    pass


def load_yaml(file_path: str) -> dict:
    """Загружает YAML-файл и возвращает словарь."""
    if not os.path.exists(file_path):
        raise ConfigError(f"File not found: {file_path}")

    try:
        with open(file_path, "r", encoding="utf-8") as file:
            return yaml.safe_load(file)
    except yaml.YAMLError as err:
        raise ConfigError(f"YAML parsing error: {err}")


def validate_config(config: dict) -> None:
    """Проверяет типы и наличие ключей в словаре конфигурации."""
    if not isinstance(config, dict):
        raise ConfigError("Config must be a dictionary")

    for key in REQUIRED_KEYS:
        if key not in config:
            raise ConfigError(f"Missing key: {key}")

    _validate_types(config)


def _validate_types(config: dict) -> None:
    """Проверяет конкретные типы значений в конфигурации."""
    if not isinstance(config["package_name"], str):
        raise ConfigError("package_name must be a string")

    if not isinstance(config["source_path"], str):
        raise ConfigError("source_path must be a string")

    if not isinstance(config["test_mode"], bool):
        raise ConfigError("test_mode must be a boolean")

    if not isinstance(config["ascii_tree"], bool):
        raise ConfigError("ascii_tree must be a boolean")

    if not isinstance(config["max_depth"], int):
        raise ConfigError("max_depth must be an integer")

    if config["max_depth"] < MIN_DEPTH:
        raise ConfigError("max_depth must be >= 1")

    if not isinstance(config["filter_substring"], str):
        raise ConfigError("filter_substring must be a string")