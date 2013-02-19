lobcon=LobCon

help:
	@echo "csv, download, lobcon, expenses"


csv:
	@echo "Converting Lobbyist Registrations from XLS to CSV"
	$(foreach file, $(wildcard $(lobcon)/*.xls), \
		in2csv $(file) > $(subst xls,csv,$(file));)

download:
	mkdir -p $(lobcon)
	rm -rf $(lobcon)/*.xls
	cd $(lobcon) && wget http://www.ethics.state.tx.us/tedd/LobCon13.xls
	cd $(lobcon) && wget http://www.ethics.state.tx.us/tedd/LobCon12.xls
	cd $(lobcon) && wget http://www.ethics.state.tx.us/tedd/LobCon11.xls
	cd $(lobcon) && wget http://www.ethics.state.tx.us/tedd/LobCon10.xls
	cd $(lobcon) && wget http://www.ethics.state.tx.us/tedd/LobCon09.xls

lobcon: download csv


expenses:
	mkdir -p Expenses
	wget http://www.ethics.state.tx.us/tedd/TEC_LA_CSV.zip
	unzip -u TEC_LA_CSV.zip -d Expenses
	rm TEC_LA_CSV.zip


.PHONY: help csv download lobcon expenses
