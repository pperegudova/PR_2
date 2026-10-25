"""Главная точка входа для инструмента анализа графа зависимостей."""

import sys
from validation import load_yaml, validate_config, ConfigError
from data_fetcher import FetchError
from graph_builder import build_dependency_graph
from visualizer import format_ascii_tree

DEFAULT_CONFIG_PATH = "config.yaml"
MIN_CLI_ARG_COUNT = 2


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

        print("\n--- Dependency Tree ---")
        print(format_ascii_tree(graph, pkg))
        print("-----------------------")

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