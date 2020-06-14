PYTHON_BIN_DIR=../../venv/bin

.PHONY: football-data-load
football-data-load:
	${PYTHON_BIN_DIR}/python football_data_co_uk.py

.PHONY: run-all
run-all:
	${PYTHON_BIN_DIR}/python football_data_co_uk.py
	${PYTHON_BIN_DIR}/python football_1xbet.py

.PHONY: 1xbet
1xbet:
	${PYTHON_BIN_DIR}/python football_1xbet.py

.PHONY: infogol
infogol:
	${PYTHON_BIN_DIR}/scrapy runspider infogol.py

.PHONY: infogol
fivethirtyeight:
	${PYTHON_BIN_DIR}/python football_fivethirtyeight.py

.PHONY: soccerpunter
soccerpunter:
	${PYTHON_BIN_DIR}/scrapy runspider soccerpunter.py -o result.json -t json

.PHONY: betstady
betstady:
	${PYTHON_BIN_DIR}/scrapy runspider betstady.py -o result.json -t json

.PHONY: hltv
hltv:
	${PYTHON_BIN_DIR}/scrapy runspider hltv.py -o result.json -t json

.PHONY: opendota
opendota:
	${PYTHON_BIN_DIR}/scrapy runspider opendota.py -o result.json -t json
