from qgis.core import QgsApplication, QgsProcessingFeedback, QgsCoordinateReferenceSystem
import processing
import os


# create a folder
def create_directory_if_not_exists(directory_path):
    # merge vector data
    """
    Checks if a directory exists, and if not, creates it.
    """
    if not os.path.exists(directory_path):
        os.makedirs(directory_path)
        print(f"Created directory: {directory_path}")


# 1. Merge data
def merge_vector_layers(layer_paths, base_output_path, output_file_name, crs='EPSG:2180'):
    # Merges given vector layers into a single layer.

    output_path_1 = os.path.join(base_output_path, output_file_name)
    processing.run("native:mergevectorlayers", {
        'LAYERS': layer_paths,
        'CRS': QgsCoordinateReferenceSystem(crs),
        'OUTPUT': output_path_1})

    print(f'Layers successfully merged. Resulting file saved at: {output_path_1}')


# 2. Mask of sunlight data
def process_sunlight_data(months, input_folder, output_folder, mask_shapefile):
    """
    Processes sunlight data files for each month by clipping them with a mask layer.
    """

    create_directory_if_not_exists(output_folder)
    for month in months:
        input_file = f"{input_folder}/map_{month}.tif"
        output_file = f"{output_folder}/MAP_{month.upper()}_CLIPPED.tif"

        processing.run("gdal:cliprasterbymasklayer", {
            'INPUT': input_file,
            'MASK': mask_shapefile,
            'SOURCE_CRS': None, 'TARGET_CRS': None,
            'TARGET_EXTENT': None, 'NODATA': None,
            'ALPHA_BAND': False, 'CROP_TO_CUTLINE': True,
            'KEEP_RESOLUTION': False, 'SET_RESOLUTION': False,
            'X_RESOLUTION': None, 'Y_RESOLUTION': None,
            'MULTITHREADING': False, 'OPTIONS': '',
            'DATA_TYPE': 0, 'EXTRA': '',
            'OUTPUT': output_file
        })

    print("Process_sunlight_data completed.")


# 3 Terrain aspect
def calculate_terrain_aspect(input_folder, input_file_name, output_folder, output_file_name):
    """
    Calculates the aspect of the terrain from an input raster file and saves the result to an output file.
    """
    # Input path = path + file
    input_path = os.path.join(input_folder, input_file_name)
    create_directory_if_not_exists(output_folder)

    # output data path director
    output_path = os.path.join(output_folder, output_file_name)

    processing.run("gdal:aspect", {
        'INPUT': input_path,
        'BAND': 1,
        'TRIG_ANGLE': False,
        'ZERO_FLAT': True,
        'COMPUTE_EDGES': True,
        'ZEVENBERGEN': False,
        'OPTIONS': '',
        'EXTRA': '',
        'OUTPUT': output_path
    })

    print("Terrain aspect calculation completed.")


# 4 Convert terrain aspect to vector data
def raster_to_vector_conversion(raster_input, output_folder_raster, output_raster_filename, output_vector_folder,
                                output_vector_file):
    """
    Converts a raster layer based on specific terrain exposure conditions to a vector layer.
    """
    # Ensure output directories exist
    for folder in [output_folder_raster, output_vector_folder]:
        create_directory_if_not_exists(folder)

    # Full path to the output raster file
    output_raster = os.path.join(output_folder_raster, output_raster_filename)

    # Condition for southern, southeast, and southwest terrain exposures
    expression = '(\"{0}@1\" > 215 AND \"{0}@1\" < 315) * 1 + (\"{0}@1\" <= 215 OR \"{0}@1\" >= 315) * 0'.format(
        raster_input)

    # Execute raster calculator with the defined condition
    processing.run("qgis:rastercalculator", {
        'EXPRESSION': expression,
        'LAYERS': [raster_input],
        'CELLSIZE': 0,
        'EXTENT': None,
        'CRS': QgsCoordinateReferenceSystem('EPSG:2180'),
        'OUTPUT': output_raster
    })

    # Full path to the output vector file
    output_vector = os.path.join(output_vector_folder, output_vector_file)

    # Convert TIF to vector
    processing.run("gdal:polygonize", {
        'INPUT': output_raster,
        'BAND': 1,
        'FIELD': 'DN',
        'EIGHT_CONNECTEDNESS': False,
        'EXTRA': '',
        'OUTPUT': output_vector
    })

    print("Raster to vector conversion completed.")


# 5. Filter by balue
def filter_values_condition_1(filter_value, base_input_path, input_filename, base_output_path, output_file):
    # path
    input_path_5 = os.path.join(base_input_path, input_filename)
    output_path_5 = os.path.join(base_output_path, output_file)
    # process
    processing.run("native:extractbyexpression", {
        'INPUT': input_path_5,
        'EXPRESSION': filter_value,
        'OUTPUT': output_path_5
    })

    print("Filtering for values that meet condition 1 is complete")


# 6 Intersection 2 layers
def intersection_exposure_bdot(base_output_path, base_layer, overlay_layer, output_file_name):
    input_path_6 = os.path.join(base_output_path, base_layer)
    overlay_path_6 = os.path.join(base_output_path, overlay_layer)
    output_path_6 = os.path.join(base_output_path, output_file_name)

    processing.run("native:intersection", {
        'INPUT': input_path_6,
        'OVERLAY': overlay_path_6,
        'INPUT_FIELDS': [],
        'OVERLAY_FIELDS': [],
        'OVERLAY_FIELDS_PREFIX': '',
        'OUTPUT': output_path_6
    })
    print("6. Część wspólna powierzchni ekspozycji i BDOT zakończona.")


# 7. Split layer
def split_into_single_parts(base_output_path, input_file_name, output_file_name):
    input_path_7 = os.path.join(base_output_path, input_file_name)
    output_path_7 = os.path.join(base_output_path, output_file_name)

    processing.run("native:multiparttosingleparts", {
        'INPUT': input_path_7,
        'OUTPUT': output_path_7
    })
    print("7. Rozbicie na pojedyncze elementy zakończone.")


# 8. Calculate area
def calculate_area(base_output_path, input_file, output_file):
    input_path_8 = os.path.join(base_output_path, input_file)
    output_path_8 = os.path.join(base_output_path, output_file)

    processing.run("native:fieldcalculator", {
        'INPUT': input_path_8,
        'FIELD_NAME': 'AREA',
        'FIELD_TYPE': 0,  # Zmiana typu pola na liczbowy
        'FIELD_LENGTH': 10,
        'FIELD_PRECISION': 2,
        'FORMULA': ' $area',
        'OUTPUT': output_path_8
    })
    print("Obliczenie powierzchni na rozbitych elementach zakończone.")


# 9. Select by area
def filter_areas(base_output_path, input_file, output_file, variable):
    input_path = os.path.join(base_output_path, input_file)
    output_path = os.path.join(base_output_path, output_file)

    processing.run("native:extractbyexpression", {
        'INPUT': input_path,
        'EXPRESSION': variable,
        'OUTPUT': output_path
    })
    print("9. Filtrowanie powierzchni powyżej 20 000 na obliczonych powierzchniach zakończone.")


# 10. Add id column
def add_id(base_output_path, input_file, output_file):
    input_path_10 = os.path.join(base_output_path, input_file)
    output_path_10 = os.path.join(base_output_path, output_file)

    processing.run("native:fieldcalculator", {
        'INPUT': input_path_10,
        'FIELD_NAME': 'ID',
        'FIELD_TYPE': 1,  # Typ Integer dla ID
        'FIELD_LENGTH': 10,
        'FIELD_PRECISION': 0,
        'FORMULA': ' $id ',
        'OUTPUT': output_path_10
    })
    print("10. Dodanie kolumny ID do odfiltrowanych danych zakończone.")


# 11. Select medium voltage lines
def select_from_layer(base_output_path, input_path, output_file_name):
    output_path_11 = os.path.join(base_output_path, output_file_name)

    processing.run("native:extractbyexpression", {
        'INPUT': input_path,
        'EXPRESSION': '"RODZAJ" = \'linia elektroenergetyczna średniego napięcia\'',
        'OUTPUT': output_path_11
    })
    print("11. Wybranie linii energetycznych średniego napięcia zakończone.")


# 12. Calculate distance to voltage lines
def calculate_distance(base_output_path, source_layer, destination_layer, output_file_name):
    output_path_10 = os.path.join(base_output_path, source_layer)
    destination_path = os.path.join(base_output_path, destination_layer)
    output_path_12 = os.path.join(base_output_path, output_file_name)

    processing.run("native:shortestline", {
        'SOURCE': output_path_10,
        'DESTINATION': destination_path,
        'OUTPUT': output_path_12
    })
    print("12. Obliczenie odległości zakończone.")


# 13. Join attributes by distance
def join_attributes_with_distances(field_1, field_2, field_to_copy, base_output_path, base_file, file_from_copy,
                                   output_file_name):
    input_path = os.path.join(base_output_path, base_file)
    distances_path = os.path.join(base_output_path, file_from_copy)
    output_path = os.path.join(base_output_path, output_file_name)

    processing.run("native:joinattributestable", {
        'INPUT': input_path,
        'FIELD': field_1,
        'INPUT_2': distances_path,
        'FIELD_2': field_2,
        'FIELDS_TO_COPY': [field_to_copy],
        'OUTPUT': output_path
    })
    print("13. Połączenie atrybutów z odległościami zakończone.")


# 14. Filter area by distance to lines

def rename_column(base_output_path, file_to_rename, field_to_rename, new_name, output_file_name):
    input_path = os.path.join(base_output_path, file_to_rename)
    output_path = os.path.join(base_output_path, output_file_name)

    processing.run("native:renametablefield", {
        'INPUT': input_path,
        'FIELD': field_to_rename,
        'NEW_NAME': new_name,
        'OUTPUT': output_path
    })
    print("15. Zmiana nazwy kolumny odległości zakończona.")


def filter_area_distance(base_output_path, variable, column_distance_name, layer_to_filter, output_file_name):
    filter_layer = 'filter_area_distance.shp'
    input_path = os.path.join(base_output_path, layer_to_filter)
    output_filter = os.path.join(base_output_path, filter_layer)
    output_path = os.path.join(base_output_path, output_file_name)
    processing.run("native:extractbyexpression", {
        'INPUT': input_path,
        'EXPRESSION': variable,
        'OUTPUT': output_filter
    })
    print("Filtrowanie powierzchni mniejszych niż 500 metrów od linii zakończone.")

    rename_column(base_output_path=base_output_path, file_to_rename=filter_layer, new_name=column_distance_name,
                  field_to_rename='distance', output_file_name=output_path)




# 18
def buffer(base_output_path, input_path, output_file, distance):
    output_path = os.path.join(base_output_path, output_file)
    processing.run("native:buffer",
                   {'INPUT': input_path
                       , 'DISTANCE': distance
                       , 'SEGMENTS': 5, 'END_CAP_STYLE': 0
                       , 'JOIN_STYLE': 0, 'MITER_LIMIT': 2
                       , 'DISSOLVE': True
                       , 'OUTPUT': output_path})


# 19
def split_into_single_parts(base_output_path, input_file_name, output_file_name):
    input_path_7 = os.path.join(base_output_path, input_file_name)
    output_path_7 = os.path.join(base_output_path, output_file_name)

    processing.run("native:multiparttosingleparts", {
        'INPUT': input_path_7,
        'OUTPUT': output_path_7
    })
    print("7. Rozbicie na pojedyncze elementy zakończone.")


# 20
def calculate_area(base_output_path, input_file, output_file):
    input_path_8 = os.path.join(base_output_path, input_file)
    output_path_8 = os.path.join(base_output_path, output_file)

    processing.run("native:fieldcalculator", {
        'INPUT': input_path_8,
        'FIELD_NAME': 'AREA',
        'FIELD_TYPE': 0,  # Zmiana typu pola na liczbowy
        'FIELD_LENGTH': 10,
        'FIELD_PRECISION': 2,
        'FORMULA': ' $area',
        'OUTPUT': output_path_8
    })
    print("8. Obliczenie powierzchni na rozbitych elementach zakończone.")


# 21
def filter_areas(base_output_path, input_file, output_file, variable):
    input_path = os.path.join(base_output_path, input_file)
    output_path = os.path.join(base_output_path, output_file)

    processing.run("native:extractbyexpression", {
        'INPUT': input_path,
        'EXPRESSION': variable,
        'OUTPUT': output_path
    })
    print("9. Filtrowanie powierzchni powyżej 20 000 na obliczonych powierzchniach zakończone.")


# 22
def intersection_exposure_bdot(base_output_path, base_layer, overlay_layer, output_file_name):
    input_path_6 = os.path.join(base_output_path, base_layer)
    overlay_path_6 = os.path.join(base_output_path, overlay_layer)
    output_path_6 = os.path.join(base_output_path, output_file_name)

    processing.run("native:intersection", {
        'INPUT': input_path_6,
        'OVERLAY': overlay_path_6,
        'INPUT_FIELDS': [],
        'OVERLAY_FIELDS': [],
        'OVERLAY_FIELDS_PREFIX': '',
        'OUTPUT': output_path_6
    })
    print("6. Część wspólna powierzchni ekspozycji i BDOT zakończona.")


### make faster script group, repair geometry, difference
# 5a group layer
def group_layer(base_output_path, base_layer, output_layer_group):
    input_path_6 = os.path.join(base_output_path, base_layer)
    output_path_6 = os.path.join(base_output_path, output_layer_group)
    processing.run("native:collect",
                   {'INPUT': input_path_6
                       , 'FIELD': [],
                    'OUTPUT': output_path_6})


# 5b
def repair_geometry(base_output_path, base_layer, output_layer_name_repair):
    input_path_6 = os.path.join(base_output_path, base_layer)
    output_path_6 = os.path.join(base_output_path, output_layer_name_repair)

    processing.run("native:fixgeometries",
                   {'INPUT': input_path_6
                       , 'METHOD': 1
                       , 'OUTPUT': output_path_6})


def difference_between_layers(base_output_path, base_layer, overlay_layer, output_file_name, variable_to_area):


    input_path = os.path.join(base_output_path, base_layer)

    output_path = os.path.join(base_output_path, output_file_name)
    overlay_layer = os.path.join(base_output_path, overlay_layer)

    processing.run("native:difference"
                   , {'INPUT': input_path
                       , 'OVERLAY': overlay_layer
                       , 'OUTPUT': output_path
                       , 'GRID_SIZE': None})


