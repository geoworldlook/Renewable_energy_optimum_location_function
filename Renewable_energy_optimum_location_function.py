from qgis.core import QgsApplication, QgsProcessingFeedback, QgsCoordinateReferenceSystem
import processing
import os


# create a folder
def create_directory_if_not_exists(directory_path):
    """
    Checks if a directory exists, and if not, creates it.

    Args:
        directory_path (str): The path to the directory to check or create.

    Returns:
        None: Prints a message indicating if the directory was created.
    """
    if not os.path.exists(directory_path):
        os.makedirs(directory_path)
        print(f"Created directory: {directory_path}")



# 1. Merge data
def merge_vector_layers(layer_paths, base_output_path, output_file_name, crs='EPSG:2180'):
    """
    Merges multiple vector layers into a single layer.

    Args:
        layer_paths (list): A list of paths to the vector layers to merge.
        base_output_path (str): Directory where the merged file will be saved.
        output_file_name (str): The name of the output merged file.
        crs (str): The Coordinate Reference System (default: 'EPSG:2180').

    Returns:
        None: Prints a message indicating the success of the merge operation.
    """
    output_path_1 = os.path.join(base_output_path, output_file_name)
    processing.run("native:mergevectorlayers", {
        'LAYERS': [layer_paths],
        'CRS': QgsCoordinateReferenceSystem(crs),
        'OUTPUT': output_path_1
    })

    print(f'Layers successfully merged. Resulting file saved at: {output_path_1}')



# 2. Mask of sunlight data
def process_sunlight_data(months, input_folder, output_folder, mask_shapefile):
    """
    Processes monthly sunlight data by clipping raster files using a shapefile mask.

    Args:
        months (list): A list of month identifiers (e.g., ['jan', 'feb']).
        input_folder (str): The folder where input raster files are located.
        output_folder (str): The folder where output clipped raster files will be saved.
        mask_shapefile (str): Path to the shapefile used for clipping the rasters.

    Returns:
        None: Prints a message indicating the completion of the processing.
    """
    create_directory_if_not_exists(output_folder)
    for month in months:
        input_file = f"{input_folder}/map_{month}.tif"
        output_file = f"{output_folder}/MAP_{month.upper()}_CLIPPED.tif"

        processing.run("gdal:cliprasterbymasklayer", {
            'INPUT': input_file,
            'MASK': mask_shapefile,
            'OUTPUT': output_file
        })

    print("Process_sunlight_data completed.")



# 3 Terrain aspect
def calculate_terrain_aspect(input_folder, input_file_name, output_folder, output_file_name):
    """
    Calculates the aspect (orientation) of terrain from a raster file and saves the result.

    Args:
        input_folder (str): The folder containing the input raster file.
        input_file_name (str): The name of the input raster file.
        output_folder (str): The folder where the output aspect file will be saved.
        output_file_name (str): The name of the output aspect file.

    Returns:
        None: Prints a message indicating the completion of the aspect calculation.
    """
    input_path = os.path.join(input_folder, input_file_name)
    create_directory_if_not_exists(output_folder)
    output_path = os.path.join(output_folder, output_file_name)

    processing.run("gdal:aspect", {
        'INPUT': input_path,
        'OUTPUT': output_path
    })

    print("Terrain aspect calculation completed.")



# 4 Convert terrain aspect to vector data
def raster_to_vector_conversion(raster_input, output_folder_raster, output_raster_filename, output_vector_folder, output_vector_file):
    """
    Converts a raster file, based on specific terrain exposure conditions, into a vector file.

    Args:
        raster_input (str): The path to the input raster file.
        output_folder_raster (str): Directory to save the processed raster file.
        output_raster_filename (str): Name of the output raster file.
        output_vector_folder (str): Directory to save the output vector file.
        output_vector_file (str): Name of the output vector file.

    Returns:
        None: Prints a message when the conversion is complete.
    """
    # Ensure output directories exist
    for folder in [output_folder_raster, output_vector_folder]:
        create_directory_if_not_exists(folder)

    # Full path to the output raster file
    output_raster = os.path.join(output_folder_raster, output_raster_filename)

    # Condition for southern, southeast, and southwest terrain exposures
    expression = '(\"{0}@1\" > 215 AND \"{0}@1\" < 315) * 1 + (\"{0}@1\" <= 215 OR \"{0}@1\" >= 315) * 0'.format(raster_input)

    # Execute raster calculator
    processing.run("qgis:rastercalculator", {
        'EXPRESSION': expression,
        'LAYERS': [raster_input],
        'OUTPUT': output_raster
    })

    # Full path to the output vector file
    output_vector = os.path.join(output_vector_folder, output_vector_file)

    # Convert TIF to vector
    processing.run("gdal:polygonize", {
        'INPUT': output_raster,
        'OUTPUT': output_vector
    })

    print("Raster to vector conversion completed.")



# 5. Filter by balue
def filter_values_condition_1(filter_value, base_input_path, input_filename, base_output_path, output_file):
    """
    Filters raster data based on a specific condition and saves the result.

    Args:
        filter_value (str): Expression to filter values by.
        base_input_path (str): Directory containing the input file.
        input_filename (str): Name of the input raster file.
        base_output_path (str): Directory to save the output file.
        output_file (str): Name of the output file.

    Returns:
        None: Prints a message when filtering is complete.
    """
    input_path_5 = os.path.join(base_input_path, input_filename)
    output_path_5 = os.path.join(base_output_path, output_file)

    processing.run("native:extractbyexpression", {
        'INPUT': input_path_5,
        'EXPRESSION': filter_value,
        'OUTPUT': output_path_5
    })

    print("Filtering for values that meet condition 1 is complete.")


# 6 Intersection 2 layers
def intersection_exposure_bdot(base_output_path, base_layer, overlay_layer, output_file_name):
    """
    Performs an intersection of two vector layers, producing a new layer with overlapping areas.

    Args:
        base_output_path (str): Directory containing the base and overlay layers.
        base_layer (str): File name of the base vector layer.
        overlay_layer (str): File name of the overlay vector layer.
        output_file_name (str): File name for the output intersection layer.

    Returns:
        None: Prints a message indicating the intersection operation is complete.
    """
    input_path_6 = os.path.join(base_output_path, base_layer)
    overlay_path_6 = os.path.join(base_output_path, overlay_layer)
    output_path_6 = os.path.join(base_output_path, output_file_name)

    processing.run("native:intersection", {
        'INPUT': input_path_6,
        'OVERLAY': overlay_path_6,
        'OUTPUT': output_path_6
    })

    print("Intersection of exposure and BDOT completed.")



# 8. Calculate area
def split_into_single_parts(base_output_path, input_file_name, output_file_name):
    """
    Splits multipart geometries in a vector layer into single-part geometries.

    Args:
        base_output_path (str): Directory containing the input file.
        input_file_name (str): Name of the input vector file.
        output_file_name (str): Name of the output vector file with single-part geometries.

    Returns:
        None: Prints a message when the splitting operation is complete.
    """
    input_path_7 = os.path.join(base_output_path, input_file_name)
    output_path_7 = os.path.join(base_output_path, output_file_name)

    processing.run("native:multiparttosingleparts", {
        'INPUT': input_path_7,
        'OUTPUT': output_path_7
    })

    print("Splitting into single parts completed.")



# 9. Select by area
def filter_areas(base_output_path, input_file, output_file, variable):
    """
    Filters areas based on a given condition (expression) and saves the results to a new file.

    Parameters:
    - base_output_path (str): The base directory where the input and output files are located.
    - input_file (str): The name of the input file containing area data.
    - output_file (str): The name of the output file that will contain the filtered areas.
    - variable (str): The expression used to filter areas.

    Returns:
    None: The filtered data is saved to a new file.
    """
    input_path = os.path.join(base_output_path, input_file)
    output_path = os.path.join(base_output_path, output_file)

    processing.run("native:extractbyexpression", {
        'INPUT': input_path,
        'EXPRESSION': variable,
        'OUTPUT': output_path
    })

    print("Area filtering based on the specified condition is complete.")


# 10. Add ID column
def add_id(base_output_path, input_file, output_file):
    """
    Adds an 'ID' column to a layer with a unique identifier for each feature.

    Parameters:
    - base_output_path (str): The base directory where the input and output files are located.
    - input_file (str): The name of the input file.
    - output_file (str): The name of the output file with the added 'ID' column.

    Returns:
    None: The updated file is saved with the 'ID' column.
    """
    input_path = os.path.join(base_output_path, input_file)
    output_path = os.path.join(base_output_path, output_file)

    processing.run("native:fieldcalculator", {
        'INPUT': input_path,
        'FIELD_NAME': 'ID',
        'FIELD_TYPE': 1,  # Integer type for ID
        'FIELD_LENGTH': 10,
        'FIELD_PRECISION': 0,
        'FORMULA': ' $id ',
        'OUTPUT': output_path
    })

    print("ID column added successfully.")


# 11. Select medium voltage lines
def select_from_layer(base_output_path, input_path, output_file_name):
    """
    Selects features from a layer where the 'RODZAJ' attribute indicates medium-voltage power lines.

    Parameters:
    - base_output_path (str): The base directory for the output file.
    - input_path (str): The path to the input file containing the power line data.
    - output_file_name (str): The name of the output file to store the filtered features.

    Returns:
    None: The filtered file is saved to the specified location.
    """
    output_path = os.path.join(base_output_path, output_file_name)

    processing.run("native:extractbyexpression", {
        'INPUT': input_path,
        'EXPRESSION': '"RODZAJ" = \'linia elektroenergetyczna średniego napięcia\'',
        'OUTPUT': output_path
    })

    print("Selection of medium-voltage power lines is complete.")


# 12. Calculate distance to voltage lines
def calculate_distance(base_output_path, source_layer, destination_layer, output_file_name):
    """
    Calculates the shortest distance between two layers, such as from a source layer to voltage lines.

    Parameters:
    - base_output_path (str): The base directory where the input and output files are located.
    - source_layer (str): The name of the source layer file.
    - destination_layer (str): The name of the destination layer file (e.g., voltage lines).
    - output_file_name (str): The name of the output file containing the distance data.

    Returns:
    None: The distance calculations are saved to the output file.
    """
    output_path = os.path.join(base_output_path, source_layer)
    destination_path = os.path.join(base_output_path, destination_layer)
    output_file = os.path.join(base_output_path, output_file_name)

    processing.run("native:shortestline", {
        'SOURCE': output_path,
        'DESTINATION': destination_path,
        'OUTPUT': output_file
    })

    print("Distance calculation completed successfully.")


# 13. Join attributes by distance
def join_attributes_with_distances(field_1, field_2, field_to_copy, base_output_path, base_file, file_from_copy,
                                   output_file_name):
    """
    Joins attributes from two layers based on distance between their features.

    Parameters:
    - field_1 (str): The field name in the base layer.
    - field_2 (str): The field name in the layer with the distances.
    - field_to_copy (str): The attribute field to copy from the second layer.
    - base_output_path (str): The base directory for input and output files.
    - base_file (str): The name of the base file (first layer).
    - file_from_copy (str): The name of the file containing distances (second layer).
    - output_file_name (str): The name of the output file with joined attributes.

    Returns:
    None: The attributes are joined and saved to the output file.
    """
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

    print("Attributes joined based on distance successfully.")


# 14. Filter area by distance to lines
def filter_area_distance(base_output_path, variable, column_distance_name, layer_to_filter, output_file_name):
    """
    Filters areas based on their distance from power lines and renames the distance column.

    Parameters:
    - base_output_path (str): The base directory where the input and output files are located.
    - variable (str): The condition/expression to filter the areas by distance.
    - column_distance_name (str): The new name for the distance column.
    - layer_to_filter (str): The name of the layer to apply the filter to.
    - output_file_name (str): The name of the output file with the filtered data.

    Returns:
    None: The filtered data is saved and the distance column is renamed.
    """
    input_path = os.path.join(base_output_path, layer_to_filter)
    output_filter = os.path.join(base_output_path, "filtered_layer")
    output_path = os.path.join(base_output_path, output_file_name)

    # Filtering areas based on distance
    processing.run("native:extractbyexpression", {
        'INPUT': input_path,
        'EXPRESSION': variable,
        'OUTPUT': output_filter
    })

    print("Filtering areas by distance is complete.")

    # Renaming the distance column
    rename_column(base_output_path=base_output_path, file_to_rename="filtered_layer", new_name=column_distance_name,
                  field_to_rename='distance', output_file_name=output_path)


# 18. Create a buffer around features
def buffer(base_output_path, input_path, output_file, distance):
    """
    Creates a buffer around features in the input layer with a specified distance.

    Parameters:
    - base_output_path (str): The base directory where the input and output files are located.
    - input_path (str): The path to the input file.
    - output_file (str): The name of the output file that will contain the buffered features.
    - distance (float): The distance to buffer around the features.

    Returns:
    None: The buffered features are saved to the output file.
    """
    output_path = os.path.join(base_output_path, output_file)

    processing.run("native:buffer", {
        'INPUT': input_path,
        'DISTANCE': distance,
        'SEGMENTS': 5,
        'END_CAP_STYLE': 0,
        'JOIN_STYLE': 0,
        'MITER_LIMIT': 2,
        'DISSOLVE': True,
        'OUTPUT': output_path
    })

    print("Buffer creation completed.")


# 19. Split layer into single parts
def split_into_single_parts(base_output_path, input_file_name, output_file_name):
    """
    Splits a multipart layer into single parts, each saved as an individual feature.

    Parameters:
    - base_output_path (str): The base directory where the input and output files are located.
    - input_file_name (str): The name of the input file containing multipart features.
    - output_file_name (str): The name of the output file that will contain the single part features.

    Returns:
    None: The multipart features are split and saved as single parts in the output file.
    """
    input_path = os.path.join(base_output_path, input_file_name)
    output_path = os.path.join(base_output_path, output_file_name)

    processing.run("native:multiparttosingleparts", {
        'INPUT': input_path,
        'OUTPUT': output_path
    })

    print("Splitting into single parts completed.")



def calculate_area(base_output_path, input_file, output_file):
    """
    Calculates the area for each feature in a vector layer and stores the result in a new field.

    Parameters:
    - base_output_path (str): The base directory where the input and output files are located.
    - input_file (str): The name of the input vector file.
    - output_file (str): The name of the output file that will contain the features with calculated areas.

    Returns:
    None: The areas are calculated and saved in the 'AREA' field of the output file.
    """
    input_path_8 = os.path.join(base_output_path, input_file)
    output_path_8 = os.path.join(base_output_path, output_file)

    processing.run("native:fieldcalculator", {
        'INPUT': input_path_8,
        'FIELD_NAME': 'AREA',
        'FIELD_TYPE': 0,  # Numeric field
        'FIELD_LENGTH': 10,
        'FIELD_PRECISION': 2,
        'FORMULA': ' $area',
        'OUTPUT': output_path_8
    })

    print("Area calculation completed.")


def filter_areas(base_output_path, input_file, output_file, variable):
    """
    Filters features from a vector layer based on a given expression.

    Parameters:
    - base_output_path (str): The base directory where the input and output files are located.
    - input_file (str): The name of the input vector file containing calculated areas.
    - output_file (str): The name of the output file that will contain the filtered features.
    - variable (str): The expression used for filtering (e.g., "AREA > 20000").

    Returns:
    None: The filtered features are saved in the output file.
    """
    input_path = os.path.join(base_output_path, input_file)
    output_path = os.path.join(base_output_path, output_file)

    processing.run("native:extractbyexpression", {
        'INPUT': input_path,
        'EXPRESSION': variable,
        'OUTPUT': output_path
    })

    print("Filtering areas based on the expression completed.")


def intersection_exposure_bdot(base_output_path, base_layer, overlay_layer, output_file_name):
    """
    Computes the intersection between two vector layers.

    Parameters:
    - base_output_path (str): The base directory where the input and output files are located.
    - base_layer (str): The name of the base layer containing the features to intersect.
    - overlay_layer (str): The name of the overlay layer.
    - output_file_name (str): The name of the output file that will contain the intersection result.

    Returns:
    None: The intersection result is saved in the output file.
    """
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

    print("Intersection between exposure and BDOT layers completed.")


def group_layer(base_output_path, base_layer, output_layer_group):
    """
    Groups multiple features in a vector layer into a single group.

    Parameters:
    - base_output_path (str): The base directory where the input and output files are located.
    - base_layer (str): The name of the input layer to be grouped.
    - output_layer_group (str): The name of the output file that will contain the grouped features.

    Returns:
    None: The grouped features are saved in the output file.
    """
    input_path_6 = os.path.join(base_output_path, base_layer)
    output_path_6 = os.path.join(base_output_path, output_layer_group)

    processing.run("native:collect", {
        'INPUT': input_path_6,
        'FIELD': [],
        'OUTPUT': output_path_6
    })


def repair_geometry(base_output_path, base_layer, output_layer_name_repair):
    """
    Repairs any invalid geometries in a vector layer.

    Parameters:
    - base_output_path (str): The base directory where the input and output files are located.
    - base_layer (str): The name of the input layer with potentially invalid geometries.
    - output_layer_name_repair (str): The name of the output file that will contain the repaired geometries.

    Returns:
    None: The repaired geometries are saved in the output file.
    """
    input_path_6 = os.path.join(base_output_path, base_layer)
    output_path_6 = os.path.join(base_output_path, output_layer_name_repair)

    processing.run("native:fixgeometries", {
        'INPUT': input_path_6,
        'METHOD': 1,
        'OUTPUT': output_path_6
    })


def difference_between_layers(base_output_path, base_layer, overlay_layer, output_file_name, variable_to_area):
    """
    Computes the difference between two vector layers.

    Parameters:
    - base_output_path (str): The base directory where the input and output files are located.
    - base_layer (str): The name of the base vector layer.
    - overlay_layer (str): The name of the overlay vector layer.
    - output_file_name (str): The name of the output file that will contain the difference result.
    - variable_to_area (str): A variable related to the area calculation.

    Returns:
    None: The difference between the layers is saved in the output file.
    """
    input_path = os.path.join(base_output_path, base_layer)
    output_path = os.path.join(base_output_path, output_file_name)
    overlay_layer = os.path.join(base_output_path, overlay_layer)

    processing.run("native:difference", {
        'INPUT': input_path,
        'OVERLAY': overlay_layer,
        'OUTPUT': output_path,
        'GRID_SIZE': None
    })

##STEP 3##

#1 raster to vector


def process_tif_files(base_input_path, base_output_path, output_file_name, field_name, months):
    """
    Processes .tif files for each month by converting them into vector polygons and saving the output.

    Parameters:
    - base_input_path (str): The base directory containing the input .tif files.
    - base_output_path (str): The base directory where the output files will be saved.
    - output_file_name (str): The base name for the output shapefiles.
    - field_name (str): The name of the field to store polygon data from the raster conversion.
    - months (list): A list of month names (e.g., ["january", "february"]) to process.

    Returns:
    None: The function iterates through each month, processes the corresponding .tif file, and saves the result as a shapefile.
    """
    create_directory_if_not_exists(base_output_path)

    # Iterate through each month to find and process relevant .tif files
    for month in months:
        # Define the input file path pattern for the current month
        file_pattern = f"MAP_{month.upper()}_CLIPPED.tif"

        # Search for files that match the pattern in the base input directory
        for file in os.listdir(base_input_path):
            if file.endswith(".tif") and file_pattern in file:
                input_file_path = os.path.join(base_input_path, file)

                # Define the output file path for the current month
                output_shapefile_path = os.path.join(base_output_path, f"{output_file_name}_{month}.shp")

                # Convert the .tif raster to vector polygons
                processing.run("gdal:polygonize", {
                    'INPUT': input_file_path,
                    'BAND': 1,
                    'FIELD': field_name,
                    'EIGHT_CONNECTEDNESS': False,
                    'EXTRA': '',
                    'OUTPUT': output_shapefile_path
                })
                print(f"Processed {file} for {month}.")


def solar_radiation_photovoltaic_area(base_output_path, photovoltaic_area_path, province, output_file_name):
    """
    Performs an intersection between solar radiation data and photovoltaic area vectors for a given province.

    Parameters:
    - base_output_path (str): The base directory where intermediate and output files will be saved.
    - photovoltaic_area_path (str): The file path of the photovoltaic area vector data.
    - province (str): The province code (e.g., "02" for Dolnośląskie).
    - output_file_name (str): The name of the output file containing the final intersection results.

    Returns:
    None: The function processes the solar radiation data for each month, intersects it with the photovoltaic area,
          renames fields, and outputs the final file containing data for all months.
    """
    import os

    # Create a support folder for intermediate files
    support_folder = os.path.join(base_output_path, "support_solar_radiation_vector")
    create_directory_if_not_exists(support_folder)

    # Define the list of months to process
    months = [
        "january", "february", "march", "april",
        "may", "june", "july", "august",
        "september", "october", "november", "december"
    ]

    # Dictionary containing province details (name and a numeric identifier)
    provinces = {
        "02": ("dolnoslaskie", "337"),
        "04": ("kujawsko_pomorskie", "994"),
        "06": ("lubelskie", "3700"),
        "08": ("lubuskie", "333"),
        "10": ("lodzkie", "340"),
        "12": ("malopolskie", "283"),
        "14": ("mazowieckie", "330"),
        "16": ("opolskie", "1833"),
        "18": ("podkarpackie", "332"),
        "20": ("podlaskie", "335"),
        "22": ("pomorskie", "336"),
        "24": ("slaskie", "238"),
        "26": ("swietokrzyskie", "370"),
        "28": ("warminsko_mazurskie", "341"),
        "30": ("wielkopolskie", "308"),
        "32": ("zachodniopomorskie", "339")
    }

    # Loop through each month to process the solar radiation data
    for index, month in enumerate(months, start=1):
        # Define file paths for the current month's solar radiation data and output
        input_support_file = os.path.join(base_output_path, f"solar_radiation_vector_{province}_{month}.shp")
        output_support_file = os.path.join(support_folder, f"solar_radiation_vector_{province}_{month}.shp")

        # Perform the intersection between the photovoltaic area and the solar radiation data
        processing.run("native:intersection", {
            'INPUT': photovoltaic_area_path,
            'OVERLAY': input_support_file,
            'INPUT_FIELDS': [],
            'OVERLAY_FIELDS': ['Solar_surf'],
            'OVERLAY_FIELDS_PREFIX': '',
            'OUTPUT': output_support_file,
            'GRID_SIZE': None
        })

        # Rename the field in the output file to match the current month
        field_to_rename = 'Solar_surf'
        new_name = f"{month}"
        file_to_rename = f"solar_radiation_vector_{province}_{month}.shp"
        output_file_name_rename = f"solar_radiation_{province}_{month}_rename.shp"

        rename_column(base_output_path=support_folder, file_to_rename=file_to_rename,
                      field_to_rename=field_to_rename, new_name=new_name,
                      output_file_name=output_file_name_rename)

        # Define file paths for joining attributes across months
        input_support_file_index_2_12 = os.path.join(support_folder, f"solar_radiation_vector_{index - 1}_{province}.shp")
        output_support_file_index = os.path.join(support_folder, f"solar_radiation_vector_{index}_{province}.shp")
        output_finally_file = os.path.join(base_output_path, output_file_name)
        output = os.path.join(support_folder, output_file_name_rename)

        # Conditionally join attributes to create a cumulative file across months
        if index == 1:
            # First month: join attributes between the photovoltaic area and solar radiation for the current month
            processing.run("native:joinattributestable", {
                'INPUT': photovoltaic_area_path,
                'FIELD': 'ID',
                'INPUT_2': output,
                'FIELD_2': 'ID',
                'FIELDS_TO_COPY': [f"{month}"],
                'METHOD': 1,
                'DISCARD_NONMATCHING': True,
                'PREFIX': '',
                'OUTPUT': output_support_file_index
            })

        elif index == 12:
            # Last month: join the attributes from the cumulative file to create the final output
            processing.run("native:joinattributestable", {
                'INPUT': input_support_file_index_2_12,
                'FIELD': 'ID',
                'INPUT_2': output,
                'FIELD_2': 'ID',
                'FIELDS_TO_COPY': [f"{month}"],
                'METHOD': 1,
                'DISCARD_NONMATCHING': True,
                'PREFIX': '',
                'OUTPUT': output_finally_file
            })

        else:
            # Intermediate months: continue joining attributes between months
            processing.run("native:joinattributestable", {
                'INPUT': input_support_file_index_2_12,
                'FIELD': 'ID',
                'INPUT_2': output,
                'FIELD_2': 'ID',
                'FIELDS_TO_COPY': [f"{month}"],
                'METHOD': 1,
                'DISCARD_NONMATCHING': True,
                'PREFIX': '',
                'OUTPUT': output_support_file_index
            })


def wind_speed_farm_area(base_output_path, wind_area_path, province, output_file_name):
    """
    Process wind speed data by intersecting wind farm area data with monthly wind speed vector data for a given province.
    The function performs the following tasks:

    1. Creates a support folder for storing intermediate shapefiles.
    2. Iterates over each month of the year to intersect wind farm areas with monthly wind speed data.
    3. Renames a field in the result for each month.
    4. Joins the data for all months into a final shapefile.

    Parameters:
    ----------
    base_output_path : str
        The directory path where output files will be stored.
    wind_area_path : str
        The path to the wind farm area shapefile used for intersection with wind speed data.
    province : str
        The code of the province (e.g., '02' for Dolnośląskie) where wind speed data is processed.
    output_file_name : str
        The name of the final output shapefile that will contain the joined data for all months.

    Returns:
    -------
    None
    """

    # Import necessary modules
    import os

    # Create a folder to store support files
    support_folder = os.path.join(base_output_path, "support_wind_speed_vector")
    create_directory_if_not_exists(support_folder)

    # Define the list of months
    months = [
        "january", "february", "march", "april",
        "may", "june", "july", "august",
        "september", "october", "november", "december"
    ]

    # Define a dictionary for provinces (province code -> (name, some value))
    provinces = {
        "02": ("dolnoslaskie", "337"),
        "04": ("kujawsko_pomorskie", "994"),
        "06": ("lubelskie", "3700"),
        "08": ("lubuskie", "333"),
        "10": ("lodzkie", "340"),
        "12": ("malopolskie", "283"),
        "14": ("mazowieckie", "330"),
        "16": ("opolskie", "1833"),
        "18": ("podkarpackie", "332"),
        "20": ("podlaskie", "335"),
        "22": ("pomorskie", "336"),
        "24": ("slaskie", "238"),
        "26": ("swietokrzyskie", "370"),
        "28": ("warminsko_mazurskie", "341"),
        "30": ("wielkopolskie", "308"),
        "32": ("zachodniopomorskie", "339")
    }

    # Loop through each month to process wind speed data
    for index, month in enumerate(months, start=1):
        # Define paths for input and output files
        input_support_file = os.path.join(base_output_path, f"wind_speed_vector_{province}_{month}.shp")
        output_support_file = os.path.join(support_folder, f"wind_speed_vector_{province}_{month}.shp")

        # Perform intersection between the wind area and wind speed vector data
        processing.run("native:intersection",
                       {'INPUT': wind_area_path,
                        'OVERLAY': input_support_file,
                        'INPUT_FIELDS': [],
                        'OVERLAY_FIELDS': ['Wind_speed'],
                        'OVERLAY_FIELDS_PREFIX': '',
                        'OUTPUT': output_support_file,
                        'GRID_SIZE': None})

        # Rename the "Wind_speed" field to the current month
        field_to_rename = 'Wind_speed'
        new_name = f"{month}"
        file_to_rename = f"wind_speed_vector_{province}_{month}.shp"
        output_file_name_rename = f"wind_speed_vector_{province}_{month}_rename.shp"

        # Call the rename_column function to rename the field
        rename_column(base_output_path=support_folder, file_to_rename=file_to_rename, field_to_rename=field_to_rename,
                      new_name=new_name, output_file_name=output_file_name_rename)

        # Define paths for support files to stack data across months
        input_support_file_index_2_12 = os.path.join(support_folder, f"wind_speed_vector_{index - 1}_{province}.shp")
        output_support_file_index = os.path.join(support_folder, f"wind_speed_vector_{index}_{province}.shp")
        output_finally_file = os.path.join(base_output_path, output_file_name)
        output = os.path.join(support_folder, output_file_name_rename)

        # Combine the data from all months into the final file
        if index == 1:
            processing.run("native:joinattributestable",
                           {'INPUT': wind_area_path,
                            'FIELD': 'ID',
                            'INPUT_2': output,
                            'FIELD_2': 'ID',
                            'FIELDS_TO_COPY': [f"{month}"],
                            'METHOD': 1,
                            'DISCARD_NONMATCHING': True,
                            'PREFIX': '',
                            'OUTPUT': output_support_file_index})

        elif index == 12:
            processing.run("native:joinattributestable",
                           {'INPUT': input_support_file_index_2_12,
                            'FIELD': 'ID',
                            'INPUT_2': output,
                            'FIELD_2': 'ID',
                            'FIELDS_TO_COPY': [f"{month}"],
                            'METHOD': 1,
                            'DISCARD_NONMATCHING': True,
                            'PREFIX': '',
                            'OUTPUT': output_finally_file})
        else:
            processing.run("native:joinattributestable",
                           {'INPUT': input_support_file_index_2_12,
                            'FIELD': 'ID',
                            'INPUT_2': output,
                            'FIELD_2': 'ID',
                            'FIELDS_TO_COPY': [f"{month}"],
                            'METHOD': 1,
                            'DISCARD_NONMATCHING': True,
                            'PREFIX': '',
                            'OUTPUT': output_support_file_index})

