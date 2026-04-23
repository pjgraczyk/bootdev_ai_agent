set dotenv-load := true
set dotenv-required := true
set dotenv-override := true

alias r := run
alias t := test
alias c := clean

script := 'src/main.py'

run *args="Hello!":
    uv run {{ script }} "{{ args }}";

test:
    uv run python -m unittest discover -p 'test*.py' -s 'tests/'
    pyrefly check
    ruff check
    ruff format

clean:
    #!/bin/sh
    rm -rf **/**.pyc;
    rm -rf ./**/__pycache__
    rm -rf ./**/.ruff_cache

default *args:
    @just run {{ args }}
