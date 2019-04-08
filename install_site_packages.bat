pip install -U pip pipenv
pipenv run pip install --target="%~pd0lib/site-packages" --upgrade -r "%~dp0requirements.txt"
