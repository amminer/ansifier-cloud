# ansifier-cloud

This is the source code for a minimal GCP Cloud Run function wrapping
[ansifier](https://github.com/amminer/ansifier),
providing a free-to-use web frontend to the function.

This is mainly just a fun little learning exercise and/or toy for me.
The design is very silly. I will probably rewrite it eventually.

## Usage

The main intended use is as an API. Valid requests must be POSTS containing FormData. A valid request has the form
```
curl -X POST 'https://ansifier.com/' \
  -F '{file|url}={U}' \
  -F 'format={F}'
  -F 'height={H}'
  -F 'width={W}'
  -F 'characters={C}'
```
where
* `{U}` is required, either a valid URL pointing to an image file or an uploaded image file,
* `{file|url}` is required, either of the literal strings "file" and "url",
* `{F}` is required, either of the literal strings "html/css" and "ansi-escaped",
* `{H}` and `{W}` are optional height and width of the desired output, in cells composed of 2 adjacent
single-line-height text characters,
* and `{C}` is an optional comma-separated list of characters to use as positive space in the output.

In other words, clients must provide:

* either a url or file upload

and they may provide:

* an output format string ("ansi-escaped" or "html/css") (defaults to ansi)
* a list of characters to convert the image into (defaults to block chars)
* height
* width

## Examples

```
curl -X POST 'https://ansifier.com/ansify' \
  -F 'file=@/path/to/file' \
```

```
curl -X POST 'https://ansifier.com/ansify' \
  -F 'url=https://somedomain.com/somefile.mp4' \
  -F 'format=html/css'
  -F 'height=90'
  -F 'width=160'
  -F 'characters=█▓▒░ '
```

You can also visit https://ansifier.com/ in a browser for a simple graphical client.

I chose to use Google Cloud's [Cloud Run Domain Mapping](https://cloud.google.com/run/docs/mapping-custom-domains#run)
service to manage my DNS records for this application. This feature of GCP is in the "preview" release stage.
Since December 3rd 2024, www.ansifier.com has returned a Google 404 error page. In retrospect, I
should have used GCP's built-in DNS system to purchase the domain or just hosted my own
infrastructure instead of using an experimental feature of Google's platform. At least it's just my
www record that isn't working - https://ansifier.com has remained online as far as I can tell.
