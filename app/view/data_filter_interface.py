# coding:utf-8
from qfluentwidgets import (
    SettingCardGroup, PushSettingCard, ScrollArea, InfoBarPosition,
    setTheme, LineEdit, ExpandLayout, StateToolTip
)
from qfluentwidgets import FluentIcon as FIF
from qfluentwidgets import InfoBar
from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtWidgets import QWidget, QLabel, QFileDialog

from ..common.config import cfg
from ..common.style_sheet import StyleSheet
from ..utils import filter_data


class DataFilterInterface(ScrollArea):
    """ data filter interface """

    downloadFolderChanged = pyqtSignal(str)

    def __init__(self, parent=None):
        super().__init__(parent=parent)
        self.scrollWidget = QWidget()
        self.expandLayout = ExpandLayout(self.scrollWidget)

        # setting label
        self.filterLabel = QLabel(self.tr("Data Filter"), self)

        # single filter
        self.dataFilterGroup = SettingCardGroup(self.tr("single filter"), self.scrollWidget)
        self.openFile = PushSettingCard(
            self.tr('open file'),
            FIF.SEARCH,
            self.tr("select excel or text file"),
            cfg.get(cfg.downloadFolder),
            self.dataFilterGroup
        )
        self.columns = LineEdit(self)
        self.columns.setPlaceholderText(self.tr('Please enter the fields to be filtered (eg: Account)'))
        self.columns.setClearButtonEnabled(True)
        self.columns.textEdited[str].connect(lambda: self.__realtimeUpdateValue())
        self.targets = PushSettingCard(
            self.tr('condition'),
            FIF.MESSAGE,
            self.tr("select the txt file to be filtered"),
            cfg.get(cfg.downloadFolder),
            self.dataFilterGroup
        )
        self.outputFolder = PushSettingCard(
            self.tr('save path'),
            FIF.FOLDER,
            self.tr("select file save path"),
            cfg.get(cfg.downloadFolder),
            self.dataFilterGroup
        )
        self.singleFilterButton = PushSettingCard(
            self.tr('filter data'),
            FIF.RETURN,
            self.tr('run single filter'),
            self.tr(''),
            self.dataFilterGroup
        )

        # multi filter
        self.dataMultiFilterGroup = SettingCardGroup(self.tr("multi filter"), self.scrollWidget)
        self.openFileMulti = PushSettingCard(
            self.tr('open file'),
            FIF.SEARCH,
            self.tr("select excel or text file"),
            cfg.get(cfg.downloadFolder),
            self.dataMultiFilterGroup
        )
        self.columnsMulti = LineEdit(self)
        self.columnsMulti.setPlaceholderText(self.tr('Please enter the fields to be filtered (eg: Number)'))
        self.columnsMulti.setClearButtonEnabled(True)
        self.columnsMulti.textEdited[str].connect(lambda: self.__realtimeUpdateValue())
        self.targetsMulti = PushSettingCard(
            self.tr('condition'),
            FIF.MESSAGE,
            self.tr("select the txt file to be filtered"),
            cfg.get(cfg.downloadFolder),
            self.dataMultiFilterGroup
        )
        self.outputFileMulti = PushSettingCard(
            self.tr('save path'),
            FIF.SAVE,
            self.tr("select file save path"),
            cfg.get(cfg.downloadFolder),
            self.dataMultiFilterGroup
        )
        self.multiFilterButton = PushSettingCard(
            self.tr('filter data'),
            FIF.RETURN,
            self.tr('run multi filter'),
            self.tr(''),
            self.dataMultiFilterGroup
        )

        # single filter - use rust
        self.pycrabFilterRowGroup = SettingCardGroup(self.tr("single filter > 10GB"), self.scrollWidget)
        self.pycrabOpenFile = PushSettingCard(
            self.tr('open file'),
            FIF.SEARCH,
            self.tr("select excel or text file"),
            cfg.get(cfg.downloadFolder),
            self.pycrabFilterRowGroup
        )
        self.pycrabColumn = LineEdit(self)
        self.pycrabColumn.setPlaceholderText(self.tr('Please enter the fields to be filtered (eg: Entity)'))
        self.pycrabColumn.setClearButtonEnabled(True)
        self.pycrabColumn.textEdited[str].connect(lambda: self.__realtimeUpdateValue())
        self.pycrabTarget = LineEdit(self)
        self.pycrabTarget.setPlaceholderText(self.tr('Please enter a filter condition (eg: 123456)'))
        self.pycrabTarget.setClearButtonEnabled(True)
        self.pycrabTarget.textEdited[str].connect(lambda: self.__realtimeUpdateValue())
        self.pycrabOutputFolder = PushSettingCard(
            self.tr('save path'),
            FIF.SAVE,
            self.tr("select file save path"),
            cfg.get(cfg.downloadFolder),
            self.pycrabFilterRowGroup
        )
        self.pycrabFilterRowButton = PushSettingCard(
            self.tr('filter data'),
            FIF.RETURN,
            self.tr('run single filter'),
            self.tr(''),
            self.pycrabFilterRowGroup
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
        self.filterLabel.setObjectName('settingLabel')
        StyleSheet.SETTING_INTERFACE.apply(self)

        # initialize layout
        self.__initLayout()
        self.__connectSignalToSlot()

    def __initLayout(self):
        self.filterLabel.move(36, 30)

        # add single filter to group
        self.dataFilterGroup.addSettingCard(self.openFile)
        self.dataFilterGroup.addSettingCard(self.columns)
        self.dataFilterGroup.addSettingCard(self.targets)
        self.dataFilterGroup.addSettingCard(self.outputFolder)
        self.dataFilterGroup.addSettingCard(self.singleFilterButton)

        # add multi filter to group
        self.dataMultiFilterGroup.addSettingCard(self.openFileMulti)
        self.dataMultiFilterGroup.addSettingCard(self.columnsMulti)
        self.dataMultiFilterGroup.addSettingCard(self.targetsMulti)
        self.dataMultiFilterGroup.addSettingCard(self.outputFileMulti)
        self.dataMultiFilterGroup.addSettingCard(self.multiFilterButton)

        # add pycrab single filter to group
        self.pycrabFilterRowGroup.addSettingCard(self.pycrabOpenFile)
        self.pycrabFilterRowGroup.addSettingCard(self.pycrabColumn)
        self.pycrabFilterRowGroup.addSettingCard(self.pycrabTarget)
        self.pycrabFilterRowGroup.addSettingCard(self.pycrabOutputFolder)
        self.pycrabFilterRowGroup.addSettingCard(self.pycrabFilterRowButton)

        # add setting card group to layout
        self.expandLayout.setSpacing(28)
        self.expandLayout.setContentsMargins(36, 10, 36, 0)
        self.expandLayout.addWidget(self.dataFilterGroup)
        self.expandLayout.addWidget(self.dataMultiFilterGroup)
        self.expandLayout.addWidget(self.pycrabFilterRowGroup)

    def __onOpenFile(self):
        self.file = QFileDialog.getOpenFileName(
            self, self.tr("Open file"), "*.csv;*.xlsx;*.txt;*.tsv;*.CSV;*.XLSX;")[0]
        if self.file:
            self.openFile.setContent(self.file)
        else:
            self.warningMessage("No file opened")

    def __onSelectTarget(self):
        """ select txt """
        try:
            self.target = QFileDialog.getOpenFileName(
                self, self.tr("Select file"), "*.txt")[0]
            if self.target:
                self.targets.setContent(self.target)
            else:
                self.warningMessage("No file selected")
        except Exception as e:
            self.errorMessage(f"{e}")

    def __onSelectSavePath(self):
        """ select save path """
        try:
            self.save_path = QFileDialog.getExistingDirectory(
                self, self.tr("Choose folder"), "./")
            self.outputFolder.setContent(self.save_path)
        except Exception as e:
            self.errorMessage(f"{e}")

    def __onSingleFilter(self):
        """ single filter """
        try:
            self.stateTooltip = StateToolTip(
                self.tr('single filter'), self.tr('Please wait patiently'), self.window())
            self.stateTooltip.move(self.stateTooltip.getSuitablePos())
            self.stateTooltip.show()
            self.thread_filter_data = filter_data.FilterDataThread(
                file_path=self.file,
                output_path=self.save_path,
                column_field=self.col_value,
                targets=self.target)
            self.thread_filter_data.signal_info.connect(self.infoMessage)
            self.thread_filter_data.signal_warning.connect(self.warningMessage)
            self.thread_filter_data.signal_error.connect(self.errorMessage)
            self.thread_filter_data.signal_done.connect(self.__onProgress)
            self.thread_filter_data.moveToThread(self.thread_filter_data)
            self.thread_filter_data.start()
        except Exception as e:
            self.stateTooltip.hide()
            self.errorMessage(f"{e}")

    def __onOpenFileMulti(self):
        self.fileMulti = QFileDialog.getOpenFileName(
            self, self.tr("Open file"), "*.csv;*.txt;*.tsv;*.xlsx")[0]
        if self.fileMulti:
            self.openFileMulti.setContent(self.fileMulti)
        else:
            self.warningMessage("No file opened")

    def __onSelectTargetMulti(self):
        try:
            self.targetMulti = QFileDialog.getOpenFileName(
                self, self.tr("Select file"), "*.txt")[0]
            if self.targetMulti:
                self.targetsMulti.setContent(self.targetMulti)
            else:
                self.warningMessage("No file selected")
        except Exception as e:
            self.errorMessage(f"{e}")

    def __onSelectSaveFile(self):
        """ select save file"""
        try:
            self.save_file = QFileDialog.getSaveFileName(
                self, self.tr("Save file"), "./")[0]
            if self.save_file:
                self.outputFileMulti.setContent(self.save_file)
            else:
                self.warningMessage("No save file selected")
        except Exception as e:
            self.errorMessage(f"{e}")

    def __onMultiFilter(self):
        """ multi filter """
        try:
            self.stateTooltip = StateToolTip(
                self.tr('multi filter'), self.tr('Please wait patiently'), self.window())
            self.stateTooltip.move(self.stateTooltip.getSuitablePos())
            self.stateTooltip.show()
            self.thread_filter_data_multi = filter_data.FilterMultiDataThread(
                file_path=self.fileMulti,
                targets=self.targetMulti,
                column_value=self.col_value_multi,
                file_out=self.save_file)
            self.thread_filter_data_multi.signal_info.connect(self.infoMessage)
            self.thread_filter_data_multi.signal_warning.connect(self.warningMessage)
            self.thread_filter_data_multi.signal_error.connect(self.errorMessage)
            self.thread_filter_data_multi.signal_done.connect(self.__onProgress)
            self.thread_filter_data_multi.moveToThread(self.thread_filter_data_multi)
            self.thread_filter_data_multi.start()
        except Exception as e:
            self.stateTooltip.hide()
            self.errorMessage(f"{e}")

    def __pycrabOpenFile(self):
        self.pycrabFile = QFileDialog.getOpenFileName(
            self, self.tr("Open file"), "*.csv;*.txt;*.tsv;")[0]
        if self.pycrabFile:
            self.pycrabOpenFile.setContent(self.pycrabFile)
        else:
            self.warningMessage("No file opened")

    def __pycrabSaveFile(self):
        """ select save file"""
        try:
            self.pycrab_save = QFileDialog.getSaveFileName(
                self, self.tr("Save file"), "./")[0]
            if self.pycrab_save:
                self.pycrabOutputFolder.setContent(self.pycrab_save)
            else:
                self.warningMessage("No save file selected")
        except Exception as e:
            self.errorMessage(f"{e}")

    def __pycrabFilterROW(self):
        """ single filter """
        try:
            self.stateTooltip = StateToolTip(
                self.tr('single filter > 10GB'), self.tr('Please wait patiently'), self.window())
            self.stateTooltip.move(self.stateTooltip.getSuitablePos())
            self.stateTooltip.show()
            self.thread_pycrab_filter_row = filter_data.PycrabFilterRow(
                file_path=self.pycrabFile,
                output_path=self.pycrab_save,
                column=self.pycrab_col_value,
                targets=self.pycrab_target)
            self.thread_pycrab_filter_row.signal_info.connect(self.infoMessage)
            self.thread_pycrab_filter_row.signal_warning.connect(self.warningMessage)
            self.thread_pycrab_filter_row.signal_error.connect(self.errorMessage)
            self.thread_pycrab_filter_row.signal_done.connect(self.__onProgress)
            self.thread_pycrab_filter_row.moveToThread(self.thread_pycrab_filter_row)
            self.thread_pycrab_filter_row.start()
        except Exception as e:
            self.stateTooltip.hide()
            self.errorMessage(f"{e}")

    def __connectSignalToSlot(self):
        """ connect signal to slot """
        cfg.themeChanged.connect(setTheme)

        # single filter
        self.openFile.clicked.connect(self.__onOpenFile)
        self.targets.clicked.connect(self.__onSelectTarget)
        self.outputFolder.clicked.connect(self.__onSelectSavePath)
        self.singleFilterButton.clicked.connect(self.__onSingleFilter)

        # multi filter
        self.openFileMulti.clicked.connect(self.__onOpenFileMulti)
        self.targetsMulti.clicked.connect(self.__onSelectTargetMulti)
        self.outputFileMulti.clicked.connect(self.__onSelectSaveFile)
        self.multiFilterButton.clicked.connect(self.__onMultiFilter)

        # pycrab single filter
        self.pycrabOpenFile.clicked.connect(self.__pycrabOpenFile)
        self.pycrabOutputFolder.clicked.connect(self.__pycrabSaveFile)
        self.pycrabFilterRowButton.clicked.connect(self.__pycrabFilterROW)

    def __onProgress(self):
        if self.stateTooltip:
            self.stateTooltip.setContent(
                self.tr('End of program operation!') + ' √')
            self.stateTooltip.setState(True)
            self.stateTooltip = False

    def __realtimeUpdateValue(self):
        # real time update of lineEdit values
        try:
            self.col_value = self.columns.text()
            self.col_value_multi = self.columnsMulti.text()
            self.pycrab_col_value = self.pycrabColumn.text()
            self.pycrab_target = self.pycrabTarget.text()
        except Exception as e:
            self.warningMessage(f"{e}")

    def infoMessage(self, text):
        InfoBar.success(
            title=self.tr('Info'),
            content=self.tr(text),
            orient=Qt.Horizontal,
            isClosable=True,
            position=InfoBarPosition.TOP,
            duration=4000,
            parent=self
        )

    def warningMessage(self, text):
        InfoBar.info(
            title=self.tr('Warning'),
            content=self.tr(text),
            orient=Qt.Horizontal,
            isClosable=True,
            position=InfoBarPosition.TOP,
            duration=5000,
            parent=self
        )

    def errorMessage(self, text):
        InfoBar.error(
            title=self.tr('Error'),
            content=self.tr(text),
            orient=Qt.Horizontal,
            isClosable=True,
            position=InfoBarPosition.BOTTOM,
            duration=10_000,
            parent=self
        )
