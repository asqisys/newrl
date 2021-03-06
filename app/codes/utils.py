import hashlib
import time


def save_file_and_get_path(upload_file):
    if upload_file is None:
        return None
    file_location = f"/tmp/{upload_file.filename}"
    with open(file_location, "wb+") as file_object:
        file_object.write(upload_file.file.read())
    return file_location


class BufferedLog():
    def __init__(self) -> None:
        self.buffer = ""
    
    def log(self, *text):
        for t in text:
            self.buffer += "\n" + str(t)
    
    def get_logs(self):
        return self.buffer


def get_time_ms():
    """Return time in milliseconds"""
    return round(time.time() * 1000)


def get_person_id_for_wallet_address(wallet_address):
    hs = hashlib.blake2b(digest_size=20)
    hs.update(wallet_address.encode())
    person_id = 'pi' + hs.hexdigest()
    return person_id
