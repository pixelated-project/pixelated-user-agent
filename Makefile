VIRTUALENV=~/.venvs/pixua

.PHONY: setup
setup: install

.PHONY: requirements
requirements: requirements_py requirements_js
	@echo "Installed requirements"

.PHONY: install
install: requirements install_py install_js
	@echo "Installed dependencies"

.PHONY: requirements_py
requirements_py: create_virtualenv
	@echo "Upgrading pip and setuptools"
	@. $(VIRTUALENV)/bin/activate;\
	pip install --upgrade pip setuptools

.PHONY: install_py
install_py: service/requirements.txt service/test_requirements.txt
	@echo "Installing python packages"
	@. $(VIRTUALENV)/bin/activate;\
	cd service;\
	pip install pysqlcipher --upgrade --force-reinstall --install-option="--bundled";\
	pip install --exists-action s -r requirements.txt -r test_requirements.txt

.PHONY: requirements_js
requirements_js:
	@echo "Installing javascript npm and bower dependencies"
	@cd web-ui;\
	npm install

.PHONY: install_js
install_js:
	@echo "Building front-end and static files"
	@cd web-ui;\
	npm run build

.PHONY: create_virtualenv
create_virtualenv: ensure_virtualenv_installed
	@if [ ! -e $(VIRTUALENV)/bin/activate ]; then\
		echo "Pixelated virtualenv doesn't exist, creating now";\
		virtualenv --python=python2 $(VIRTUALENV);\
	else\
		echo "Pixelated virtualenv already exists, moving on";\
	fi

.PHONY: test
test: test_py test_js coverage

.PHONY: test_py
test_py: clean requirements install coverage linters_py unit_tests_py integration_tests_py

.PHONY: test_js
test_js: clean requirements_js install_js linters_js unit_tests_js

.PHONY: test_all
test_all: test functional_tests

.PHONY: linters
linters: clean requirements install linters_py linters_js

.PHONY: linters_py
linters_py:
	@echo "Running pep8"
	@. $(VIRTUALENV)/bin/activate;\
	cd service;\
	pep8 --ignore=E501 pixelated test

.PHONY: linters_js
linters_js:
	@echo "Running jshint"
	@cd web-ui;\
	npm run jshint

.PHONY: coverage
coverage:
	@. $(VIRTUALENV)/bin/activate;\
	cd service;\
	coverage run -p --source=pixelated `which trial` test.unit;\
	coverage run -p --source=pixelated `which trial` test.integration;\
	coverage combine;\
	coverage html

.PHONY: unit_tests_py
unit_tests_py:
	@echo "Running python unit tests"
	@. $(VIRTUALENV)/bin/activate;\
	cd service;\
	trial --reporter=text test.unit

.PHONY: unit_tests_js
unit_tests_js:
	@echo "Running javascript unit tests"
	@cd web-ui;\
	npm run test

.PHONY: integration_tests_py
integration_tests:
	@echo "Running integration tests"
	@. $(VIRTUALENV)/bin/activate;\
	cd service;\
	trial -j`grep -c "^processor" /proc/cpuinfo || sysctl -n hw.logicalcpu` --reporter=text test.integration

.PHONY: functional_tests
functional_tests: clean requirements install ensure_phantomjs_installed
	@echo "Running behave functional tests"
	@. $(VIRTUALENV)/bin/activate;\
	cd service;\
	behave --tags ~@wip --tags ~@smoke test/functional/features

.PHONY: ensure_phantomjs_installed
ensure_phantomjs_installed:
	@if [ ! `which phantomjs` ]; then\
		echo "You need phantomJS to run these tests";\
		exit 1;\
	fi

.PHONY: ensure_virtualenv_installed
ensure_virtualenv_installed:
	@if [ ! `which virtualenv` ]; then\
		echo "Virtualenv must be installed";\
		exit 1;\
	else\
		echo "Virtualenv located at "`which virtualenv`;\
	fi

.PHONY: clean
clean: clean_py clean_js clean_cache
	@echo "Cleaning temporary files and the caches"

.PHONY: clean_all
clean_all: clean remove_javascript_packages remove_virtualenv
	@echo "Cleaning temporary files, the caches and the virtualenv"

.PHONY: clean_py
clean_py:
	rm -rf service/_trial_temp
	find . -name "*.pyc" -delete
	rm -rf service/.coverage
	rm -rf service/htmlcov

.PHONY: clean_js
clean_js:
	rm -rf web-ui/dist
	rm -rf web-ui/.sass-cache

.PHONY: clean_cache
clean_cache:
	rm -rf ~/.config/leap
	rm -rf ~/.leap
	rm -rf service/ghostdriver.log

.PHONY: remove_virtualenv
remove_virtualenv:
	rm -rf $(VIRTUALENV)

.PHONY: remove_javascript_packages
remove_javascript_packages:
	rm -rf web-ui/node_modules
	rm -rf web-ui/app/bower_components
