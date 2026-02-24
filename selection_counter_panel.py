from collections import Counter

from qgis.PyQt.QtWidgets import (
    QDockWidget, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QComboBox, QTableWidget, QTableWidgetItem,
    QHeaderView, QPushButton, QSizePolicy
)
from qgis.PyQt.QtCore import Qt, QSize
from qgis.PyQt.QtGui import QColor, QFont
from qgis.core import QgsProject, QgsMapLayer


class SelectionCounterPanel(QDockWidget):
    def __init__(self, iface):
        super().__init__('Selection Counter')
        self.iface = iface
        self._current_layer = None
        self._setup_ui()
        self._connect_project_signals()
        self._populate_layers()

    # ------------------------------------------------------------------ #
    #  Dock configuration                                                  #
    # ------------------------------------------------------------------ #
    def dock_area(self):
        return Qt.RightDockWidgetArea

    # ------------------------------------------------------------------ #
    #  UI setup                                                            #
    # ------------------------------------------------------------------ #
    def _setup_ui(self):
        container = QWidget()
        main_layout = QVBoxLayout(container)
        main_layout.setContentsMargins(10, 10, 10, 10)
        main_layout.setSpacing(8)

        # ---------- title ----------
        title = QLabel('Selection Counter')
        title_font = QFont()
        title_font.setBold(True)
        title_font.setPointSize(11)
        title.setFont(title_font)
        main_layout.addWidget(title)

        # ---------- layer dropdown ----------
        lbl_layer = QLabel('Camada:')
        main_layout.addWidget(lbl_layer)

        self.combo_layer = QComboBox()
        self.combo_layer.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        self.combo_layer.currentIndexChanged.connect(self._on_layer_changed)
        main_layout.addWidget(self.combo_layer)

        # ---------- field dropdown ----------
        lbl_field = QLabel('Campo:')
        main_layout.addWidget(lbl_field)

        self.combo_field = QComboBox()
        self.combo_field.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        self.combo_field.currentIndexChanged.connect(self._refresh_table)
        main_layout.addWidget(self.combo_field)

        # ---------- summary label ----------
        self.lbl_summary = QLabel('Nenhuma feição selecionada.')
        self.lbl_summary.setStyleSheet('color: #555555; font-style: italic;')
        main_layout.addWidget(self.lbl_summary)

        # ---------- table ----------
        self.table = QTableWidget(0, 2)
        self.table.setHorizontalHeaderLabels(['Valor', 'Qtd. selecionada'])
        self.table.horizontalHeader().setSectionResizeMode(0, QHeaderView.Stretch)
        self.table.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeToContents)
        self.table.verticalHeader().setVisible(False)
        self.table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.table.setSelectionMode(QTableWidget.NoSelection)
        self.table.setAlternatingRowColors(True)
        main_layout.addWidget(self.table)

        # ---------- refresh button ----------
        self.btn_refresh = QPushButton('↺  Atualizar')
        self.btn_refresh.clicked.connect(self._refresh_table)
        main_layout.addWidget(self.btn_refresh)

        self.setWidget(container)
        self.setMinimumWidth(260)

    # ------------------------------------------------------------------ #
    #  Layer / field population                                            #
    # ------------------------------------------------------------------ #
    def _populate_layers(self):
        self.combo_layer.blockSignals(True)
        self.combo_layer.clear()
        self.combo_layer.addItem('-- Selecione uma camada --', None)

        for layer in QgsProject.instance().mapLayers().values():
            if layer.type() == QgsMapLayer.VectorLayer:
                self.combo_layer.addItem(layer.name(), layer.id())

        self.combo_layer.blockSignals(False)
        self._on_layer_changed()

    def _populate_fields(self, layer):
        self.combo_field.blockSignals(True)
        self.combo_field.clear()
        self.combo_field.addItem('-- Selecione um campo --', None)

        if layer:
            for field in layer.fields():
                self.combo_field.addItem(field.name(), field.name())

        self.combo_field.blockSignals(False)

    # ------------------------------------------------------------------ #
    #  Slot: layer changed                                                 #
    # ------------------------------------------------------------------ #
    def _on_layer_changed(self):
        # disconnect from old layer
        if self._current_layer:
            try:
                self._current_layer.selectionChanged.disconnect(self._refresh_table)
            except Exception:
                pass
            self._current_layer = None

        layer_id = self.combo_layer.currentData()
        if layer_id:
            layer = QgsProject.instance().mapLayer(layer_id)
            if layer:
                self._current_layer = layer
                layer.selectionChanged.connect(self._refresh_table)

        self._populate_fields(self._current_layer)
        self._refresh_table()

    # ------------------------------------------------------------------ #
    #  Slot: refresh table                                                 #
    # ------------------------------------------------------------------ #
    def _refresh_table(self):
        self.table.setRowCount(0)

        layer = self._current_layer
        field_name = self.combo_field.currentData()

        if not layer or not field_name:
            self.lbl_summary.setText('Selecione uma camada e um campo.')
            return

        selected = layer.selectedFeatures()
        total = len(selected)

        if total == 0:
            self.lbl_summary.setText('Nenhuma feição selecionada.')
            return

        # count per value
        values = [f[field_name] for f in selected]
        counter = Counter(values)

        self.lbl_summary.setText(
            f'<b>{total}</b> feição(ões) selecionada(s) | '
            f'<b>{len(counter)}</b> valor(es) único(s)'
        )

        # populate table
        self.table.setRowCount(len(counter))
        for row, (val, count) in enumerate(sorted(counter.items(), key=lambda x: str(x[0]))):
            val_item = QTableWidgetItem(str(val) if val is not None else '(nulo)')
            count_item = QTableWidgetItem(str(count))
            count_item.setTextAlignment(Qt.AlignCenter)

            # highlight rows with high counts
            if count == max(counter.values()):
                for item in (val_item, count_item):
                    item.setBackground(QColor('#d0eaff'))

            self.table.setItem(row, 0, val_item)
            self.table.setItem(row, 1, count_item)

    # ------------------------------------------------------------------ #
    #  Project-level signals (layers added/removed)                        #
    # ------------------------------------------------------------------ #
    def _connect_project_signals(self):
        QgsProject.instance().layersAdded.connect(self._populate_layers)
        QgsProject.instance().layersRemoved.connect(self._populate_layers)

    # ------------------------------------------------------------------ #
    #  Cleanup on unload                                                   #
    # ------------------------------------------------------------------ #
    def cleanup(self):
        if self._current_layer:
            try:
                self._current_layer.selectionChanged.disconnect(self._refresh_table)
            except Exception:
                pass
        try:
            QgsProject.instance().layersAdded.disconnect(self._populate_layers)
            QgsProject.instance().layersRemoved.disconnect(self._populate_layers)
        except Exception:
            pass
