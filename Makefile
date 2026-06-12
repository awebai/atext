.PHONY: test compile run e2e e2e-up e2e-down

test:
	PYTHONPATH=src:../aweb/awid/src:../pgdbm/src python3 -m pytest -q

e2e:
	set -e; \
	trap 'docker compose -p atext-e2e -f docker-compose.e2e.yml down -v --remove-orphans' EXIT; \
	docker compose -p atext-e2e -f docker-compose.e2e.yml up --build --wait -d; \
	ATEXT_E2E=1 uv run pytest -q -m e2e

e2e-up:
	docker compose -p atext-e2e -f docker-compose.e2e.yml up --build --wait -d

e2e-down:
	docker compose -p atext-e2e -f docker-compose.e2e.yml down -v --remove-orphans

compile:
	PYTHONPATH=src:../aweb/awid/src:../pgdbm/src python3 -m compileall -q src tests

run:
	PYTHONPATH=src:../aweb/awid/src:../pgdbm/src python3 -m uvicorn atext.api:app --host 127.0.0.1 --port 8765 --reload
