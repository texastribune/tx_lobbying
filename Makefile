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
	@echo "  make models.png - make a graph of the app's model"


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
	echo "DROP SCHEMA public CASCADE; CREATE SCHEMA public;" | $(MANAGE) dbshell
# sqlclear does not work on postgres
#	$(MANAGE) sqlclear tx_lobbying | $(MANAGE) dbshell
	$(MANAGE) migrate --noinput


data:
	cd data && $(MAKE) all

import:
	DEBUG=0 YEAR_START=2012 $(MANAGE) lobbying_expenses data/expenses -v 2
# haha I suck at this
	DEBUG=0 $(MANAGE) lobbying_registrations data/lobcon/LobCon09.csv
	DEBUG=0 $(MANAGE) lobbying_registrations data/lobcon/LobCon10.csv
	DEBUG=0 $(MANAGE) lobbying_registrations data/lobcon/LobCon11.csv
	DEBUG=0 $(MANAGE) lobbying_registrations data/lobcon/LobCon12.csv
	DEBUG=0 $(MANAGE) lobbying_registrations data/lobcon/LobCon13.csv
	DEBUG=0 $(MANAGE) lobbying_registrations data/lobcon/LobCon14.csv
	DEBUG=0 python tx_lobbying/scrapers/canonical_interests.py
	DEBUG=0 $(MANAGE) lobbying_stats

# hopefully a slimmer version for dev
import1:
	DEBUG=0 $(MANAGE) lobbying_registrations data/lobcon/LobCon14.csv
	DEBUG=0 YEAR_START=2013 $(MANAGE) lobbying_expenses data/expenses -v 2
# haha I suck at this
	DEBUG=0 $(MANAGE) lobbying_registrations data/lobcon/LobCon12.csv
	DEBUG=0 python tx_lobbying/scrapers/canonical_interests.py
	DEBUG=0 $(MANAGE) lobbying_stats

# stuff I took out of `import1` to make it run faster during dev
import2:
	DEBUG=0 $(MANAGE) lobbying_registrations data/lobcon/LobCon09.csv
	DEBUG=0 $(MANAGE) lobbying_registrations data/lobcon/LobCon10.csv
	DEBUG=0 $(MANAGE) lobbying_registrations data/lobcon/LobCon11.csv
	DEBUG=0 $(MANAGE) lobbying_registrations data/lobcon/LobCon13.csv
	DEBUG=0 $(MANAGE) lobbying_expenses data/expenses -v 2
	DEBUG=0 python tx_lobbying/scrapers/canonical_interests.py
	DEBUG=0 $(MANAGE) lobbying_stats

scrape: data import


models.png:
	$(MANAGE) graph_models -o models.png --disable-fields tx_lobbying


.PHONY: help clean test resetdb data import scrape models.png
