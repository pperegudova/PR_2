"""Модуль для получения данных о прямых зависимостях пакетов."""

import json
import re
import urllib.request
import urllib.error
import os
import ssl

PYPI_URL_TEMPLATE = "{base}/{package}/json"
TIMEOUT_SECONDS = 10
PACKAGE_NAME_PATTERN = re.compile(r'^([a-zA-Z0-9\-_\.]+)')


class FetchError(Exception):
    """Исключение для ошибок при получении данных."""
    pass


def _parse_dependency_name(dep_string: str) -> str:
    """Извлекает чистое имя пакета из строки зависимости."""
    match = PACKAGE_NAME_PATTERN.match(dep_string.strip())
    if match:
        return match.group(1).lower().replace('_', '-')
    return ""


def _fetch_from_pypi(package_name: str, repo_url: str) -> list:
    """Получает прямые зависимости через PyPI JSON API."""
    base_url = repo_url.rstrip('/')
    url = PYPI_URL_TEMPLATE.format(base=base_url, package=package_name)
    ssl_context = ssl._create_unverified_context()
    try:
        req = urllib.request.urlopen(url, timeout=TIMEOUT_SECONDS,
                                     context=ssl_context)
        data = json.loads(req.read().decode('utf-8'))

        requires_dist = data.get("info", {}).get("requires_dist")
        if not requires_dist:
            return []

        deps = []
        for req_str in requires_dist:
            if 'extra ==' in req_str:
                continue
            name = _parse_dependency_name(req_str)
            if name:
                deps.append(name)
        return deps
    except urllib.error.HTTPError as e:
        raise FetchError(f"HTTP error: {e.code}")
    except urllib.error.URLError as e:
        raise FetchError(f"Network error: {e.reason}")
    except Exception as e:
        raise FetchError(f"Unexpected error: {e}")


def _fetch_from_file(package_name: str, file_path: str) -> list:
    """Получает зависимости из локального тестового файла."""
    if not os.path.exists(file_path):
        raise FetchError(f"File not found: {file_path}")

    with open(file_path, 'r', encoding='utf-8') as f:
        for line in f:
            line = line.strip()
            if line.startswith(f"{package_name}:"):
                deps_str = line.split(':', 1)[1].strip()
                if not deps_str:
                    return []
                return [d.strip().lower() for d in deps_str.split(',')]
    return []


def get_direct_dependencies(config: dict) -> list:
    """Главная функция получения прямых зависимостей."""
    pkg_name = config["package_name"].lower().replace('_', '-')
    source_path = config["source_path"]

    if config["test_mode"]:
        return _fetch_from_file(pkg_name, source_path)

    return _fetch_from_pypi(pkg_name, source_path)