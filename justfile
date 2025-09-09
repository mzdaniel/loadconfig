export VIRTUAL_ENV := justfile_directory() + "/build/venv"
export PATH := justfile_directory() + "/build/venv/bin:" + env('PATH')

all: test docs build

test:
    @just mkenv "test" '"pytest>=8.2.2" "ruff>=0.12.11" "pytest-cov>=6.2.1" "clg>=3.3" "PyYAML>=6.0.2"'
    ruff check
    pytest
    coverage html -d build/coverage
    @rm -rf build/venv build/lib .ruff_cache .pytest_cache .coverage loadconfig.egg-info

docs:
    @just mkenv "docs" '"sphinx>=8.1.3" "sphinx_bootstrap_theme>=0.8.1" "sphinx_simplepdf>=1.6" "clg>=3.3" "PyYAML>=6.0.2"'
    sphinx-build -E -d build/.doctrees -b doctest docs build/html
    sphinx-build -E -d build/.doctrees docs build/html
    sphinx-build -E -d build/.doctrees -b simplepdf docs build
    @rm -rf build/venv build/.doctrees build/_static build/objects.inv build/.buildinfo build/index.html

build:
    @just mkenv "build" '"wheel>=0.42"'
    pip wheel -w build/wheel .
    @rm -rf build/venv build/lib build/bdist.linux-aarch64 loadconfig.egg-info

mkenv name wheels:
    @echo -e '\n'
    @rm -rf build/venv
    echo 'Building {{name}}'
    python -m venv build/venv
    uv pip install {{wheels}}
