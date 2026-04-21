import sys
from calculator.pkg import Calculator, format_json_output


def main():
    calculator = Calculator()
    if len(sys.argv) <= 1:
        return

    expression = " ".join(sys.argv[1:])
    try:
        result = calculator.evaluate(expression)
        if result is not None:
            to_print = format_json_output(expression, result)
        else:
            pass
    except Exception as e:
        pass


if __name__ == "__main__":
    main()
