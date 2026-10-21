"""Keep the documented separation enforceable as the application grows."""
import ast
from pathlib import Path

APP = Path(__file__).resolve().parents[1] / "app"


def imports(path):
    tree = ast.parse(path.read_text())
    return [node.module or "" for node in ast.walk(tree) if isinstance(node, ast.ImportFrom)] + [alias.name for node in ast.walk(tree) if isinstance(node, ast.Import) for alias in node.names]


def test_domain_is_framework_and_storage_free():
    for path in (APP / "features").glob("*/domain.py"):
        assert not any(name.split(".")[0] in {"fastapi", "starlette", "pydantic", "sqlite3"} or "storage" in name or "routes" in name for name in imports(path)), path


def test_middleware_is_transport_only_and_storage_has_no_framework():
    assert not any("domain" in name or "storage" in name or "schemas" in name for name in imports(APP / "middleware.py"))
    for path in [APP / "database.py", *(APP / "features").glob("*/storage.py")]:
        assert not any(name.split(".")[0] in {"fastapi", "starlette", "pydantic"} for name in imports(path))
    for path in (APP / "features").glob("*/routes.py"):
        assert "sqlite3" not in imports(path), path


def test_features_do_not_import_sibling_features():
    for directory in (APP / "features").iterdir():
        if not directory.is_dir() or directory.name.startswith("_"):
            continue
        for path in directory.glob("*.py"):
            assert not any("features." in name and f"features.{directory.name}" not in name for name in imports(path)), path
