import os
from shutil import copy
import hashlib
import logging
import shutil
from config_reader import ConfigReader

FORMATTER = logging.Formatter(
    "[%(asctime)s] [%(levelname)8s] --- %(message)s", "%Y-%m-%d %H:%M:%S")

class FindFiles:
    unique_file_paths = list()
    dupe_file_paths = list()
    # I mark file read errors as 1 so they aren't moved
    hash_list = [1]

    file_info = None
    general = None

    def __init__(self):
        config = ConfigReader()
        self.extensions_to_find = config.extensions_to_find
        self.path_to_scan = os.path.normpath(config.path_to_scan)
        self.path_to_copy_to = os.path.normpath(config.path_to_copy_to)
        self.testing = config.testing
        self.log_level = config.log_level.upper()

        if not os.path.isdir("logs"):
            os.mkdir("logs")
        self.file_info = self.set_logger(os.path.join(
            "logs", "file_info.log"), self.log_level)
        self.general = self.set_logger(os.path.join(
            "logs", "general.log"), self.log_level)

        self.get_free_disk_space()

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
        # We don't need to use dir
        for root, dir, files in os.walk(self.path_to_scan):
            for progress, file in enumerate(files):
                if os.path.splitext(file.lower())[-1] in self.extensions_to_find:
                    file_counter += 1
                    self.general.debug(f'Found file named: "{file}"')
                    file_path = os.path.join(root, file)
                    self.free_space -= os.path.getsize(file_path)
                    if self.free_space <= 0:
                        self.general.error(
                            f'Not enough room left on device - stopping before: "{file_path}"')
                        break
                    hash_value = self.get_hash(file_path)
                    self.general.debug(f'"{file}" has hash value of {hash_value}')

                    if hash_value not in self.hash_list:
                        self.hash_list.append(hash_value)
                        self.unique_file_paths.append(file_path)
                        self.general.info(f'"{file}" is UNIQUE')
                    else:
                        self.hash_list.append(hash_value)
                        self.dupe_file_paths.append(file_path)
                        self.general.warning(f'"{file}" is DUPLICATE')


        final_results = [
            'Found ' + str(file_counter) +' file in total',
            'Found ' + str(len(self.unique_file_paths)) +' unique files',
            'Found ' + str(len(self.dupe_file_paths)) +' duplicate files',
        ]
        self.general.info('#'*50)
        self.general.info(f'{final_results[0]}')
        self.general.info(f'{final_results[1]}')
        self.general.info(f'{final_results[2]}')
        self.general.info('#'*50)
        
        print(f'{final_results[0]}')
        print(f'{final_results[1]}')
        print(f'{final_results[2]}')

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
            self.file_info.warning(
                f'Permission denied trying to read "{file_path}" marked it as a duplicate')
            return 1

    def move_files(self):
        for file_path in self.unique_file_paths:
            if self.testing == True:
                self.file_info.info(
                    f'IN TESTING MODE: Moved "{file_path}" to "{self.path_to_copy_to}"')
            else:
                copy(file_path, os.path.normpath(self.path_to_copy_to))
                self.file_info.info(
                    f'Moved "{file_path}" to "{self.path_to_copy_to}"')

    def get_free_disk_space(self):
        total, used, self.free_space = shutil.disk_usage(self.path_to_copy_to)
        self.general.info("Free space on destination: %d GiB" %
                          (self.free_space // (2**30)))


if __name__ == "__main__":
    find_files = FindFiles()
