# coding:utf-8
from typing import Union

from PyQt5.QtCore import Qt, QEvent, pyqtSignal
from PyQt5.QtGui import QResizeEvent, QIcon
from PyQt5.QtWidgets import QWidget

from .navigation_panel import NavigationPanel, NavigationItemPosition, NavigationWidget, NavigationDisplayMode
from .navigation_widget import NavigationPushButton
from ...common.style_sheet import FluentStyleSheet
from ...common.icon import FluentIconBase


class NavigationInterface(QWidget):
    """ Navigation interface """

    displayModeChanged = pyqtSignal(NavigationDisplayMode)

    def __init__(self, parent=None, showMenuButton=True, showReturnButton=False):
        """
        Parameters
        ----------
        parent: widget
            parent widget

        showMenuButton: bool
            whether to show menu button

        showReturnButton: bool
            whether to show return button
        """
        super().__init__(parent=parent)
        self.panel = NavigationPanel(self)
        self.panel.setMenuButtonVisible(showMenuButton)
        self.panel.setReturnButtonVisible(showReturnButton)
        self.panel.installEventFilter(self)
        self.panel.displayModeChanged.connect(self.displayModeChanged)

        self.resize(48, self.height())
        self.setMinimumWidth(48)
        self.setAttribute(Qt.WA_StyledBackground)
        FluentStyleSheet.NAVIGATION_INTERFACE.apply(self)

    def addItem(self, routeKey: str, icon: Union[str, QIcon, FluentIconBase], text: str, onClick, selectable=True,
                position=NavigationItemPosition.TOP, tooltip: str = None) -> NavigationPushButton:
        """ add navigation item

        Parameters
        ----------
        routKey: str
            the unique name of item

        icon: str | QIcon | FluentIconBase
            the icon of navigation item

        text: str
            the text of navigation item

        onClick: callable
            the slot connected to item clicked signal

        selectable: bool
            whether the item is selectable

        position: NavigationItemPosition
            where the button is added

        tooltip: str
            the tooltip of item
        """
        button = self.panel.addItem(routeKey, icon, text, onClick, selectable, position, tooltip)
        self.setMinimumHeight(self.panel.layoutMinHeight())
        return button

    def addWidget(self, routeKey: str, widget: NavigationWidget, onClick, position=NavigationItemPosition.TOP,
                  tooltip: str = None):
        """ add custom widget

        Parameters
        ----------
        routKey: str
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
        self.panel.addWidget(routeKey, widget, onClick, position, tooltip)
        self.setMinimumHeight(self.panel.layoutMinHeight())

    def addSeparator(self, position=NavigationItemPosition.TOP):
        """ add separator

        Parameters
        ----------
        position: NavigationPostion
            where to add the separator
        """
        self.panel.addSeparator(position)
        self.setMinimumHeight(self.panel.layoutMinHeight())

    def removeWidget(self, routeKey: str):
        """ remove widget

        Parameters
        ----------
        routKey: str
            the unique name of item
        """
        self.panel.removeWidget(routeKey)

    def setCurrentItem(self, name: str):
        """ set current selected item

        Parameters
        ----------
        name: str
            the unique name of item
        """
        self.panel.setCurrentItem(name)

    def setDefaultRouteKey(self, key: str):
        """ set the routing key to use when the navigation history is empty """
        self.panel.setDefaultRouteKey(key)

    def setExpandWidth(self, width: int):
        """ set the maximum width """
        self.panel.setExpandWidth(width)

    def eventFilter(self, obj, e: QEvent):
        if obj is not self.panel or e.type() != QEvent.Resize:
            return super().eventFilter(obj, e)

        if self.panel.displayMode != NavigationDisplayMode.MENU:
            event = QResizeEvent(e)
            if event.oldSize().width() != event.size().width():
                self.setFixedWidth(event.size().width())

        return super().eventFilter(obj, e)

    def resizeEvent(self, e: QResizeEvent):
        if e.oldSize().height() != self.height():
            self.panel.setFixedHeight(self.height())
