import os
from colorama import Fore, Style

c = Fore.LIGHTCYAN_EX
y = Fore.LIGHTYELLOW_EX
re = Fore.RESET

D = Style.DIM
R = Style.RESET_ALL

def count_lines_in_file(file_path):
    """Count the number of lines in a given file."""
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            lines = file.readlines()
            return len(lines)
    except Exception as e:
        print(f"Error reading {file_path}: {e}")
        return 0
    

def count_lines_in_directory(directory_path):
    """Count the total number of lines in all .py files in the given directory."""
    total_lines = 0
    for root, _, files in os.walk(directory_path):
        for file in files:
            if file.endswith('.py'):
                file_path = os.path.join(root, file)
                lines_in_file = count_lines_in_file(file_path)
                total_lines += lines_in_file
                print(f"{'{:>6}'.format('{:,}'.format(lines_in_file).replace(',', '.'))} lines {D}{y}{file_path.replace('..\\', '')}{R}")
    return total_lines


if __name__ == "__main__":
    # app.py
    app_lines = count_lines_in_file('..\\app.py')
    print(f"{'{:>6}'.format('{:,}'.format(app_lines).replace(',', '.'))} lines {D}{y}app.py{R}")

    # classes directory
    classes_directory = '..\\classes'
    total_class_lines = count_lines_in_directory(classes_directory)
    print(f"{'{:>6}'.format('{:,}'.format(total_class_lines).replace(',', '.'))} lines {D}{y}Total lines in 'classes' directory{R}")

    # Total lines
    grand_total = app_lines + total_class_lines
    print(f"{c}{'{:>6}'.format('{:,}'.format(grand_total).replace(',', '.'))} lines {D}Grand Total lines of code{R}")
