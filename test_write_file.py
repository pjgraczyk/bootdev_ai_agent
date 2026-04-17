from functions.write_file import write_file

print("Test 1: Write to a simple file")
result1 = write_file("calculator", "lorem.txt", "wait, this isn't lorem ipsum")
print(result1)
print()

print("Test 2: Write to a file in a subdirectory")
result2 = write_file("calculator", "pkg/morelorem.txt", "lorem ipsum dolor sit amet")
print(result2)
print()

print("Test 3: Try to write outside working directory (should fail)")
result3 = write_file("calculator", "/tmp/temp.txt", "this should not be allowed")
print(result3)
