import argparse
import os
import zipfile
from concurrent.futures import ThreadPoolExecutor, wait
import logging

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger('extractor')


def extract(entry: os.DirEntry, destination: str, dry_run: bool):
    if '.zip' in entry.name:
        logger.info("unzipping '{}'".format(entry.name))
        zipped = zipfile.ZipFile(entry.path)
        for name in zipped.namelist():
            if '.zip' in name:
                logger.debug("unzipping internal entries...")
                tmp = os.path.join(entry.name, destination)
                if not dry_run:
                    zipped.extractall(path=tmp)
                # os.remove(entry.path)
                for entry in os.scandir(tmp):
                    extract(entry, destination, dry_run)
            else:
                if not dry_run:
                    zipped.extractall(path=destination)
        logger.info("unzipped '{}'".format(entry.name))
    else:
        logger.info("skipping '{}'".format(entry.name))


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("-i", "--input", help="the directory of the zip files", type=str, required=True)
    parser.add_argument("-o", "--output", help="the directory to unzip everything to", type=str,  default="./unzipped")
    parser.add_argument("--dry_run", help="print out what would be done, but don't actualy unzip", type=bool, default=False)
    args = parser.parse_args()

    source = args.input
    destination = args.output
    dry_run = args.dry_run

    submissions = {}
    executor = ThreadPoolExecutor()

    for entry in os.scandir(source):
        submissions[executor.submit(extract, entry, destination, dry_run)] = entry.name

    _, _ = wait(submissions)


if __name__ == "__main__":
    main()
