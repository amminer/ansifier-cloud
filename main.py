import functions_framework
import requests
import validators

from ansifier import ansify
from PIL import UnidentifiedImageError


FILE_EXTENSIONS = [ "blp", "bmp", "dds", "dib", "eps", "gif", "icns", "ico", "im", "jpeg", "jpg",
                   "msp", "pcx", "pfm", "png", "ppm", "sgi", "spider", "tga", "tiff", "webp", "xbm",
                   "cur", "dcx", "fits", "fli", "flc", "fpx", "ftex", "gbr", "gd", "imt",
                   "iptc/naa", "mcidas", "mic", "mpo", "pcd", "pixar", "psd", "qoi", "sun", "wal",
                   "wmf", "emf", "xpm", "palm", "pdf", "bufr", "grib", "hdf5", "mpeg",

                   ".mp4", ".mov", ".mkv", ".avi", ".wmv", ".flv", ".mpeg", ".mpg", ".3gp", ".webm",
                   ".ogv", ".m4v", ".ts", ".mts", ".m2ts", ".divx", ".vob", ".rm", ".rmvb", ".asf"
                   ]
IMAGE_FILEPATH = "IMAGEFILE"
MAX_FILESIZE_MB = 5
MAX_FILESIZE_KB = 1000 * MAX_FILESIZE_MB
MAX_FILESIZE_B = 1000 * MAX_FILESIZE_KB


@functions_framework.http
def main(request):
    """
    Args:
        request (flask.Request): The request object.
        <https://flask.palletsprojects.com/en/1.1.x/api/#incoming-request-data>
    Returns:
        The response text, or any set of values that can be turned into a Response object using
        `make_response`
        <https://flask.palletsprojects.com/en/1.1.x/api/#flask.make_response>.
    """
    received_file = request.files["file"] if "file" in request.files else None
    received_url = request.form.get("url")

    if received_file is not None:
        return file_flow(received_file, request)

    if received_url is not None:
        return url_flow(received_url, request)

    return serve_UI()


def file_flow(received_file, request):
    """
    :param received_file: werkzeug.FileStorage
    """
    message = r"ERROR: unable to process your request ¯\_(ツ)_/¯"
    status = False
    format = request.form.get("format")
    try:
        status, message = save_image_werkzeug(received_file)
        if status:
            _, message = process_imagefile(request, "the file you uploaded")
    except Exception as e:
        message = message + "\n" + str(e)
    return message


def url_flow(image_url, request):
    message = r"ERROR: unable to process your request ¯\_(ツ)_/¯"
    status = False
    try:
        status, message = validate_url(image_url)
        if status:
            status, message = download_url(image_url)
        if status:
            status, message = save_image_bytes(message)
        if status:
            _, message = process_imagefile(request, image_url)
    except Exception as e:
        message = message + "\n" + str(e)
    return message


def process_imagefile(request, image_url):

    ret = (False, r"failed to process image ¯\_(ツ)_/¯")
    try:
        format = request.form.get('format')

        width = request.form.get('width')
        if width is None:
            width = 20
        else:
            width = int(width)
            if width > 1000:
                width = 1000

        height = request.form.get('height')
        if height is None:
            height = 20
        else:
            height = int(height)
            if height > 1000:
                height = 1000

        characters = list(request.form.get('characters'))
        output = ansify(IMAGE_FILEPATH, output_format=format, chars=characters,
                        height=height, width=width)[0]

        ret = (True, output)
    except UnidentifiedImageError as e:
        ret = (False, f"ERROR: {image_url} does not appear to be an image")
    except Exception as e:
        ret = (False, "ERROR: " + str(e))
    return ret


def save_image_werkzeug(image):
    ret = (False, r"failed to process image ¯\_(ツ)_/¯")
    file_size = len(image.read())
    image.seek(0)
    try:
        if file_size > MAX_FILESIZE_B:
            raise ValueError(f"File is ~{file_size//1000/1000} MB, must not exceed {MAX_FILESIZE_MB} MB")
        image.save(IMAGE_FILEPATH)  # TODO may be reading into memory twice here

        ret = (True, "")
    except Exception as e:
        ret = (False, "ERROR: " + str(e))
    return ret


def save_image_bytes(content):
    ret = (False, r"failed to process image ¯\_(ツ)_/¯")
    try:
        with open(IMAGE_FILEPATH, "wb") as wf:
            wf.write(content)

        ret = (True, "")
    except Exception as e:
        ret = (False, "ERROR: " + str(e))
    return ret


def download_url(url):
    ret = (False, r"failed to download image ¯\_(ツ)_/¯")
    try:
        s = requests.session()
        head_r = s.head(url)
        if head_r.status_code < 200 or head_r.status_code > 299:
            raise ValueError(f"image url returned code {head_r.status_code}")
        size = int(head_r.headers.get("Content-Length", 0))
        if size > MAX_FILESIZE_B:
            raise ValueError(f"File must not exceed {MAX_FILESIZE_MB} MB")
        content_r = s.get(url, timeout=10)

        ret = (True, content_r.content)
    except Exception as e:
        ret = (False, "ERROR: " + str(e))
    return ret


def validate_url(url):
    ret = (False, r"no valid image URL provided ¯\_(ツ)_/¯")
    try:
        if not validators.url(url):
            raise ValueError("valid URL must be supplied")
        if not url.startswith("https"):
            raise ValueError("only HTTPS urls are allowed")
        if not any(map(lambda ex: url.endswith(ex), FILE_EXTENSIONS)):
            raise ValueError(f"file type must be one of {FILE_EXTENSIONS}")

        ret = (True, "")
    except Exception as e:
        ret = (False, "ERROR: " + str(e))
    return ret


def serve_UI():
    ret = r"<html><body>Something went wrong ¯\_(ツ)_/¯</body></html>"
    with open("./index.html", "r") as rf:
        ret = "".join(rf.readlines())
    return ret
