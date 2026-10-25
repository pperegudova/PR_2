"""Модуль для построения графа зависимостей алгоритмом BFS."""

from collections import deque
from typing import Dict, Set
from data_fetcher import get_direct_dependencies, FetchError

CYCLE_MARKER = {"__cycle__": True}


def build_dependency_graph(config: dict) -> Dict:
    """Строит дерево зависимостей итеративным поиском в ширину (BFS)."""
    root_pkg = config["package_name"]
    if not config["test_mode"]:
        root_pkg = root_pkg.lower().replace('_', '-')

    max_depth = config["max_depth"]
    filter_str = config["filter_substring"].lower()

    tree = {root_pkg: {}}
    queue = deque([(root_pkg, 0, tree[root_pkg])])
    visited: Set[str] = {root_pkg}

    while queue:
        current_pkg, depth, parent_dict = queue.popleft()
        if depth >= max_depth:
            continue
        try:
            deps = get_direct_dependencies(config, target_package=current_pkg)
        except FetchError:
            continue

        for dep in deps:
            if filter_str and filter_str in dep.lower():
                continue
            if dep in visited:
                parent_dict[dep] = CYCLE_MARKER
            else:
                visited.add(dep)
                parent_dict[dep] = {}
                queue.append((dep, depth + 1, parent_dict[dep]))

    return tree