import os
import csv
import warnings

import pandas as pd
from python_calamine.pandas import pandas_monkeypatch
from PyQt5.QtCore import QThread, pyqtSignal

warnings.filterwarnings("ignore")


class MergeExcelThread(QThread):
    """ merge excel """
    signal_info = pyqtSignal(str)
    signal_warning = pyqtSignal(str)
    signal_error = pyqtSignal(str)
    signal_done = pyqtSignal(bool)

    def __init__(self, folder_path: str, output_path: str) -> None:
        super(MergeExcelThread, self).__init__()
        self.folder_path = folder_path
        self.output_path = output_path

    def info(self, text: str) -> None:
        self.signal_info.emit(text)

    def run(self) -> None:
        pandas_monkeypatch()
        try:
            list_df: list = []
            files = os.listdir(self.folder_path)
            for idx, file in enumerate(files):
                file_path = os.path.join(self.folder_path, file)
                if file.lower().endswith(".xlsx"):
                    df = pd.read_excel(
                        file_path, dtype_backend="pyarrow", engine='calamine')
                    list_df.append(df)
                    self.info(f"read {os.path.basename(file_path)} successfully")
                if file.lower().endswith(".xls"):
                    try:
                        df = pd.read_excel(
                            file_path, dtype_backend="pyarrow", engine="calamine")
                    except:
                        df = pd.read_csv(
                            file_path, dtype_backend="pyarrow")
                    list_df.append(df)
                    self.info(f"read {os.path.basename(file_path)} successfully")
            merge_df = pd.concat(list_df, sort=False)
            self.info("merging...")
            if len(merge_df) < 100_0000:
                merge_df.to_excel(f"{self.output_path}.xlsx", index=False, engine="xlsxwriter")
                self.info(f"save xlsx file: {self.output_path}.xlsx")
            else:
                merge_df.to_csv(f"{self.output_path}.csv", index=False, sep="|")
                self.info(f"save csv file: {self.output_path}.csv")
            self.signal_done.emit(True)
        except Exception as e:
            self.signal_done.emit(True)
            self.signal_error.emit(f"{e}")


class MergeTextThread(QThread):
    """ merge excel """
    signal_info = pyqtSignal(str)
    signal_warning = pyqtSignal(str)
    signal_error = pyqtSignal(str)
    signal_done = pyqtSignal(bool)

    def __init__(self, folder_path: str, output_path: str) -> None:
        super(MergeTextThread, self).__init__()
        self.folder_path = folder_path
        self.output_path = output_path

    def info(self, text: str) -> None:
        self.signal_info.emit(text)

    def run(self) -> None:
        try:
            self.info("start running")
            list_df: list = []
            files = os.listdir(self.folder_path)
            for idx, file in enumerate(files):
                file_path = os.path.join(self.folder_path, file)
                with open(file_path, 'r') as csvfile:
                    delimiter = csv.Sniffer().sniff(csvfile.read(5000)).delimiter
                reader = pd.read_csv(
                    file_path, dtype_backend="pyarrow", chunksize=100_0000, sep=str(delimiter))
                for chunk in reader:
                    list_df.append(chunk)
                self.info(f"{idx+1} read {file} successfully")
            merge_df = pd.concat(list_df, sort=False)
            if len(merge_df) < 100_0000:
                merge_df.to_excel(f"{self.output_path}.xlsx", index=False, engine="xlsxwriter")
                self.info(f"save xlsx file: {self.output_path}.xlsx")
            else:
                merge_df.to_csv(f"{self.output_path}.csv", index=False, sep="|")
                self.info(f"save csv file: {self.output_path}.csv")
            self.signal_done.emit(True)
        except Exception as e:
            self.signal_done.emit(True)
            self.signal_error.emit(f"{e}")
