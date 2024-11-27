import sys
from PyQt5.QtWidgets import (
    QApplication,
    QVBoxLayout,
    QPushButton,
    QLabel,
    QWidget,
    QMessageBox,
)
from PyQt5.QtGui import QFont
from PyQt5.QtCore import Qt
from barcode_generate_print import get_airpods_serial, main


class AirPodsApp(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("AirPods Barcode Printer")
        self.setGeometry(300, 300, 400, 200)
        self.init_ui()

    def init_ui(self):
        """Initialize the UI layout."""
        layout = QVBoxLayout()

        # AirPods Status Label
        self.status_label = QLabel("Checking AirPods connection...")
        self.status_label.setAlignment(Qt.AlignCenter)
        self.status_label.setFont(QFont("Arial", 14))
        layout.addWidget(self.status_label)

        # Print Button
        self.print_button = QPushButton("Print the Barcodes")
        self.print_button.setFont(QFont("Arial", 12))
        self.print_button.setEnabled(False)
        self.print_button.clicked.connect(self.print_barcodes)
        layout.addWidget(self.print_button)

        # Exit Button
        self.exit_button = QPushButton("Exit")
        self.exit_button.setFont(QFont("Arial", 12))
        self.exit_button.clicked.connect(self.close_app)
        layout.addWidget(self.exit_button)

        # Set the main layout
        self.setLayout(layout)

        # Check AirPods connection
        self.check_airpods_connection()

    def check_airpods_connection(self):
        """Check if AirPods are connected and update the status."""
        airpods_serials = get_airpods_serial()
        connected = all(v != "Not Found" for v in airpods_serials.values())
        if connected:
            self.status_label.setText("AirPods Connected")
            self.status_label.setStyleSheet("color: green;")
            self.print_button.setEnabled(True)
        else:
            self.status_label.setText("AirPods Not Connected")
            self.status_label.setStyleSheet("color: red;")
            self.print_button.setEnabled(False)

    def print_barcodes(self):
        """Generate and print barcodes if AirPods are connected."""
        try:
            airpods_serials = get_airpods_serial()
            if all(v != "Not Found" for v in airpods_serials.values()):
                QMessageBox.information(self, "Printing", "Barcodes are being printed...")
                main()  # Call the barcode generation and printing function
            else:
                QMessageBox.warning(self, "Error", "No AirPods connected. Cannot print barcodes.")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"An error occurred during printing: {e}")

    def close_app(self):
        """Exit the application."""
        self.close()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = AirPodsApp()
    window.show()
    sys.exit(app.exec())
