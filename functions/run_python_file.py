
import os
import sys
import subprocess

def run_python_file(working_directory, file_path, args=[]):

    abs_working_dir = os.path.abspath(working_directory)
    abs_file_path = os.path.abspath(os.path.join(working_directory, file_path))
    
    if not abs_file_path.startswith(abs_working_dir):
        return (f'Error: Cannot execute "{file_path}" as it is outside the permitted working directory')

    if not os.path.exists(abs_file_path):
        return(f'Error: File "{file_path}" not found.')

    if not abs_file_path.endswith(".py"):
        return (f'Error: "{file_path}" is not a Python file.')

    try:
        completed_process = subprocess.run(
        [sys.executable, abs_file_path] + args,
        timeout=30,
        capture_output=True,
        cwd=abs_working_dir
    )

        result_output = ""
        decoded_stdout = completed_process.stdout.decode('utf-8')
        decoded_stderr = completed_process.stderr.decode('utf-8')
        
        if decoded_stdout: 
            result_output += (f"STDOUT: {decoded_stdout}\n")

        if decoded_stderr:
            result_output += (f"STDERR: {decoded_stderr}\n")

        if completed_process.returncode:
            result_output += (f"Exited process with code {completed_process.returncode}\n")

        if not result_output:
            return ("No output produced.")

        else:
            return result_output

    
    except Exception as e:
        return (f"Error: executing Python file: {e}")