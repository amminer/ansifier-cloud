SHELL=/bin/bash

main:
	ANSIFIER_CLOUD_DEBUG=1 flask run &

kill:
	-pkill -f 'ansifier-cloud.*flask'

rebuild: kill main

prod:
	flask run &

test_url:
	curl -X POST 'http://127.0.0.1:5000/ansify' \
	-F 'url=https://cdn.outsideonline.com/wp-content/uploads/2023/03/Funny_Dog_H.jpg' \
	-F "width=100"

test_file_upload:
	curl -X POST 'http://127.0.0.1:5000/ansify' \
	-F 'file=@./test.png' \
	-F "format=ansi-escaped" \
	-F "characters=#" \
	-F "width=100"
