venv: venv/bin/activate

venv/bin/activate: requirements.txt
	@test -d venv || virtualenv --python=/usr/bin/python3.5 venv
	@venv/bin/pip install -Ur requirements.txt
	@touch venv/bin/activate
	@echo "source venv/bin/activate to activate venv"

test: venv
	venv/bin/python -m unittest discover -v

pep8:
	@for f in $(git ls-files **/*.py); do pep8 $f; done

