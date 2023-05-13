# coding:utf-8
from enum import Enum
from typing import Dict, Union

from PyQt5.QtCore import Qt, QPropertyAnimation, QRect, QSize, QEvent, QEasingCurve, pyqtSignal, QObject
from PyQt5.QtGui import QResizeEvent, QIcon
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QFrame, QApplication

from .navigation_widget import NavigationPushButton, NavigationToolButton, NavigationWidget, NavigationSeparator
from ..widgets.scroll_area import SingleDirectionScrollArea
from ..widgets.tool_tip import ToolTipFilter
from ...common.style_sheet import FluentStyleSheet
from ...common.icon import FluentIconBase
from ...common.icon import FluentIcon as FIF


class NavigationDisplayMode(Enum):
    """ Navigation display mode """
    MINIMAL = 0
    COMPACT = 1
    EXPAND = 2
    MENU = 3


class NavigationItemPosition(Enum):
    """ Navigation item position """
    TOP = 0
    SCROLL = 1
    BOTTOM = 2


class NavigationToolTipFilter(ToolTipFilter):
    """ Navigation tool tip filter """

    def _canShowToolTip(self) -> bool:
        isVisible = super()._canShowToolTip()
        parent = self.parent()  # type: NavigationWidget
        return isVisible and parent.isCompacted


class NavigationPanel(QFrame):
    """ Navigation panel """

    displayModeChanged = pyqtSignal(NavigationDisplayMode)

    def __init__(self, parent=None, isMinimalEnabled=False):
        super().__init__(parent=parent)
        self._parent = parent   # type: QWidget
        self._isMenuButtonVisible = True
        self._isReturnButtonVisible = False

        self.scrollArea = SingleDirectionScrollArea(self)
        self.scrollWidget = QWidget()

        self.menuButton = NavigationToolButton(FIF.MENU, self)
        self.returnButton = NavigationToolButton(FIF.RETURN, self)

        self.vBoxLayout = NavigationItemLayout(self)
        self.topLayout = NavigationItemLayout()
        self.bottomLayout = NavigationItemLayout()
        self.scrollLayout = NavigationItemLayout(self.scrollWidget)

        self.items = {}   # type: Dict[str, NavigationWidget]
        self.history = NavigationHistory(self.items)

        self.expandAni = QPropertyAnimation(self, b'geometry', self)
        self.expandWidth = 322

        self.isMinimalEnabled = isMinimalEnabled
        if isMinimalEnabled:
            self.displayMode = NavigationDisplayMode.MINIMAL
        else:
            self.displayMode = NavigationDisplayMode.COMPACT

        self.__initWidget()

    def __initWidget(self):
        self.resize(48, self.height())
        self.setAttribute(Qt.WA_StyledBackground)
        self.window().installEventFilter(self)

        self.returnButton.hide()
        self.returnButton.setDisabled(True)

        self.scrollArea.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.scrollArea.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.scrollArea.setWidget(self.scrollWidget)
        self.scrollArea.setWidgetResizable(True)

        self.expandAni.setEasingCurve(QEasingCurve.OutQuad)
        self.expandAni.setDuration(150)

        self.menuButton.clicked.connect(self.toggle)
        self.expandAni.finished.connect(self._onExpandAniFinished)
        self.history.emptyChanged.connect(self.returnButton.setDisabled)
        self.returnButton.clicked.connect(self.history.pop)

        # add tool tip
        self.returnButton.installEventFilter(ToolTipFilter(self.returnButton, 1000))
        self.returnButton.setToolTip(self.tr('Back'))

        self.menuButton.installEventFilter(ToolTipFilter(self.menuButton, 1000))
        self.menuButton.setToolTip(self.tr('Open Navigation'))

        self.setProperty('menu', False)
        self.scrollWidget.setObjectName('scrollWidget')
        FluentStyleSheet.NAVIGATION_INTERFACE.apply(self)
        self.__initLayout()

    def __initLayout(self):
        self.vBoxLayout.setContentsMargins(0, 5, 0, 5)
        self.topLayout.setContentsMargins(4, 0, 4, 0)
        self.bottomLayout.setContentsMargins(4, 0, 4, 0)
        self.scrollLayout.setContentsMargins(4, 0, 4, 0)
        self.vBoxLayout.setSpacing(4)
        self.topLayout.setSpacing(4)
        self.bottomLayout.setSpacing(4)
        self.scrollLayout.setSpacing(4)

        self.vBoxLayout.addLayout(self.topLayout, 0)
        self.vBoxLayout.addWidget(self.scrollArea, 1, Qt.AlignTop)
        self.vBoxLayout.addLayout(self.bottomLayout, 0)

        self.vBoxLayout.setAlignment(Qt.AlignTop)
        self.topLayout.setAlignment(Qt.AlignTop)
        self.scrollLayout.setAlignment(Qt.AlignTop)
        self.bottomLayout.setAlignment(Qt.AlignBottom)

        self.topLayout.addWidget(self.returnButton, 0, Qt.AlignTop)
        self.topLayout.addWidget(self.menuButton, 0, Qt.AlignTop)

    def addItem(self, routeKey: str, icon: Union[str, QIcon, FluentIconBase], text: str, onClick, selectable=True,
                position=NavigationItemPosition.TOP, tooltip: str = None):
        """ add navigation item

        Parameters
        ----------
        routeKey: str
            the unique name of item

        icon: str | QIcon | FluentIconBase
            the icon of navigation item

        text: str
            the text of navigation item

        onClick: callable
            the slot connected to item clicked signal

        position: NavigationItemPosition
            where the button is added

        selectable: bool
            whether the item is selectable

        tooltip: str
            the tooltip of item
        """
        if routeKey in self.items:
            return

        button = NavigationPushButton(icon, text, selectable, self)
        self.addWidget(routeKey, button, onClick, position, tooltip)

        return button

    def addWidget(self, routeKey: str, widget: NavigationWidget, onClick, position=NavigationItemPosition.TOP,
                  tooltip: str = None):
        """ add custom widget

        Parameters
        ----------
        routeKey: str
            the unique name of item

        widget: NavigationWidget
            the custom widget to be added

        onClick: callable
            the slot connected to item clicked signal

        position: NavigationItemPosition
            where the button is added

        tooltip: str
            the tooltip of widget
        """
        if routeKey in self.items:
            return

        widget.clicked.connect(self._onWidgetClicked)
        widget.clicked.connect(onClick)
        widget.setProperty('routeKey', routeKey)
        self.items[routeKey] = widget

        if self.displayMode in [NavigationDisplayMode.EXPAND, NavigationDisplayMode.MENU]:
            widget.setCompacted(False)

        if tooltip:
            widget.setToolTip(tooltip)
            widget.installEventFilter(NavigationToolTipFilter(widget, 1000))

        self._addWidgetToLayout(widget, position)

    def addSeparator(self, position=NavigationItemPosition.TOP):
        """ add separator

        Parameters
        ----------
        position: NavigationPostion
            where to add the separator
        """
        separator = NavigationSeparator(self)
        self._addWidgetToLayout(separator, position)

    def _addWidgetToLayout(self, widget: NavigationWidget, position: NavigationItemPosition):
        """ add widget to layout """
        if position == NavigationItemPosition.TOP:
            widget.setParent(self)
            self.topLayout.addWidget(widget, 0, Qt.AlignTop)
        elif position == NavigationItemPosition.SCROLL:
            widget.setParent(self.scrollWidget)
            self.scrollLayout.addWidget(widget, 0, Qt.AlignTop)
        else:
            widget.setParent(self)
            self.bottomLayout.addWidget(widget, 0, Qt.AlignBottom)

        widget.show()

    def removeWidget(self, routeKey: str):
        """ remove widget

        Parameters
        ----------
        routeKey: str
            the unique name of item
        """
        if routeKey not in self.items:
            return

        w = self.items.pop(routeKey)
        w.deleteLater()
        self.history.remove(routeKey, True)

    def setMenuButtonVisible(self, isVisible: bool):
        """ set whether the menu button is visible """
        self._isMenuButtonVisible = isVisible
        self.menuButton.setVisible(isVisible)

    def setReturnButtonVisible(self, isVisible: bool):
        """ set whether the return button is visible """
        self._isReturnButtonVisible = isVisible
        self.returnButton.setVisible(isVisible)

    def setExpandWidth(self, width: int):
        """ set the maximum width """
        if width <= 42:
            return

        self.expandWidth = width
        NavigationWidget.EXPAND_WIDTH = width - 10

    def expand(self):
        """ expand navigation panel """
        self._setWidgetCompacted(False)
        self.expandAni.setProperty('expand', True)
        self.menuButton.setToolTip(self.tr('Close Navigation'))

        # determine the display mode according to the width of window
        # https://learn.microsoft.com/en-us/windows/apps/design/controls/navigationview#default
        expandWidth = 1007 + self.expandWidth - 322
        if self.window().width() > expandWidth and not self.isMinimalEnabled:
            self.displayMode = NavigationDisplayMode.EXPAND
        else:
            self.setProperty('menu', True)
            self.setStyle(QApplication.style())
            self.displayMode = NavigationDisplayMode.MENU
            if not self._parent.isWindow():
                pos = self.parent().pos()
                self.setParent(self.window())
                self.move(pos)

            self.show()

        self.displayModeChanged.emit(self.displayMode)
        self.expandAni.setStartValue(
            QRect(self.pos(), QSize(48, self.height())))
        self.expandAni.setEndValue(
            QRect(self.pos(), QSize(self.expandWidth, self.height())))
        self.expandAni.start()

    def collapse(self):
        """ collapse navigation panel """
        if self.expandAni.state() == QPropertyAnimation.Running:
            return

        self.expandAni.setStartValue(
            QRect(self.pos(), QSize(self.width(), self.height())))
        self.expandAni.setEndValue(
            QRect(self.pos(), QSize(48, self.height())))
        self.expandAni.setProperty('expand', False)
        self.expandAni.start()

        self.menuButton.setToolTip(self.tr('Open Navigation'))

    def toggle(self):
        """ toggle navigation panel """
        if self.displayMode in [NavigationDisplayMode.COMPACT, NavigationDisplayMode.MINIMAL]:
            self.expand()
        else:
            self.collapse()

    def setCurrentItem(self, routeKey: str):
        """ set current selected item

        Parameters
        ----------
        routeKey: str
            the unique name of item
        """
        if routeKey not in self.items:
            return

        self.history.push(routeKey)
        for k, item in self.items.items():
            item.setSelected(k == routeKey)

    def _onWidgetClicked(self):
        widget = self.sender()  # type: NavigationWidget
        if not widget.isSelectable:
            return

        self.setCurrentItem(widget.property('routeKey'))
        if widget is not self.menuButton and self.displayMode == NavigationDisplayMode.MENU:
            self.collapse()

    def resizeEvent(self, e: QResizeEvent):
        if e.oldSize().height() == self.height():
            return

        th = self.topLayout.minimumSize().height()
        bh = self.bottomLayout.minimumSize().height()
        h = self.height()-th-bh-20
        self.scrollArea.setFixedHeight(max(h, 36))

    def eventFilter(self, obj, e: QEvent):
        if obj is not self.window():
            return super().eventFilter(obj, e)

        if e.type() == QEvent.MouseButtonRelease:
            if not self.geometry().contains(e.pos()) and self.displayMode == NavigationDisplayMode.MENU:
                self.collapse()
        elif e.type() == QEvent.Resize:
            w = QResizeEvent(e).size().width()
            if w < 1008 and self.displayMode == NavigationDisplayMode.EXPAND:
                self.collapse()
            elif w >= 1008 and self.displayMode == NavigationDisplayMode.COMPACT and \
                    not self._isMenuButtonVisible:
                self.expand()

        return super().eventFilter(obj, e)

    def _onExpandAniFinished(self):
        if not self.expandAni.property('expand'):
            if self.isMinimalEnabled:
                self.displayMode = NavigationDisplayMode.MINIMAL
            else:
                self.displayMode = NavigationDisplayMode.COMPACT

            self.displayModeChanged.emit(self.displayMode)

        if self.displayMode == NavigationDisplayMode.MINIMAL:
            self.hide()
            self.setProperty('menu', False)
            self.setStyle(QApplication.style())
        elif self.displayMode == NavigationDisplayMode.COMPACT:
            self.setProperty('menu', False)
            self.setStyle(QApplication.style())

            for item in self.items.values():
                item.setCompacted(True)

            if not self._parent.isWindow():
                self.setParent(self._parent)
                self.move(0, 0)
                self.show()

    def _setWidgetCompacted(self, isCompacted: bool):
        """ set whether the navigation widget is compacted """
        for item in self.findChildren(NavigationWidget):
            item.setCompacted(isCompacted)

    def layoutMinHeight(self):
        th = self.topLayout.minimumSize().height()
        bh = self.bottomLayout.minimumSize().height()
        sh = sum(w.height() for w in self.findChildren(NavigationSeparator))
        spacing = self.topLayout.count() * self.topLayout.spacing()
        spacing += self.bottomLayout.count() * self.bottomLayout.spacing()
        return 36 + th + bh + sh + spacing

    def setDefaultRouteKey(self, key: str):
        """ set the routing key to use when the navigation history is empty """
        self.history.defaultRouteKey = key


class NavigationItemLayout(QVBoxLayout):
    """ Navigation layout """

    def setGeometry(self, rect: QRect):
        super().setGeometry(rect)
        for i in range(self.count()):
            item = self.itemAt(i)
            if isinstance(item.widget(), NavigationSeparator):
                geo = item.geometry()
                item.widget().setGeometry(0, geo.y(), geo.width(), geo.height())


class NavigationHistory(QObject):
    """ Navigation history """

    emptyChanged = pyqtSignal(bool)

    def __init__(self, items: Dict[str, NavigationWidget]):
        super().__init__()
        self.items = items
        self.history = []
        self._defaultRouteKey = None

    @property
    def defaultRouteKey(self):
        return self._defaultRouteKey

    @defaultRouteKey.setter
    def defaultRouteKey(self, key):
        if key not in self.items:
            raise ValueError(
                f'The route key `{key}` has not been registered yet.')

        self._defaultRouteKey = key

    def push(self, routeKey: str):
        """ push history """
        if not self.history and self.defaultRouteKey != routeKey:
            self.history.append(routeKey)
            self.emptyChanged.emit(False)
        elif self.history and self.history[-1] != routeKey:
            self.history.append(routeKey)

    def pop(self):
        """ pop history """
        if not self.history:
            return

        self.history.pop()
        self._navigate()

    def remove(self, routeKey: str, all=False):
        """ remove history """
        if routeKey not in self.history:
            return

        if all:
            self.history = [i for i in self.history if i != routeKey]
        else:
            for i in range(len(self.history)-1, -1, -1):
                if self.history[i] == routeKey:
                    self.history.pop(i)
                    break

        self._navigate()

    def _navigate(self):
        if self.history:
            self.items[self.history[-1]].clicked.emit(False)
        else:
            if self.defaultRouteKey is not None:
                self.items[self.defaultRouteKey].clicked.emit(False)

            self.emptyChanged.emit(True)