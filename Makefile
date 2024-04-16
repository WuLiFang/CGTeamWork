.PHONY: default

default: .venv/.sentinel

CGTEAMWORK_PYTHON?="C:\cgteamwork\python\python.exe"

.venv:
	virtualenv --python "$(CGTEAMWORK_PYTHON)" --clear .venv
	touch $@


.venv/.sentinel: export PYTHONIOENCODING=utf8
.venv/.sentinel: .venv requirements.txt vendor/*.whl
	. ./scripts/activate-venv.sh &&\
		pip install -U -r requirements.txt
	touch $@
