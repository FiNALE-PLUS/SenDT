import re
import warnings
from pathlib import Path

from PySide6.QtCore import Slot
from PySide6.QtWidgets import QDialog, QGroupBox, QFormLayout, QPushButton, QVBoxLayout, \
    QMessageBox, QDoubleSpinBox

from errors.chart import ChartError, ChartWarning
from parsers.sentakki import get_chart_bpm, convert_sentakki_file_to_SDB_file
from db.models import Chart
from tableUI.gui.widgets.form.files.file_select import SentakkiSelectRow, SentakkiSaveRow
from tableUI.utils.paths.internal_data_paths import get_internal_chart_path

# 7-bit C1 ANSI sequences
# Used to remove colorisation used in the CLI
# TODO: add args in CLI to remove need for retroactive removal
ansi_escape_pattern = re.compile(r'''
    \x1B  # ESC
    (?:   # 7-bit C1 Fe (except CSI)
        [@-Z\\-_]
    |     # or [ for CSI, followed by a control sequence
        \[
        [0-?]*  # Parameter bytes
        [ -/]*  # Intermediate bytes
        [@-~]   # Final byte
    )
''', re.VERBOSE)


class ChartDataConversionDialog(QDialog):
    min_bpm = 1
    max_bpm = 1000
    bpm_step = 1

    def __init__(self, parent=None, chart: Chart | None = None):
        super(ChartDataConversionDialog, self).__init__(parent)

        self.setWindowTitle("Chart Data Conversion")

        dialog_layout = QVBoxLayout()
        self.setLayout(dialog_layout)

        self.file_path_box = QGroupBox("File I/O")
        dialog_layout.addWidget(self.file_path_box)
        file_path_layout = QFormLayout()
        self.file_path_box.setLayout(file_path_layout)

        self.input_path_select = SentakkiSelectRow()
        file_path_layout.addRow("Input Path:", self.input_path_select)

        self.output_path_select = SentakkiSaveRow()
        file_path_layout.addRow("Output Path:", self.output_path_select)

        self.bpm_box = QGroupBox("Chart BPM")
        bpm_box_form = QFormLayout()
        bpm_box_layout = QVBoxLayout()
        bpm_box_layout.addLayout(bpm_box_form)
        self.bpm_box.setLayout(bpm_box_layout)
        dialog_layout.addWidget(self.bpm_box)

        self.bpm_select = QDoubleSpinBox()
        self.bpm_select.setRange(self.min_bpm, self.max_bpm)
        self.bpm_select.setSingleStep(self.bpm_step)
        self.bpm_select.setValue(self.min_bpm)
        bpm_box_form.addRow("Chart BPM:", self.bpm_select)

        self.infer_bpm = QPushButton("Infer BPM from file")
        self.infer_bpm.clicked.connect(self.inferBpmFromInputFile)
        bpm_box_layout.addWidget(self.infer_bpm)

        self.start_conversion_button = QPushButton("Convert")
        self.start_conversion_button.clicked.connect(self.convertCharts)
        dialog_layout.addWidget(self.start_conversion_button)

        if chart is not None:
            self.fill_form_from_chart_data(chart)

    def fill_form_from_chart_data(self, chart):
        self.output_path_select.setCurrentPath(str(get_internal_chart_path(chart).absolute()))
        self.output_path_select.file_path_entry.setEnabled(False)
        self.output_path_select.browse_button.setEnabled(False)

        self.bpm_select.setValue(chart.chart_song.bpm)
        self.bpm_select.setEnabled(False)

        self.infer_bpm.setEnabled(False)

    # TODO: Make validation more thorough
    def validateForm(self):
        if not self.input_path_select.getCurrentPath():
            raise ValueError("No input file has been selected.")
        if not self.output_path_select.getCurrentPath():
            raise ValueError("No output file has been selected.")

    # TODO: Add batch conversion
    @Slot()
    def convertCharts(self):
        try:
            self.validateForm()
        except Exception as e:
            QMessageBox.critical(self, "Invalid Form input",
                                 f"Your input could not be validated. Please check your input and try again."
                                 f"\n({str(e)})")
            return

        if self.bpm_select.value() == self.min_bpm:
            conversion_confirmed = QMessageBox.question(self, "Convert?",
                                                        f"The BPM for the chart has been left as the "
                                                        f"default value of {self.min_bpm}. "
                                                        f"Is this correct?")

            if not conversion_confirmed == QMessageBox.StandardButton.Yes:
                return

        try:
            with warnings.catch_warnings(record=True, category=ChartWarning) as collected_chart_warnings:
                output_path = Path(self.output_path_select.getCurrentPath())
                output_path.parent.mkdir(parents=True, exist_ok=True)
                convert_sentakki_file_to_SDB_file(
                    self.input_path_select.getCurrentPath(), self.output_path_select.getCurrentPath(),
                    True, self.bpm_select.value()
                )

            if not collected_chart_warnings:
                QMessageBox.information(self, "Chart Conversion Complete", "Chart(s) converted successfully.")
            else:
                # Builds a warning box including all warnings from the CLI in the more details section
                warn_box = QMessageBox()
                warn_box.setWindowTitle("Chart Conversion Complete")
                warn_box.setText("The chart(s) converted successfully, but with warnings emitted in the process. "
                                 "This is not always an issue, but is usually worth analysing for potential issues.")
                warn_box.setDetailedText(
                    ansi_escape_pattern.sub('',
                                            '\n'.join(
                                                tuple(str(warning.message) for warning in collected_chart_warnings)))
                )
                warn_box.setIcon(QMessageBox.Icon.Warning)
                warn_box.exec()

        except ChartError as e:
            QMessageBox.critical(self, "Error parsing chart",
                                 f"An error occurred when parsing chart: {str(e)}")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"An error occurred attempting to convert chart: "
                                                f"{type(e)} -  {str(e)}")

    @Slot()
    def inferBpmFromInputFile(self):
        try:
            with open(self.input_path_select.getCurrentPath(), "r") as f:
                chart_content = f.read()

            inferred_bpm = get_chart_bpm(chart_content)
            if inferred_bpm < self.min_bpm or inferred_bpm > self.max_bpm:
                raise ValueError("The BPM of the chart is out of the expected range (0-1000). "
                                 "Please check your chart for validity.")

            self.bpm_select.setValue(inferred_bpm)

            QMessageBox.information(self, "BPM Inference Complete", "BPM inferred successfully.")
        except ChartError:
            QMessageBox.critical(self, "Invalid Chart",
                                 "The input file doesn't seem to be valid. Please check your input and try again.")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"An error occurred when parsing the file for its BPM: "
                                                f"{type(e)} -  {str(e)}")
