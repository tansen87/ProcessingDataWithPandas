import os
import re
import csv
import warnings
from typing import Union

import yaml
import numpy as np
import pandas as pd
from pypinyin import pinyin, Style
from pandas.core.frame import DataFrame
from PyQt5.QtCore import QThread, pyqtSignal

from ..utils.log import Log

warnings.filterwarnings("ignore")


class JournalsTemplate(QThread):
    signal_info = pyqtSignal(str)
    signal_warning = pyqtSignal(str)
    signal_error = pyqtSignal(str)
    signal_done = pyqtSignal(bool)

    def __init__(self, yaml_path: str, file_path: str, output_path: str) -> None:
        super(JournalsTemplate, self).__init__()
        self.yaml_path = yaml_path
        self.file_path = file_path
        self.output_path = output_path

    def info(self, text: str) -> None:
        self.signal_info.emit(text)

    def err(self, text: str) -> None:
        self.signal_error.emit(text)

    def read_yaml(self, yaml_path):
        yaml_file = ReadYaml(yaml_path)
        return yaml_file.read()

    def insert_column(
            self,
            df: DataFrame
    ) -> DataFrame:
        """ insert column """
        try:
            # read template column name
            with open("../config/columnName.txt", "r", encoding="utf-8") as fp:
                column_names = fp.readlines()
            list_cs = [column_name.strip("\n") for column_name in column_names]
            # insert column
            for value in list_cs:
                df[value] = None
            Log.info("insert column successfully.")
            self.info("step 1 => insert column successfully")
            return df
        except Exception as e:
            self.signal_done.emit(True)
            self.err(f"{e}")
            Log.error(f"{e}")

    def reset_column(
            self,
            df: DataFrame,
    ) -> DataFrame:
        try:
            content = self.read_yaml(self.yaml_path)
            df["Entity"] = df[content["Entity"]]
            df["Company Name"] = df[content["CompanyName"]]
            df["Currency"] = df[content["Currency"]]
            df["Entity Currency (EC)"] = df[content["EntityCurrency(EC)"]]
            df["Signed Journal Amount"] = df[content["SignedJournalAmount"]]
            df["Unsigned Debit Amount"] = df[content["UnsignedDebitAmount"]]
            df["Unsigned Credit Amount"] = df[content["UnsignedCreditAmount"]]
            df["Signed Amount EC"] = df[content["SignedAmountEC"]]
            df["Unsigned Debit Amount EC"] = df[content["UnsignedDebitAmountEC"]]
            df["Unsigned Credit Amount EC"] = df[content["UnsignedCreditAmountEC"]]
            df["Journal Number"] = df[content["JournalNumber"]]
            df["Spotlight Type"] = None
            df["Date Entered"] = df[content["DateEntered"]]
            df["Time Entered"] = None
            df["Date Updated"] = df[content["DateUpdated"]]
            df["Time Updated"] = None
            df["UserID Entered"] = df[content["UserIDEntered"]]
            df["Name of User Entered"] = df[content["NameofUserEntered"]]
            df["UserID Updated"] = df[content["UserIDUpdated"]]
            df["Name of User Updated"] = df[content["NameofUserUpdated"]]
            df["Date Effective"] = df[content["DateEffective"]]
            df["Date of Journal"] = None
            df["Financial Period"] = None
            df["Journal Type"] = None
            df["Journal Type Description"] = None
            df["Auto Manual or Interface"] = content["AutoManualorInterface"]
            df["Journal Description"] = df[content["JournalDescription"]]
            df["Line Number"] = None
            df["Line Description"] = df[content["LineDescription"]]
            df["Exchange Rate"] = None
            df["DC Indicator"] = None
            df["Account Number"] = df[content["AccountNumber"]]
            df["Account Description"] = df[content["AccountDescription"]]
            df["Controlling Area for Cost and Profit Centre"] = None
            df["Cost Centre"] = None
            df["Cost Centre Description"] = None
            df["Profit Centre"] = None
            df["Profit Centre Description"] = None
            df["Source Activity or Transaction Code"] = None
            self.info("step 2 => reset column successfully")
            return df
        except Exception as e:
            self.signal_done.emit(True)
            self.err(f"{e}")

    def get(
            self,
            df: DataFrame
    ) -> DataFrame:
        """ get standard templates """
        try:
            # read template column name
            with open("config/columnName.txt", "r", encoding="utf-8") as fp:
                column_names = fp.readlines()
            list_cs = [column_name.strip("\n") for column_name in column_names]
            Log.info("get columns successfully.")
            self.info("step 3 => get columns successfully")
            return df.loc[:, list_cs]
        except Exception as e:
            self.signal_done.emit(True)
            self.err(f"{e}")
            Log.error(e)

    def sort(
            self,
            df: DataFrame,
            journalNumber: str = "Journal Number",
            ascending: bool = True,
    ) -> DataFrame:
        """ sort values """
        try:
            df = df.sort_values(by=journalNumber, ascending=ascending, ignore_index=True)
            Log.info("sort values successfully.")
            self.info("step 8 => sort values successfully")
            return df
        except Exception as e:
            self.signal_done.emit(True)
            self.err(f"{e}")
            Log.error(e)

    def convert_date(
            self,
            df: DataFrame,
            dateEffective: str = "Date Effective",
            dateEntered: str = "Date Entered",
    ) -> DataFrame:
        """ convert date format to dd/mm/yyyy """
        try:
            df[dateEffective] = pd.to_datetime(df[dateEffective])
            df[dateEffective] = pd.to_datetime(df[dateEffective]).dt.strftime("%d/%m/%Y")
            df[dateEntered] = pd.to_datetime(df[dateEntered])
            df[dateEntered] = pd.to_datetime(df[dateEntered]).dt.strftime("%d/%m/%Y")
            Log.info("convert date format successfully.")
            self.info("step 4 => convert date format successfully")
            return df
        except Exception as e:
            self.signal_done.emit(True)
            self.err(f"{e}")
            Log.error(e)

    def convert_number(
            self,
            df: DataFrame,
    ) -> DataFrame:
        """" retain 2 decimals """
        try:
            df = df.round({'Unsigned Debit Amount': 2, 'Unsigned Credit Amount': 2, "Signed Journal Amount": 2,
                           "Unsigned Debit Amount EC": 2, "Unsigned Credit Amount EC": 2, "Signed Amount EC": 2})
            Log.info("retain 2 decimals successfully.")
            self.info("step 5 => retain 2 decimals successfully")
            return df
        except Exception as e:
            self.signal_done.emit(True)
            self.err(f"{e}")
            Log.error(e)

    def convert_string(
            self,
            df: DataFrame,
            lineDescription: str = "Line Description"
    ) -> DataFrame:
        """ clear special symbols and limits string length """
        try:
            df[lineDescription] = df[lineDescription].astype(str)
            df[lineDescription] = df[lineDescription].apply(lambda x: re.sub("\W", "", x))
            df[lineDescription] = df[lineDescription].apply(lambda x: x[: 200])
            Log.info("clear special symbols and limits string length successfully.")
            self.info("step 6 => clear special symbols and limits string length successfully")
            return df
        except Exception:
            self.signal_done.emit(True)
            self.err("'Line Description' column is null")
            Log.error("'Line Description' column is null.")

    def convert_chinese(
            self,
            df: DataFrame,
            journalNumber: str = "Journal Number",
            py_type: str = "upper",  # upper, lower, captial, abbre
    ) -> DataFrame:
        """ convert chinese to pinyin """
        try:
            df[journalNumber] = df[journalNumber].astype(str)
            list_pinyin: list = []
            for value in df[journalNumber]:
                py_single = pinyin(value, style=Style.NORMAL)
                py_mutiple = [value[0] for value in py_single]
                if py_type == "upper":
                    py_result = ''.join([i.upper() for i in py_mutiple])
                    list_pinyin.append(py_result)
                if py_type == "lower":
                    py_result = ''.join([i.lower() for i in py_mutiple])
                    list_pinyin.append(py_result)
                if py_type == "captial":
                    py_result = py_mutiple[0].capitalize(
                    ) + ''.join(py_mutiple[1:])
                    list_pinyin.append(py_result)
                if py_type == "abbre":
                    py_result = ''.join([i[0].upper() for i in py_mutiple])
                    list_pinyin.append(py_result)
                df.replace(value, list_pinyin[0], inplace=True)
            self.info("step 7 => convert pinyin successfully")
            Log.info("convert pinyin successfully.")
            return df
        except Exception:
            self.signal_done.emit(True)
            self.err("'Journal Number' column is null")
            Log.error("'Journal Number' column is null.")

    def pivot(
            self,
            df: DataFrame,
            index: Union[str, list[str], None] = None,
            values: Union[str, list[str], None] = None,
            save_path: str = "saveFile",
            is_pivot: bool = True,  # export pivot table -> default(yes)
            is_net2zero: bool = True  # export net 2 zero table -> default(yes)
    ) -> None:
        """ get pivot table and net 2 zero table """
        try:
            pt = pd.pivot_table(df, index=index, values=values, aggfunc=np.sum)
            pt.reset_index(inplace=True)
            if is_pivot:
                pt.to_excel(f"{save_path}/pivot.xlsx", index=False)
                Log.info(f"pivot save file path: {save_path}\\pivot.xlsx")
            if is_net2zero:
                pt.to_excel(f"{save_path}/net2zero.xlsx", index=False)
                Log.info(f"net2zero save file path: {save_path}\\net2zero.xlsx")
        except Exception as e:
            Log.error(e)

    def calculation_sum(
            self,
            df: DataFrame,
            debit: str = "Unsigned Debit Amount EC",
            credit: str = "Unsigned Credit Amount EC",
            amount: str = "Signed Amount EC"
    ) -> None:
        """ calculation of summation """
        try:
            df[debit] = df[debit].astype(float)
            df[credit] = df[credit].astype(float)
            df[amount] = df[amount].astype(float)
            Log.info(f"Debit -> {df[debit].sum()}")
            Log.info(f"Credit -> {df[credit].sum()}")
            Log.info(f"Amount -> {df[amount].sum()}")
        except Exception as e:
            Log.error(e)

    def add_number(
            self,
            df: DataFrame,
            journalNumber: str = "Journal Number",
            lineNumber: str = "Line Number"
    ) -> DataFrame:
        """ add Line Number """
        try:
            df_cols = [col for col in df.columns]  # get all columns
            jn = df.columns.get_loc(journalNumber)  # get Journal Number location
            ln = df.columns.get_loc(lineNumber)  # get Line Number location
            df[lineNumber] = int(1)
            df_len = len(df)  # get df length
            df2arr = np.array(df)  # convert pandas.dataframe to numpy.array
            for value in range(1, df_len):
                if df2arr[value][jn] == df2arr[value - 1][jn]:
                    df2arr[value][ln] = df2arr[value - 1][ln] + 1
                else:
                    df2arr[value][ln] = int(1)
            arr2df = pd.DataFrame(df2arr)  # convert numpy.array to pandas.dataframe
            arr2df.columns = df_cols  # reset all columns
            Log.info("add Line Number successfully.")
            self.info("step 9 => add Line Number successfully")
            return arr2df
        except Exception:
            self.signal_done.emit(True)
            self.err("'Journal Number' column is null")
            Log.error("'Journal Number' column is null.")

    def add_month(
            self,
            df: DataFrame,
            financialPeriod: str = "Financial Period",
    ) -> DataFrame:
        """ add Financial Period """
        try:
            df[financialPeriod] = df["Date Effective"].str.split("/").str[1]
            df[financialPeriod] = df[financialPeriod].astype("uint8")
            Log.info("add Financial Period successfully.")
            self.info("step 10 => add Financial Period successfully")
            return df
        except Exception as e:
            self.signal_done.emit(True)
            self.err(f"{e}")
            Log.error(e)

    def add_direction(
            self,
            df: DataFrame,
            amount: str = "Signed Amount EC",
            dcIndicator: str = "DC Indicator",
    ) -> DataFrame:
        """ adjust 'DC Indicator' direction """
        try:
            df[amount] = df[amount].astype("double[pyarrow]")
            df[dcIndicator] = np.where(df[amount] >= 0, "D", "C")
            Log.info("adjust dc direction successfully.")
            self.info("step 11 => adjust dc direction successfully")
            return df
        except Exception as e:
            self.signal_done.emit(True)
            self.err(f"{e}")
            Log.error(e)

    def add_dc_amount(
            self,
            df: DataFrame,
            amount: str = "Signed Amount EC",
            debit: str = "Unsigned Debit Amount EC",
            credit: str = "Unsigned Credit Amount EC",
    ) -> DataFrame:
        """ calculation dc values """
        try:
            df[debit] = np.where(df[amount] > 0, df[amount], 0)
            df[credit] = np.where(df[amount] < 0, df[amount] * -1, 0)
            df["Unsigned Debit Amount"] = df[debit]
            df["Unsigned Credit Amount"] = df[credit]
            Log.info("calculation dc values successfully.")
            self.info("step 12 => calculation dc values successfully")
            return df
        except Exception as e:
            self.signal_done.emit(True)
            self.err(f"{e}")
            Log.error(e)

    def get_last_account(
            self,
            df: DataFrame,
            location: int = 0,  # entity_accountCode loaction
            entity_account: str = "enacc",  # entity_accountCode column
    ) -> list:
        """ get end-level account """
        cell = 0
        last_acc: list = []
        df_len = len(df)
        try:
            while cell < df_len - 1:
                try:
                    if df.iloc[cell, location - 1] == df.iloc[cell + 1, location - 1][
                                                      :len(df.iloc[cell, location - 1])]:
                        pass
                    else:
                        last_acc.append(df.iloc[cell, df.columns.get_loc(entity_account)])
                    cell += 1
                except:
                    break
            last_acc.append(df.iloc[df_len - 1, location - 1])
            Log.info("get end-level account successfully.")
            return last_acc
        except Exception as e:
            self.signal_done.emit(True)
            Log.error(e)

    def screen(
            self,
            df: DataFrame,
            entity_account: str = "enacc",  # entity_accountCode column
            screen_condition: Union[str, list[str], None] = None  # screening conditions
    ) -> DataFrame:
        """ screen data """
        list_screen: list = []
        try:
            for condition in screen_condition:
                df_screen = df.loc[df[entity_account] == condition]
                list_screen.append(df_screen)
            df = pd.concat(list_screen, axis=0, ignore_index=True)
            Log.info("screen data successfully.")
            return df
        except Exception as e:
            self.signal_done.emit(True)
            Log.error(e)

    def read(self, file_path: str) -> DataFrame:
        try:
            list_df: list = []
            with open(file_path, 'r', encoding="utf-8") as csvfile:
                delimiter = csv.Sniffer().sniff(csvfile.read(5000)).delimiter
            reader = pd.read_csv(
                file_path, dtype_backend="pyarrow", chunksize=100_0000, sep=str(delimiter))
            for chunk in reader:
                list_df.append(chunk)
            df = pd.concat(list_df, ignore_index=True)
            name = os.path.basename(file_path)
            self.info(f"read {name} successfully")
            return df
        except Exception as e:
            self.signal_done.emit(True)
            self.err(f"{e}")

    def write(
            self,
            df: DataFrame,
            path: str = "handleGL.txt"
    ) -> None:
        try:
            df.to_csv(path, index=False, encoding="utf-16le", sep="|")
            Log.info(f"save path -> {path}.")
            self.info(f"save file: {path}")
        except Exception as e:
            self.signal_done.emit(True)
            self.err(f"{e}")

    def check(
            self,
            df: DataFrame,
            entity: str = "Entity",
            currency: str = "Currency",
            currencyEC: str = "Entity Currency (EC)",
            amount: str = "Signed Amount EC",
            debit: str = "Unsigned Debit Amount EC",
            credit: str = "Unsigned Credit Amount EC",
            mi: str = "Auto Manual or Interface",
            fp: str = "Financial Period",
            linedesc: str = "Line Description",
            linenum: str = "Line Number",
            is_equal: bool = True,  # check debit credit and amount column
            is_mi: bool = True,  # check auto manual or interface column
            is_negative: bool = True,  # check negative number
            is_month: bool = True,  # check Financial Period
            is_entity: bool = True,  # check entity
            is_currency: bool = True,  # check currency,
            is_specialSymbol: bool = True,  # check Line Description
            is_linenum: bool = True,  # check Line Number
    ) -> None:
        try:
            if is_equal:
                debit_sum = df[debit].sum()
                credit_sum = df[credit].sum()
                amount_sum = df[amount].sum()
                if debit_sum == credit_sum and amount_sum == float(0):
                    Log.info("Test passed -> (debit === credit) & (amount === 0).")
                else:
                    Log.error("Test failed -> please check debit, credit and amount column.")
            if is_mi:
                ami = df[mi].unique().tolist()
                if pd.isna(ami):
                    Log.error("Test failed -> [Auto Manual or Interface] column is null.")
                else:
                    Log.info(f"Test passed -> [Auto Manual or Interface] -> {ami}")
            if is_negative:
                uni_d = df[debit].unique().tolist()
                uni_c = df[credit].unique().tolist()
                neg_d = [value for value in uni_d if value < 0]
                neg_c = [value for value in uni_c if value < 0]
                if len(neg_d) == 0 and len(neg_c) == 0:
                    Log.info("Test passed -> no negative number.")
                else:
                    Log.error(
                        "Test failed -> [Unsigned Debit Amount EC] and "
                        "[Unsigned Credit Amount EC] contains negative numbers.")
            if is_month:
                month = df[fp].unique().tolist()
                month.sort()
                if len(month) <= 0:
                    Log.error("Test failed -> [Financial Period] column is null.")
                else:
                    Log.info(f"Test passed -> [Financial Period] -> {month}")
            if is_entity:
                ent = df[entity].unique().tolist()
                if pd.isna(ent):
                    Log.error("Test failed -> [Entity] column is null.")
                else:
                    Log.info(f"Test passed -> [Entity] -> {ent}")
            if is_currency:
                curr = df[currency].unique().tolist()
                curr_ec = df[currencyEC].unique().tolist()
                if pd.isna(curr) or pd.isna(curr_ec):
                    Log.error("Test failed -> [Currency] or [Currency EC] column is null.")
                else:
                    Log.info(f"Test passed -> [currency] -> {curr}; [Currency EC] -> {curr_ec}")
            if is_specialSymbol:
                ld_len = df[linedesc].str.len().unique().tolist()
                find_len = [x for x in ld_len if x > 200]
                if len(find_len) > 0:
                    Log.error("Test failed -> [Line Description].")
                else:
                    Log.info("Test passed -> [Line Description].")
            if is_linenum:
                line_number = df[linenum].unique().tolist()
                if len(line_number) <= 0:
                    Log.error("Test failed -> [Line Number] column is null.")
                else:
                    Log.info("Test passed -> [Line Number].")
        except Exception as e:
            self.signal_done.emit(True)
            Log.error(e)

    def run(self) -> None:
        try:
            df = self.read(self.file_path)
            df = self.insert_column(df)
            df = self.reset_column(df)
            df = self.get(df)
            df = self.convert_date(df)
            df = self.convert_number(df)
            df = self.convert_string(df)
            df = self.convert_chinese(df, py_type="lower")
            df = self.sort(df)
            df = self.add_number(df)
            df = self.add_month(df)
            df = self.add_direction(df)
            df = self.add_dc_amount(df)
            self.check(df)
            self.write(df, self.output_path)
            self.info("completed")
        except Exception as e:
            self.signal_done.emit(True)
            self.signal_error.emit(f"{e}")


class ReadYaml:
    def __init__(self, file_path):
        self.file_path = file_path
        self.data = self.read()

    def read(self):
        try:
            with open(self.file_path, 'r', encoding="utf-8") as f:
                content = yaml.load(f, Loader=yaml.FullLoader)
                return content
        except Exception as e:
            print(f"Read yaml file Error: {e}")

    def get_value(self, dataOne):
        return self.data[dataOne]
