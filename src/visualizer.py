"""Модуль для визуализации графа зависимостей в консоли."""

CYCLE_MARKER = {"__cycle__": True}


def format_ascii_tree(tree: dict, pkg_name: str) -> str:
    """Форматирует дерево зависимостей в виде ASCII-строки."""
    lines = [pkg_name]

    def _render(node: dict, prefix: str = "", is_last: bool = True):
        items = list(node.items())
        for i, (child, children_tree) in enumerate(items):
            is_last_child = (i == len(items) - 1)
            connector = "└── " if is_last_child else "├── "
            extension = "    " if is_last_child else "│   "

            if children_tree == CYCLE_MARKER:
                lines.append(f"{prefix}{connector}{child} (cycle)")
            else:
                lines.append(f"{prefix}{connector}{child}")
                if children_tree:
                    _render(children_tree, prefix + extension, is_last_child)

    _render(tree.get(pkg_name, {}))
    return "\n".join(lines)


def format_load_order(load_order: list) -> str:
    """Форматирует список порядка загрузки в виде нумерованного списка."""
    lines = ["--- Load Order ---"]
    for i, pkg in enumerate(load_order, 1):
        lines.append(f"{i:2d}. {pkg}")
    lines.append("------------------")
    return "\n".join(lines)


def format_plantuml(tree: dict, pkg_name: str) -> str:
    """Форматирует дерево зависимостей в виде текста на языке PlantUML."""
    lines = ["@startuml"]
    lines.append(f"' Dependency graph for {pkg_name}'")
    lines.append("skinparam monochrome true")

    root_children = tree.get(pkg_name, {})

    if not root_children:
        lines.append(f'"{pkg_name}"')
    else:
        def _collect_edges(node: dict, parent: str, visited_edges: set):
            for child, children_tree in node.items():
                edge_str = f'"{parent}" --> "{child}"'
                if edge_str not in visited_edges:
                    lines.append(edge_str)
                    visited_edges.add(edge_str)

                if children_tree != CYCLE_MARKER:
                    _collect_edges(children_tree, child, visited_edges)

        _collect_edges(tree.get(pkg_name, {}), pkg_name, set())
    lines.append("@enduml")
    return "\n".join(lines)