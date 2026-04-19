set dotenv-load := true
set dotenv-required := true
set dotenv-override := true

alias r := run

script := 'main.py'

run *args="Hello!":
    uv run {{ script }} "{{ args }}";

default *args:
    @just run {{ args }}
