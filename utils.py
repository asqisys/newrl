def save_file_and_get_path(upload_file):
    file_location = f"/tmp/{upload_file.filename}"
    with open(file_location, "wb+") as file_object:
        file_object.write(upload_file.file.read())
    return file_location