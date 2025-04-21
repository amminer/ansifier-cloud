# ansifier-cloud

This is the source code for a minimal, containerized Google Cloud Run serverless function wrapping
[ansifier](https://github.com/amminer/ansifier),
exposing both graphical and programmatic web frontends for the function,
as well as a gallery of user-submitted text art created on the site (this feature is under
development).

This project largely exists in its current form as a portfolio item, to illustrate some of my full
stack software engineering skills. I'm currently looking for a new full time position in the SE space.
Feel free to [reach out ](https://linkedin.com/in/ameliamminer/)if you smell what I'm cooking, so to speak.

## Usage

The original intended use of this project was to provide an API over HTTP into
[ansifier](https://github.com/amminer/ansifier/). While the graphical interface and related social
features are the main focus of development at this point, this API has been stabilizing for some
time and should be the most consistent and reliable way to use the site for the time being. That
being said, I'm not versioning this application yet, and ansifier itself is in semantic version
0.y.z, so the API is still subject to change especially as needed to keep up with new library
features. Valid requests MUST be POSTs to the /ansify endpoint containing FormData.
A valid request has the form:
```
curl -X POST 'https://ansifier.com/' \
  -F '{file|url}={U}' \
  -F 'format={F}'
  -F 'height={H}'
  -F 'width={W}'
  -F 'characters={C}'
```
where:
* `{U}` is required, either a valid URL pointing to an image file or an uploaded image file,
* `{file|url}` is required, either of the literal strings "file" and "url",
* `{F}` is required, either of the literal strings "html/css" and "ansi-escaped",
* `{H}` and `{W}` are optional height and width of the desired output, in cells composed of 2 adjacent
single-line-height text characters,
* and `{C}` is an optional comma-separated list of characters to use as positive space in the output.

In other words, clients MUST provide:

* either a url or file upload

and they MAY provide:

* an output format string ("ansi-escaped" or "html/css") (defaults to ansi)
* a list of characters to convert the image into (defaults to block chars)
* height
* width

You can also visit https://ansifier.com/ in a browser for a simple graphical client.
By using the graphical client you can optionally submit your ansified image to a public gallery of ansi
art created by users of the site. You can view the gallery at https://ansifier.com/gallery; this feature
is in early development and may change substantially or disappear in the near future.

## API Usage Examples

```
curl -X POST 'https://ansifier.com/ansify' \
  -F 'file=@/path/to/file'
```

```
curl -X POST 'https://ansifier.com/ansify' \
  -F 'url=https://somedomain.com/somefile.mp4' \
  -F 'format=html/css' \
  -F 'height=90' \
  -F 'width=160' \
  -F 'characters=█▓▒░ '
```

## implementation notes

DNS is tricky and somewhat irritating to me, and this is just a fun little project,
so the www.ansifier.com hostname is not officially supported at this point in time.

You can run this locally using `python3` and `make`.
Some environment variables are required; this list is likely to be out of date at times:

* `ANSIFIER_DATABASE` tells the application which backend it should try to use; see
  `/data_model/__init__.py`

