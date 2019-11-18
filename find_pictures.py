from glob import glob
from os import path, walk, mkdir
from shutil import copy
import hashlib
import logging

TESTING = True
FORMATTER = logging.Formatter('%(asctime)s:%(levelname)s:%(message)s')


class FindPictures:
    unique_file_paths = list()
    dupe_file_paths = list()
    hash_list = list()

    pic_info = None
    general = None

    def __init__(self):
        self.extension_to_find = ".jpg"
        self.path_to_scan = "test_scan"
        self.path_to_copy_to = path.normpath("test_save\\")
        # This is where I'll grab my config
        if not path.isdir("logs"):
            mkdir("logs")
        self.pic_info = self.set_logger(path.join("logs","picture_info.log"), logging.DEBUG)
        self.general =  self.set_logger(path.join("logs","general.log"), logging.DEBUG)

        self.scan_directories()

        print(len(self.unique_file_paths))
        print(len(self.dupe_file_paths))

        self.move_files()

    def set_logger(self, log_name, level):
        handler = logging.FileHandler(log_name)
        handler.setFormatter(FORMATTER)

        logger = logging.getLogger(log_name)
        logger.setLevel(level)
        logger.addHandler(handler)
        return logger

    def scan_directories(self):
        file_counter = 0
        for root, dir, files in walk(self.path_to_scan): # We don't need to use dir
            for file in files:
                if file.lower().endswith(self.extension_to_find): # Will likely change to check it's in a list rather than a string
                    file_counter += 1
                    self.general.debug(f'Found picture named: "{file}"')
                    file_path = path.join(root, file)
                    hash_value = self.get_hash(file_path)
                    if hash_value not in self.hash_list:
                        self.hash_list.append(hash_value)
                        self.unique_file_paths.append(file_path)
                        self.general.info(f"{file} is UNIQUE")
                    else:
                        self.dupe_file_paths.append(file_path)
                        self.general.info(f"{file} is DUPLICATE")



        self.general.info(f'Found {file_counter} file in total')
        self.general.info(f'Found {len(self.unique_file_paths)} unique files')
        self.general.info(f'Found {len(self.dupe_file_paths)} duplicate files')

    def get_hash(self, file_path):
        blocksize = 65536
        afile = open(file_path, 'rb')
        hasher = hashlib.md5()
        buf = afile.read(blocksize)
        while len(buf) > 0:
            hasher.update(buf)
            buf = afile.read(blocksize)
        afile.close()
        return hasher.hexdigest()

    def move_files(self):
        for file_path in self.unique_file_paths:
            if TESTING == True:
                self.pic_info.info(f'IN TESTING MODE: Moved "{file_path}" to "{self.path_to_copy_to}"')
            else:
                copy(file_path, path.normpath(self.path_to_copy_to))
                self.pic_info.info(f'Moved "{file_path}" to "{self.path_to_copy_to}"')


if __name__ == "__main__":
    find_pictures = FindPictures()