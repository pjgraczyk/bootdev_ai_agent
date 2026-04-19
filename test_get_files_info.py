import unittest
from functions.get_files_info import get_files_info


class TestGetFilesInfo(unittest.TestCase):
    def test_current_directory(self):
        result = get_files_info("calculator", '.')
        self.assertIsNotNone(result)

    def test_subdirectory(self):
        result = get_files_info("calculator", "pkg")
        self.assertIsNotNone(result)

    def test_absolute_path(self):
        result = get_files_info("calculator", "/bin")
        self.assertIsNotNone(result)

    def test_parent_directory(self):
        result = get_files_info("calculator", "../")
        self.assertIsNotNone(result)


if __name__ == "__main__":
    unittest.main()