#!/usr/bin/python
import sys
import pandas as pd
import matplotlib.pyplot as plt
import os


#CSV v3 de RaceChrono

RENAME_PREFIX = '.copy-'
COLORS = ['blue', 'red', 'green', 'yellow', 'purple']

def rename_file(filepath):
    directory, filename = os.path.split(filepath)    
    new_filename = RENAME_PREFIX + filename
    return os.path.join(directory, new_filename)

def eliminar_cabeceras(filename):
    with open(filename, 'r') as file:
        lines = file.readlines()
    lineas_a_eliminar = [0,1,2,3,4,5,6,7,8,10,11]  
    lines = [line for i, line in enumerate(lines) if i not in lineas_a_eliminar]
    filename = rename_file(filename)
    with open(filename, 'w') as file:
        file.writelines(lines)
    return filename

def read_csv(filename):
    try:
        raw_data = pd.read_csv(filename)
    except:
        try:
            raw_data = pd.read_csv(rename_file(filename))
        except:
            filename = eliminar_cabeceras(filename)
            raw_data = pd.read_csv(filename)

    data = {
        'distance_traveled': [], #raw_data['distance_traveled'],
        'speed': [], #raw_data['speed'],
    }

    initial_lap = raw_data['lap_number'][0]
    for i in range(len(raw_data['lap_number'])):
        if raw_data['lap_number'][i] == ((initial_lap or 0) +1):
            start_index = i
            break
            
    for i in range(len(raw_data['lap_number'])-1 , -1, -1):
        if raw_data['lap_number'][i] == ((initial_lap or 0) +1):
            stop_index = i
            break

    data['distance_traveled'] = raw_data['distance_traveled'][start_index:stop_index].values
    data['speed'] = raw_data['speed'][start_index:stop_index].values
    return data

def ms_to_kph(lista):
    return [3.6 *x for x in lista]

def normalize_distance(lista):
    if len(lista) <= 0:
        return
    offset = lista[0]
    return [x-offset for x in lista]

def main(filenames):
    plt.figure(figsize=(100, 60))
    i = 0

    while i < len(filenames):

        data = read_csv(filenames[i])
        distancia = data['distance_traveled']
        distancia = normalize_distance(distancia)  

        velocidad = data['speed']
        velocidad = ms_to_kph(velocidad)


        plt.plot(distancia, velocidad, label=filenames[i][:-4], color=COLORS[i%len(COLORS)])
        i += 1
        
    plt.title('Laptimes')
    plt.xlabel('Distancia recorrida (metros)')
    plt.ylabel('Velocidad (km/h)')
    plt.legend()
    plt.grid(True)

    plt.show()

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print(f"Use: python {sys.argv[0]} racechrono_csv_v3_hotlap1.csv racechrono_csv_v3_hotlap2.csv ... racechrono_csv_v3_hotlapN.csv")
    else:
        main(sys.argv[1:])
