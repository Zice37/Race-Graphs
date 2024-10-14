#!/usr/bin/python3
import matplotlib
matplotlib.use("TkAgg")  # Asegúrate de que estás usando un backend interactivo
import tkinter as tk
import matplotlib.pyplot as plt
import os
from tkinter import filedialog, messagebox, ttk
from plot import analizar_csv, trim_csv, COLORS, RENAME_DIR, RENAME_PREFIX, clear_cache_directory, rename_file

def add_file_row_header():
    """Agrega una fila a la lista de archivos."""
    row_frame = tk.Frame(file_list_frame)
    row_frame.pack(side="top",padx=5, pady=5)  # Usar "center" para centrar horizontalmente
    row_frame.pack(fill='both', expand=True)

    filename_label = tk.Label(row_frame, text="Fichero", width=30, anchor='w')
    filename_label.pack(side='left', padx=5)

    combo = ttk.Label(row_frame, text="Vuelta")
    combo.pack(side='right', padx=5)

def on_frame_configure(canvas):
    """Actualizar la región desplazable del canvas para que cubra el contenido completo."""
    canvas.configure(scrollregion=canvas.bbox("all"))

def select_file():
    """Abre un cuadro de diálogo para seleccionar un archivo y lo procesa."""
    filepath = filedialog.askopenfilename()
    directory, filename = os.path.split(filepath)

    current_file, laps = analizar_csv(filepath)
    if current_file is None or laps is None:
        add_file_row(filename, "Error", laps)  # Agregar fila con error
    else:
        add_file_row(filename, "Success", laps)  # Agregar fila con éxito

def add_file_row(filepath, status, laps):
    """Agrega una fila a la lista de archivos."""
    row_frame = tk.Frame(file_list_frame)
    row_frame.pack(side="top",padx=5, pady=5)  # Usar "center" para centrar horizontalmente
    row_frame.pack(fill='both', expand=True)

    # Asignar valores para el Combobox
    comboValues = []

    # Configurar el icono basado en el estado
    if status == "Success":
        icon = "✔️"  
        comboValues.extend(laps)  # Agregar los laps si el estado es exitoso
    else:
        icon = "❌"
        comboValues.append("Invalido")

    # Crear el icono de estado
    icon_label = tk.Label(row_frame, text=icon, font=("Arial", 14))
    icon_label.pack(side='left')

    # Mostrar el nombre del archivo
    filename_label = tk.Label(row_frame, text=os.path.basename(filepath), width=30, anchor='w')
    filename_label.pack(side='left', padx=5)

    # Crear el Combobox con los valores
    combo = ttk.Combobox(row_frame, values=comboValues, state="readonly")
    combo.pack(side='left', padx=5)

    # Botón para eliminar la fila
    delete_button = tk.Button(row_frame, text="Eliminar", command=lambda: delete_file_row(row_frame))
    delete_button.pack(side='right', padx=5)


def delete_file_row(row_frame):
    """Elimina la fila de archivos."""
    row_frame.destroy()

def visualizar(file_list_frame):
    plt.close('all')
    plt.figure(figsize=(10, 6))
    cont = 0

    for child in file_list_frame.children.values():
        if isinstance(child, tk.Frame):
            # Obtener el estado de la fila
            status_label = child.winfo_children()[0]  # Asumimos que el icono está primero
            status = status_label.cget("text")

            if status == "✔️":  # Comprobar si el estado es éxito
                # Obtener el nombre del archivo
                filename_label = child.winfo_children()[1]  # Asumimos que el nombre está en la segunda posición
                current_file = filename_label.cget("text")

                # Obtener el valor del Combobox
                combo_box = child.winfo_children()[2]  # Asumimos que el Combobox está en la tercera posición
                combo_value = combo_box.get()  # Obtener el valor seleccionado en el Combobox
                try:
                    lap = int(combo_value)
                except:
                    continue

                # Aquí llamas a tu función para obtener los datos
                data = trim_csv(rename_file(current_file), lap)
                
                plt.plot(data['distance_traveled'], data['speed'], label=current_file[:-4], color=COLORS[cont % len(COLORS)])
                cont += 1
    if cont > 0:
        plt.title('Laptimes')
        plt.xlabel('Distancia recorrida (metros)')
        plt.ylabel('Velocidad (km/h)')
        plt.legend()
        plt.grid(True)
        plt.show()



if not os.path.exists(RENAME_DIR):
        os.makedirs(RENAME_DIR)

# Crear la ventana principal
root = tk.Tk()
root.title("RaceChrono-Graphs")
root.geometry("740x600")  # Tamaño de la ventana
root.minsize(740, 600)
root.maxsize(740, 600)

# Cambiar el tema
style = ttk.Style()
style.theme_use('clam')

# Título
title_label = tk.Label(root, text="RaceChrono-Graphs", font=("Arial", 16))
title_label.pack(pady=10)

#Botón para añadir ficheros
add_file_button = tk.Button(root, text="Importar CSV*", command=select_file)
add_file_button.pack(pady=10)

main_frame = tk.Frame(root)
main_frame.pack(fill="both", expand=True)

# Crear un frame para envolver el canvas y la scrollbar
frame_container = tk.Frame(main_frame)
frame_container.pack(side="top", fill="both", padx=10, pady=10, expand=True)

# Crear un canvas para añadir el frame desplazable
canvas = tk.Canvas(frame_container)
canvas.pack(side="left", fill="both", expand=True)

# Añadir una scrollbar al canvas
scrollbar = tk.Scrollbar(frame_container, orient="vertical", command=canvas.yview)
scrollbar.pack(side="right", fill="y")

# Configurar el canvas con la scrollbar
canvas.configure(yscrollcommand=scrollbar.set)

# Frame que contendrá las filas de archivos, y está dentro del canvas
file_list_frame = tk.Frame(canvas)

# Crear una ventana dentro del canvas para que el frame sea desplazable
canvas.create_window((0, 0), window=file_list_frame, anchor="nw")

# Asegurar que el canvas se ajuste a la altura de su contenido
file_list_frame.bind("<Configure>", lambda e: on_frame_configure(canvas))

# Añadir una fila de cabeceras (si es necesario)
add_file_row_header()

# Botón para visualizar siempre visible
visualize_button = tk.Button(root, text="Visualizar", command=lambda: visualizar(file_list_frame), bg="blue", fg="white", font=("Arial", 14))
visualize_button.pack(side="bottom", pady=10)

# Texto de ayuda siempre visible
help_label = tk.Label(root, text="*Recerda que debe ser un CSV v3 de RaceChrono", font=("Arial", 6))
help_label.pack(side="bottom", anchor="se")

# Ejecutar el bucle principal de la aplicación
root.mainloop()

# Limpiar caché (opcional)
clear_cache_directory()

