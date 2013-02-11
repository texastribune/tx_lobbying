PROJECT=./example_project

help:
	@echo "  make test    - run test suite"
	@echo "  make resetdb - delete and recreate the database"


test:
	python $(PROJECT)/manage.py test


resetdb:
	python $(PROJECT)/manage.py reset_db --router=default --noinput
	python $(PROJECT)/manage.py syncdb --noinput


.PHONY: help test resetdb
