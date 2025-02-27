SHELL=/bin/bash

main:
	# have to make sure script in index.html is POSTing to / instead of ansifier.com...
	gcloud alpha functions local deploy ansifier_local --entry-point=main --runtime=python312

clean:
	gcloud alpha functions local delete ansifier_local

test:
	gcloud alpha functions local call ansifier_local --data='{"url": "https://cdn.pixabay.com/photo/2015/04/23/22/00/tree-736885_640.jpg", "format": "ansi-escaped"}'

rebuild: clean main
