import sys

from calculator.pkg import Calculator, format_json_output


def main() -> None:
    calculator = Calculator()
    if len(sys.argv) <= 1:
        return

    expression = " ".join(sys.argv[1:])
    try:
        result = calculator.evaluate(expression)
        if result is not None:
            print(format_json_output(expression, result))
    except Exception:
        pass


if __name__ == "__main__":
    main()
