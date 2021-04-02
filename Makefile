.PHONY: default

default: .venv/.sentinel

CGTEAMWORK_PYTHON?="C:\cgteamwork\python\python.exe"

.venv:
	virtualenv --python "$(CGTEAMWORK_PYTHON)" --clear .venv
	touch $@

.venv/.sentinel: .venv requirements.txt
	. ./scripts/activate-venv.sh &&\
		pip install -U -r requirements.txt
	touch $@
