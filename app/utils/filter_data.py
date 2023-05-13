import os
import csv
import warnings

import pandas as pd
from python_calamine.pandas import pandas_monkeypatch
from PyQt5.QtCore import QThread, pyqtSignal

try:
    import pycrab
except ImportError as e:
    raise "No pycrab, please pip install pycrab"

warnings.filterwarnings("ignore")


class FilterDataThread(QThread):
    """ single filter """
    signal_info = pyqtSignal(str)
    signal_warning = pyqtSignal(str)
    signal_error = pyqtSignal(str)
    signal_done = pyqtSignal(bool)

    def __init__(
            self,
            file_path: str,
            output_path: str,
            column_field: str,
            targets: str
    ) -> None:
        super(FilterDataThread, self).__init__()
        self.file_path = file_path
        self.output_path = output_path
        self.column_field = column_field
        self.targets = targets

    def info(self, text: str) -> None:
        self.signal_info.emit(text)

    def run(self) -> None:
        pandas_monkeypatch()
        try:
            with open(self.targets, 'r', encoding='utf-8') as fp:
                lines = fp.readlines()
            self.targets = [line.strip('\n') for line in lines]
            try:
                df = pd.read_excel(
                    self.file_path, dtype_backend="pyarrow", engine="calamine")
            except:
                with open(self.file_path, 'r') as csvfile:
                    delimiter = csv.Sniffer().sniff(csvfile.read(5000)).delimiter
                df = pd.read_csv(
                    self.file_path, dtype_backend="pyarrow", sep=str(delimiter))
            self.info(f"open {os.path.basename(self.file_path)} successfully")
            for tar in range(len(self.targets)):
                mask = df[self.column_field].apply(lambda x: x in self.targets[tar])
                filter_df = df[mask]
                if len(filter_df) < 100_0000:
                    filter_df.to_excel(
                        f"{self.output_path}/{str(self.targets[tar])}.xlsx",
                        index=False, engine="xlsxwriter")
                    self.info(f"{str(tar + 1)} => {str(self.targets[tar])}.xlsx is saved.")
                else:
                    filter_df.to_csv(f"{self.output_path}/{str(self.targets[tar])}.csv", index=False)
                    self.info(f"{str(tar + 1)} {str(self.targets[tar])}.csv is saved.")
            self.signal_done.emit(True)
        except Exception as e:
            self.signal_done.emit(True)
            self.signal_error.emit(f"{e}")


class FilterMultiDataThread(QThread):
    """ multi filter """
    signal_info = pyqtSignal(str)
    signal_warning = pyqtSignal(str)
    signal_error = pyqtSignal(str)
    signal_done = pyqtSignal(bool)

    def __init__(
            self,
            file_path: str,
            targets: str,
            column_value: str,
            file_out: str
    ) -> None:
        super(FilterMultiDataThread, self).__init__()
        self.file_path = file_path
        self.targets = targets
        self.column_value = column_value
        self.file_out = file_out

    def info(self, text: str) -> None:
        self.signal_info.emit(text)

    def run(self) -> None:
        try:
            self.info("start running...")
            file_extension = os.path.splitext(self.file_path)[1].lower()
            if file_extension == ".xlsx":
                self.info(f"read {os.path.basename(self.file_path)}")
                df = pd.read_excel(
                    self.file_path, dtype_backend="pyarrow", engine="calamine")
                filter_df = df[df[self.column_value].isin(self.targets)]
                if len(filter_df) < 100_0000:
                    filter_df.to_excel(
                        f"{str(self.file_out)}.xlsx", index=False, engine="xlsxwriter")
                    self.info(f"save xlsx file: {self.file_out}.xlsx")
                else:
                    filter_df.to_csv(f"{str(self.file_out)}.csv", index=False, sep="|")
                    self.info(f"save csv file: {self.file_out}.csv")
            if file_extension == ".csv" or file_extension == ".tsv" or file_extension == ".txt":
                self.info(f"read {os.path.basename(self.file_path)}")
                chunk_size: int = 100_0000
                list_df: list = []
                with open(self.file_path, 'r') as csvfile:
                    delimiter = csv.Sniffer().sniff(csvfile.read(5000)).delimiter
                reader = pd.read_csv(
                    self.file_path, dtype_backend="pyarrow",
                    chunksize=chunk_size, sep=str(delimiter))
                for chunk in reader:
                    tmp_df = chunk[chunk[self.column_value].isin(self.targets)]
                    list_df.append(tmp_df)
                filter_df = pd.concat(list_df)
                if len(filter_df) < 100_0000:
                    filter_df.to_excel(
                        f"{str(self.file_out)}.xlsx", index=False, engine="xlsxwriter")
                    self.info(f"save xlsx file: {self.file_out}.xlsx")
                else:
                    filter_df.to_csv(f"{str(self.file_out)}/filter.csv", index=False, sep="|")
                    self.info(f"save csv file: {self.file_out}.csv")
            self.signal_done.emit(True)
        except Exception as e:
            self.signal_done.emit(True)
            self.signal_error(f"{e}")


class PycrabFilterRow(QThread):
    """ single filter - use rust """
    signal_info = pyqtSignal(str)
    signal_warning = pyqtSignal(str)
    signal_error = pyqtSignal(str)
    signal_done = pyqtSignal(bool)

    def __init__(
            self,
            file_path: str,
            output_path: str,
            column: str,
            targets: str,
            is_exact: bool = True
    ) -> None:
        super(PycrabFilterRow, self).__init__()
        self.file_path = file_path
        self.output_path = output_path
        self.column = column
        self.targets = targets
        self.is_exact = is_exact

    def info(self, text) -> None:
        self.signal_info.emit(str(text))

    def run(self) -> None:
        try:
            with open(self.file_path, 'r') as csvfile:
                delimiter = csv.Sniffer().sniff(csvfile.read(5000)).delimiter
            self.info(f"read {os.path.basename(self.file_path)}")
            df = pd.read_csv(self.file_path, nrows=5, sep=str(delimiter))
            col_idx = df.columns.get_loc(self.column)
            list_delimiter: list = []
            if delimiter == ",":
                list_delimiter.append(list(b',')[0])
            if delimiter == "|":
                list_delimiter.append(list(b'|')[0])
            if delimiter == "\t":
                list_delimiter.append(list(b'\t')[0])
            if delimiter == ";":
                list_delimiter.append(list(b';')[0])
            pycrab.filter_row(
                csv_path=self.file_path,
                output_path=f"{self.output_path}.csv",
                sep=list_delimiter[0],
                col=col_idx,
                cond=self.targets,
                is_exac=self.is_exact)
            self.info(f"save file path {self.output_path}.csv")
            self.signal_done.emit(True)
        except Exception as e:
            self.signal_done.emit(True)
            self.signal_error.emit(f"{e}")
