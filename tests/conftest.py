import os
import sys
import subprocess
from pathlib import Path

# Set test database environment variables BEFORE any Masonite imports
os.environ["DB_CONNECTION"] = "sqlite"
os.environ["SQLITE_DB_DATABASE"] = "masonite_test.sqlite3"
os.environ.setdefault("DB_LOG", "false")

# Temporarily move .env file to prevent it from overriding test settings
_env_backup = None
_env_file = Path(".env")
if _env_file.exists():
    _env_backup = _env_file.read_text(encoding="utf-8")
    try:
        _env_file.rename(".env.backup")
    except Exception:
        pass


def pytest_sessionstart(session):
    """Configure an isolated test database and run migrations before tests."""
    # Ensure a dedicated test env file is used by Masonite loader in subprocesses
    env_test_path = Path(".env.test").resolve()
    os.environ["ENVPATH"] = str(env_test_path)

    # Write a minimal .env.test so the craft process loads the test DB
    env_test_content = (
        "DB_CONNECTION=sqlite\n"
        "SQLITE_DB_DATABASE=masonite_test.sqlite3\n"
        "DB_LOG=false\n"
    )
    try:
        env_test_path.write_text(env_test_content, encoding="utf-8")
    except Exception:
        pass

    db_file = Path(os.environ["SQLITE_DB_DATABASE"]).resolve()
    # Start from a clean slate
    if db_file.exists():
        try:
            db_file.unlink()
        except Exception:
            pass

    # Run migrations against the test DB
    subprocess.check_call([sys.executable, "craft", "migrate"]) 


def pytest_sessionfinish(session, exitstatus):
    """Restore .env file and optionally remove the test database after the run."""
    # Restore the original .env file
    if _env_backup is not None:
        env_file = Path(".env")
        try:
            env_file.write_text(_env_backup, encoding="utf-8")
        except Exception:
            pass

    # Remove the backup file
    backup_file = Path(".env.backup")
    if backup_file.exists():
        try:
            backup_file.unlink()
        except Exception:
            pass

    db_path = os.environ.get("SQLITE_DB_DATABASE")
    if db_path:
        db_file = Path(db_path).resolve()
        # Comment out the next 3 lines if you prefer to keep the DB for inspection.
        # Only remove if it's our test database
        # if db_file.exists() and db_file.name == "masonite_test.sqlite3":
        #     try:
        #         db_file.unlink()
        #     except Exception:
        #         pass

    # Keep .env.test by default; uncomment to remove automatically
    # try:
    #     Path(os.environ.get("ENVPATH", ".env.test")).unlink()
    # except Exception:
    #     pass


