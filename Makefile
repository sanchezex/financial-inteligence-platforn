.PHONY: build-backend test-docker test-local

build-backend:
	docker build -t future-backend:dev backend

test-docker: build-backend
	docker run --rm future-backend:dev sh -c "cd backend && PYTHONPATH=. pytest -q"

test-local:
	PYTHONPATH=backend python3 -m pytest -q
