# coding:utf-8
from qfluentwidgets import (
    SettingCardGroup, PushSettingCard, ScrollArea, InfoBarPosition, setTheme,
    ExpandLayout, LineEdit, StateToolTip
)
from qfluentwidgets import FluentIcon as FIF
from qfluentwidgets import InfoBar
from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtWidgets import QWidget, QLabel, QFileDialog

from ..common.config import cfg
from ..common.style_sheet import StyleSheet
from ..utils import split_data


class DataSplitInterface(ScrollArea):
    """ data pivot interface """

    downloadFolderChanged = pyqtSignal(str)

    def __init__(self, parent=None):
        super().__init__(parent=parent)
        self.scrollWidget = QWidget()
        self.expandLayout = ExpandLayout(self.scrollWidget)

        # setting label
        self.splitLabel = QLabel(self.tr("Data Split"), self)

        # split csv to xlsx
        self.toExcelGroup = SettingCardGroup(self.tr("csv2xlsx"), self.scrollWidget)
        self.csv2xlsxOpenFile = PushSettingCard(
            self.tr('open file'),
            FIF.SEARCH,
            self.tr("open csv file"),
            cfg.get(cfg.downloadFolder),
            self.toExcelGroup
        )
        self.csv2xlsx_lines = LineEdit(self)
        self.csv2xlsx_lines.setPlaceholderText(
            self.tr('Please enter the number of split rows (eg: 30000)'))
        self.csv2xlsx_lines.setClearButtonEnabled(True)
        self.csv2xlsx_lines.textEdited[str].connect(lambda: self.__realtimeUpdateValue())
        self.csv2xlsxSaveFile = PushSettingCard(
            self.tr('save path'),
            FIF.SAVE,
            self.tr("select file save path"),
            cfg.get(cfg.downloadFolder),
            self.toExcelGroup
        )
        self.csv2xlsxButton = PushSettingCard(
            self.tr('csv2xlsx'),
            FIF.RETURN,
            self.tr('split csv to xlsx'),
            self.tr(''),
            self.toExcelGroup
        )

        self.__initWidget()

    def __initWidget(self):
        self.resize(1000, 800)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.setViewportMargins(0, 80, 0, 20)
        self.setWidget(self.scrollWidget)
        self.setWidgetResizable(True)

        # initialize style sheet
        self.scrollWidget.setObjectName('scrollWidget')
        self.splitLabel.setObjectName('settingLabel')
        StyleSheet.SETTING_INTERFACE.apply(self)

        # initialize layout
        self.__initLayout()
        self.__connectSignalToSlot()

    def __initLayout(self):
        self.splitLabel.move(36, 30)

        # add csv2xlsx to group
        self.toExcelGroup.addSettingCard(self.csv2xlsxOpenFile)
        self.toExcelGroup.addSettingCard(self.csv2xlsx_lines)
        self.toExcelGroup.addSettingCard(self.csv2xlsxSaveFile)
        self.toExcelGroup.addSettingCard(self.csv2xlsxButton)

        # add pivot group to layout
        self.expandLayout.setSpacing(28)
        self.expandLayout.setContentsMargins(36, 10, 36, 0)
        self.expandLayout.addWidget(self.toExcelGroup)

    def __connectSignalToSlot(self):
        """ connect signal to slot """
        cfg.themeChanged.connect(setTheme)

        # pivot
        self.csv2xlsxOpenFile.clicked.connect(self.__csv2xlsxOpenFile)
        self.csv2xlsxSaveFile.clicked.connect(self.__csv2xlsxSaveFile)
        self.csv2xlsxButton.clicked.connect(self.__csv2xlsx)

    def __onProgress(self):
        if self.stateTooltip:
            self.stateTooltip.setContent(
                self.tr('End of program operation!') + ' √')
            self.stateTooltip.setState(True)
            self.stateTooltip = False

    def __csv2xlsxOpenFile(self):
        """ open csv file """
        self.csv2xlsxFile = QFileDialog.getOpenFileName(
            self, self.tr("Open file"), "*.csv;*.txt;*.tsv")[0]
        if self.csv2xlsxFile:
            self.csv2xlsxOpenFile.setContent(self.csv2xlsxFile)
        else:
            self.warningMessage("No file opened")

    def __csv2xlsxSaveFile(self):
        """ select save path """
        try:
            self.xlsxSaveFile = QFileDialog.getExistingDirectory(
                self, self.tr("Choose folder"), "./")
            if self.xlsxSaveFile:
                self.csv2xlsxSaveFile.setContent(self.xlsxSaveFile)
            else:
                self.warningMessage("No save file selected")
        except Exception as e:
            self.errorMessage(f"{e}")

    def __csv2xlsx(self):
        """ split csv to xlsx """
        try:
            self.stateTooltip = StateToolTip(
                self.tr('csv2xlsx'), self.tr('Please wait patiently'), self.window())
            self.stateTooltip.move(self.stateTooltip.getSuitablePos())
            self.stateTooltip.show()
            self.thread_pivot = split_data.SplitDataThread(
                file_path=self.csv2xlsxFile,
                row_count=self.csv2xlsx_values,
                output_path=self.xlsxSaveFile)
            self.thread_pivot.signal_info.connect(self.infoMessage)
            self.thread_pivot.signal_warning.connect(self.warningMessage)
            self.thread_pivot.signal_error.connect(self.errorMessage)
            self.thread_pivot.signal_done.connect(self.__onProgress)
            self.thread_pivot.moveToThread(self.thread_pivot)
            self.thread_pivot.start()
        except Exception as e:
            self.stateTooltip.hide()
            self.errorMessage(f"{e}")

    def __realtimeUpdateValue(self):
        # real time update of lineEdit values
        try:
            self.csv2xlsx_values = int(self.csv2xlsx_lines.text())
        except Exception as e:
            self.warningMessage(f"{e}")

    def infoMessage(self, text: str):
        InfoBar.success(
            title=self.tr('Info'),
            content=self.tr(text),
            orient=Qt.Horizontal,
            isClosable=True,
            position=InfoBarPosition.TOP,
            duration=4000,
            parent=self
        )

    def warningMessage(self, text: str):
        InfoBar.info(
            title=self.tr('Warning'),
            content=self.tr(text),
            orient=Qt.Horizontal,
            isClosable=True,
            position=InfoBarPosition.TOP,
            duration=5000,
            parent=self
        )

    def errorMessage(self, text: str):
        InfoBar.error(
            title=self.tr('Error'),
            content=self.tr(text),
            orient=Qt.Horizontal,
            isClosable=True,
            position=InfoBarPosition.BOTTOM,
            duration=8000,
            parent=self
        )
