import os
import csv
import warnings

import numpy as np
import pandas as pd
from PyQt5.QtCore import QThread, pyqtSignal

warnings.filterwarnings("ignore")


class PivotDataThread(QThread):
    """ data pivot """
    signal_info = pyqtSignal(str)
    signal_warning = pyqtSignal(str)
    signal_error = pyqtSignal(str)
    signal_done = pyqtSignal(bool)

    def __init__(
            self,
            file_path: str,
            index: str,
            values: str,
            output_path: str
    ) -> None:
        super(PivotDataThread, self).__init__()
        self.file_path = file_path
        self.index = index
        self.values = values
        self.output_path = output_path

    def info(self, text: str) -> None:
        self.signal_info.emit(text)

    def run(self) -> None:
        try:
            self.info(f"read {os.path.basename(self.file_path)}")
            list_df: list = []
            with open(self.file_path, 'r') as csvfile:
                delimiter = csv.Sniffer().sniff(csvfile.read(5000)).delimiter
            reader = pd.read_csv(
                self.file_path, dtype_backend="pyarrow", chunksize=100_0000, sep=str(delimiter))
            for chunk in reader:
                list_df.append(chunk)
            df = pd.concat(list_df, ignore_index=True)
            list_index = self.index.split(",")
            list_values = self.values.split(",")
            pt = pd.pivot_table(df, index=list_index, values=list_values, aggfunc=np.sum)
            pt.reset_index(inplace=True)
            pt.to_excel(f"{self.output_path}.xlsx", index=False, engine="xlsxwriter")
            self.info(f"save file: {self.output_path}.xlsx")
            self.signal_done.emit(True)
        except Exception as e:
            self.signal_done.emit(True)
            self.signal_error.emit(f"{e}")
