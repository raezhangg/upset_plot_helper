import sys
import pandas as pd
import matplotlib.pyplot as plt
from upsetplot import UpSet, from_indicators
from PyQt6.QtWidgets import (
    QApplication, QWidget, QLabel, QPushButton, QVBoxLayout, 
    QLineEdit, QTextEdit, QFileDialog, QMessageBox, QFormLayout, QHBoxLayout
)


class UpSetMatrixApp(QWidget):
    def __init__(self):
        super().__init__()
        self.set_data = {}  # Dictionary to store set data
        self.init_ui()

    def init_ui(self):
        """Initialize the GUI layout"""
        self.setWindowTitle("UpSet Matrix Generator")
        self.setGeometry(200, 200, 600, 500)

        layout = QVBoxLayout()

        # Input for number of sets
        form_layout = QFormLayout()
        self.num_sets_entry = QLineEdit()
        form_layout.addRow("Enter the number of sets:", self.num_sets_entry)
        layout.addLayout(form_layout)

        # Submit button
        self.submit_button = QPushButton("Submit")
        self.submit_button.clicked.connect(self.get_user_input)
        layout.addWidget(self.submit_button)

        # Dynamic input area for sets
        self.dynamic_layout = QVBoxLayout()
        layout.addLayout(self.dynamic_layout)

        # Buttons for generating matrix and saving
        self.generate_button = QPushButton("Generate Matrix & UpSet Plot")
        self.generate_button.clicked.connect(self.process_sets)
        self.generate_button.setEnabled(False)
        layout.addWidget(self.generate_button)

        self.save_matrix_button = QPushButton("Save Binary Matrix")
        self.save_matrix_button.clicked.connect(self.save_to_csv)
        self.save_matrix_button.setEnabled(False)
        layout.addWidget(self.save_matrix_button)

        self.save_plot_button = QPushButton("Save UpSet Plot")
        self.save_plot_button.clicked.connect(self.save_upset_plot)
        self.save_plot_button.setEnabled(False)
        layout.addWidget(self.save_plot_button)

        self.setLayout(layout)

    def get_user_input(self):
        """Collect number of sets and create input fields dynamically."""
        try:
            self.num_sets = int(self.num_sets_entry.text().strip())
            if self.num_sets <= 0:
                raise ValueError
        except ValueError:
            QMessageBox.critical(self, "Error", "Please enter a valid positive integer.")
            return

        # Clear previous inputs
        for i in reversed(range(self.dynamic_layout.count())):
            widget = self.dynamic_layout.itemAt(i).widget()
            if widget:
                widget.setParent(None)

        self.set_entries = []
        self.item_textboxes = []

        for i in range(self.num_sets):
            sub_layout = QVBoxLayout()
            set_entry = QLineEdit()
            sub_layout.addWidget(QLabel(f"Set {i+1} Name:"))
            sub_layout.addWidget(set_entry)
            self.set_entries.append(set_entry)

            item_textbox = QTextEdit()
            sub_layout.addWidget(QLabel(f"Enter items (one per line):"))
            sub_layout.addWidget(item_textbox)
            self.item_textboxes.append(item_textbox)

            self.dynamic_layout.addLayout(sub_layout)

        self.generate_button.setEnabled(True)

    def process_sets(self):
        """Process sets and generate the binary matrix."""
        self.set_data.clear()

        for i in range(self.num_sets):
            set_name = self.set_entries[i].text().strip()
            if not set_name:
                QMessageBox.critical(self, "Error", "Set name cannot be empty.")
                return

            items = self.item_textboxes[i].toPlainText().strip().split("\n")
            items = set(item.strip() for item in items if item.strip())

            if not items:
                QMessageBox.critical(self, "Error", f"Set '{set_name}' cannot be empty.")
                return

            self.set_data[set_name] = items

        QMessageBox.information(self, "Success", "Sets processed successfully.")
        self.save_matrix_button.setEnabled(True)
        self.save_plot_button.setEnabled(True)

        # Generate and display UpSet plot
        self.show_upset_plot()

    def save_to_csv(self):
        """Save binary matrix as a CSV file."""
        if not self.set_data:
            QMessageBox.critical(self, "Error", "No data to save.")
            return

        all_items = sorted(set.union(*self.set_data.values()))
        binary_matrix = {item: [1 if item in self.set_data[set_name] else 0 for set_name in self.set_data] for item in all_items}
        df = pd.DataFrame.from_dict(binary_matrix, orient="index", columns=self.set_data.keys())

        file_path, _ = QFileDialog.getSaveFileName(self, "Save CSV", "", "CSV files (*.csv)")
        if file_path:
            df.to_csv(file_path, index=True)
            QMessageBox.information(self, "Saved", f"Binary matrix saved as '{file_path}'")

    def show_upset_plot(self):
        """Generate and display the UpSet plot with auto-labeled subset sizes."""
        if not self.set_data:
            QMessageBox.critical(self, "Error", "No data to visualize.")
            return

        all_items = sorted(set.union(*self.set_data.values()))
        binary_matrix = {item: [1 if item in self.set_data[set_name] else 0 for set_name in self.set_data] for item in all_items}
        df = pd.DataFrame.from_dict(binary_matrix, orient="index", columns=self.set_data.keys())

        # Convert DataFrame to UpSet format
        data_for_upset = from_indicators(df.columns, df.astype(bool))
        upset = UpSet(data_for_upset, show_counts=True) 

        # Generate the plot
        plt.figure(figsize=(10, 6))
        upset.plot()
        plt.show()

    def save_upset_plot(self):
        """Save UpSet plot as an image file."""
        if not self.set_data:
            QMessageBox.critical(self, "Error", "No data to visualize.")
            return

        file_path, _ = QFileDialog.getSaveFileName(self, "Save UpSet Plot", "", "PNG files (*.png)")
        if file_path:
            all_items = sorted(set.union(*self.set_data.values()))
            binary_matrix = {item: [1 if item in self.set_data[set_name] else 0 for set_name in self.set_data] for item in all_items}
            df = pd.DataFrame.from_dict(binary_matrix, orient="index", columns=self.set_data.keys())

            data_for_upset = from_indicators(df.columns, df.astype(bool))
            upset = UpSet(data_for_upset, show_counts=True)

            plt.figure(figsize=(10, 6))
            upset.plot()
            plt.savefig(file_path, dpi=300, bbox_inches='tight')
            plt.close()
            QMessageBox.information(self, "Saved", f"UpSet plot saved as '{file_path}'")


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = UpSetMatrixApp()
    window.show()
    sys.exit(app.exec())
