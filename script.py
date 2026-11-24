# ============================================================
# Basic ID GENERATOR - FINAL POWER VERSION
# FjBa Edition
# ============================================================

import os

from qgis.PyQt.QtCore import (
    Qt,
    QTimer,
    QVariant,
)
from qgis.PyQt.QtGui import (
    QIcon,
    QKeySequence,
    QColor,
    QFont,
    QPainter,
    QPainterPath,
    QLinearGradient,
    QBrush,
    QPen,
)
from qgis.PyQt.QtWidgets import (
    QAction,
    QDialog,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QListWidget,
    QListWidgetItem,
    QLineEdit,
    QSpinBox,
    QCheckBox,
    QComboBox,
    QProgressBar,
    QMessageBox,
    QShortcut,
    QWidget,
)

from qgis.core import (
    QgsProject,
    QgsVectorLayer,
    QgsField,
    QgsFeatureRequest,
    QgsTask,
    QgsApplication,
)


# ============================================================
# FjBa METALLIC LOGO
# Gold / Emerald gradient with animated light sweep
# ============================================================

class FjBaMetallicLogo(QWidget):

    def __init__(self, parent=None):
        super().__init__(parent)

        self.phase = 0.0

        self.setMinimumSize(80, 70)
        self.setMaximumSize(100, 90)

        self.setAttribute(
            Qt.WA_TranslucentBackground,
            True
        )

        self.timer = QTimer(self)
        self.timer.timeout.connect(
            self.advance_animation
        )

        self.timer.start(35)

    def advance_animation(self):

        self.phase = (
            self.phase + 0.018
        ) % 1.5

        self.update()

    def paintEvent(self, event):

        painter = QPainter(self)

        painter.setRenderHint(
            QPainter.Antialiasing
        )

        rect = self.rect()

        font = QFont(
            "Segoe UI",
            27,
            QFont.Bold
        )

        painter.setFont(font)

        text = "FjBa"

        metrics = painter.fontMetrics()

        text_width = metrics.horizontalAdvance(
            text
        )

        x = (
            rect.width() - text_width
        ) / 2

        baseline = rect.height() * 0.62

        path = QPainterPath()

        path.addText(
            x,
            baseline,
            font,
            text
        )

        # ----------------------------------------------------
        # Metallic emerald / gold gradient
        # ----------------------------------------------------

        gradient = QLinearGradient(
            0,
            0,
            rect.width(),
            rect.height()
        )

        gradient.setColorAt(
            0.0,
            QColor("#FFF2B0")
        )

        gradient.setColorAt(
            0.22,
            QColor("#D5A832")
        )

        gradient.setColorAt(
            0.45,
            QColor("#F9E7A0")
        )

        gradient.setColorAt(
            0.68,
            QColor("#16A879")
        )

        gradient.setColorAt(
            1.0,
            QColor("#075C43")
        )

        painter.setPen(
            QPen(
                QColor("#B68A28"),
                0.8
            )
        )

        painter.setBrush(
            QBrush(gradient)
        )

        painter.drawPath(path)

        # ----------------------------------------------------
        # Animated white light sweep
        # ----------------------------------------------------

        sweep_x = (
            self.phase * rect.width()
        )

        sweep = QLinearGradient(
            sweep_x - 12,
            0,
            sweep_x + 12,
            0
        )

        sweep.setColorAt(
            0.0,
            QColor(
                255,
                255,
                255,
                0
            )
        )

        sweep.setColorAt(
            0.5,
            QColor(
                255,
                255,
                255,
                180
            )
        )

        sweep.setColorAt(
            1.0,
            QColor(
                255,
                255,
                255,
                0
            )
        )

        painter.save()

        painter.setClipPath(path)

        painter.fillRect(
            rect,
            sweep
        )

        painter.restore()

        painter.end()

    def stop(self):

        if (
            self.timer is not None
            and self.timer.isActive()
        ):
            self.timer.stop()

    def closeEvent(self, event):

        self.stop()

        super().closeEvent(event)


# ============================================================
# BACKGROUND TASK
# ============================================================

class AssignIDsTask(QgsTask):

    def __init__(
        self,
        layers,
        field_name,
        prefix,
        start,
        step,
        overwrite,
        sort_field,
        descending
    ):

        super().__init__(
            "Basic ID Generator",
            QgsTask.CanCancel
        )

        self.layers = layers
        self.field_name = field_name
        self.prefix = prefix
        self.start = start
        self.step = step
        self.overwrite = overwrite
        self.sort_field = sort_field
        self.descending = descending

        self.results = {}
        self.exception = None

    # ========================================================
    # RUN
    # ========================================================

    def run(self):

        try:

            total_features = sum(
                layer.featureCount()
                for layer in self.layers
            )

            if total_features == 0:

                self.setProgress(100)

                return True

            processed = 0

            for layer in self.layers:

                if self.isCanceled():
                    return False

                existing_fields = [
                    field.name()
                    for field in layer.fields()
                ]

                create_field = (
                    self.field_name
                    not in existing_fields
                )

                request = (
                    QgsFeatureRequest()
                    .setFlags(
                        QgsFeatureRequest.NoGeometry
                    )
                )

                features = list(
                    layer.getFeatures(request)
                )

                # ------------------------------------------------
                # SORT
                # ------------------------------------------------

                if (
                    self.sort_field != "No Sorting"
                    and self.sort_field
                    in existing_fields
                ):

                    def sort_key(feature):

                        value = feature[
                            self.sort_field
                        ]

                        if value is None:
                            return ""

                        return value

                    features.sort(
                        key=sort_key,
                        reverse=self.descending
                    )

                # ------------------------------------------------
                # FIELD INDEX
                # ------------------------------------------------

                if create_field:

                    field_index = len(
                        existing_fields
                    )

                else:

                    field_index = (
                        layer.fields()
                        .indexOf(
                            self.field_name
                        )
                    )

                changes = {}

                value = self.start

                # ------------------------------------------------
                # PROCESS FEATURES
                # ------------------------------------------------

                for feature in features:

                    if self.isCanceled():
                        return False

                    current_value = None

                    if not create_field:

                        current_value = feature[
                            field_index
                        ]

                    # --------------------------------------------
                    # Don't overwrite existing values
                    # --------------------------------------------

                    if (
                        not self.overwrite
                        and current_value
                        not in (None, "")
                    ):

                        processed += 1

                        self.setProgress(
                            int(
                                (
                                    processed
                                    / total_features
                                ) * 100
                            )
                        )

                        continue

                    # --------------------------------------------
                    # Generate new ID
                    # --------------------------------------------

                    if self.prefix:

                        new_value = (
                            f"{self.prefix}"
                            f"{value}"
                        )

                    else:

                        new_value = value

                    changes[
                        feature.id()
                    ] = new_value

                    value += self.step

                    processed += 1

                    self.setProgress(
                        int(
                            (
                                processed
                                / total_features
                            ) * 100
                        )
                    )

                self.results[
                    layer.id()
                ] = {

                    "layer": layer,

                    "create_field":
                        create_field,

                    "field_index":
                        field_index,

                    "changes":
                        changes,

                }

            return True

        except Exception as error:

            self.exception = error

            return False


# ============================================================
# MAIN DIALOG
# ============================================================

class UltraIDGeneratorDialog(QDialog):

    def __init__(self, iface):

        super().__init__(
            iface.mainWindow()
        )

        self.iface = iface

        self.dark_mode = True

        self.task = None

        self.logo = None

        self.setWindowTitle(
            "Basic ID Generator - FjBa"
        )

        self.resize(
            650,
            850
        )

        self.setMinimumSize(
            550,
            700
        )

        self.load_layers()

        self.build_ui()

        self.apply_dark_theme()

        self.setup_shortcuts()

    # ========================================================
    # LOAD LAYERS
    # ========================================================

    def load_layers(self):

        self.layers = []

        for layer in (
            QgsProject.instance()
            .mapLayers()
            .values()
        ):

            if (
                isinstance(
                    layer,
                    QgsVectorLayer
                )
                and layer.isValid()
            ):

                self.layers.append(
                    layer
                )

    # ========================================================
    # BUILD UI
    # ========================================================

    def build_ui(self):

        layout = QVBoxLayout()

        layout.setSpacing(8)

        # ====================================================
        # HEADER
        # ====================================================

        header_layout = QHBoxLayout()

        self.logo = FjBaMetallicLogo()

        header_layout.addWidget(
            self.logo
        )

        title_layout = QVBoxLayout()

        title = QLabel(
            "⚡ ULTRA ID GENERATOR ⚡"
        )

        title.setAlignment(
            Qt.AlignCenter
        )

        title.setStyleSheet("""
            font-size: 24px;
            font-weight: bold;
            padding: 5px;
        """)

        subtitle = QLabel(
            "FjBa Power Edition"
        )

        subtitle.setAlignment(
            Qt.AlignCenter
        )

        subtitle.setStyleSheet("""
            font-size: 12px;
            font-weight: normal;
            padding-bottom: 5px;
        """)

        title_layout.addWidget(
            title
        )

        title_layout.addWidget(
            subtitle
        )

        header_layout.addLayout(
            title_layout,
            1
        )

        layout.addLayout(
            header_layout
        )

        # ====================================================
        # THEME BUTTON
        # ====================================================

        self.theme_btn = QPushButton(
            "🌙 Toggle Dark / Light Mode"
        )

        self.theme_btn.clicked.connect(
            self.toggle_theme
        )

        layout.addWidget(
            self.theme_btn
        )

        # ====================================================
        # LAYER LIST
        # ====================================================

        layout.addWidget(
            QLabel("Select Layers")
        )

        self.layer_list = QListWidget()

        self.layer_list.setSelectionMode(
            QListWidget.ExtendedSelection
        )

        for layer in self.layers:

            item = QListWidgetItem(
                layer.name()
            )

            item.setData(
                Qt.UserRole,
                layer.id()
            )

            item.setCheckState(
                Qt.Unchecked
            )

            self.layer_list.addItem(
                item
            )

        layout.addWidget(
            self.layer_list,
            1
        )

        # ====================================================
        # SELECT BUTTONS
        # ====================================================

        btn_layout = QHBoxLayout()

        self.select_all_btn = QPushButton(
            "✅ Select All"
        )

        self.deselect_all_btn = QPushButton(
            "❌ Deselect All"
        )

        self.select_all_btn.clicked.connect(
            self.select_all_layers
        )

        self.deselect_all_btn.clicked.connect(
            self.deselect_all_layers
        )

        btn_layout.addWidget(
            self.select_all_btn
        )

        btn_layout.addWidget(
            self.deselect_all_btn
        )

        layout.addLayout(
            btn_layout
        )

        # ====================================================
        # FIELD NAME
        # ====================================================

        layout.addWidget(
            QLabel("ID Field Name")
        )

        self.field_name = QLineEdit(
            "id"
        )

        self.field_name.setPlaceholderText(
            "Example: id, object_id, asset_id"
        )

        layout.addWidget(
            self.field_name
        )

        # ====================================================
        # PREFIX
        # ====================================================

        layout.addWidget(
            QLabel("Prefix")
        )

        self.prefix_input = QLineEdit()

        self.prefix_input.setPlaceholderText(
            "Optional - Example: ID-"
        )

        layout.addWidget(
            self.prefix_input
        )

        # ====================================================
        # START
        # ====================================================

        layout.addWidget(
            QLabel("Start Value")
        )

        self.start_value = QSpinBox()

        self.start_value.setRange(
            -999999999,
            999999999
        )

        self.start_value.setValue(
            1
        )

        layout.addWidget(
            self.start_value
        )

        # ====================================================
        # STEP
        # ====================================================

        layout.addWidget(
            QLabel("Step")
        )

        self.step_value = QSpinBox()

        self.step_value.setRange(
            -999999999,
            999999999
        )

        self.step_value.setValue(
            1
        )

        layout.addWidget(
            self.step_value
        )

        # ====================================================
        # OVERWRITE
        # ====================================================

        self.overwrite_checkbox = QCheckBox(
            "Overwrite Existing Values"
        )

        self.overwrite_checkbox.setChecked(
            True
        )

        layout.addWidget(
            self.overwrite_checkbox
        )

        # ====================================================
        # SORT
        # ====================================================

        layout.addWidget(
            QLabel("Sort Field")
        )

        self.sort_combo = QComboBox()

        self.sort_combo.addItem(
            "No Sorting"
        )

        fields = set()

        for layer in self.layers:

            for field in layer.fields():

                fields.add(
                    field.name()
                )

        self.sort_combo.addItems(
            sorted(fields)
        )

        layout.addWidget(
            self.sort_combo
        )

        # ====================================================
        # DESCENDING
        # ====================================================

        self.desc_checkbox = QCheckBox(
            "Descending Order"
        )

        layout.addWidget(
            self.desc_checkbox
        )

        # ====================================================
        # PROGRESS
        # ====================================================

        self.progress_bar = QProgressBar()

        self.progress_bar.setRange(
            0,
            100
        )

        self.progress_bar.setValue(
            0
        )

        layout.addWidget(
            self.progress_bar
        )

        # ====================================================
        # RUN
        # ====================================================

        self.run_btn = QPushButton(
            "🚀 RUN"
        )

        self.run_btn.clicked.connect(
            self.run_tool
        )

        layout.addWidget(
            self.run_btn
        )

        # ====================================================
        # CANCEL
        # ====================================================

        self.cancel_btn = QPushButton(
            "🛑 CANCEL TASK"
        )

        self.cancel_btn.clicked.connect(
            self.cancel_task
        )

        self.cancel_btn.setEnabled(
            False
        )

        layout.addWidget(
            self.cancel_btn
        )

        self.setLayout(
            layout
        )

    # ========================================================
    # SHORTCUTS
    # ========================================================

    def setup_shortcuts(self):

        self.shortcut_select = QShortcut(
            QKeySequence("Ctrl+A"),
            self
        )

        self.shortcut_select.activated.connect(
            self.select_all_layers
        )

        self.shortcut_deselect = QShortcut(
            QKeySequence("Ctrl+D"),
            self
        )

        self.shortcut_deselect.activated.connect(
            self.deselect_all_layers
        )

        self.shortcut_run = QShortcut(
            QKeySequence("Ctrl+Return"),
            self
        )

        self.shortcut_run.activated.connect(
            self.run_tool
        )

    # ========================================================
    # DARK THEME
    # ========================================================

    def apply_dark_theme(self):

        self.setStyleSheet("""

            QDialog {
                background-color: #121212;
                color: white;
            }

            QLabel {
                color: white;
                font-weight: bold;
                font-size: 13px;
            }

            QListWidget {
                background-color: #1e1e1e;
                color: #13ff00;
                border: 2px solid #13ff00;
                font-size: 13px;
                padding: 4px;
            }

            QLineEdit,
            QSpinBox,
            QComboBox {

                background-color: #1e1e1e;
                color: white;
                border: 2px solid #555;
                padding: 5px;
            }

            QCheckBox {
                color: white;
                padding: 4px;
            }

            QPushButton {

                background-color: #23ff00;
                color: black;
                border: 2px solid #13ff00;
                padding: 8px;
                border-radius: 6px;
                font-weight: bold;
            }

            QPushButton:hover {
                background-color: #009cff;
                color: white;
            }

            QPushButton:disabled {
                background-color: #444444;
                color: #888888;
                border: 1px solid #555555;
            }

            QProgressBar {

                border: 2px solid #555;
                text-align: center;
                height: 28px;
                font-weight: bold;
                color: white;
            }

            QProgressBar::chunk {
                background-color: #13ff00;
            }

        """)

    # ========================================================
    # LIGHT THEME
    # ========================================================

    def apply_light_theme(self):

        self.setStyleSheet("""

            QDialog {
                background-color: #dcefff;
                color: black;
            }

            QLabel {
                color: black;
                font-weight: bold;
            }

            QListWidget {
                background-color: white;
                color: black;
                border: 2px solid #007acc;
            }

            QLineEdit,
            QSpinBox,
            QComboBox {

                background-color: white;
                color: black;
                border: 2px solid #888;
                padding: 5px;
            }

            QCheckBox {
                color: black;
                padding: 4px;
            }

            QPushButton {

                background-color: #007acc;
                color: white;
                border: 2px solid black;
                padding: 8px;
                border-radius: 6px;
                font-weight: bold;
            }

            QPushButton:hover {
                background-color: #005f9e;
            }

            QPushButton:disabled {
                background-color: #aaaaaa;
                color: #666666;
            }

            QProgressBar {

                border: 2px solid #555;
                text-align: center;
                height: 28px;
            }

            QProgressBar::chunk {
                background-color: #007acc;
            }

        """)

    # ========================================================
    # TOGGLE THEME
    # ========================================================

    def toggle_theme(self):

        self.dark_mode = not self.dark_mode

        if self.dark_mode:

            self.apply_dark_theme()

        else:

            self.apply_light_theme()

    # ========================================================
    # SELECT ALL
    # ========================================================

    def select_all_layers(self):

        for i in range(
            self.layer_list.count()
        ):

            self.layer_list.item(
                i
            ).setCheckState(
                Qt.Checked
            )

    # ========================================================
    # DESELECT ALL
    # ========================================================

    def deselect_all_layers(self):

        for i in range(
            self.layer_list.count()
        ):

            self.layer_list.item(
                i
            ).setCheckState(
                Qt.Unchecked
            )

    # ========================================================
    # GET SELECTED LAYERS
    # ========================================================

    def get_selected_layers(self):

        selected = []

        project = QgsProject.instance()

        for i in range(
            self.layer_list.count()
        ):

            item = self.layer_list.item(i)

            if item.checkState() != Qt.Checked:
                continue

            layer_id = item.data(
                Qt.UserRole
            )

            layer = project.mapLayer(
                layer_id
            )

            if (
                layer is not None
                and layer.isValid()
            ):

                selected.append(
                    layer
                )

        return selected

    # ========================================================
    # VALIDATE FIELD
    # ========================================================

    def validate_field_name(
        self,
        field_name
    ):

        if not field_name:

            return (
                False,
                "Field name cannot be empty."
            )

        if len(field_name) > 255:

            return (
                False,
                "Field name is too long."
            )

        invalid_characters = [
            " ",
            "\t",
            "\n",
            "\r"
        ]

        for char in invalid_characters:

            if char in field_name:

                return (
                    False,
                    "Field name cannot contain spaces "
                    "or line breaks."
                )

        return True, ""

    # ========================================================
    # RUN TOOL
    # ========================================================

    def run_tool(self):

        if self.task is not None:

            QMessageBox.warning(
                self,
                "Task Running",
                "An ID generation task is already running."
            )

            return

        selected_layers = (
            self.get_selected_layers()
        )

        if not selected_layers:

            QMessageBox.warning(
                self,
                "No Layers",
                "Please select at least one layer."
            )

            return

        field_name = (
            self.field_name
            .text()
            .strip()
        )

        valid, message = (
            self.validate_field_name(
                field_name
            )
        )

        if not valid:

            QMessageBox.warning(
                self,
                "Invalid Field Name",
                message
            )

            return

        prefix = (
            self.prefix_input
            .text()
        )

        start = (
            self.start_value
            .value()
        )

        step = (
            self.step_value
            .value()
        )

        if step == 0:

            QMessageBox.warning(
                self,
                "Invalid Step",
                "Step cannot be zero."
            )

            return

        # ----------------------------------------------------
        # Warn if field exists with incompatible type
        # ----------------------------------------------------

        if prefix:

            for layer in selected_layers:

                index = layer.fields().indexOf(
                    field_name
                )

                if index >= 0:

                    field = layer.fields().at(
                        index
                    )

                    if field.type() not in (
                        QVariant.String,
                        QVariant.Char,
                    ):

                        answer = QMessageBox.question(
                            self,
                            "Field Type Warning",
                            (
                                f"Layer '{layer.name()}' "
                                f"already contains '{field_name}', "
                                "but it is not a text field.\n\n"
                                "Continue anyway?"
                            ),
                            QMessageBox.Yes
                            | QMessageBox.No,
                            QMessageBox.No
                        )

                        if answer != QMessageBox.Yes:
                            return

        # ----------------------------------------------------
        # Create task
        # ----------------------------------------------------

        self.task = AssignIDsTask(

            selected_layers,

            field_name,

            prefix,

            start,

            step,

            self.overwrite_checkbox
            .isChecked(),

            self.sort_combo
            .currentText(),

            self.desc_checkbox
            .isChecked()

        )

        self.task.progressChanged.connect(
            self.update_progress
        )

        self.task.taskCompleted.connect(
            self.task_finished
        )

        self.task.taskTerminated.connect(
            self.task_failed
        )

        QgsApplication.taskManager().addTask(
            self.task
        )

        self.run_btn.setEnabled(
            False
        )

        self.cancel_btn.setEnabled(
            True
        )

        self.progress_bar.setValue(
            0
        )

    # ========================================================
    # PROGRESS
    # ========================================================

    def update_progress(
        self,
        value
    ):

        try:

            self.progress_bar.setValue(
                int(value)
            )

        except RuntimeError:
            pass

    # ========================================================
    # TASK FINISHED
    # ========================================================

    def task_finished(self):

        if self.task is None:
            return

        try:

            field_name = (
                self.field_name
                .text()
                .strip()
            )

            for result in (
                self.task.results.values()
            ):

                layer = result[
                    "layer"
                ]

                create_field = result[
                    "create_field"
                ]

                changes = result[
                    "changes"
                ]

                # --------------------------------------------
                # Create field
                # --------------------------------------------

                if create_field:

                    if self.prefix_input.text():

                        field_type = (
                            QVariant.String
                        )

                    else:

                        field_type = (
                            QVariant.Int
                        )

                    success = (
                        layer.dataProvider()
                        .addAttributes([
                            QgsField(
                                field_name,
                                field_type
                            )
                        ])
                    )

                    if not success:

                        raise Exception(
                            f"Could not create field "
                            f"'{field_name}' in "
                            f"layer '{layer.name()}'."
                        )

                    layer.updateFields()

                # --------------------------------------------
                # Get actual field index
                # --------------------------------------------

                field_index = (
                    layer.fields()
                    .indexOf(
                        field_name
                    )
                )

                if field_index < 0:

                    raise Exception(
                        f"Field '{field_name}' "
                        f"was not found in "
                        f"layer '{layer.name()}'."
                    )

                # --------------------------------------------
                # Build changes
                # --------------------------------------------

                fixed_changes = {}

                for fid, value in changes.items():

                    fixed_changes[fid] = {
                        field_index: value
                    }

                # --------------------------------------------
                # Apply changes
                # --------------------------------------------

                if fixed_changes:

                    if not layer.isEditable():

                        if not layer.startEditing():

                            raise Exception(
                                f"Could not start editing "
                                f"layer '{layer.name()}'."
                            )

                    success = (
                        layer.dataProvider()
                        .changeAttributeValues(
                            fixed_changes
                        )
                    )

                    if not success:

                        raise Exception(
                            f"Could not update "
                            f"layer '{layer.name()}'."
                        )

                    if not layer.commitChanges():

                        errors = (
                            layer.commitErrors()
                        )

                        raise Exception(
                            f"Could not commit "
                            f"layer '{layer.name()}'.\n"
                            f"{errors}"
                        )

            self.progress_bar.setValue(
                100
            )

            QMessageBox.information(
                self,
                "Success",
                (
                    "ID generation completed "
                    "successfully."
                )
            )

        except Exception as error:

            QMessageBox.critical(
                self,
                "Error",
                str(error)
            )

        finally:

            self.run_btn.setEnabled(
                True
            )

            self.cancel_btn.setEnabled(
                False
            )

            self.task = None

    # ========================================================
    # TASK FAILED / CANCELLED
    # ========================================================

    def task_failed(self):

        try:

            task_error = None

            if self.task:

                task_error = (
                    self.task.exception
                )

            self.run_btn.setEnabled(
                True
            )

            self.cancel_btn.setEnabled(
                False
            )

            if task_error:

                QMessageBox.critical(
                    self,
                    "Task Error",
                    str(task_error)
                )

            else:

                QMessageBox.warning(
                    self,
                    "Cancelled",
                    "The ID generation task was cancelled."
                )

        except RuntimeError:
            pass

        finally:

            self.task = None

    # ========================================================
    # CANCEL
    # ========================================================

    def cancel_task(self):

        if self.task is None:
            return

        try:

            self.task.cancel()

            self.cancel_btn.setEnabled(
                False
            )

        except RuntimeError:
            pass

    # ========================================================
    # CLOSE
    # ========================================================

    def closeEvent(self, event):

        try:

            if self.task is not None:

                self.task.cancel()

            if self.logo is not None:

                self.logo.stop()

        except RuntimeError:
            pass

        event.accept()


# ============================================================
# PLUGIN
# ============================================================

class UltraIDPlugin:

    def __init__(self, iface):

        self.iface = iface

        self.action = None

        self.dialog = None

    # ========================================================
    # INIT GUI
    # ========================================================

    def initGui(self):

        icon_path = os.path.join(
            os.path.dirname(__file__),
            "icon.png"
        )

        self.action = QAction(
            QIcon(icon_path),
            "Basic ID Generator",
            self.iface.mainWindow()
        )

        self.action.setToolTip(
            "Basic ID Generator - FjBa"
        )

        self.action.triggered.connect(
            self.run
        )

        self.iface.addToolBarIcon(
            self.action
        )

        self.iface.addPluginToMenu(
            "&Basic ID Generator",
            self.action
        )

    # ========================================================
    # UNLOAD
    # ========================================================

    def unload(self):

        if self.action is not None:

            self.iface.removeToolBarIcon(
                self.action
            )

            self.iface.removePluginMenu(
                "&Basic ID Generator",
                self.action
            )

            self.action.deleteLater()

            self.action = None

    # ========================================================
    # RUN
    # ========================================================

    def run(self):

        if (
            self.dialog is not None
            and self.dialog.isVisible()
        ):

            self.dialog.raise_()
            self.dialog.activateWindow()

            return

        self.dialog = (
            UltraIDGeneratorDialog(
                self.iface
            )
        )

        self.dialog.exec_()

        self.dialog = None


# ============================================================
# QGIS PLUGIN ENTRY POINT
# ============================================================

def classFactory(iface):

    return UltraIDPlugin(iface)
    
# ============================================================
# QGIS PLUGIN ENTRY POINT
# ============================================================

def main(iface):

    dialog = UltraIDGeneratorDialog(iface)

    dialog.exec_()


def classFactory(iface):

    return UltraIDPlugin(iface)
