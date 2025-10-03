set export
export VIRTUAL_ENV := justfile_directory() + "/build/venv"
export PATH := justfile_directory() + "/build/venv/bin:" + env('PATH')

all: test docs build

test:
    @just mkenv 'test' 'clg>=3.3 PyYAML>=6.0.2 pytest>=8.2.2 pytest-cov>=6.2.1 pytest-ruff>=0.5'
    pytest
    coverage html
    @rm -rf build/venv .ruff_cache .pytest_cache .coverage birds.yml libpath.cfg

docs:
    @just mkenv 'docs' 'clg>=3.3 PyYAML>=6.0.2 mkdocs>=1.6.1 mkdocs-codeinclude-plugin>=0.2.1'
    @rm -rf build/site
    mkdocs build
    @rm -rf build/venv

build:
    @just mkenv 'build' 'twine'
    @rm -rf build/wheel
    pip wheel -w build/wheel .
    twine check --strict build/wheel/loadconfig*
    cp build/wheel/loadconfig-*-py3-none-any.whl build/wheel/loadconfig-0.0.0-py3-none-any.whl
    python -c "from tomllib import load; c=load(open('ChangeLog','rb')); v=next(iter(c)); print(c[v]['notes'])" > build/notes.md
    @rm -rf build/venv build/lib build/bdist.linux-aarch64 build/scripts-3.12 loadconfig.egg-info

mkenv name wheels:
    @echo -e '\n'
    @rm -rf build/venv
    echo "Building $name"
    python -m venv build/venv
    [ "$wheels" != "" ] && pip install $wheels || true
