.PHONY: test compile run

test:
	PYTHONPATH=src:../aweb/awid/src:../pgdbm/src python3 -m pytest -q

compile:
	PYTHONPATH=src:../aweb/awid/src:../pgdbm/src python3 -m compileall -q src tests

run:
	PYTHONPATH=src:../aweb/awid/src:../pgdbm/src python3 -m uvicorn atext.api:app --host 127.0.0.1 --port 8765 --reload
