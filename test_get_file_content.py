from functions.get_file_content import get_file_content

# Test 1: Large file truncation
print("Test 1: Large file truncation")
result = get_file_content("calculator", "lorem.txt")
print(f"Length: {len(result)}")
print(f"Truncated: {'[...File' in result}")
print()

# Test 2: Valid file
print("Test 2: Valid file (main.py)")
result = get_file_content("calculator", "main.py")
print(result)
print()

# Test 3: Valid file in subdirectory
print("Test 3: Valid file in subdirectory")
result = get_file_content("calculator", "pkg/calculator.py")
print(result)
print()

# Test 4: File outside working directory
print("Test 4: File outside working directory")
result = get_file_content("calculator", "/bin/cat")
print(result)
print()

# Test 5: Non-existent file
print("Test 5: Non-existent file")
result = get_file_content("calculator", "pkg/does_not_exist.py")
print(result)
