.PHONY: test compile run e2e e2e-up e2e-down site

HUGO_VERSION ?= 0.160.1

test:
	PYTHONPATH=src:../aweb/awid/src:../pgdbm/src python3 -m pytest -q

e2e:
	set -e; \
	trap 'docker compose -p atext-e2e -f docker-compose.e2e.yml down -v --remove-orphans' EXIT; \
	docker compose -p atext-e2e -f docker-compose.e2e.yml down -v --remove-orphans >/dev/null 2>&1 || true; \
	docker compose -p atext-e2e -f docker-compose.e2e.yml up --build -d; \
	ATEXT_E2E=1 uv run pytest -q -m e2e

e2e-up:
	docker compose -p atext-e2e -f docker-compose.e2e.yml up --build -d

e2e-down:
	docker compose -p atext-e2e -f docker-compose.e2e.yml down -v --remove-orphans

site:
	@hugo version | grep -q "v$(HUGO_VERSION)" || { echo "Expected Hugo v$(HUGO_VERSION); install/pin that version or update HUGO_VERSION intentionally."; exit 1; }
	hugo --source site --destination public --minify

compile:
	PYTHONPATH=src:../aweb/awid/src:../pgdbm/src python3 -m compileall -q src tests

run:
	PYTHONPATH=src:../aweb/awid/src:../pgdbm/src python3 -m uvicorn atext.api:app --host 127.0.0.1 --port 8765 --reload
