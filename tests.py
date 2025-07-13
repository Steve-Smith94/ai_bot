# from subdirectory.filename import function_name
from functions.get_files_info import get_files_info

result = get_files_info("calculator", ".")
print("Result for current directory:")
print(result)

result = get_files_info("calculator", "pkg")
print("Result for pkg directory:")
print(result)

result = get_files_info("calculator","/bin")
print("Result for '/bin' directory:")
print(result)

result = get_files_info("calculator", "../")
print("Result for '../' directory:")
print(result)