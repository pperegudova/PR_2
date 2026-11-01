"""Главная точка входа для инструмента анализа графа зависимостей."""

import sys
import ssl
import urllib.request
import urllib.error
from validation import load_yaml, validate_config, ConfigError
from data_fetcher import FetchError
from graph_builder import build_dependency_graph, get_load_order
from visualizer import format_ascii_tree, format_load_order, format_plantuml

DEFAULT_GRAPH_PATH = "graph.png"
DEFAULT_CONFIG_PATH = "config.yaml"
MIN_CLI_ARG_COUNT = 2
KROKI_API_URL = "https://kroki.io/plantuml/png"
TIMEOUT_SECONDS = 10


def print_config(config: dict) -> None:
    """Выводит все настраиваемые пользователем параметры."""
    print("--- Configuration Parameters ---")
    for key, value in config.items():
        print(f"{key}: {value}")
    print("--------------------------------")


def print_dependencies(pkg_name: str, deps: list) -> None:
    """Выводит список прямых зависимостей на экран."""
    print(f"\nDirect dependencies for '{pkg_name}':")
    if not deps:
        print("No direct dependencies found.")
    else:
        for dep in deps:
            print(f" - {dep}")
    print("-" * 40)


def save_plantuml_as_png(plantuml_text: str, output_path: str) -> None:
    """Сохраняет текст PlantUML в файл PNG через публичный API Kroki."""
    if not output_path:
        return

    data = plantuml_text.encode('utf-8')
    req = urllib.request.Request(KROKI_API_URL, data=data, method='POST')
    req.add_header('Content-Type', 'text/plain')
    req.add_header('User-Agent',
                   'Mozilla/5.0 (Windows NT 10.0; Win64; x64) '
                   'AppleWebKit/537.36 (KHTML, like Gecko) '
                   'Chrome/120.0.0.0 Safari/537.36')

    ssl_context = ssl._create_unverified_context()

    try:
        with urllib.request.urlopen(
            req, timeout=TIMEOUT_SECONDS, context=ssl_context
        ) as response:
            png_data = response.read()
        with open(output_path, 'wb') as file:
            file.write(png_data)
        print(f"[OK] Graph image saved to: {output_path}")
    except urllib.error.URLError as err:
        print(f"[WARNING] Failed to generate PNG via Kroki API: {err.reason}",
              file=sys.stderr)


def _render_graph_outputs(config: dict, graph: dict, pkg_name: str) -> None:
    """Выводит все форматы представления графа согласно настройкам."""
    plantuml_text = format_plantuml(graph, pkg_name)
    save_plantuml_as_png(plantuml_text, DEFAULT_GRAPH_PATH)

    print("\n--- PlantUML Graph Description ---")
    print(plantuml_text)
    print("----------------------------------")

    if config.get("ascii_tree", False):
        print("\n--- Dependency Tree ---")
        print(format_ascii_tree(graph, pkg_name))
        print("-----------------------")

    if config.get("show_load_order", False):
        print("\nCalculating load order...")
        load_order = get_load_order(graph, pkg_name)
        print(format_load_order(load_order))


def main() -> None:
    """Главная функция запуска приложения."""
    config_path = DEFAULT_CONFIG_PATH

    if len(sys.argv) >= MIN_CLI_ARG_COUNT:
        config_path = sys.argv[1]

    try:
        raw_config = load_yaml(config_path)
        validate_config(raw_config)

        pkg = raw_config["package_name"]
        depth = raw_config["max_depth"]
        print(f"\nBuilding graph for '{pkg}' (depth={depth})...")

        graph = build_dependency_graph(raw_config)

        _render_graph_outputs(raw_config, graph, pkg)

    except ConfigError as err:
        print(f"Configuration Error: {err}", file=sys.stderr)
        sys.exit(1)
    except FetchError as err:
        print(f"Data Fetch Error: {err}", file=sys.stderr)
        sys.exit(1)
    except Exception as err:
        print(f"Unexpected Error: {err}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()