import unittest

from functions.run_python_file import run_python_file


class TestRunPythonFile(unittest.TestCase):
    def test_run_python_file_main_no_args(self) -> None:
        result = run_python_file("calculator", "main.py")
        self.assertIsNotNone(result)

    def test_run_python_file_main_with_args(self) -> None:
        result = run_python_file("main.py", "calculator", args=["3 + 5"])
        self.assertIsNotNone(result)

    def test_run_python_file_tests(self) -> None:
        result = run_python_file("calculator", "tests.py")
        self.assertIsNotNone(result)

    def test_run_python_file_parent_directory(self) -> None:
        result = run_python_file("calculator", "../main.py")
        self.assertIn("Error", result)

    def test_run_python_file_nonexistent(self) -> None:
        result = run_python_file("calculator", "nonexistent.py")
        self.assertIn("Error", result)

    def test_run_python_file_wrong_extension(self) -> None:
        result = run_python_file("calculator", "lorem.txt")
        self.assertIn("Error", result)


if __name__ == "__main__":
    unittest.main()
