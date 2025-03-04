#import google.cloud.logging
import logging
import os
import requests
import validators

from ansifier import ansify

from flask import Flask, request, render_template


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
app = Flask('ansifier-cloud')
#client = google.cloud.logging.Client()
#client.setup_logging()
def log_info(message):
    app.logger.info(message)
    logging.info(message)


@app.route('/', methods=['GET'])
def serve_UI():
    log_info("serving UI")
    return render_template("index.html")


@app.route('/ansify', methods=['POST'])
def main():
    """
    entry point for API, UI can hit this from an existing client's JS process.
    calls exactly one of the *_flow functions based on what source the request provides,
    prioritizing file inputs, then URL inputs.
    :return: str, response message from processing input image.
        May be a successful result of ansification or an error message.
    """
    log_info(f"entered main with file \"{request.files}\" & url \"{request.form.get('url')}\"")

    received_file = request.files["file"] if "file" in request.files else None
    received_url = request.form.get("url")

    if received_file is not None:
        return file_flow(received_file, request), 200

    if received_url is not None:
        return url_flow(received_url, request), 200

    return "Please supply a valid file or URL to ansify", 500


def file_flow(received_file, request):
    """
    :param received_file: werkzeug.FileStorage
    :return: str, see main
    """
    log_info(f" processing {received_file}")
    message = r"ERROR: unable to process your request ¯\_(ツ)_/¯"
    try:
        message = save_image_werkzeug(received_file)
        message = process_imagefile(request, "the file you uploaded")
    except Exception as e:
        message = message + "\n" + str(e)
    return message


def url_flow(image_url, request):
    """
    :param image_url: str
    :return: str, see main
    """
    log_info(f" processing {image_url}")
    message = r"ERROR: unable to process your request ¯\_(ツ)_/¯"
    try:
        message = validate_url(image_url)
        message = download_url(image_url)
        message = save_image_bytes(message)
        message = process_imagefile(request, image_url)
    except Exception as e:
        message = message + "\n" + str(e)
    return message


def process_imagefile(request, image_url):
    """
    ansifies the data stored at IMAGE_FILEPATH; meant to be called after file has been saved there
    :param image_url: str, only used for logging
    :return: str, see main
    """
    log_info(f"ansifying downloaded copy of {image_url}")

    format_raw = request.form.get('format')
    characters_raw = request.form.get('characters')

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

    return ansify(IMAGE_FILEPATH, output_format=format_raw, chars=characters,
                    height=height, width=width)[0]


def save_image_werkzeug(image):
    """ saves an image to disk from a werkzeug file object """
    log_info("werkzeug-saving image to file...")
    message = r"failed to process image ¯\_(ツ)_/¯"
    image.seek(0)
    file_size = len(image.read())
    log_info(f"received {file_size} byte image to save")
    if file_size > MAX_FILESIZE_B:
        raise ValueError(f"File is ~{file_size/1e6} MB, must not exceed {MAX_FILESIZE_MB} MB")
    image.seek(0)
    image.save(IMAGE_FILEPATH)  # TODO may be reading into memory twice here
    saved_size = os.path.getsize(IMAGE_FILEPATH)
    log_info(f"saved {saved_size} bytes to {IMAGE_FILEPATH}")

    message = f"Image saved to {IMAGE_FILEPATH}"
    return message


def save_image_bytes(content):
    log_info("wb-saving image to file...")
    message = r"failed to process image ¯\_(ツ)_/¯"
    with open(IMAGE_FILEPATH, "wb") as wf:
        wf.write(content)

    message = f"image saved to {IMAGE_FILEPATH}"
    return message


def download_url(url):
    log_info(f"downloading image from {url}")
    message = r"failed to download image ¯\_(ツ)_/¯"
    s = requests.session()
    head_raw = s.head(url)
    if head_raw.status_code < 200 or head_raw.status_code > 299:
        raise ValueError(f"image url returned code {head_raw.status_code}")
    size = int(head_raw.headers.get("Content-Length", 0))
    if size > MAX_FILESIZE_B:
        raise ValueError(f"File must not exceed {MAX_FILESIZE_MB} MB")

    content_raw = s.get(url, timeout=10)
    message = content_raw.content
    return message


def validate_url(url):
    log_info(f"validating {url}")
    message = r"no valid image URL provided ¯\_(ツ)_/¯"

    if not validators.url(url):
        raise ValueError("valid URL must be supplied")
    if not url.startswith("https"):
        raise ValueError("only HTTPS urls are allowed")
    if not any(map(lambda ex: url.endswith(ex), FILE_EXTENSIONS)):
        raise ValueError(f"file type must be one of {FILE_EXTENSIONS}")

    message = f"{url} validated"
    return message


if __name__ == '__main__':
    app.run(debug=True)
