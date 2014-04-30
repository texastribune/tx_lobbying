PROJECT=./example_project
MANAGE=python $(PROJECT)/manage.py


help:
	@echo "make commands:"
	@echo "  make help    - this help"
	@echo "  make clean   - remove temporary files in .gitignore"
	@echo "  make test    - run test suite"
	@echo "  make resetdb - delete and recreate the database"
	@echo "  make import  - download everything, import everything"


clean:
	find -name "*.pyc" -delete
	find . -name ".DS_Store" -delete
	rm -rf MANIFEST
	rm -rf build
	rm -rf dist
	rm -rf *.egg-info


test:
	ENVIRONMENT=test $(MANAGE) test


resetdb:
	$(MANAGE) sqlclear tx_lobbying | $(MANAGE) dbshell
	$(MANAGE) migrate --noinput


import:
# cd data && $(MAKE) all
# python example_project/manage.py lobbying_expenses data/expenses
	find data/lobcon/*.csv | xargs python example_project/manage.py lobbying_registrations
	python tx_lobbying/scrapers/canonical_interests.py
	python example_project/manage.py lobbying_stats


.PHONY: help clean test resetdb import
