import os
import hashlib
from optparse import OptionParser

def get_digest(file_path):
    h = hashlib.sha256()

    with open(file_path, 'rb') as file:
        while True:
            # Reading is buffered, so we can read smaller chunks.
            chunk = file.read(h.block_size)
            if not chunk:
                break
            h.update(chunk)

    return h.hexdigest()


def main():
	parser = OptionParser()
	parser.add_option("-f", "--ipfile", dest="ipfile",default=None,help="Input chainfile. default - none");
#	parser.add_option("-d", "--dir", dest="dir",default="./",help="Destination directory. default - ./");
	(options, args) = parser.parse_args()

#	with open(options.ipfile,"rb") as read_file:
	hashval=get_digest(options.ipfile)
	print("Hashvalue of file ",options.ipfile," is ",hashval)
	return hashval

if __name__ == "__main__":
	main();

