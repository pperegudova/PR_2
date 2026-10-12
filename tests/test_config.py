"""Модульные тесты для модуля конфигурации."""

import sys
import os
import unittest
import tempfile

sys.path.insert(
    0, os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
)

from src.validation import load_yaml, validate_config, ConfigError


class TestConfig(unittest.TestCase):
    """Тестовые сценарии для загрузки и валидации конфигурации."""

    def test_load_valid_yaml(self):
        """Тест загрузки валидного YAML-файла."""
        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".yaml", delete=False
        ) as tmp:
            tmp.write("package_name: 'test'\n")
            tmp.flush()
            data = load_yaml(tmp.name)
            self.assertEqual(data["package_name"], "test")
        os.unlink(tmp.name)

    def test_validate_missing_key(self):
        """Тест валидации при отсутствии обязательных ключей."""
        bad_config = {"package_name": "test"}
        with self.assertRaises(ConfigError):
            validate_config(bad_config)

    def test_validate_invalid_depth(self):
        """Тест валидации при некорректном значении max_depth."""
        config = {
            "package_name": "a", "source_path": "b",
            "test_mode": True, "ascii_tree": False,
            "max_depth": 0, "filter_substring": "c"
        }
        with self.assertRaises(ConfigError):
            validate_config(config)