"""Package the bot into a zip suitable for upload to aiarena.net."""
import os
import zipfile

INCLUDE_FILES = ["run.py", "requirements.txt"]
INCLUDE_DIRS = ["bot"]
SKIP_DIRS = {"__pycache__", ".git", ".github", "venv", ".venv", ".mypy_cache"}
OUTPUT = "bot.zip"


def _add_dir(zf: zipfile.ZipFile, dir_path: str, base: str) -> None:
    for root, dirs, files in os.walk(dir_path):
        dirs[:] = [d for d in dirs if d not in SKIP_DIRS]
        for name in files:
            if name.endswith(".pyc"):
                continue
            full = os.path.join(root, name)
            zf.write(full, os.path.relpath(full, base))


def main() -> None:
    base = os.path.dirname(os.path.abspath(__file__))
    with zipfile.ZipFile(OUTPUT, "w", zipfile.ZIP_DEFLATED) as zf:
        for f in INCLUDE_FILES:
            path = os.path.join(base, f)
            if os.path.isfile(path):
                zf.write(path, f)
        for d in INCLUDE_DIRS:
            path = os.path.join(base, d)
            if os.path.isdir(path):
                _add_dir(zf, path, base)
    print(f"Created {OUTPUT}")


if __name__ == "__main__":
    main()
