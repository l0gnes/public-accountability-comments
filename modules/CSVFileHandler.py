from glob import glob
from os import PathLike
import os.path
from typing import List, Generator
import csv
from objects.CSVFileMetadata import CSVFileMetadata
import regex

class CSVFileHandler(object):

    working_directory : PathLike

    def __init__(self, d : PathLike) -> None:

        self.working_directory : PathLike = d
        self.files = self.fetch_all_csv_files()

    def fetch_all_csv_files(
            self, 
            recursive : bool = False) -> List[PathLike]:
        
        return list( glob("*.csv", root_dir=self.working_directory, recursive=recursive) )
    
    def csv_generator(self) -> Generator[CSVFileMetadata, None, None]:

        for csvFile in self.files:

            # This little code snippet just grabs the correct channel handle
            formatting_regex = r"(\w+)_IDs"
            hre = regex.search(
                formatting_regex, os.path.splitext(csvFile)[0])
            hg = hre.group(1)            

            # Read the CSV file, and yield the metadata to be processed later
            # Using "yield" lets us directly use this function in a for loop
            # without having to load all of the video ids into memory
            with open(os.path.join(self.working_directory, csvFile)) as buf:
                reader = csv.reader(buf)
                
                vids = []

                for row in reader:
                    for i in row:                    
                        vids.append(i.strip())

                yield CSVFileMetadata(hg, vids)

    @property
    def channel_count(self) -> int:
        return len(self.files)