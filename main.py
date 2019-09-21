import argparse
import os
import zipfile
from concurrent.futures import ThreadPoolExecutor, wait


def extract(entry: os.DirEntry, destination: str):
    if '.zip' in entry.name:
        print("unzipping '{}'".format(entry.name))
        zipped = zipfile.ZipFile(entry.path)
        zipped.extractall(path=destination)
        print("unzipped '{}'".format(entry.name))
    else:
        print("skipping '{}'".format(entry.name))


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("-i", "--input", help="the directory of the zip files", type=str, required=True)
    parser.add_argument("-o", "--output", help="the directory to unzip everything to", type=str,  default="./unzipped")
    args = parser.parse_args()

    source = args.input
    destination = args.output

    submissions = {}
    executor = ThreadPoolExecutor()

    for entry in os.scandir(source):
        submissions[executor.submit(extract, entry, destination)] = entry.name

    _, _ = wait(submissions)


if __name__ == "__main__":
    main()
