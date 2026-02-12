Title: CI: add Docker-based tests and make tests robust

Summary:
- Add GitHub Actions workflow to build the backend Docker image and run pytest inside it.
- Make code resilient to CI vs local differences:
  - provide safe fallbacks for optional services during local runs
  - add a compatibility import for `pydantic-settings` and a minimal fallback for environments without it (temporary)
  - make `PortfolioService` and `PaperTradingService` handling more robust for tests
  - add `backend/tests/conftest.py` shim to avoid Decimal/pytest.approx issues in legacy environments
- Add `Makefile` and `backend/README_TESTING.md` with instructions to run tests locally and with Docker.

Why:
- Ensure consistent, reproducible test runs in CI using Docker.
- Allow contributors to run tests locally even if system Python lacks venv/ensurepip.

Notes/TODO:
- Consider removing test-only fallbacks and fully migrating code to Pydantic v2 (`pydantic-settings`) once CI is green. See MIGRATE_PYDANTIC.md.
