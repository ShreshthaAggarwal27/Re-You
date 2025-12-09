import os
import ast
import subprocess
from pathlib import Path
from dotenv import load_dotenv
import re

load_dotenv()
REPO_PATH = Path("data/repo")


def extract_python_functions(file_path):
    """
    Extracts Python functions & classes using AST.
    """
    chunks = []
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            source = f.read()

        tree = ast.parse(source)
        lines = source.splitlines(keepends=True)

        for node in ast.walk(tree):
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
                start = node.lineno - 1
                end = node.body[-1].lineno if node.body else node.lineno
                chunk_code = "".join(lines[start:end])
                chunks.append({
                    "language": "python",
                    "type": "function" if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)) else "class",
                    "name": node.name,
                    "path": str(file_path),
                    "code": chunk_code
                })
    except Exception as e:
        print(f"Error parsing {file_path}: {e}")
    return chunks


def extract_js_functions(file_path):
    chunks = []
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            source = f.read()

        lines = source.splitlines()

        # ✅ function name(...) { ... }
        func_pattern = re.compile(
            r'(function\s+([a-zA-Z0-9_]+)\s*\([^)]*\)\s*{)',
            re.MULTILINE
        )

        # ✅ const name = (...) => { ... }
        arrow_func_pattern = re.compile(
            r'(const\s+([a-zA-Z0-9_]+)\s*=\s*\([^)]*\)\s*=>\s*{)',
            re.MULTILINE
        )

        patterns = [(func_pattern, "function"), (arrow_func_pattern, "function")]

        for pattern, type_name in patterns:
            for match in pattern.finditer(source):
                name = match.group(2) or "anonymous"
                start_line = source[:match.start()].count('\n')
                snippet = "\n".join(lines[start_line:start_line+40])  # grab 40 lines
                chunks.append({
                    "language": "javascript",
                    "type": type_name,
                    "name": name,
                    "path": str(file_path),
                    "code": snippet
                })

        # ✅ class ClassName { ... }
        class_pattern = re.compile(r'class\s+([a-zA-Z0-9_]+)\s*{')
        for match in class_pattern.finditer(source):
            name = match.group(1)
            start_line = source[:match.start()].count('\n')
            snippet = "\n".join(lines[start_line:start_line+80])
            chunks.append({
                "language": "javascript",
                "type": "class",
                "name": name,
                "path": str(file_path),
                "code": snippet
            })

    except Exception as e:
        print(f"Error parsing {file_path}: {e}")

    return chunks


def extract_commits(repo_path):
    """
    Extracts commit history via git log.
    """
    result = subprocess.run(
        ["git", "-C", str(repo_path), "log", "--pretty=format:%H|%ad|%s", "--date=short"],
        capture_output=True,
        text=True
    )

    commits = []
    for line in result.stdout.splitlines():
        parts = line.split("|", 2)
        if len(parts) == 3:
            sha, date, message = parts
            commits.append({
                "sha": sha,
                "date": date,
                "message": message
            })
    return commits


def run_extraction():
    if not REPO_PATH.exists():
        raise FileNotFoundError("Repo not found! Make sure you ran clone_repo.py")

    all_chunks = []

    for file_path in REPO_PATH.rglob("*.py"):
        all_chunks.extend(extract_python_functions(file_path))

    for file_path in REPO_PATH.rglob("*.js"):
        all_chunks.extend(extract_js_functions(file_path))



    commits = extract_commits(REPO_PATH)

    print(f"✅ Extracted {len(all_chunks)} code chunks (functions/classes)")
    print(f"✅ Extracted {len(commits)} commits")

    return all_chunks, commits


if __name__ == "__main__":
    run_extraction()
