# ansifier-cloud

This is the source code for a minimal GCP Cloud Run function wrapping
[ansifier](https://github.com/amminer/ansifier),
providing a dependency-free frontend over the internet.

This is mainly just a fun little learning exercise and/or toy for me.
The design is very silly. I will probably rewrite it eventually.

## Usage

The main intended use is as an API. Valid requests must be POSTS containing FormData.
Clients must provide:

* either a url or file upload, and
* an output format string

and they may provide:

* height
* width
* character set to convert into

You can also visit https://ansifier.com/ in a browser for a simple graphical client.

## Examples

```
curl -X POST 'https://ansifier.com/' \
  -F 'file=@/path/to/file' \
  -F 'format=ansi-escaped'
```

```
curl -X POST 'https://ansifier.com/' \
  -F 'url=https://somedomain.com/somefile.mp4' \
  -F 'format=html/css'
  -F 'height=90'
  -F 'width=160'
  -F 'characters=█,▓,▒,░, '
```
