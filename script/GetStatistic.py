import os
import pickle
import numpy as np
import matplotlib.pyplot as plt
import cv2 as cv

def load_dict(path):
    pickle_in = open(path, "rb")
    return pickle.load(pickle_in)


def removeOutliersNoises(values):
    # Calculate quartiles
    q1 = np.percentile(values, 2)
    q3 = np.percentile(values, 98)
    
    # Calculate IQR
    iqr = q3 - q1
    
    # Define lower and upper bounds
    lower_bound = q1 - 1.5 * iqr
    upper_bound = q3 + 1.5 * iqr
    
    # Remove outliers
    filtered_values = [v for v in values if v >= lower_bound and v <= upper_bound]
    
    return filtered_values
 
def normalizeData(values):
    # Max value: 1, Min value: 0
    max_val = np.max(values)
    min_val = np.min(values)

    # Normalize values
    normalized_values = [(v - min_val) / (max_val - min_val) for v in values]

    return normalized_values

def GetMinMaxIndex(values):
    min_val = np.min(values)
    max_val = np.max(values)
    min_index = values.index(min_val)
    max_index = values.index(max_val)
    return min_index, max_index

def GetMinMaxIndexes(values, n=5):
    # get top 5 min and max values
    min_indexes = []
    max_indexes = []

    for i in range(n):
        min_val = np.min(values)
        max_val = np.max(values)
        min_index = values.index(min_val)
        max_index = values.index(max_val)
        min_indexes.append(min_index)
        max_indexes.append(max_index)
        values[min_index] = 0.5
        values[max_index] = 0.5

    return min_indexes, max_indexes

def showPlt(values, key):
    # Plot values as dots
    plt.plot(values, 'bo', markersize=3)  # 'bo' specifies blue dots
    plt.title(f'{key} Distribution')
    plt.xlabel('Index')
    plt.ylabel(key)
    
    # Calculate statistics
    mean_val = np.mean(values)
    max_val = np.max(values)
    min_val = np.min(values)
    median_val = np.median(values)
    variance_val = np.var(values)
    range_val = max_val - min_val
    std_deviation_val = np.std(values)
    
    # Add statistics to plot
    plt.text(0.5, 0.9, f'Mean: {mean_val:.2f}', ha='center', va='center', transform=plt.gca().transAxes)
    plt.text(0.5, 0.85, f'Max: {max_val:.2f}', ha='center', va='center', transform=plt.gca().transAxes)
    plt.text(0.5, 0.8, f'Min: {min_val:.2f}', ha='center', va='center', transform=plt.gca().transAxes)
    plt.text(0.5, 0.75, f'Median: {median_val:.2f}', ha='center', va='center', transform=plt.gca().transAxes)
    plt.text(0.5, 0.7, f'Variance: {variance_val:.2f}', ha='center', va='center', transform=plt.gca().transAxes)
    plt.text(0.5, 0.65, f'Range: {range_val:.2f}', ha='center', va='center', transform=plt.gca().transAxes)
    plt.text(0.5, 0.6, f'Standard Deviation: {std_deviation_val:.2f}', ha='center', va='center', transform=plt.gca().transAxes)
    
    plt.show()


def GetImagePath(file_name):
    return 'FaceOn/data/samples/' + file_name.replace('.pickle', '.jpg')

def SaveImage(source_path, target_path, order = -1):
    img = cv.imread(source_path)
    source_name = source_path.split('/')[-1]

    if not os.path.exists(target_path):
        os.makedirs(target_path)

    if order != -1:
        target_path = target_path + '/' + str(order)+'.jpg'
    else:
        target_path = target_path + '/' + source_name

    cv.imwrite(target_path, img)


dicts = load_dict('FaceOn/data/Gathered_Features.pickle')

print(dicts.keys())
for key in dicts:
    if key == 'fileNames' or key == 'skinColor' or key == 'lipColor' or key == 'symmetry':
        continue
    
    print(len(dicts[key]))

    # showPlt(dicts[key], key)
    # values = removeOutliersNoises(dicts[key])
    values = dicts[key]
    values = normalizeData(values)
    # showPlt(values, f'Normalized {key}')

    n = 50
    min_indexes, max_indexes = GetMinMaxIndexes(values, n)

    min_paths = []
    max_paths = []

    path = 'FaceOn/data/examples/'+ key
    min_path = path + '/min'
    max_path = path + '/max'
    
    if not os.path.exists('FaceOn/data/examples'):
        os.makedirs('FaceOn/data/examples')

    for i in range(n):
        SaveImage(GetImagePath(dicts['fileNames'][min_indexes[i]]), min_path, i)
        SaveImage(GetImagePath(dicts['fileNames'][max_indexes[i]]), max_path, i)
    
    showPlt(values, f'Normalized {key}')

    cv.waitKey(0)