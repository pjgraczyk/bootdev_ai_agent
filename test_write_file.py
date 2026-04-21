import unittest
from functions.write_file import write_file


class TestWriteFile(unittest.TestCase):
    def test_write_simple_file(self):
        result = write_file(
            "calculator", "lorem.txt", "wait, this isn't lorem ipsum"
        )
        self.assertNotIn("Error", result)

    def test_write_file_in_subdirectory(self):
        result = write_file(
            "calculator", "pkg/morelorem.txt", "lorem ipsum dolor sit amet"
        )
        self.assertNotIn("Error", result)

    def test_write_outside_working_directory(self):
        result = write_file(
            "calculator", "/tmp/temp.txt", "this should not be allowed"
        )
        self.assertIn("Error", result)


if __name__ == "__main__":
    unittest.main()
