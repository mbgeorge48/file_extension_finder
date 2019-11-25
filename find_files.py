import os
from shutil import copy
import hashlib
import logging
from config_reader import ConfigReader

TESTING = True
FORMATTER = logging.Formatter("[%(asctime)s] [%(levelname)8s] --- %(message)s (%(filename)s:%(lineno)s)", "%Y-%m-%d %H:%M:%S")

class FindFiles:
    unique_file_paths = list()
    dupe_file_paths = list()
    hash_list = list()

    file_info = None
    general = None

    def __init__(self):
        config = ConfigReader()
        self.extensions_to_find = config.extensions_to_find
        self.path_to_scan = os.path.normpath(config.path_to_scan)
        self.path_to_copy_to =  os.path.normpath(config.path_to_copy_to)
        if not  os.path.isdir("logs"):
            os.mkdir("logs")
        self.file_info = self.set_logger( os.path.join("logs","file_info.log"), logging.DEBUG)
        self.general =  self.set_logger( os.path.join("logs","general.log"), logging.DEBUG)

        self.scan_directories()
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
        for root, dir, files in os.walk(self.path_to_scan): # We don't need to use dir
            for file in files:
                if os.path.splitext(file.lower())[-1] in self.extensions_to_find:
                    file_counter += 1
                    self.general.debug(f'Found file named: "{file}"')
                    file_path =  os.path.join(root, file)
                    hash_value = self.get_hash(file_path)
                    if hash_value not in self.hash_list or hash_value != 1:
                        self.hash_list.append(hash_value)
                        self.unique_file_paths.append(file_path)
                        self.general.info(f'"{file}" is UNIQUE')
                    else:
                        self.dupe_file_paths.append(file_path)
                        self.general.info(f'"{file}" is DUPLICATE')
                        self.general.debug(f'"{file}" has hash value of {hash_value}, which has already been allocated')

        self.general.info('#'*50)
        self.general.info(f'Found {file_counter} file in total')
        self.general.info(f'Found {len(self.unique_file_paths)} unique files')
        self.general.info(f'Found {len(self.dupe_file_paths)} duplicate files')
        self.general.info('#'*50)


    def get_hash(self, file_path):
        blocksize = 65536
        try:
            afile = open(file_path, 'rb')
            hasher = hashlib.md5()
            buf = afile.read(blocksize)
            while len(buf) > 0:
                hasher.update(buf)
                buf = afile.read(blocksize)
            afile.close()
            return hasher.hexdigest()
        except PermissionError:
            self.file_info.warning(f'Permission denied trying to read "{file_path}" marked it as a duplicate')
            return 1

    def move_files(self):
        for file_path in self.unique_file_paths:
            if TESTING == True:
                self.file_info.info(f'IN TESTING MODE: Moved "{file_path}" to "{self.path_to_copy_to}"')
            else:
                copy(file_path, os.path.normpath(self.path_to_copy_to))
                self.file_info.info(f'Moved "{file_path}" to "{self.path_to_copy_to}"')


if __name__ == "__main__":
    find_files = FindFiles()