import functions_framework
import requests
import validators

from ansifier import ImageFilePrinter
from PIL import UnidentifiedImageError


# https://github.com/amminer/ansifier#Usage
FORMATS = ['ansi-escaped', 'html/css']
# https://pillow.readthedocs.io/en/stable/handbook/image-file-formats.html
FILE_EXTENSIONS = [ "blp", "bmp", "dds", "dib", "eps", "gif", "icns", "ico", "im", "jpeg", "jpg",
                   "msp", "pcx", "pfm", "png", "ppm", "sgi", "spider", "tga", "tiff", "webp", "xbm",
                   "cur", "dcx", "fits", "fli", "flc", "fpx", "ftex", "gbr", "gd", "imt",
                   "iptc/naa", "mcidas", "mic", "mpo", "pcd", "pixar", "psd", "qoi", "sun", "wal",
                   "wmf", "emf", "xpm", "palm", "pdf", "bufr", "grib", "hdf5", "mpeg" ]
IMAGE_FILEPATH = 'IMAGEFILE'
MAX_FILESIZE_MB = 5
MAX_FILESIZE_KB = 1024 * MAX_FILESIZE_MB
MAX_FILESIZE_B = 1024 * MAX_FILESIZE_KB


@functions_framework.http
def image_url_to_html_text(request):
    """
    Args:
        request (flask.Request): The request object.
        <https://flask.palletsprojects.com/en/1.1.x/api/#incoming-request-data>
    Returns:
        The response text, or any set of values that can be turned into a Response object using
        `make_response`
        <https://flask.palletsprojects.com/en/1.1.x/api/#flask.make_response>.
    """
    request_json = request.get_json(silent=True)

    if request_json is None:
        return serve_UI()

    image_url = None
    if "imageURL" in request_json:
        image_url = request_json["imageURL"]

    format = None
    if "format" in request_json:
        format = request_json["format"]

    message = "unable to process your request ¯\_(ツ)_/¯"
    status = False
    if image_url is not None and format is not None:
        status, message = validate_format(format)
    if status:
        status, message = validate_url(image_url)
    if status:
        status, message = download_url(image_url)
    if status:
        status, message = save_image(message)
    if status:
        _, message = process_imagefile(format, image_url)
    return message


def process_imagefile(format, image_url):
    ret = (False, "failed to process image ¯\_(ツ)_/¯")
    try:
        image_printer = ImageFilePrinter(IMAGE_FILEPATH, output_format=format)

        ret = (True, image_printer.output)
    except UnidentifiedImageError as e:
        ret = (False, f"ERROR: {image_url} does not appear to be an image file")
    except Exception as e:
        ret = (False, 'ERROR: ' + str(e))
    return ret

def save_image(content):
    ret = (False, "failed to process image ¯\_(ツ)_/¯")
    try:
        with open(IMAGE_FILEPATH, 'wb') as wf:
            wf.write(content)

        ret = (True, "")
    except Exception as e:
        ret = (False, 'ERROR: ' + str(e))
    return ret


def download_url(url):
    ret = (False, "failed to download image ¯\_(ツ)_/¯")
    try:
        s = requests.session()
        head_r = s.head(url)
        if head_r.status_code < 200 or head_r.status_code > 299:
            raise ValueError(f"image url returned code {head_r.status_code}")
        size = int(head_r.headers.get('Content-Length', 0))
        if size > MAX_FILESIZE_B:
            raise ValueError(f"File must not exceed {MAX_FILESIZE_MB} MB")
        content_r = s.get(url, timeout=10)

        ret = (True, content_r.content)
    except Exception as e:
        ret = (False, 'ERROR: ' + str(e))
    return ret


def validate_url(url):
    ret = (False, "no valid image URL provided ¯\_(ツ)_/¯")
    try:
        if not validators.url(url):
            raise ValueError("valid URL must be supplied")
        if not url.startswith("https"):
            raise ValueError("only HTTPS urls are allowed")
        if not any(map(lambda ex: url.endswith(ex), FILE_EXTENSIONS)):
            raise ValueError(f"file type must be one of {FILE_EXTENSIONS}")

        ret = (True, "")
    except Exception as e:
        ret = (False, 'ERROR: ' + str(e))
    return ret


def validate_format(format):
    ret = (False, "invalid format ¯\_(ツ)_/¯")
    try:
        if not format in FORMATS:
            raise ValueError(f"Format must be one of {FORMATS}")

        ret = (True, "")
    except Exception as e:
        ret = (False, 'ERROR: ' + str(e))
    return ret


def serve_UI():
    ret = "<html><body>Something went wrong ¯\_(ツ)_/¯</body></html>"
    with open('./index.html', 'r') as rf:
        ret = '\n'.join(rf.readlines())
    return ret
