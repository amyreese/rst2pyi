build:
	python3 setup.py build

venv:
	python3 -m venv .venv
	echo 'run `source .venv/bin/activate` to use virtualenv'

setup:
	python3 -m pip install -Ur requirements.txt
	python3 -m pip install -Ur requirements-dev.txt

dev: venv
	source .venv/bin/activate && make setup
	source .venv/bin/activate && python3 setup.py develop

release: clean lint test
	python3 setup.py sdist bdist_wheel
	python3 -m twine upload dist/*

format:
	isort --apply --recursive rst2pyi setup.py
	black rst2pyi setup.py

lint:
	mypy rst2pyi
	pylint --rcfile .pylint rst2pyi setup.py
	isort --diff --recursive rst2pyi setup.py
	black --check rst2pyi setup.py

test:
	python3 -m coverage run -m rst2pyi.tests
	python3 -m coverage report

clean:
	rm -rf build dist README MANIFEST *.egg-info

distclean:
	rm -rf .venv
