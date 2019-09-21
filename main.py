import zipfile
import os
import argparse


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("-i", "--input", help="the directory of the zip files", type=str, required=True)
    parser.add_argument("-o", "--output", help="the directory to unzip everything to", type=str,  default="./unzipped")
    args = parser.parse_args()

    source = args.input
    destination = args.output

    for entry in os.scandir(source):
        if '.zip' in entry.name:
            print("unzipping '{}'".format(entry.name))
            zipped = zipfile.ZipFile(entry.path)
            zipped.extractall(path=os.path.join(destination, entry.name))
            print("unzipped '{}'".format(entry.name))
        else:
            print("skipping '{}'".format(entry.name))


if __name__ == "__main__":
    main()
