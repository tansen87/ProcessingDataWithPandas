import os
import csv
import warnings

import pandas as pd
from PyQt5.QtCore import QThread, pyqtSignal

warnings.filterwarnings("ignore")


class SplitDataThread(QThread):
    """ data split """
    signal_info = pyqtSignal(str)
    signal_warning = pyqtSignal(str)
    signal_error = pyqtSignal(str)
    signal_done = pyqtSignal(bool)

    def __init__(
            self,
            file_path: str,
            row_count: int,
            output_path: str
    ) -> None:
        super(SplitDataThread, self).__init__()
        self.file_path = file_path
        self.row_count = row_count
        self.output_path = output_path

    def info(self, text: str) -> None:
        self.signal_info.emit(text)

    def run(self) -> None:
        try:
            self.info(f"read {os.path.basename(self.file_path)}")
            list_df: list = []
            with open(self.file_path, 'r', encoding="utf-8") as csvfile:
                delimiter = csv.Sniffer().sniff(csvfile.read(5000)).delimiter
            reader = pd.read_csv(
                self.file_path, dtype_backend="pyarrow", chunksize=100_0000, sep=str(delimiter))
            for chunk in reader:
                list_df.append(chunk)
            df = pd.concat(list_df, ignore_index=True)
            j: int = 1
            file_name = os.path.splitext(os.path.basename(self.file_path))[0]
            for start in range(0, len(df), self.row_count):
                stop = start + self.row_count
                name = f"{file_name}_{j}.xlsx"
                d = df[start: stop]
                d.to_excel(f"{self.output_path}/{name}", index=False, engine="xlsxwriter")
                j += 1
                self.info(f"save xlsx file: {self.output_path}/{name}")
            self.signal_done.emit(True)
        except Exception as e:
            self.signal_done.emit(True)
            self.signal_error.emit(f"{e}")
