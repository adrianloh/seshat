import os
import ast
import importlib
from importlib.metadata import version, PackageNotFoundError
from pathlib import Path
from typing import Set, Dict

class ImportVisitor(ast.NodeVisitor):
    def __init__(self):
        self.imports = set()

    def visit_Import(self, node):
        for name in node.names:
            self.imports.add(name.name.split('.')[0])

    def visit_ImportFrom(self, node):
        if node.module:
            self.imports.add(node.module.split('.')[0])

def find_imports_in_file(file_path: str) -> Set[str]:
    with open(file_path, 'r', encoding='utf-8') as file:
        try:
            tree = ast.parse(file.read())
            visitor = ImportVisitor()
            visitor.visit(tree)
            return visitor.imports
        except SyntaxError:
            print(f"Warning: Could not parse {file_path}")
            return set()

def is_built_in(module_name: str) -> bool:
    try:
        spec = importlib.util.find_spec(module_name)
        if spec is None:
            return False
        return 'site-packages' not in str(spec.origin)
    except (AttributeError, ImportError, ValueError):
        return False

def get_package_version(module_name: str) -> str:
    try:
        return version(module_name)
    except PackageNotFoundError:
        return None

def discover_dependencies(module_path: str) -> Dict[str, str]:
    all_imports = set()
    
    for root, _, files in os.walk(module_path):
        for file in files:
            if file.endswith('.py'):
                file_path = os.path.join(root, file)
                all_imports.update(find_imports_in_file(file_path))

    dependencies = {}
    for module in all_imports:
        if not is_built_in(module):
            version = get_package_version(module)
            if version:
                dependencies[module] = version

    return dependencies

def create_pyproject_toml(module_name: str, version: str, author: str, description: str, dependencies: Dict[str, str]):
    requires = [f"{pkg}>={ver}" for pkg, ver in dependencies.items()]
    content = f'''[build-system]
requires = ["setuptools>=42", "wheel"]
build-backend = "setuptools.build_meta"

[project]
name = "{module_name}"
version = "{version}"
authors = [
    {{ name = "{author}" }}
]
description = "{description}"
readme = "README.md"
requires-python = ">=3.6"
classifiers = [
    "Programming Language :: Python :: 3",
    "License :: OSI Approved :: MIT License",
    "Operating System :: OS Independent",
]
dependencies = [
{chr(10).join(f'    "{req}",' for req in requires)}
]

[tool.setuptools.packages.find]
where = ["."]  # list of folders that contain the packages (["."] by default)
'''
    with open("pyproject.toml", "w") as f:
        f.write(content)

def setup_package():
    # Get module name first
    print("Please provide your module name:")
    module_name = input("Module name: ").strip()
    
    # Check if module directory exists
    module_path = Path(module_name)
    if not module_path.is_dir():
        print(f"Error: Directory '{module_name}' not found!")
        return
    
    # Check for __init__.py
    if not (module_path / "__init__.py").exists():
        print(f"Warning: No __init__.py found in {module_name}/")
        create_init = input("Create __init__.py? (y/n): ")
        if create_init.lower() == 'y':
            (module_path / "__init__.py").touch()
    
    print(f"\nDiscovering dependencies in {module_name}/...")
    dependencies = discover_dependencies(module_name)
    
    if dependencies:
        print("\nDiscovered dependencies:")
        for pkg, version in dependencies.items():
            print(f"- {pkg} (>={version})")
    else:
        print("\nNo external dependencies found.")
    
    confirm = input("\nAre these dependencies correct? (y/n): ")
    if confirm.lower() != 'y':
        print("Please modify setup.cfg manually after creation.")
    
    # Get and validate version
    while True:
        version = input("Version (e.g., 0.1.0): ").strip()
        if not version:
            print("Version cannot be empty!")
            continue
        try:
            from packaging.version import Version
            Version(version)  # This will raise InvalidVersion if format is wrong
            break
        except ImportError:
            if not version.replace('.', '').isdigit():
                print("Please use a simple version format like 0.1.0")
                continue
            break
        except Exception as e:
            print(f"Invalid version format: {e}")
            print("Please use a valid version format (e.g., 0.1.0)")
            continue
    
    # Get other required fields
    while True:
        author = input("Author name: ").strip()
        if author:
            break
        print("Author name cannot be empty!")
    
    while True:
        description = input("Short description: ").strip()
        if description:
            break
        print("Description cannot be empty!")
    
    # Create the necessary files
    create_pyproject_toml(module_name, version, author, description, dependencies)
    
    print("\nFiles created successfully!")
    print("\nNext steps:")
    print("1. Review and update the README.md")
    print("2. Install build tools: pip install build twine")
    print("3. Build your package: python -m build")
    print("4. Upload to PyPI: twine upload dist/*")

if __name__ == "__main__":
    setup_package()