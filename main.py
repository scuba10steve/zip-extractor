import argparse
import logging
import os
import tkinter as tk
from tkinter.scrolledtext import ScrolledText
import zipfile
from concurrent.futures import ThreadPoolExecutor, wait

import pyunpack as pyunpack

logging.basicConfig(level=logging.INFO)


class Extractor:
    def __init__(self, source: str, destination: str, dry_run: bool):
        self.source = source
        self.destination = destination
        self.dry_run = dry_run
        self.logger = logging.getLogger('extractor')
        self.output = []

    def extract(self):
        submissions = {}
        executor = ThreadPoolExecutor()

        for entry in os.scandir(self.source):
            submissions[executor.submit(self.__extract_internal, entry)] = entry.name

        _, output = wait(submissions)
        self.output = output
        return True

    def get_output(self):
        return self.output

    def __extract_internal(self, entry: os.DirEntry):
        tmp = os.path.join(self.destination, entry.name)
        if '.zip' in entry.name:
            log = "unzipping '{}'".format(entry.name)
            self.logger.info(log)
            self.output.append(log)
            zipped = zipfile.ZipFile(entry.path)
            for name in zipped.namelist():
                if '.zip' in name:
                    log = "unzipping internal entries..."
                    self.logger.debug(log)
                    self.output.append(log)
                    if not self.dry_run:
                        zipped.extractall(path=tmp)
                    # os.remove(entry.path)
                    for entry in os.scandir(tmp):
                        self.__extract_internal(entry)
                else:
                    if not self.dry_run:
                        zipped.extractall(path=self.destination)
            log = "unzipped '{}'".format(entry.name)
            self.logger.info(log)
            self.output.append(log)
        elif '.7z' in entry.name:
            zipped = pyunpack.Archive(entry.path)
            if not self.dry_run:
                zipped.extractall(self.destination, auto_create_dir=True)
                for entry in os.scandir(tmp):
                    if '.7z' in entry.name:
                        log = "unzipping internal entries..."
                        self.logger.debug(log)
                        self.output.append(log)
                        self.__extract_internal(entry)
        else:
            log = "skipping '{}'".format(entry.name)
            self.logger.info(log)
            self.output.append(log)


class Application(tk.Frame):
    def __init__(self, master=None):
        super().__init__(master)
        self.master = master

        self.pack()
        self.create_widgets()

    def create_widgets(self):
        self.extract_button = tk.Button(self)
        self.extract_button["text"] = "Extract"
        self.extract_button["command"] = self.extract
        self.extract_button.pack(side="top")

        self.input = tk.Entry(self)
        self.input.pack(side="right")
        self.input["textvariable"] = tk.StringVar(value="./zipped")
        self.destination = tk.Entry(self)
        self.destination["textvariable"] = tk.StringVar(value="./unzipped")
        self.destination.pack(side="right")
        self.output = ScrolledText(self.master)
        self.output.insert(index=1.0, chars="output will appear here")
        self.output.pack(side="bottom")

        self.quit = tk.Button(self, text="QUIT", fg="red",
                              command=self.master.destroy)
        self.quit.pack(side="bottom")

    def extract(self):
        extractor = Extractor(self.input.get(), self.destination.get(), False)
        if extractor.extract():
            self.output.delete(1.0, float(len("output will appear here")))
            text = extractor.get_output()
            built = ""
            for entry in text:
                built += entry + "\n"

            self.output.insert(1.0, "finished")
            for index, entry in enumerate(built.split('\n')):
                self.output.insert(float(index + 1), entry)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("-i", "--input", help="the directory of the zip files", type=str, required=True)
    parser.add_argument("-o", "--output", help="the directory to unzip everything to", type=str,  default="./unzipped")
    parser.add_argument("--dry_run", help="print out what would be done, but don't actualy unzip", type=bool, default=False)
    args = parser.parse_args()

    source = args.input
    destination = args.output
    dry_run = args.dry_run

    root = tk.Tk()
    app = Application(master=root)
    app.mainloop()

    # extractor = Extractor(source, destination, dry_run)
    # extractor.extract()


if __name__ == "__main__":
    main()
