help:
	@echo "typecheck - run mypy typechecking"
	@echo "typecheck-xml - run mypy typechecking with junit output"
	@echo "lint - run flake8 checks"
	@echo "lint-xml - run flake8 checks with junit output"
	@echo "pytest - run unit tests"
	@echo "pytest-xml - run unit tests with junit output"

typecheck:
	mypy deva tests server/mlserver python_client

typecheck-xml:
	mypy deva tests server/mlserver python_client | mypy2junit > ./tests/results/mypy.xml

lint:
	flake8 deva tests server/mlserver python_client

lint-xml:
	flake8 deva tests server/mlserver python_client --tee --output-file ./tests/results/flake8.txt
	flake8_junit ./tests/results/flake8.txt ./tests/results/flake8.xml

test:
	pytest . --cov=deva tests/	

test-xml:
	py.test --junitxml=tests/results/cov.xml --cov=deva --cov-report=html:tests/results/coverage --cache-clear tests/
