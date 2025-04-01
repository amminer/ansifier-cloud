SHELL=/bin/bash
ANSIFIER_DB_TYPE = sqlite3
ANSIFIER_DEBUG = 1

main:
	ANSIFIER_DEBUG=$(ANSIFIER_DEBUG) ANSIFIER_DB_TYPE=$(ANSIFIER_DB_TYPE) flask run &

kill:
	-pkill -f 'ansifier-cloud.*flask'

rebuild: kill main

prod:
	ANSIFIER_DB_TYPE=$(ANSIFIER_DB_TYPE) flask run &

test_url:
	curl -X POST 'http://127.0.0.1:5000/ansify' \
	-F 'url=https://cdn.outsideonline.com/wp-content/uploads/2023/03/Funny_Dog_H.jpg' \
	-F "width=60" \
	-F "height=60"

test_file_upload:
	curl -X POST 'http://127.0.0.1:5000/ansify' \
	-F 'file=@./test.png' \
	-F "format=ansi-escaped" \
	-F "characters=#" \
	-F "width=60" \
	-F "height=60"
