SHELL=/bin/bash

main:
	python -m venv venv
	source venv/bin/activate;\
	pip install -r requirements.txt;\
	echo "running server on localhost:8080...";\
	functions-framework-python --target image_url_to_text;
