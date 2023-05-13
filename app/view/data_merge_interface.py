# coding:utf-8
from qfluentwidgets import (
    SettingCardGroup, PushSettingCard, ScrollArea, InfoBarPosition,
    setTheme, ExpandLayout, StateToolTip
)
from qfluentwidgets import FluentIcon as FIF
from qfluentwidgets import InfoBar
from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtWidgets import QWidget, QLabel, QFileDialog

from ..common.config import cfg
from ..common.style_sheet import StyleSheet
from ..utils import merge_data


class DataMergeInterface(ScrollArea):
    """ data filter interface """

    downloadFolderChanged = pyqtSignal(str)

    def __init__(self, parent=None):
        super().__init__(parent=parent)
        self.scrollWidget = QWidget()
        self.expandLayout = ExpandLayout(self.scrollWidget)

        # setting label
        self.mergeLabel = QLabel(self.tr("Data Merge"), self)

        # merge excel
        self.mergeExcelGroup = SettingCardGroup(self.tr("excel merge"), self.scrollWidget)
        self.openExcelFolder = PushSettingCard(
            self.tr('choose folder'),
            FIF.FOLDER,
            self.tr("select a folder with excel"),
            cfg.get(cfg.downloadFolder),
            self.mergeExcelGroup
        )
        self.mergeExcelSaveFile = PushSettingCard(
            self.tr('save path'),
            FIF.SAVE,
            self.tr("select file save path"),
            cfg.get(cfg.downloadFolder),
            self.mergeExcelGroup
        )
        self.mergeExcelButton = PushSettingCard(
            self.tr('merge execl'),
            FIF.RETURN,
            self.tr('merge all excel files in one folder'),
            self.tr(''),
            self.mergeExcelGroup
        )

        # merge csv
        self.mergeTextGroup = SettingCardGroup(self.tr("csv merge"), self.scrollWidget)
        self.openTextFolder = PushSettingCard(
            self.tr('choose folder'),
            FIF.FOLDER,
            self.tr("select a folder with csv"),
            cfg.get(cfg.downloadFolder),
            self.mergeTextGroup
        )
        self.mergeTextSaveFile = PushSettingCard(
            self.tr('save path'),
            FIF.SAVE,
            self.tr("select file save path"),
            cfg.get(cfg.downloadFolder),
            self.mergeTextGroup
        )
        self.mergeTextButton = PushSettingCard(
            self.tr('merge csv'),
            FIF.RETURN,
            self.tr('merge all text files in one folder'),
            self.tr(''),
            self.mergeTextGroup
        )

        # merge csv - use rust
        self.pycrabMergeGroup = SettingCardGroup(self.tr("csv merge > 10GB"), self.scrollWidget)
        self.pycrabOpenFolder = PushSettingCard(
            self.tr('choose folder'),
            FIF.FOLDER,
            self.tr("select a folder with csv"),
            cfg.get(cfg.downloadFolder),
            self.pycrabMergeGroup
        )
        self.pycrabMergeSaveFile = PushSettingCard(
            self.tr('save path'),
            FIF.SAVE,
            self.tr("select file save path"),
            cfg.get(cfg.downloadFolder),
            self.pycrabMergeGroup
        )
        self.pycrabMergeButton = PushSettingCard(
            self.tr('merge csv'),
            FIF.RETURN,
            self.tr('merge all text files in one folder'),
            self.tr(''),
            self.pycrabMergeGroup
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
        self.mergeLabel.setObjectName('settingLabel')
        StyleSheet.SETTING_INTERFACE.apply(self)

        # initialize layout
        self.__initLayout()
        self.__connectSignalToSlot()

    def __initLayout(self):
        self.mergeLabel.move(36, 30)

        # add excel merge to group
        self.mergeExcelGroup.addSettingCard(self.openExcelFolder)
        self.mergeExcelGroup.addSettingCard(self.mergeExcelSaveFile)
        self.mergeExcelGroup.addSettingCard(self.mergeExcelButton)

        # add csv merge to group
        self.mergeTextGroup.addSettingCard(self.openTextFolder)
        self.mergeTextGroup.addSettingCard(self.mergeTextSaveFile)
        self.mergeTextGroup.addSettingCard(self.mergeTextButton)

        # add pycrab csv merge to group
        self.pycrabMergeGroup.addSettingCard(self.pycrabOpenFolder)
        self.pycrabMergeGroup.addSettingCard(self.pycrabMergeSaveFile)
        self.pycrabMergeGroup.addSettingCard(self.pycrabMergeButton)

        # add merge group to layout
        self.expandLayout.setSpacing(28)
        self.expandLayout.setContentsMargins(36, 10, 36, 0)
        self.expandLayout.addWidget(self.mergeExcelGroup)
        self.expandLayout.addWidget(self.mergeTextGroup)
        self.expandLayout.addWidget(self.pycrabMergeGroup)

    def __onOpenExcelFolder(self):
        self.excelFolder = QFileDialog.getExistingDirectory(
            self, self.tr("Choose folder"), "./")
        if self.excelFolder:
            self.openExcelFolder.setContent(self.excelFolder)
        else:
            self.warningMessage("No folder selected")

    def __onSelectExcelSaveFile(self):
        """ select save path """
        try:
            self.excelSaveFile = QFileDialog.getSaveFileName(
                self, self.tr("Save file"), "./")[0]
            if self.excelSaveFile:
                self.mergeExcelSaveFile.setContent(self.excelSaveFile)
            else:
                self.warningMessage("No save file selected")
        except Exception as e:
            self.errorMessage(f"{e}")

    def __onExcelMerge(self):
        """ merge excel """
        try:
            self.stateTooltip = StateToolTip(
                self.tr('Merge Excel'), self.tr('Please wait patiently'), self.window())
            self.stateTooltip.move(self.stateTooltip.getSuitablePos())
            self.stateTooltip.show()
            self.thread_merge_excel = merge_data.MergeExcelThread(
                folder_path=self.excelFolder,
                output_path=self.excelSaveFile)
            self.thread_merge_excel.signal_info.connect(self.infoMessage)
            self.thread_merge_excel.signal_warning.connect(self.warningMessage)
            self.thread_merge_excel.signal_error.connect(self.errorMessage)
            self.thread_merge_excel.signal_done.connect(self.__onProgress)
            self.thread_merge_excel.moveToThread(self.thread_merge_excel)
            self.thread_merge_excel.start()
        except Exception as e:
            self.stateTooltip.hide()
            self.errorMessage(f"{e}")

    def __onOpenTextFolder(self):
        """ open csv file folder """
        self.textFolder = QFileDialog.getExistingDirectory(
            self, self.tr("Choose folder"), "./")
        if self.textFolder:
            self.openTextFolder.setContent(self.textFolder)
        else:
            self.warningMessage("No folder selected")

    def __onSelectTextSaveFile(self):
        """ select save path """
        try:
            self.textSaveFile = QFileDialog.getSaveFileName(
                self, self.tr("Save file"), "./")[0]
            if self.textSaveFile:
                self.mergeTextSaveFile.setContent(self.textSaveFile)
            else:
                self.warningMessage("No save file selected")
        except Exception as e:
            self.errorMessage(f"{e}")

    def __onTextMerge(self):
        """ merge csv """
        try:
            self.stateTooltip = StateToolTip(
                self.tr('Merge csv'), self.tr('Please wait patiently'), self.window())
            self.stateTooltip.move(self.stateTooltip.getSuitablePos())
            self.stateTooltip.show()
            self.thread_merge_csv = merge_data.MergeTextThread(
                folder_path=self.textFolder,
                output_path=self.textSaveFile)
            self.thread_merge_csv.signal_info.connect(self.infoMessage)
            self.thread_merge_csv.signal_warning.connect(self.warningMessage)
            self.thread_merge_csv.signal_error.connect(self.errorMessage)
            self.thread_merge_csv.signal_done.connect(self.__onProgress)
            self.thread_merge_csv.moveToThread(self.thread_merge_csv)
            self.thread_merge_csv.start()
        except Exception as e:
            self.stateTooltip.hide()
            self.errorMessage(f"{e}")

    def __connectSignalToSlot(self):
        """ connect signal to slot """
        cfg.themeChanged.connect(setTheme)

        # merge excel
        self.openExcelFolder.clicked.connect(self.__onOpenExcelFolder)
        self.mergeExcelSaveFile.clicked.connect(self.__onSelectExcelSaveFile)
        self.mergeExcelButton.clicked.connect(self.__onExcelMerge)

        # merge csv
        self.openTextFolder.clicked.connect(self.__onOpenTextFolder)
        self.mergeTextSaveFile.clicked.connect(self.__onSelectTextSaveFile)
        self.mergeTextButton.clicked.connect(self.__onTextMerge)

    def __onProgress(self):
        if self.stateTooltip:
            self.stateTooltip.setContent(
                self.tr('End of program operation!') + ' √')
            self.stateTooltip.setState(True)
            self.stateTooltip = False

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
