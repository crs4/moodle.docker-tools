#!/usr/bin/env python

import os, sys
from os import listdir, path

KB = 1024
MB = 1024 * KB
GB = 1024 * MB
MIN_NUM_FILES = 10
TOTAL_AVAILABLE_SPACE = 2 * 1024 * 1024 * 1024  # default 2GB


def get_size(start_path='.'):
    total_size = 0
    for dirpath, dirnames, filenames in os.walk(start_path):
        for f in filenames:
            fp = path.join(dirpath, f)
            total_size += path.getsize(fp)
    return total_size


def main(folder="."):
    folder = path.abspath(folder)
    folder_size = get_size(folder)
    file_list = os.listdir(folder)

    if len(file_list) > 0:
        last_file = file_list[-1]
        largest_file_size = path.getsize(folder + "/" + last_file)
        min_free_space = largest_file_size * MIN_NUM_FILES

        print "Size of folder '%s': %s bytes (%s MB)" % (folder, folder_size, folder_size / MB)
        print "Last created file: %s (size: %s KB)" % (last_file, 1.0 * largest_file_size / KB)
        print "Total available space: %s (%s KB, %s MB, %s GB)" % (
            1.0 * TOTAL_AVAILABLE_SPACE, 1.0 * TOTAL_AVAILABLE_SPACE / KB,
            1.0 * TOTAL_AVAILABLE_SPACE / MB, 1.0 * TOTAL_AVAILABLE_SPACE / GB
        )
        while True:
            free_space = TOTAL_AVAILABLE_SPACE - get_size(folder)
            print "Current free space: %s (%s KB, %s MB, %s GB)" % (
                1.0 * free_space, 1.0 * free_space / KB,
                1.0 * free_space / MB, 1.0 * free_space / GB
            )
            if free_space >= min_free_space or len(file_list) == 0:
                break
            else:
                f = file_list[0]
                print "Removing %s " % f
                os.remove(folder + "/" + f)
                file_list.remove(f)


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print "No folder name !!!"
        exit(-1)
    main(sys.argv[1])
