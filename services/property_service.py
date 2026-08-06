import os
import uuid

from werkzeug.utils import secure_filename

from flask import current_app


def allowed_file(filename):

    return (
        "." in filename
        and filename.rsplit(".", 1)[1].lower()
        in current_app.config["ALLOWED_EXTENSIONS"]
    )


def save_image(image):

    filename = secure_filename(image.filename)

    extension = filename.rsplit(".", 1)[1]

    unique_name = f"{uuid.uuid4()}.{extension}"

    path = os.path.join(
        current_app.config["UPLOAD_FOLDER"],
        unique_name
    )

    image.save(path)

    return f"uploads/properties/{unique_name}"