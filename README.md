# Инструмент визуализации графа зависимостей пакетов (Этапы 1-5, Вариант 13)

---

## 1. Общее описание

Проект представляет собой CLI-приложение (работающее через командную
строку) для анализа и визуализации графа зависимостей пакетов. 
На Этапе 5 реализовано формирование текстового представления графа на языке PlantUML, сохранение изображения графа в формате PNG.
 

### Основные особенности и реализованные требования Этапа 1:

- читает настраиваемые пользователем параметры из конфигурационного
  файла формата YAML;
- выполняет полную валидацию всех параметров;
- выводит все параметры в формате «ключ-значение»;
- корректно обрабатывает ошибки конфигурации, завершая работу с
  ненулевым кодом возврата и сообщением в поток `stderr`.

### Основные особенности и реализованные требования Этапа 2:
- Получение данных осуществляется через стандартные средства языка (модули `urllib` и `json`), без использования сторонних библиотек или готовых менеджеров пакетов.
- Поддержка двух режимов: обращение к реальному репозиторию (PyPI API) по URL и чтение из локального тестового файла.
- Корректный парсинг сырых данных репозитория: извлечение чистых имен пакетов из строк с ограничениями версий и фильтрация опциональных зависимостей (`extra`).
- Нормализация имен пакетов.
- Вывод списка прямых зависимостей на экран.

### Основные особенности и реализованные требования Этапа 3:
- Построение графа: Реализован алгоритм поиска в ширину (BFS, с помощью очереди `collections.deque`).
- Ограничение глубины: Анализ зависимостей строго ограничен параметром `max_depth`.
- Пакеты, имя которых содержит заданную пользователем подстроку (`filter_substring`), исключаются из анализа.
- Алгоритм корректно обрабатывает циклические зависимости, помечая их маркером `(cycle)` и предотвращая бесконечный обход.
- Вывод построенного графа в консоль в виде ASCII-дерева с использованием символов псевдографики.
- Поддержка локального файла тестового репозитория, в котором имена пакетов называются большими латинскими буквами.

### Основные особенности и реализованные требования Этапа 4:
- Расчёт порядка загрузки зависимостей с использованием алгоритма
  топологической сортировки (алгоритм Кана).
- Искусственный «разрыв» циклов: пакеты, участвующие в цикле, помечаются
  `(cycle)`, а зависимые от них пакеты загружаются в обычном порядке.
- Добавлен параметр конфигурации `show_load_order` для управления выводом.

### Основные особенности и реализованные требования Этапа 5:
- Формирование текстового представления графа зависимостей на языке диаграмм PlantUML.
- Вывод описания графа на языке PlantUML на экран.
- Сохранение изображения графа в файле формата PNG (через публичный API рендеринга Kroki.io).
- Условный вывод зависимостей в виде ASCII-дерева (управляется параметром `ascii_tree`).

---

## 2. Описание всех функций и настроек

### Настраиваемые параметры

Все параметры задаются в файле `config.yaml`:
- `package_name` (str): Имя анализируемого пакета.
- `source_path` (str): URL-адрес репозитория или путь к файлу тестового репозитория.
- `test_mode` (bool): Режим работы с тестовым репозиторием.
- `ascii_tree` (bool): Режим вывода зависимостей в формате ASCII-дерева.
- `max_depth` (int): Максимальная глубина анализа зависимостей (должна быть >= 1).
- `filter_substring` (str): Подстрока для фильтрации пакетов.
- `show_load_order` (bool): Вывод порядка загрузки зависимостей.

### Описание функций

**Модуль `src/validation.py`:**
- `load_yaml(file_path)`: Загружает YAML-файл по указанному пути и возвращает словарь. Обрабатывает ошибки отсутствия файла и синтаксиса YAML.
- `validate_config(config)`: Проверяет наличие всех обязательных ключей в словаре конфигурации.
- `_validate_types(config)`: Проверяет соответствие типов данных для каждого параметра и валидность значений (например, `max_depth` > 0).

**Модуль `src/data_fetcher.py`:**
- `_parse_dependency_name(dep_string)`: Извлекает чистое имя пакета из строки вида `"urllib3 (<2,>=1.21.1)"` с помощью регулярных выражений и нормализует его.
- `_fetch_from_pypi(package_name, repo_url)`: Формирует запрос к JSON API репозитория, обрабатывает сетевые ошибки и извлекает массив `requires_dist`.
- `_fetch_from_file(package_name, file_path)`: Читает зависимости из локального текстового файла формата `имя_пакета: зависимость1, зависимость2`.
- `get_direct_dependencies(config, target_package=None)`: Главная функция, которая маршрутизирует запрос в зависимости от параметра `test_mode`.

**Модуль `src/graph_builder.py`:**
- `build_dependency_graph(config)`: Строит дерево зависимостей итеративным алгоритмом BFS. Применяет фильтрацию по подстроке и ограничение по глубине.
- `_extract_dependencies(tree, pkg_name)`: преобразует дерево в плоский
  словарь множеств зависимостей.
- `_collect_all_packages(deps_map)`: Собирает все уникальные пакеты.
- `_build_graph_metrics(deps_map, all_packages)`: Строит `in_degree` и
  `reverse_deps` для топологической сортировки.
- `_topological_sort(in_degree, reverse_deps)`: Выполняет классический
  алгоритм Кана.
- `_find_cycle_members(remaining, deps_map)`: Находит пакеты,
  непосредственно участвующие в цикле.
- `_break_cycles_and_continue(...)`: Разрывает циклы и продолжает
  сортировку для оставшихся пакетов.
- `get_load_order(tree, pkg_name)`: Вычисляет итоговый порядок загрузки.

**Модуль `src/visualizer.py`:**
- `format_ascii_tree(tree, pkg_name)`: Форматирует полученный словарь-дерево в строку с использованием символов ASCII-псевдографики (`├──`, `└──`, `│`). Циклические зависимости помечаются как `(cycle)`.
- `format_load_order(load_order)`: Форматирует список порядка загрузки в
  виде нумерованного списка.
- `format_plantuml(tree, pkg_name)`: Формирует текстовое описание графа зависимостей на языке PlantUML со списком уникальных рёбер.

**Модуль `src/main.py`:**
- `print_config(config)`: Выводит все прочитанные параметры в консоль в формате ключ-значение.
- `print_dependencies(pkg_name, deps)`: Форматирует и выводит список полученных прямых зависимостей.
- `_render_graph_outputs(config, graph, pkg_name)`: Координирует вывод всех форматов представления графа.
- `save_plantuml_as_png(plantuml_text, output_path)`: Сохраняет текст PlantUML в файл PNG через публичный API Kroki.io.
- `main()`: Точка входа в приложение. Загружает конфиг, валидирует его, вызывает построение графа, визуализирует результат и перехватывает исключения.

---
## 3. Описание команд для сборки проекта и запуска тестов

**Установка зависимостей (выполняется один раз):**

```bash
pip install -r requirements.txt
```

**Запуск приложения**

```bash
python3 src/main.py
```

**Запуск модульных тестов**

```bash
python3 -m unittest discover -s tests
```

---

## 4. Примеры использования

### 4.1. Успешный запуск (Реальный репозиторий PyPI)

Содержимое `config.yaml`:

```yaml
package_name: "boto3"
source_path: "https://pypi.org/pypi/"
test_mode: false
ascii_tree: true
max_depth: 6
filter_substring: ""
show_load_order: false
```

Результат:

```bash
Building graph for 'boto3' (depth=6)...
[OK] Graph image saved to: graph.png

--- PlantUML Graph Description ---
@startuml
' Dependency graph for boto3'
skinparam monochrome true
"boto3" --> "botocore"
"botocore" --> "jmespath"
"botocore" --> "python-dateutil"
"python-dateutil" --> "tzdata"
"botocore" --> "urllib3"
"boto3" --> "jmespath"
"boto3" --> "s3transfer"
"s3transfer" --> "botocore"
@enduml
----------------------------------

--- Dependency Tree ---
boto3
├── botocore
│   ├── jmespath
│   ├── python-dateutil
│   │   └── tzdata
│   └── urllib3
├── jmespath
└── s3transfer
    └── botocore
        ├── jmespath
        ├── python-dateutil
        │   └── tzdata
        └── urllib3
-----------------------
```

Содержимое `graph.png`:
![graph.png](graph.png)

### 4.2. Успешный запуск (Тестовый режим)

Содержимое `config.yaml`:

```yaml
package_name: "WEBAPP"
source_path: "tests/test_repo_stage4.txt"
test_mode: true
ascii_tree: true
max_depth: 6
filter_substring: ""
show_load_order: false
```

Содержимое `test_repo_stage4.txt`:

```yaml
WEBAPP: FRONTEND, BACKEND
FRONTEND: REACT
BACKEND: NODE
NODE: EXPRESS
EXPRESS: LOOP_A
LOOP_A: LOOP_B
LOOP_B: LOOP_A
```

Результат:

```bash
Building graph for 'WEBAPP' (depth=6)...
[OK] Graph image saved to: graph.png

--- PlantUML Graph Description ---
@startuml
' Dependency graph for WEBAPP'
skinparam monochrome true
"WEBAPP" --> "FRONTEND"
"FRONTEND" --> "REACT"
"WEBAPP" --> "BACKEND"
"BACKEND" --> "NODE"
"NODE" --> "EXPRESS"
"EXPRESS" --> "LOOP_A"
"LOOP_A" --> "LOOP_B"
"LOOP_B" --> "LOOP_A"
@enduml
----------------------------------

--- Dependency Tree ---
WEBAPP
├── FRONTEND
│   └── REACT
└── BACKEND
    └── NODE
        └── EXPRESS
            └── LOOP_A
                └── LOOP_B
                    └── LOOP_A (cycle)
-----------------------
```

Содержимое `graph.png`:
![img.png](img.png)

### 4.3. Обработка ошибок конфигурации

Каждая ошибка выводится в поток `stderr`, приложение завершает работу
с кодом возврата `1`.

Содержимое `config.yaml` (ошибка: недостаточно параметров):

```yaml
package_name: "requests"
source_path: "./test_repo.txt"
test_mode: true
ascii_tree: false
max_depth: 5
show_load_order: true
```

Результат:

```bash
Configuration Error: Missing key: filter_substring
```

### 4.4. Обработка сетевых ошибок

Содержимое `config.yaml` (несуществующий пакет):

```yaml
package_name: "non_existent_package"
source_path: "https://pypi.org/pypi/"
test_mode: false
ascii_tree: false
max_depth: 5
filter_substring: "urllib"
show_load_order: true
```

Результат:

```bash
Data Fetch Error: HTTP error: 404
```