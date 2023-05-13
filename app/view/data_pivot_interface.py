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
from ..utils import pivot_data


class DataPivotInterface(ScrollArea):
    """ data pivot interface """

    downloadFolderChanged = pyqtSignal(str)

    def __init__(self, parent=None):
        super().__init__(parent=parent)
        self.scrollWidget = QWidget()
        self.expandLayout = ExpandLayout(self.scrollWidget)

        # setting label
        self.pivotLabel = QLabel(self.tr("Data Pivot"), self)

        # pivot data
        self.pivotDataGroup = SettingCardGroup(self.tr("group sum"), self.scrollWidget)
        self.openFile = PushSettingCard(
            self.tr('open file'),
            FIF.SEARCH,
            self.tr("open csv file"),
            cfg.get(cfg.downloadFolder),
            self.pivotDataGroup
        )
        self.index = LineEdit(self)
        self.index.setPlaceholderText(
            self.tr('Please enter the index column, separate with commas (eg: Account,Entity)'))
        self.index.setClearButtonEnabled(True)
        self.index.textEdited[str].connect(lambda: self.__realtimeUpdateValue())
        self.values = LineEdit(self)
        self.values.setPlaceholderText(
            self.tr('Please enter the values column, separate with commas (eg: debit,credit)'))
        self.values.setClearButtonEnabled(True)
        self.values.textEdited[str].connect(lambda: self.__realtimeUpdateValue())
        self.pivotSaveFile = PushSettingCard(
            self.tr('save path'),
            FIF.SAVE,
            self.tr("select file save path"),
            cfg.get(cfg.downloadFolder),
            self.pivotDataGroup
        )
        self.pivotButton = PushSettingCard(
            self.tr('pivot'),
            FIF.RETURN,
            self.tr('run data pivot'),
            self.tr(''),
            self.pivotDataGroup
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
        self.pivotLabel.setObjectName('settingLabel')
        StyleSheet.SETTING_INTERFACE.apply(self)

        # initialize layout
        self.__initLayout()
        self.__connectSignalToSlot()

    def __initLayout(self):
        self.pivotLabel.move(36, 30)

        # add data pivot to group
        self.pivotDataGroup.addSettingCard(self.openFile)
        self.pivotDataGroup.addSettingCard(self.index)
        self.pivotDataGroup.addSettingCard(self.values)
        self.pivotDataGroup.addSettingCard(self.pivotSaveFile)
        self.pivotDataGroup.addSettingCard(self.pivotButton)

        # add pivot group to layout
        self.expandLayout.setSpacing(28)
        self.expandLayout.setContentsMargins(36, 10, 36, 0)
        self.expandLayout.addWidget(self.pivotDataGroup)

    def __connectSignalToSlot(self):
        """ connect signal to slot """
        cfg.themeChanged.connect(setTheme)

        # pivot
        self.openFile.clicked.connect(self.__onOpenFile)
        self.pivotSaveFile.clicked.connect(self.__onSelectPivotSaveFile)
        self.pivotButton.clicked.connect(self.__onPivot)

    def __onProgress(self):
        if self.stateTooltip:
            self.stateTooltip.setContent(
                self.tr('End of program operation!') + ' √')
            self.stateTooltip.setState(True)
            self.stateTooltip = False

    def __onOpenFile(self):
        self.file = QFileDialog.getOpenFileName(
            self, self.tr("Open file"), "*.csv;*.txt;*.tsv")[0]
        if self.file:
            self.openFile.setContent(self.file)
        else:
            self.warningMessage("No file opened")

    def __onSelectPivotSaveFile(self):
        """ select save path """
        try:
            self.saveFile = QFileDialog.getSaveFileName(
                self, self.tr("Save file"), "./")[0]
            if self.saveFile:
                self.pivotSaveFile.setContent(self.saveFile)
            else:
                self.warningMessage("No save file selected")
        except Exception as e:
            self.errorMessage(f"{e}")

    def __onPivot(self):
        """ pivot """
        try:
            self.stateTooltip = StateToolTip(
                self.tr('Data Pivot'), self.tr('Please wait patiently'), self.window())
            self.stateTooltip.move(self.stateTooltip.getSuitablePos())
            self.stateTooltip.show()
            self.thread_pivot = pivot_data.PivotDataThread(
                file_path=self.file,
                index=self.index_v,
                values=self.values_v,
                output_path=self.saveFile)
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
            self.index_v = self.index.text()
            self.values_v = self.values.text()
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
