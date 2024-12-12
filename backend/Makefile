install:
	poetry install

install-test: WITH_GROUP = test
install-lint: WITH_GROUP = lint

install-%:
    # 对应pyproject.toml [tool.poetry.group.$WITH_GROUP.xx]
	poetry install --with $(WITH_GROUP)

lint: install-lint
	poetry run ruff check --config .ruff.toml --fix --unsafe-fixes
	# 优化import顺序
	poetry run importanize --config=importanize.json
    # 静态类型检查
	poetry run mypy --config-file=.mypy.ini .

install-with-pip:
	pip3 install --no-cache-dir -r requirements.txt --index-url https://pypi.org/simple

lint-ci: install-lint
	ruff check --config .ruff.toml --fix --unsafe-fixes
	importanize --ci --config=importanize.json
	mypy --config-file=.mypy.ini .

format:
	ruff format --check

exporter:
	poetry export -f requirements.txt --without-hashes --output requirements.txt

migration:
	python3 command.py migrate up

lock:
	poetry lock --no-update

test-ci: install-test
	pytest tests/test_in_ci
