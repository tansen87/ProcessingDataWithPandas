# coding:utf-8
from PyQt5.QtCore import Qt, QRectF
from PyQt5.QtGui import QPixmap, QPainter, QColor, QBrush, QPainterPath
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLabel

from qfluentwidgets import ScrollArea, isDarkTheme, FluentIcon
from ..common.config import cfg, HELP_URL, REPO_URL, EXAMPLE_URL, FEEDBACK_URL
from ..common.icon import Icon, FluentIconBase
from ..components.link_card import LinkCardView
from ..components.sample_card import SampleCardView
from ..common.style_sheet import StyleSheet


class BannerWidget(QWidget):
    """ Banner widget """

    def __init__(self, parent=None):
        super().__init__(parent=parent)
        self.setFixedHeight(336)
        self.vBoxLayout = QVBoxLayout(self)
        self.galleryLabel = QLabel('Processing Data With Pandas', self)
        self.banner = QPixmap(':/gallery/images/header1.png')
        self.linkCardView = LinkCardView(self)

        self.galleryLabel.setObjectName('galleryLabel')

        self.vBoxLayout.setSpacing(0)
        self.vBoxLayout.setContentsMargins(0, 20, 0, 0)
        self.vBoxLayout.addWidget(self.galleryLabel)
        self.vBoxLayout.addWidget(self.linkCardView, 1, Qt.AlignBottom)
        self.vBoxLayout.setAlignment(Qt.AlignLeft | Qt.AlignTop)

        self.linkCardView.addCard(
            ':/gallery/images/logo.png',
            self.tr('README'),
            self.tr('Click on me to view the document'),
            HELP_URL
        )

        self.linkCardView.addCard(
            FluentIcon.GITHUB,
            self.tr('Github'),
            self.tr(
                'Click on me to view the source code'),
            REPO_URL
        )

        self.linkCardView.addCard(
            FluentIcon.CODE,
            self.tr('Contact me'),
            self.tr('tansen87@qq.com'),
            None
        )

        self.linkCardView.addCard(
            FluentIcon.FEEDBACK,
            self.tr('Feedback'),
            self.tr('Click on me to submit an issue'),
            FEEDBACK_URL
        )

    def paintEvent(self, e):
        super().paintEvent(e)
        painter = QPainter(self)
        painter.setRenderHints(
            QPainter.SmoothPixmapTransform | QPainter.Antialiasing)
        painter.setPen(Qt.NoPen)

        path = QPainterPath()
        path.setFillRule(Qt.WindingFill)
        w, h = self.width(), 200
        path.addRoundedRect(QRectF(0, 0, w, h), 10, 10)
        path.addRect(QRectF(0, h-50, 50, 50))
        path.addRect(QRectF(w-50, 0, 50, 50))
        path.addRect(QRectF(w-50, h-50, 50, 50))
        path = path.simplified()

        # draw background color
        if not isDarkTheme():
            painter.fillPath(path, QColor(206, 216, 228))
        else:
            painter.fillPath(path, QColor(0, 0, 0))

        # draw banner image
        pixmap = self.banner.scaled(
            self.size(), transformMode=Qt.SmoothTransformation)
        path.addRect(QRectF(0, h, w, self.height() - h))
        painter.fillPath(path, QBrush(pixmap))


class HomeInterface(ScrollArea):
    """ Home interface """

    def __init__(self, parent=None):
        super().__init__(parent=parent)
        self.banner = BannerWidget(self)
        self.view = QWidget(self)
        self.vBoxLayout = QVBoxLayout(self.view)

        self.__initWidget()
        self.loadSamples()

    def __initWidget(self):
        self.view.setObjectName('view')
        StyleSheet.HOME_INTERFACE.apply(self)

        self.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.setWidget(self.view)
        self.setWidgetResizable(True)

        self.vBoxLayout.setContentsMargins(0, 0, 0, 36)
        self.vBoxLayout.setSpacing(40)
        self.vBoxLayout.addWidget(self.banner)
        self.vBoxLayout.setAlignment(Qt.AlignTop)

    def loadSamples(self):
        """ load samples """
        # data filter
        dataFilterView = SampleCardView(
            self.tr("Data Filter"), self.view)
        dataFilterView.addSampleCard(
            icon=":/gallery/images/controls/Checkbox.png",
            title="single filter",
            content=self.tr(
                "Query qualified data and write it to a csv or Excel file"),
            routeKey="basicInputInterface",
            index=0
        )
        dataFilterView.addSampleCard(
            icon=":/gallery/images/controls/Checkbox.png",
            title="multi filter",
            content=self.tr(
                "Write data that meets multiple criteria to a csv file"),
            routeKey="basicInputInterface",
            index=1
        )
        dataFilterView.addSampleCard(
            icon=":/gallery/images/controls/Checkbox.png",
            title="single filter >10GB",
            content=self.tr(
                "A fast csv file query written in Rust"),
            routeKey="basicInputInterface",
            index=2
        )
        self.vBoxLayout.addWidget(dataFilterView)

        # data merge
        dataMergeView = SampleCardView(self.tr('Data Merge'), self.view)
        dataMergeView.addSampleCard(
            icon=":/gallery/images/controls/Acrylic.png",
            title="Excel merge",
            content=self.tr(
                "Merge Excel files within the same folder"),
            routeKey="dateTimeInterface",
            index=0
        )
        dataMergeView.addSampleCard(
            icon=":/gallery/images/controls/Acrylic.png",
            title="csv merge",
            content=self.tr(
                "Merge csv files within the same folder"),
            routeKey="dateTimeInterface",
            index=1
        )
        dataMergeView.addSampleCard(
            icon=":/gallery/images/controls/Acrylic.png",
            title="csv merge > 10GB",
            content=self.tr(
                "Merge csv files within the same folder, written in Rust"),
            routeKey="dateTimeInterface",
            index=2
        )
        self.vBoxLayout.addWidget(dataMergeView)

        # data pivot
        dataPivotView = SampleCardView(self.tr('Data Pivot'), self.view)
        dataPivotView.addSampleCard(
            icon=":/gallery/images/controls/DataGrid.png",
            title="data pivot",
            content=self.tr("Just fill in the index and values"),
            routeKey="dialogInterface",
            index=0
        )
        self.vBoxLayout.addWidget(dataPivotView)

        # data split
        dataSplitView = SampleCardView(self.tr('Data Split'), self.view)
        dataSplitView.addSampleCard(
            icon=":/gallery/images/controls/Grid.png",
            title="csv2xlsx",
            content=self.tr(
                "Split the CSV file into n Excel files"),
            routeKey="layoutInterface",
            index=0
        )
        self.vBoxLayout.addWidget(dataSplitView)

        # jet
        materialView = SampleCardView(self.tr('JET'), self.view)
        materialView.addSampleCard(
            icon=":/gallery/images/controls/ProgressRing.png",
            title="jet",
            content=self.tr(
                "Just fill out the yaml file to generate the jet template"),
            routeKey="materialInterface",
            index=0
        )
        self.vBoxLayout.addWidget(materialView)
