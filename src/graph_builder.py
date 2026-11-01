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
    queue = deque([(root_pkg, 0, tree[root_pkg], (root_pkg,))])

    while queue:
        current_pkg, depth, parent_dict, path = queue.popleft()
        if depth >= max_depth:
            continue
        try:
            deps = get_direct_dependencies(config, target_package=current_pkg)
        except FetchError:
            continue

        for dep in deps:
            if filter_str and filter_str in dep.lower():
                continue
            if dep in path:
                parent_dict[dep] = CYCLE_MARKER
                continue

            parent_dict[dep] = {}
            queue.append((dep, depth + 1, parent_dict[dep], path + (dep,)))
    return tree


def _extract_dependencies(tree: dict, pkg_name: str) -> dict:
    """Преобразует дерево зависимостей в плоский словарь множеств зависимостей."""
    deps_map = {}

    def _traverse(node: dict, parent: str):
        if parent not in deps_map:
            deps_map[parent] = set()
        for child, children_tree in node.items():
            deps_map[parent].add(child)
            if children_tree != CYCLE_MARKER:
                _traverse(children_tree, child)

    _traverse(tree.get(pkg_name, {}), pkg_name)
    return deps_map


def _collect_all_packages(deps_map: dict) -> set:
    """Собирает все уникальные пакеты из карты зависимостей."""
    all_packages = set(deps_map.keys())
    for deps in deps_map.values():
        all_packages.update(deps)
    return all_packages


def _build_graph_metrics(deps_map: dict, all_packages: set) -> tuple:
    """Строит in_degree и reverse_deps для топологической сортировки."""
    in_degree = {pkg: 0 for pkg in all_packages}
    reverse_deps = {pkg: [] for pkg in all_packages}

    for pkg, deps in deps_map.items():
        for dep in deps:
            in_degree[pkg] += 1
            reverse_deps[dep].append(pkg)

    return in_degree, reverse_deps


def _topological_sort(in_degree: dict, reverse_deps: dict) -> list:
    """Выполняет классическую топологическую сортировку (алгоритм Кана)."""
    queue = deque([
        pkg for pkg, degree in in_degree.items() if degree == 0
    ])
    load_order = []

    while queue:
        current = queue.popleft()
        load_order.append(current)
        for dependent in reverse_deps[current]:
            in_degree[dependent] -= 1
            if in_degree[dependent] == 0:
                queue.append(dependent)

    return load_order


def _find_cycle_members(remaining: list, deps_map: dict) -> set:
    """Находит пакеты, непосредственно участвующие в цикле."""
    cycle_members = set()
    remaining_set = set(remaining)

    for pkg in remaining:
        for dep in deps_map.get(pkg, set()):
            if dep in remaining_set and pkg in deps_map.get(dep, set()):
                cycle_members.add(pkg)
                cycle_members.add(dep)

    return cycle_members


def _break_cycles_and_continue(
    remaining: list, in_degree: dict, reverse_deps: dict,
    deps_map: dict, processed: set
) -> list:
    """Разрывает циклы и продолжает сортировку для оставшихся пакетов."""
    cycle_members = _find_cycle_members(remaining, deps_map)
    result = []

    for pkg in sorted(cycle_members):
        result.append(f"{pkg} (cycle)")
        processed.add(pkg)

    for pkg in cycle_members:
        for dependent in reverse_deps[pkg]:
            if dependent not in processed:
                in_degree[dependent] -= 1

    queue = deque([pkg for pkg in remaining if in_degree[pkg] == 0])

    while queue:
        current = queue.popleft()
        if current not in processed:
            result.append(current)
            processed.add(current)
            for dependent in reverse_deps[current]:
                if dependent not in processed:
                    in_degree[dependent] -= 1
                    if in_degree[dependent] == 0:
                        queue.append(dependent)

    for pkg in remaining:
        if pkg not in processed:
            result.append(f"{pkg} (cycle)")

    return result


def get_load_order(tree: dict, pkg_name: str) -> list:
    """Вычисляет порядок загрузки зависимостей через топологическую сортировку."""
    deps_map = _extract_dependencies(tree, pkg_name)
    all_packages = _collect_all_packages(deps_map)
    in_degree, reverse_deps = _build_graph_metrics(deps_map, all_packages)

    load_order = _topological_sort(in_degree, reverse_deps)
    processed = set(load_order)

    remaining = [pkg for pkg in all_packages if pkg not in processed]
    if remaining:
        cycle_result = _break_cycles_and_continue(
            remaining, in_degree, reverse_deps, deps_map, processed
        )
        load_order.extend(cycle_result)

    return load_order