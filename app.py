#!/usr/bin/python3
import matplotlib.pyplot as plt
import os
from plot import analizar_csv, trim_csv, COLORS, RENAME_DIR, RENAME_PREFIX, clear_cache_directory, rename_file
from PyQt5 import QtWidgets, QtCore, QtGui
from PyQt5.QtGui import QIcon
import sys


if not os.path.exists(RENAME_DIR):
    os.makedirs(RENAME_DIR)

class MainWindow(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()

        # Configurar la ventana principal
        self.setWindowTitle("Race-Graphs")

        icon = QIcon("icon.ico")
        self.setWindowIcon(icon)

        self.setGeometry(100, 100, 740, 600)

        # Crear el layout principal
        layout = QtWidgets.QVBoxLayout()

        # Título
        title_label = QtWidgets.QLabel("Race-Graphs")
        title_label.setFont(QtGui.QFont("Arial", 16))
        layout.addWidget(title_label, alignment=QtCore.Qt.AlignCenter)

        # Botón para añadir ficheros
        add_file_button = QtWidgets.QPushButton("Importar CSV*")
        add_file_button.clicked.connect(self.select_file)
        layout.addWidget(add_file_button, alignment=QtCore.Qt.AlignCenter)

        # Crear un marco para el contenido desplazable
        self.file_list_frame = QtWidgets.QFrame()
        self.file_list_layout = QtWidgets.QVBoxLayout(self.file_list_frame)

        # Crear un área de desplazamiento
        self.scroll_area = QtWidgets.QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setWidget(self.file_list_frame)

        layout.addWidget(self.scroll_area)

        # Botón para visualizar
        visualize_button = QtWidgets.QPushButton("Visualizar")
        visualize_button.clicked.connect(self.visualize)
        visualize_button.setStyleSheet("background-color: blue; color: white; font-size: 14px;")
        layout.addWidget(visualize_button, alignment=QtCore.Qt.AlignCenter)

        # Texto de ayuda
        help_label = QtWidgets.QLabel("*Recuerda que debe ser un CSV v3 de RaceChrono")
        help_label.setFont(QtGui.QFont("Arial", 6))
        layout.addWidget(help_label, alignment=QtCore.Qt.AlignRight)

        self.setLayout(layout)

    def select_file(self):
        """Abre un cuadro de diálogo para seleccionar un archivo y lo procesa."""
        filepath, _ = QtWidgets.QFileDialog.getOpenFileName(self, "Seleccionar archivo CSV", "", "CSV Files (*.csv)")
        if not filepath:
            return  # Salir si no se selecciona un archivo

        directory, filename = os.path.split(filepath)

        current_file, laps = analizar_csv(filepath)
        if current_file is None or laps is None:
            self.add_file_row(filename, "Error", [])  # Agregar fila con error
        else:
            self.add_file_row(filename, "Correcto", laps)  # Agregar fila con éxito

    def add_file_row(self, filename, status, laps):
        """Agrega una fila a la lista de archivos con su estado y un botón para eliminar."""
        row_frame = QtWidgets.QFrame()  # Crear un nuevo frame para la fila
        row_layout = QtWidgets.QHBoxLayout(row_frame)

        # Etiqueta para el estado
        status_label = QtWidgets.QLabel(status)
        if status == "Correcto":
            status_label.setStyleSheet("color: green;")  # Color para éxito
        else:
            status_label.setStyleSheet("color: red;")  # Color para error

        # Etiqueta para el nombre del archivo
        filename_label = QtWidgets.QLabel(filename)
        filename_label.setFont(QtGui.QFont("Arial", 10))

        # Combobox para laps
        combo_box = QtWidgets.QComboBox()
        for lap in laps:  # Suponiendo que 'laps' es una lista de opciones
            combo_box.addItem(str(lap))

        # Botón de eliminar
        delete_button = QtWidgets.QPushButton("Eliminar")
        delete_button.clicked.connect(lambda: self.remove_file_row(row_frame))

        # Añadir widgets al layout
        row_layout.addWidget(status_label)
        row_layout.addWidget(filename_label)
        row_layout.addWidget(combo_box)
        row_layout.addWidget(delete_button)  # Añadir el botón de eliminar

        # Añadir la fila al layout de la lista de archivos
        self.file_list_layout.addWidget(row_frame)  # Usar el layout para añadir el frame

        #separator = QtWidgets.QFrame()
        #separator.setFrameShape(QtWidgets.QFrame.HLine)  # Establecer como línea horizontal
        #separator.setFrameShadow(QtWidgets.QFrame.Sunken)  # Sombrar la línea
        #self.file_list_layout.addWidget(separator)  # Añadir el separador al layout

    def remove_file_row(self, row_frame):
        """Elimina la fila del archivo de la lista."""
        row_frame.deleteLater()  # Eliminar la fila del layout
    
    def visualize(self):
        plt.close('all')
        plt.figure(figsize=(10, 6))
        cont = 0
        for i in range(self.file_list_layout.count()):
            item = self.file_list_layout.itemAt(i)
            # Imprimir información sobre el item actual
            if item is None:
                continue
            
            # Verificar si el item tiene un widget asociado
            widget = item.widget()
            if widget is None:
                continue
            # Asegúrate de que sea un QFrame
            if isinstance(widget, QtWidgets.QFrame):
                row_layout = widget.layout()
                if row_layout:
                    # Obtener el estado de la fila
                    status_label = row_layout.itemAt(0).widget()  # Suponiendo que el estado está en la primera posición
                    status = status_label.text()

                    if status == "Correcto":  # Comprobar si el estado es éxito
                        # Obtener el nombre del archivo
                        filename_label = row_layout.itemAt(1).widget()  # Suponiendo que el nombre está en la segunda posición
                        current_file = filename_label.text()
                        print(f"Archivo actual: {current_file}")  # Imprimir el nombre del archivo

                        # Obtener el valor del ComboBox
                        combo_box = row_layout.itemAt(2).widget()  # Suponiendo que el ComboBox está en la tercera posición
                        combo_value = combo_box.currentText()  # Obtener el valor seleccionado en el ComboBox
                        print(f"Lap seleccionado: {combo_value}")  # Imprimir el valor del ComboBox

                        try:
                            lap = int(combo_value)  # Convertir a entero
                        except ValueError:
                            continue  # Si no se puede convertir a int, continuar

                        # Aquí llamas a tu función para obtener los datos
                        data = trim_csv(rename_file(current_file), lap)

                        # Verificar si se obtuvieron datos
                        if data is not None:
                            plt.plot(data['distance_traveled'], data['speed'], label=current_file[:-4], color=COLORS[cont % len(COLORS)])
                            cont += 1
            
        if cont > 0:
            plt.title('Laptimes')
            plt.xlabel('Distancia recorrida (metros)')
            plt.ylabel('Velocidad (km/h)')
            plt.legend()
            plt.grid(True)
            plt.show()

    def closeEvent(self, event):
        clear_cache_directory()
        event.accept() 

if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())

