VIRTUAL_ENV ?= .venv

.PHONY: run
run: $(VIRTUAL_ENV)
	$(VIRTUAL_ENV)/bin/pip install -r requirements.txt
	yarn install || npm install
	cp -n Lagerregal/template_development.py Lagerregal/settings.py
	$(VIRTUAL_ENV)/bin/python manage.py compilemessages -l de
	$(VIRTUAL_ENV)/bin/python manage.py migrate
	$(VIRTUAL_ENV)/bin/python manage.py populate
	$(VIRTUAL_ENV)/bin/python manage.py runserver

.PHONY: makemessages
makemessages: $(VIRTUAL_ENV)
	$(VIRTUAL_ENV)/bin/python manage.py makemessages -l de -d django --ignore=node_modules
	$(VIRTUAL_ENV)/bin/python manage.py makemessages -l de -d djangojs --ignore=node_modules

.PHONY: test
test: $(VIRTUAL_ENV)
	$(VIRTUAL_ENV)/bin/pip install coverage
	$(VIRTUAL_ENV)/bin/coverage run --branch --omit=.venv/* manage.py test
	$(VIRTUAL_ENV)/bin/coverage html --skip-covered

.PHONY: lint
lint: $(VIRTUAL_ENV)
	$(VIRTUAL_ENV)/bin/pip install flake8 isort
	$(VIRTUAL_ENV)/bin/isort -rc api demo devicegroups devices devicetags devicetypes history Lagerregal locale locations mail main media network users
	$(VIRTUAL_ENV)/bin/flake8

$(VIRTUAL_ENV):
	python3 -m venv $(VIRTUAL_ENV)
	$(VIRTUAL_ENV)/bin/pip install -U pip
