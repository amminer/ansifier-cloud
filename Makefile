SHELL=/bin/bash

main:
	ANSIFIER_DEBUG=1 flask run &

kill:
	-pkill -f 'ansifier-cloud.*flask'
	-pkill -f 'gunicorn*'

rebuild: kill main

prod:
	gunicorn -p :443 app:app

get_all_ansi_from_sqlite3:
	sqlite3 ./test.db 'SELECT art FROM art WHERE format = "ansi-escaped"'
