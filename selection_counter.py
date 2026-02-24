from qgis.PyQt.QtWidgets import QAction
from qgis.PyQt.QtGui import QIcon
import os

class SelectionCounterPlugin:
    def __init__(self, iface):
        self.iface = iface
        self.panel = None
        self.action = None

    def initGui(self):
        icon_path = os.path.join(os.path.dirname(__file__), 'icon.png')
        self.action = QAction(QIcon(icon_path), 'Selection Counter', self.iface.mainWindow())
        self.action.setCheckable(True)
        self.action.triggered.connect(self.toggle_panel)
        self.iface.addToolBarIcon(self.action)
        self.iface.addPluginToVectorMenu('Selection Counter', self.action)

        from .selection_counter_panel import SelectionCounterPanel
        self.panel = SelectionCounterPanel(self.iface)
        self.iface.addDockWidget(self.panel.dock_area(), self.panel)
        self.panel.hide()

    def toggle_panel(self, checked):
        if self.panel:
            self.panel.setVisible(checked)

    def unload(self):
        if self.panel:
            self.iface.removeDockWidget(self.panel)
            self.panel.cleanup()
            self.panel = None
        self.iface.removeToolBarIcon(self.action)
        self.iface.removePluginVectorMenu('Selection Counter', self.action)
        self.action = None
