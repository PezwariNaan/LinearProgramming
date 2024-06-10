from os import getenv
from pathlib import Path
import pandas as pd

class DF:
    def __init__(self):
        self.create_df()
        pd.set_option('display.max_columns', 10)
        pd.set_option('display.max_rows', 200)
        return 

    def create_df(self):
        user = getenv('USER')
        dir = Path(f"/home/{user}/Documents/Competitions/Shell/dataset/CSV_Files/")
        file_list = [file for file in dir.iterdir()]
        file_list.remove(file_list[0])
        for file in file_list:
            df_name = str(file.stem) # Filename no extension
            df = pd.read_csv(file)
            df.reset_index(inplace = True, drop = True)
            setattr(self, df_name, df)
        return 

