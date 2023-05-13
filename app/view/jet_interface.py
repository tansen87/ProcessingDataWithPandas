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
from ..utils import jet


class JETInterface(ScrollArea):
    """ jet interface """

    downloadFolderChanged = pyqtSignal(str)

    def __init__(self, parent=None):
        super().__init__(parent=parent)
        self.scrollWidget = QWidget()
        self.expandLayout = ExpandLayout(self.scrollWidget)

        # setting label
        self.jetLabel = QLabel(self.tr("JET"), self)

        # create jet gl template
        self.jetGroup = SettingCardGroup(self.tr("..."), self.scrollWidget)
        self.openFile = PushSettingCard(
            self.tr('open csv'),
            FIF.SEARCH,
            self.tr("select a file with csv"),
            cfg.get(cfg.downloadFolder),
            self.jetGroup
        )
        self.yamlFile = PushSettingCard(
            self.tr('open yaml'),
            FIF.SEARCH,
            self.tr("select a file with yaml"),
            cfg.get(cfg.downloadFolder),
            self.jetGroup
        )
        self.saveFile = PushSettingCard(
            self.tr('save path'),
            FIF.SAVE,
            self.tr("select file save path"),
            cfg.get(cfg.downloadFolder),
            self.jetGroup
        )
        self.startButton = PushSettingCard(
            self.tr('start'),
            FIF.RETURN,
            self.tr('click me to start running'),
            self.tr(''),
            self.jetGroup
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
        self.jetLabel.setObjectName('settingLabel')
        StyleSheet.SETTING_INTERFACE.apply(self)

        # initialize layout
        self.__initLayout()
        self.__connectSignalToSlot()

    def __initLayout(self):
        self.jetLabel.move(36, 30)

        # add jet to group
        self.jetGroup.addSettingCard(self.openFile)
        self.jetGroup.addSettingCard(self.yamlFile)
        self.jetGroup.addSettingCard(self.saveFile)
        self.jetGroup.addSettingCard(self.startButton)

        # add jet group to layout
        self.expandLayout.setSpacing(28)
        self.expandLayout.setContentsMargins(36, 10, 36, 0)
        self.expandLayout.addWidget(self.jetGroup)

    def __onOpenTextFile(self):
        """ open csv file """
        self.file = QFileDialog.getOpenFileName(
            self, self.tr("Open file"), "*.csv;*.txt;*.tsv;")[0]
        if self.file:
            self.openFile.setContent(self.file)
        else:
            self.warningMessage("No file opened")

    def __onOpenYamlFile(self):
        """ open yaml file """
        self.yaml_file = QFileDialog.getOpenFileName(
            self, self.tr("Open file"), "*.yaml")[0]
        if self.yaml_file:
            self.yamlFile.setContent(self.yaml_file)
        else:
            self.warningMessage("No file opened")

    def __onSaveFile(self):
        """ select save file"""
        try:
            self.save_file = QFileDialog.getSaveFileName(
                self, self.tr("Save file"), "./")[0]
            if self.save_file:
                self.saveFile.setContent(self.save_file)
            else:
                self.warningMessage("No save file selected")
        except Exception as e:
            self.errorMessage(f"{e}")

    def __onRun(self):
        """ create jet template """
        try:
            self.stateTooltip = StateToolTip(
                self.tr('JET'), self.tr('Please wait patiently'), self.window())
            self.stateTooltip.move(self.stateTooltip.getSuitablePos())
            self.stateTooltip.show()
            self.thread_jet = jet.JournalsTemplate(
                yaml_path=self.yaml_file,
                file_path=self.file,
                output_path=self.save_file)
            self.thread_jet.signal_info.connect(self.infoMessage)
            self.thread_jet.signal_warning.connect(self.warningMessage)
            self.thread_jet.signal_error.connect(self.errorMessage)
            self.thread_jet.signal_done.connect(self.__onProgress)
            self.thread_jet.moveToThread(self.thread_jet)
            self.thread_jet.start()
        except Exception as e:
            self.stateTooltip.hide()
            self.errorMessage(f"{e}")

    def __connectSignalToSlot(self):
        """ connect signal to slot """
        cfg.themeChanged.connect(setTheme)

        # jet
        self.openFile.clicked.connect(self.__onOpenTextFile)
        self.yamlFile.clicked.connect(self.__onOpenYamlFile)
        self.saveFile.clicked.connect(self.__onSaveFile)
        self.startButton.clicked.connect(self.__onRun)

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
