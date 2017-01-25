.PHONY: tests docs

docs:
	${MAKE} -C docs html


tests:
	py.test --pep8 --cov oscar_mws
	py.test -m integration

ROOT_PATH = $(CURDIR)
ENV_VARS = PYTHONPATH=$(ROOT_PATH) # DJANGO_SETTINGS_MODULE=sandbox.sandbox.settings
VIRTUAL_DIR ?= venv
VIRTUAL_DIR_FLAG= $(VIRTUAL_DIR)/bin/python
VIRTUAL = . venv/bin/activate && $(ENV_VARS)

$(VIRTUAL_DIR_FLAG):
	virtualenv \
		--unzip-setuptools \
		--system-site-packages \
		--python=python2.7 \
		$(VIRTUAL_DIR)

.PHONY : setup
setup: $(VIRTUAL_DIR_FLAG)
	$(VIRTUAL) pip install -r requirements.txt

.PHONY : env
env: $(VIRTUAL_DIR_FLAG)
	$(VIRTUAL) /bin/bash

.PHONY : run-py
run-py: $(VIRTUAL_DIR_FLAG)
	$(VIRTUAL) ./sandbox/manage.py runserver

.PHONY : collectstatic
collectstatic: $(VIRTUAL_DIR_FLAG)
	$(VIRTUAL) ./sandbox/manage.py collectstatic --noinput

.PHONY : run
run: $(VIRTUAL_DIR_FLAG)
	$(VIRTUAL) cd sandbox && uwsgi uwsgi.ini

.PHONY : migrate
migrate: $(VIRTUAL_DIR_FLAG)
	$(VIRTUAL) ./sandbox/manage.py migrate

.PHONY : migrate
migrate: $(VIRTUAL_DIR_FLAG)
	$(VIRTUAL) ./sandbox/manage.py migrate

.PHONY : clean
clean:
	rm -fr $(VIRTUAL_DIR)

