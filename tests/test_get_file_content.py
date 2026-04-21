import unittest
from functions.get_file_content import get_file_content


class TestGetFileContent(unittest.TestCase):
    def test_file_content_returned(self):
        result = get_file_content("calculator", "lorem.txt")
        self.assertGreater(len(result), 0)
        self.assertNotIn("Error", result)

    def test_valid_file(self):
        result = get_file_content("calculator", "main.py")
        self.assertIsNotNone(result)
        self.assertGreater(len(result), 0)

    def test_valid_file_in_subdirectory(self):
        result = get_file_content("calculator", "pkg/calculator.py")
        self.assertIsNotNone(result)
        self.assertGreater(len(result), 0)

    def test_file_outside_working_directory(self):
        result = get_file_content("calculator", "/bin/cat")
        self.assertIn("Error", result)

    def test_nonexistent_file(self):
        result = get_file_content("calculator", "pkg/does_not_exist.py")
        self.assertIn("Error", result)


if __name__ == "__main__":
    unittest.main()
