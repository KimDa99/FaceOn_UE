import os
import numpy as np
import mediapipe as mp
try:
    from sklearn.cluster import KMeans  # pip install scikit-learn
except ImportError as e:
    print(f'Failed to import scikit-learn: {e}')
import pickle

# Eyes
eye_front_right_index = 133
eye_front_left_index = 362
eye_back_right_index = 33
eye_back_left_index = 263

eye_top_left_index = 386
eye_top_right_index = 159
eye_bottom_left_index = 374
eye_bottom_right_index = 145

# brows
brow_start_left_indexs = [336, 285]
brow_arch_left_indexs = [334, 282]
brow_end_left_indexs = [300, 276]
brow_start_right_indexs = [107, 55]
brow_arch_right_indexs = [105, 52]
brow_end_right_indexs = [70, 46]

# lips
top_lip_indexes = [ 61, 78, 185, 191, 40,
                    80, 39, 81, 37, 82, 
                    0, 13, 267, 312, 269, 
                    311, 270, 310, 409, 415, 
                    291, 308]

bottom_lip_indexes = [ 61, 146, 91, 181, 84,
                      17, 314, 405, 321, 375,
                      291, 308, 324, 318, 402,
                      317, 14, 87, 178, 88,
                      95, 78]

top_lip_top_index = 0
top_lip_bottom_index = 13
bottom_lip_top_index = 14
bottom_lip_bottom_index = 17
lip_right_end_index = 61
lip_left_end_index = 291

# Nose
nose_bridge_indexs = [168, 6, 197, 195, 5, 4, 1, 19, 94]
nose_bridge_right_indexs = [193, 122, 196, 3, 51, 45, 44, 125, 141]
nose_bridge_left_indexs = [417, 351, 419, 248, 281, 275, 274, 354, 370]

nose_right_index = 64
nose_left_index = 294
nose_end_index = 94
nose_start_index = 168

# forehead
forehead_end_indexs = [107, 9, 136]
forehead_start_indexs = [109, 10, 338]

# chin
chin_end_index = 152
chin_end_right_indexs = [149, 176, 148]
chin_end_left_indexs = [378, 400, 377]

# jaw
jaw_right_indexs = [132, 58, 172]
jaw_left_indexs = [361, 288, 397]

# temple
temple_right_index = 127
temple_left_index = 356

def GetVectorLength(vector):
    return np.linalg.norm(vector)

def GetLength(point0, point1):
    return np.linalg.norm(point0 - point1)

def GetLengthBetweenPointLine(point, line_point0, line_point1):
    return np.linalg.norm(np.cross(line_point1 - line_point0, line_point0 - point)) / np.linalg.norm(line_point1 - line_point0)

def GetDegreeBetweenVectorXYPlane(vector):
    return np.arccos(vector[2] / np.linalg.norm(vector))

def GetSkinColor(colors, n_clusters=3):
    # Apply K-means clustering
    kmeans = KMeans(n_clusters=n_clusters)
    kmeans.fit(colors)
    labels = kmeans.labels_
    
    # Find the largest cluster
    largest_cluster_index = np.argmax(np.bincount(labels))
    
    # Extract the colors in the largest cluster
    largest_cluster_colors = colors[labels == largest_cluster_index]
    
    # Compute the median color of the largest cluster
    median_color = np.median(largest_cluster_colors, axis=0)
    
    return median_color

def GetLipColor(colors):
    # get lip indexs from mediapipe
    lip_indexes = top_lip_indexes + bottom_lip_indexes
    lip_colors = colors[lip_indexes]
    mean_color = np.mean(lip_colors, axis=0)    
    return mean_color

def GetEyeBetween(points):
    return GetLength(points[eye_top_right_index], points[eye_top_left_index])

def GetEyeFront(points):
    right_front_length = GetLengthBetweenPointLine(points[eye_front_right_index], points[eye_top_right_index], points[eye_bottom_right_index])
    left_front_length = GetLengthBetweenPointLine(points[eye_front_left_index], points[eye_top_left_index], points[eye_bottom_left_index])
    return right_front_length + left_front_length

def GetEyeBack(points):
    right_back_length = GetLengthBetweenPointLine(points[eye_back_right_index], points[eye_top_right_index], points[eye_bottom_right_index])
    left_back_length = GetLengthBetweenPointLine(points[eye_back_left_index], points[eye_top_left_index], points[eye_bottom_left_index])
    return right_back_length + left_back_length

def GetEyeAbove(points):
    right_above_length = GetLengthBetweenPointLine(points[eye_top_right_index], points[eye_front_right_index], points[eye_back_right_index])
    left_above_length = GetLengthBetweenPointLine(points[eye_top_left_index], points[eye_front_left_index], points[eye_back_left_index])
    return right_above_length + left_above_length

def GetEyeBelow(points):
    right_below_length = GetLengthBetweenPointLine(points[eye_bottom_right_index], points[eye_front_right_index], points[eye_back_right_index])
    left_below_length = GetLengthBetweenPointLine(points[eye_bottom_left_index], points[eye_front_left_index], points[eye_back_left_index])
    return right_below_length + left_below_length

def GetEyeDegree(points):
    right_eye = points[eye_front_right_index] - points[eye_back_right_index]
    left_eye = points[eye_front_left_index] - points[eye_back_left_index]
    right_eye_degree = GetDegreeBetweenVectorXYPlane(right_eye)
    left_eye_degree = GetDegreeBetweenVectorXYPlane(left_eye)

    return right_eye_degree + left_eye_degree

def GetBrowBetween(points):
    right_brow = points[brow_arch_right_indexs[0]] + points[brow_arch_right_indexs[1]]
    left_brow = points[brow_arch_left_indexs[0]] + points[brow_arch_left_indexs[1]]
    return GetLength(right_brow, left_brow)

def GetBrowFront(points):
    right_fronts = points[brow_start_right_indexs[0]] + points[brow_start_right_indexs[1]]
    right_archs = points[brow_arch_right_indexs[0]] + points[brow_arch_right_indexs[1]]

    left_fronts = points[brow_start_left_indexs[0]] + points[brow_start_left_indexs[1]]
    left_archs = points[brow_arch_left_indexs[0]] + points[brow_arch_left_indexs[1]]

    return GetLength(right_fronts, right_archs) + GetLength(left_fronts, left_archs)

def GetBrowBack(points):
    right_backs = points[brow_end_right_indexs[0]] + points[brow_end_right_indexs[1]]
    right_archs = points[brow_arch_right_indexs[0]] + points[brow_arch_right_indexs[1]]

    left_backs = points[brow_end_left_indexs[0]] + points[brow_end_left_indexs[1]]
    left_archs = points[brow_arch_left_indexs[0]] + points[brow_arch_left_indexs[1]]

    return GetLength(right_backs, right_archs) + GetLength(left_backs, left_archs)

def GetBrowDegree(points):
    right_brow = points[brow_start_right_indexs[0]] - points[brow_end_right_indexs[0]]
    left_brow = points[brow_start_left_indexs[0]] - points[brow_end_left_indexs[0]]

    return GetDegreeBetweenVectorXYPlane(right_brow) + GetDegreeBetweenVectorXYPlane(left_brow)

def GetBrowThickness(points):
    right_fronts = GetLength(points[brow_start_right_indexs[0]], points[brow_start_right_indexs[1]])
    right_archs = GetLength(points[brow_arch_right_indexs[0]], points[brow_arch_right_indexs[1]])
    right_ends = GetLength(points[brow_end_right_indexs[0]], points[brow_end_right_indexs[1]])

    left_fronts = GetLength(points[brow_start_left_indexs[0]], points[brow_start_left_indexs[1]])
    left_archs = GetLength(points[brow_arch_left_indexs[0]], points[brow_arch_left_indexs[1]])
    left_ends = GetLength(points[brow_end_left_indexs[0]], points[brow_end_left_indexs[1]])

    return right_fronts + right_archs + right_ends + left_fronts + left_archs + left_ends

def GetBrowShape(points):
    right_arch = points[brow_arch_right_indexs[0]] + points[brow_arch_right_indexs[1]]
    right_start = points[brow_start_right_indexs[0]] + points[brow_start_right_indexs[1]]
    right_end = points[brow_end_right_indexs[0]] + points[brow_end_right_indexs[1]]

    left_arch = points[brow_arch_left_indexs[0]] + points[brow_arch_left_indexs[1]]
    left_start = points[brow_start_left_indexs[0]] + points[brow_start_left_indexs[1]]
    left_end = points[brow_end_left_indexs[0]] + points[brow_end_left_indexs[1]]

    right_shape = GetLengthBetweenPointLine(right_arch, right_start, right_end) / GetLength(right_start, right_end)
    left_shape = GetLengthBetweenPointLine(left_arch, left_start, left_end) / GetLength(left_start, left_end)

    return right_shape + left_shape

def GetNoseLength(points):
    nose_start = points[nose_start_index][2]
    nose_end = points[nose_end_index][2]

    return nose_end - nose_start

def GetNoseBridgeThickness(points):
    nose_bridge_right = points[nose_bridge_indexs] - points[nose_bridge_right_indexs]
    nose_bridge_left = points[nose_bridge_indexs] - points[nose_bridge_left_indexs]
    return GetVectorLength(nose_bridge_right) + GetVectorLength(nose_bridge_left)

def GetNoseAlar(points):
    nose_right = points[nose_right_index] - points[nose_bridge_indexs[-1]]
    nose_left = points[nose_left_index] - points[nose_bridge_indexs[-1]]
    return GetVectorLength(nose_right) + GetVectorLength(nose_left)

def GetPhiltrum(points):
    philtrum = points[nose_end_index] - points[top_lip_top_index]
    return GetVectorLength(philtrum)

def GetLipLength(points):    
    return GetVectorLength(points[lip_right_end_index] - points[lip_left_end_index])

def GetUpperLipThickness(points):
    return GetVectorLength(points[top_lip_top_index] - points[top_lip_bottom_index])

def GetLowerLipThickness(points):
    return GetVectorLength(points[bottom_lip_top_index] - points[bottom_lip_bottom_index])

def GetForeheadLength(points):
    forehead_vector = points[forehead_start_indexs] - points[forehead_end_indexs]
    return GetVectorLength(forehead_vector)

def GetChinLength(points):
    return GetVectorLength(points[bottom_lip_bottom_index] - points[chin_end_index])

def GetJaw(points):
    right_jaw = points[jaw_right_indexs[0]] + points[jaw_right_indexs[1]] + points[jaw_right_indexs[2]]
    jaw_right = GetLengthBetweenPointLine( right_jaw, points[chin_end_index], points[temple_right_index])

    left_jaw = points[jaw_left_indexs[0]] + points[jaw_left_indexs[1]] + points[jaw_left_indexs[2]]
    jaw_left = GetLengthBetweenPointLine( left_jaw, points[chin_end_index], points[temple_left_index])

    return jaw_right + jaw_left

def GetJawPosition(points):
    right_jaw = points[chin_end_index] - points[jaw_right_indexs[0]]
    left_jaw = points[chin_end_index] - points[jaw_left_indexs[0]]
    right_jaw = right_jaw[2]
    left_jaw = left_jaw[2]
    return right_jaw + left_jaw

def ExtractFeatures(points, colors):
    dict = {}
    
    print('Extracting Eye values...')
    dict.update({"eyeBetween": GetEyeBetween(points)})
    dict.update({"eyeFront": GetEyeFront(points)})
    dict.update({"eyeBack": GetEyeBack(points)})
    dict.update({"eyeAbove": GetEyeAbove(points)})
    dict.update({"eyeBelow": GetEyeBelow(points)})
    dict.update({"eyeDegree": GetEyeDegree(points)})

    dict.update({"browBetween": GetBrowBetween(points)})
    dict.update({"browFront": GetBrowFront(points)})
    dict.update({"browBack": GetBrowBack(points)})
    print('Extracting Brow values...')
    dict.update({"browDegree": GetBrowDegree(points)})
    dict.update({"browThickness": GetBrowThickness(points)})
    dict.update({"browShape": GetBrowShape(points)})

    print('Extracting Nose values...')
    dict.update({"noseLength": GetNoseLength(points)})
    dict.update({"noseBridgeThickness": GetNoseBridgeThickness(points)})
    dict.update({"noseAlar": GetNoseAlar(points)})
    dict.update({"philtrum": GetPhiltrum(points)})

    print('Extracting Lip values...')
    dict.update({"lipLength": GetLipLength(points)})
    dict.update({"upperLipThickness": GetUpperLipThickness(points)})
    dict.update({"lowerLipThickness": GetLowerLipThickness(points)})

    print('Extracting Forehead values...')
    dict.update({"foreheadLength": GetForeheadLength(points)})

    dict.update({"chinLength": GetChinLength(points)})

    dict.update({"jaw": GetJaw(points)})
    dict.update({"jawPosition": GetJawPosition(points)})

    print('Extracting Skin and Lip colors...')
    dict.update({"skinColor": GetSkinColor(colors)})
    dict.update({"lipColor": GetLipColor(colors)})
    return dict

def printFeatures(dicts):
    for key in dicts:
        print(f'{key}: {dicts[key]}')

def SaveValues(points_path, export_path):
    try:
        print(f'Loading data from {points_path}...')
        data = np.load(points_path, allow_pickle=True)
        points = data[0][0]
        colors = data[1][0]

        print('Extracting features...')
        values = ExtractFeatures(points, colors)
        print('Features extracted')

        if not os.path.exists(export_path):
            os.makedirs(export_path)

        export_file_path = f'{export_path}/{points_path.split("/")[-1].split(".")[0]}.pickle'
        with open(export_file_path, 'wb') as handle:
            pickle.dump(values, handle, protocol=pickle.HIGHEST_PROTOCOL)
        
        print(f'Values saved to {export_file_path}')
        printFeatures(values)
    except Exception as e:
        print(f'An error occurred: {e}')


def SaveBatchValues(path, export_path):
    for file in os.listdir(path):
        if file.endswith('.npy'):
            SaveValues(f'{path}/{file}', export_path)


# path = 'FaceOn/data/combined_Normalized/part1/_0_0_20161219140627985_combined.npy'
# export_path = 'FaceOn/data/numbers/part1'
# SaveValues(path, export_path)

SaveBatchValues('FaceOn/data/combined_Normalized/part1', 'FaceOn/data/numbers/part1')
SaveBatchValues('FaceOn/data/combined_Normalized/part2', 'FaceOn/data/numbers/part2')
SaveBatchValues('FaceOn/data/combined_Normalized/part3', 'FaceOn/data/numbers/part3')