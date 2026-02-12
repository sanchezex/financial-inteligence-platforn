# Pydantic v2 Migration Plan

This repository currently pins `pydantic==2.x` and `pydantic-settings`. During development we added a small compatibility fallback in `backend/app/core/config.py` to allow running tests in environments where `pydantic-settings` is not installed.

Long-term recommended migration steps (to remove test-only fallbacks):

1. Ensure `backend/requirements.txt` includes both `pydantic` and `pydantic-settings` (it does).
2. Remove the fallback `BaseSettings` and `Field` implementations from `backend/app/core/config.py` so the code imports directly from `pydantic_settings` and `pydantic`.
3. Update any code that relied on Pydantic v1 behaviour to v2 equivalents. Key areas:
   - `BaseSettings` moved to `pydantic-settings` package.
   - `validator` and `root_validator` behavior changes — consult Pydantic migration guide.
4. Add integration tests that run in a clean environment (CI Docker) to catch missing runtime deps.
5. Remove `backend/tests/conftest.py` monkeypatch for `pytest.approx` after ensuring numeric types are consistent across code and tests.

If you want, I can create a PR that performs the safe removal and runs CI to validate. Reply "migrate" to proceed.
