This is the source code for a minimal GCP Cloud Run function wrapping
[ansifier](https://github.com/amminer/ansifier)

# Usage

Visit https://ansifier.com/ in a browser for a simple graphical client.

You can also use the function programatically by sending a POST request to the site.

Valid requests must be JSON if the source image is behind a URL, like so:

```
curl -X POST 'https://ansifier.com/' \
  -H 'Content-Type: application/json' \
  -d '{"imageURL":"https://cdn.freebiesupply.com/logos/large/2x/debian-2-logo-png-transparent.png",
       "format":"ansi-escaped"}'
```

Or FormData if the source image is a direct file upload, like so:

```
curl -X POST 'https://ansifier.com/' \
  -F 'file=@/path/to/imagefile' \
  -F 'format=ansi-escaped'
```

"soon"™️ I plan to...
* strip this interface back to just one of these formats 
* add fields to allow most of the knobs the backend has to be tweaked
