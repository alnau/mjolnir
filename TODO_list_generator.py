import os

def find_todo_comments(directory):
    todo_comments = []
    
    # Walk through the directory
    for dirpath, _, filenames in os.walk(directory):
        for filename in filenames:
            if filename.endswith('.py'):
                file_path = os.path.join(dirpath, filename)
                with open(file_path, 'r', encoding='utf-8') as file:
                    for line_number, line in enumerate(file, start=1):
                        if 'TODO' in line:
                            todo_comments.append(f"{file_path}:{line_number}: {line.strip()}")
    
    return todo_comments

def write_todo_list(todo_comments, output_file):
    with open(output_file, 'w', encoding='utf-8') as file:
        if todo_comments:
            file.write("# TODO List\n\n")
            for comment in todo_comments:
                file.write(f"- {comment}\n")
        else:
            file.write("# TODO List\n\nNo TODO comments found.\n")

def main():
    directory = os.getcwd()  # Get the current working directory
    output_file = os.path.join(directory, 'TODO_list.md')  # Ensure the output file is in the same directory
    
    todo_comments = find_todo_comments(directory)
    write_todo_list(todo_comments, output_file)

if __name__ == "__main__":
    main()
