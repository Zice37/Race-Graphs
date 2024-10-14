import sys
import pandas as pd
import matplotlib.pyplot as plt
import os
import shutil
import hashlib


#CSV v3 de RaceChrono
LINEAS_A_ELIMINAR = [0,1,2,3,4,5,6,7,8,10,11]  
    
RENAME_PREFIX = '.copy-'
RENAME_DIR = './.tmp'
COLORS = ['blue', 'red', 'green', 'yellow', 'purple']

def clear_cache_directory():
    # Verificar si el directorio existe antes de intentar eliminarlo
    if os.path.exists(RENAME_DIR):
        # Eliminar todo el contenido del directorio /cache
        shutil.rmtree(RENAME_DIR)
        # Volver a crear el directorio vacío
        os.makedirs(RENAME_DIR)

def rename_file(filepath):
    directory, filename = os.path.split(filepath)
    hash_object = hashlib.sha256()
    hash_object.update(filename.encode('utf-8'))
    
    new_filename = RENAME_PREFIX + hash_object.hexdigest()
    return os.path.join(RENAME_DIR, new_filename)

def preparar_csv(filename):
    with open(filename, 'r') as file:
        lines = file.readlines()
    lines = [line for i, line in enumerate(lines) if i not in LINEAS_A_ELIMINAR]
    filename = rename_file(filename)
    with open(filename, 'w') as file:
        file.writelines(lines)
    return filename

def analizar_csv(filename):
    try:
        raw_data = pd.read_csv(filename)
    except:
        try:
            file = rename_file(filename)
            raw_data = pd.read_csv(file)
        except:
            try:
                file = preparar_csv(filename)
                raw_data = pd.read_csv(file)
            except:
                return None, None

    try:
        return file, set(raw_data['lap_number'])
    except:
        return None, None

def trim_csv(filename, lap):
    #filename ya esta preparado
    raw_data = pd.read_csv(filename)
    
    data = {
        'distance_traveled': [], #raw_data['distance_traveled'],
        'speed': [], #raw_data['speed'],
    }
    
    start_index = 0
    for i in range(len(raw_data['lap_number'])):
        if raw_data['lap_number'][i] == lap:
            start_index = i
            break
            
    
    stop_index = len(raw_data['lap_number'])-1
    for i in range(len(raw_data['lap_number'])-1 , -1, -1):
        if raw_data['lap_number'][i] == lap:
            stop_index = i
            break

    data['distance_traveled'] = normalize_distance(raw_data['distance_traveled'][start_index:stop_index].values)
    data['speed'] = ms_to_kph(raw_data['speed'][start_index:stop_index].values)
    return data

def ms_to_kph(lista):
    return [3.6 *x for x in lista]

def normalize_distance(lista):
    if len(lista) <= 0:
        return
    offset = lista[0]
    return [x-offset for x in lista]

def main(filenames):
    if not os.path.exists(RENAME_DIR):
        os.makedirs(RENAME_DIR)


    plt.figure(figsize=(100, 60))
    for i in range(len(filenames)):
        current_file, laps = analizar_csv(filenames[i])
        if current_file is None or laps is None:
            print("El fichero "+ filenames[i]+" no cumple la especificación requerida")
            continue

        print("File: "+filenames[i]+" tiene las siguientes vueltas")
        for lap in laps:
            print(lap)
        lap = int(input("Introduce cual ver: "))
        assert(lap in laps)
        data = trim_csv(current_file, lap)

        plt.plot(data['distance_traveled'], data['speed'], label=filenames[i][:-4], color=COLORS[i%len(COLORS)])
        
    plt.title('Laptimes')
    plt.xlabel('Distancia recorrida (metros)')
    plt.ylabel('Velocidad (km/h)')
    plt.legend()
    plt.grid(True)

    clear_cache_directory()

    plt.show()

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print(f"Use: python {sys.argv[0]} racechrono_csv_v3_hotlap1.csv ... racechrono_csv_v3_hotlapN.csv")
    else:
        main(sys.argv[1:])