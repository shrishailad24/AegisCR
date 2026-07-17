import os

inner_app_path = r"c:\Users\shash\PycharmProjects\PythonProject1\PythonProject1\app.py"
outer_app_path = r"c:\Users\shash\PycharmProjects\PythonProject1\app.py"

if os.path.exists(inner_app_path):
    with open(inner_app_path, "r", encoding="utf-8") as f:
        content = f.read()

    prefix = (
        "import sys\n"
        "import os\n"
        'sys.path.append(os.path.join(os.path.dirname(__file__), "PythonProject1"))\n\n'
    )

    new_content = prefix + content

    with open(outer_app_path, "w", encoding="utf-8") as f:
        f.write(new_content)

    print("Synchronized app.py successfully!")
else:
    print("Inner app.py not found at path:", inner_app_path)
