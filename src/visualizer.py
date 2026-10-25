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