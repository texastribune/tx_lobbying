PROJECT=./example_project
MANAGE=python $(PROJECT)/manage.py


help:
	@echo "make commands:"
	@echo "  make help    - this help"
	@echo "  make clean   - remove temporary files in .gitignore"
	@echo "  make test    - run test suite"
	@echo "  make resetdb - delete and recreate the database"
	@echo "  make data    - download everything"
	@echo "  make import  - import everything"
	@echo "  make scrape  - download everything, import everything"


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


data:
	cd data && $(MAKE) all

import:
	DEBUG=0 python example_project/manage.py lobbying_expenses data/expenses -v 2
# haha I suck at this
#	DEBUG=0 python example_project/manage.py lobbying_registrations data/lobcon/LobCon09.csv
#	DEBUG=0 python example_project/manage.py lobbying_registrations data/lobcon/LobCon10.csv
#	DEBUG=0 python example_project/manage.py lobbying_registrations data/lobcon/LobCon11.csv
	DEBUG=0 python example_project/manage.py lobbying_registrations data/lobcon/LobCon12.csv
	DEBUG=0 python example_project/manage.py lobbying_registrations data/lobcon/LobCon13.csv
	DEBUG=0 python example_project/manage.py lobbying_registrations data/lobcon/LobCon14.csv
	DEBUG=0 python tx_lobbying/scrapers/canonical_interests.py
	DEBUG=0 python example_project/manage.py lobbying_stats

scrape: data import


.PHONY: help clean test resetdb data import scrape
