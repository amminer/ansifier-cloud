import logging
import os
import requests
import validators

from ansifier import ansify
from flask import Flask, request, render_template
from sqlite3 import DatabaseError

from data_model import Database


FILE_EXTENSIONS = [ "blp", "bmp", "dds", "dib", "eps", "gif", "icns", "ico", "im", "jpeg", "jpg",
                   "msp", "pcx", "pfm", "png", "ppm", "sgi", "spider", "tga", "tiff", "webp", "xbm",
                   "cur", "dcx", "fits", "fli", "flc", "fpx", "ftex", "gbr", "gd", "imt",
                   "iptc/naa", "mcidas", "mic", "mpo", "pcd", "pixar", "psd", "qoi", "sun", "wal",
                   "wmf", "emf", "xpm", "palm", "pdf", "bufr", "grib", "hdf5", "mpeg",

                   "mp4", "mov", "mkv", "avi", "wmv", "flv", "mpeg", "mpg", "3gp", "webm",
                   "ogv", "m4v", "ts", "mts", "m2ts", "divx", "vob", "rm", "rmvb", "asf"
                   ]
FORMATTED_FILE_EXTENSIONS = ' '.join([ext if i % 10 else ext + '<br/>'
                                      for i, ext in enumerate(FILE_EXTENSIONS)])
IMAGE_FILEPATH = "IMAGEFILE"
MAX_FILESIZE_MB = 5
MAX_FILESIZE_KB = 1000 * MAX_FILESIZE_MB
MAX_FILESIZE_B = 1000 * MAX_FILESIZE_KB
app = Flask('ansifier-cloud')
debug = os.environ.get("ANSIFIER_DEBUG")

def log_info(message):
    app.logger.info(message)
    logging.info(message)
    print(message)

class AnsifierError(Exception):
    def __init__(self, message, http_code):
        super().__init__(message)
        self.http_code = http_code


@app.route('/', methods=['GET'])
def serve_UI():
    log_info("serving UI")
    return render_template("index.html")


@app.route('/ansify', methods=['POST'])
def main() -> (str, int):
    """
    entry point for API, UI can hit this from an existing client's JS process.
    calls exactly one of the *_flow functions based on what source the request provides,
    prioritizing file inputs, then URL inputs.

    :return: (message, httpcode),
        :message: the message that resulted from processing input image
            (which will be either an error message or the result of ansification)
        :httpcode: the http response code for the request

    *_flow functions MUST return the message and an HTTP response code as a pair
    """
    log_info(f"entered main with file \"{request.files}\" & url \"{request.form.get('url')}\"")

    received_file = request.files["file"] if "file" in request.files else None
    received_url = request.form.get("url")
    message = "Please supply a valid file or URL to ansify"
    http_response_code = 200

    try:
        if received_file is not None:
            message = file_flow(received_file, request)

        if received_url is not None:
            message = url_flow(received_url, request)

    except AnsifierError as e:
        http_response_code = e.http_code
        message = str(e)

    except DatabaseError as e:
        http_response_code = 500
        message = 'db err: ' + str(e)

    except Exception as e:  # TODO generate a crash UID and ask user to submit it
        http_response_code = 500
        message = str(e) if debug else "Sorry, something went wrong"

    finally:
        return message, http_response_code


def file_flow(received_file, request):
    """
    :param received_file: werkzeug.FileStorage
    :return: str, see main
    """
    log_info(f" processing {received_file}")
    message = save_image_werkzeug(received_file)
    message = process_imagefile(request, "the file you uploaded")
    return message


def url_flow(image_url, request):
    """
    :param image_url: str
    :return: str, see main
    """
    log_info(f" processing {image_url}")
    message = validate_url(image_url)
    message = download_url(image_url)
    message = save_image_bytes(message)
    message = process_imagefile(request, image_url)
    return message


    
def process_imagefile(request, image_url):
    """
    ansifies the data stored at IMAGE_FILEPATH; meant to be called after file has been saved there
    :param image_url: str, only used for logging
    :return: str, see main
    """
    log_info(f"processing downloaded copy of {image_url}")

    #moderate_imagefile()

    format_raw = request.form.get('format')
    characters_raw = request.form.get('characters')
    gallery_choice_raw = request.form.get('gallery')

    if format_raw is None:
        format_raw = 'ansi-escaped'
    if characters_raw is None:
        characters_raw = '█▓▒░ '

    characters = list(characters_raw)

    def validate_dim(dim):
        if dim is None:
            dim = 20
        else:
            dim = int(dim)
            if dim > 1000:
                dim = 1000
        return dim

    width = validate_dim(request.form.get('width'))
    height = validate_dim(request.form.get('height'))

    try:
        result = ansify(IMAGE_FILEPATH, output_format=format_raw, chars=characters,
                        height=height, width=width)[0]
    except ValueError as e:  #TODO this should be an IOError, probably need to update ansifier
        raise AnsifierError(str(e) + f"; valid image formats are {FORMATTED_FILE_EXTENSIONS}",
                            http_code=400)

    #if gallery_choice_raw:
        #db = Database()
        #db.check_schema()
        #db.insert_art(result)
        #db.close()

    return result


def moderate_imagefile():
    """
    runs the data stored at IMAGE_FILEPATH through Google's safesearch ML model,
    raises an exception if the image is deemed inappropriate
    :param image_url: str, only used for logging
    :return: None
    """
    log_info("moderating locally stored image file")
    image = vision.Image()
    vision_client = vision.ImageAnnotatorClient()

    with open(IMAGE_FILEPATH, 'rb') as rf:
        image.content = rf.read() # TODO reading file twice, once to moderate and once to ansify...
    response = vision_client.safe_search_detection(image=image)
    if response.error.message:
        raise Exception(
            "{}\nFor more info on error messages, check: "
            "https://cloud.google.com/apis/design/errors".format(response.error.message)
        )

    safe = response.safe_search_annotation
    # Names of likelihood from google.cloud.vision.enums
    #"UNKNOWN",  # 0
    #"VERY_UNLIKELY",  # 1
    #"UNLIKELY",  # 2
    #"POSSIBLE",  # 3
    #"LIKELY",  # 4
    #"VERY_LIKELY",  # 5
    #safe.adult, medical, spoofed, violence, racy
    if safe.violence > 3:
        raise Exception("Detected violence in image - service refused")
    # TODO anything else to restrict?


def save_image_werkzeug(image):
    """ saves an image to disk from a werkzeug file object """
    log_info("werkzeug-saving image to file")
    image.seek(0)
    file_size = len(image.read())
    log_info(f"received {file_size} byte image to save")
    if file_size > MAX_FILESIZE_B:
        raise AnsifierError(f"File is ~{file_size/1e6} MB, must not exceed {MAX_FILESIZE_MB} MB",
                            http_code=400)
    image.seek(0)
    image.save(IMAGE_FILEPATH)  # TODO may be reading into memory twice here
    saved_size = os.path.getsize(IMAGE_FILEPATH)
    log_info(f"saved {saved_size} bytes to {IMAGE_FILEPATH}")
    return f"Image saved to {IMAGE_FILEPATH}"


def save_image_bytes(content):
    log_info(f"writing binary image data to file at {IMAGE_FILEPATH}")
    with open(IMAGE_FILEPATH, "wb") as wf:
        wf.write(content)
    return f"image saved to {IMAGE_FILEPATH}"


def download_url(url):
    log_info(f"downloading image from {url}")
    s = requests.session()
    head_raw = s.head(url)

    if head_raw.status_code < 200 or head_raw.status_code > 299:
        raise AnsifierError(f"image url returned code {head_raw.status_code}",
                            http_code=500)
    size = int(head_raw.headers.get("Content-Length", 0))
    if size > MAX_FILESIZE_B:
        raise AnsifierError(f"File must not exceed {MAX_FILESIZE_MB} MB",
                            http_code=400)

    content_raw = s.get(url, timeout=10)
    return content_raw.content


def validate_url(url):
    log_info(f"validating {url}")
    if not validators.url(url):
        raise AnsifierError("valid URL must be supplied",
                            http_code=400)
    if not url.startswith("https"):
        raise AnsifierError("only HTTPS urls are allowed",
                            http_code=400)
    if not any(map(lambda ex: url.endswith(ex), FILE_EXTENSIONS)):
        raise AnsifierError(f"file type must be one of {FORMATTED_FILE_EXTENSIONS}",
                            http_code=400)
    return f"{url} validated"


if __name__ == '__main__':
    app.run()
