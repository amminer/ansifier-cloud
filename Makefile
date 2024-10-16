SHELL=/bin/bash

main:
	# have to make sure script in index.html is POSTing to / instead of ansifier.com...
	gcloud alpha functions local delete ansifier_local
	gcloud alpha functions local deploy ansifier_local --entry-point=image_url_to_text --runtime=python312
	sleep 5
	gcloud alpha functions local call ansifier_local --data='{"imageURL": "https://cdn.pixabay.com/photo/2015/04/23/22/00/tree-736885_640.jpg", "format": "ansi-escaped"}'
