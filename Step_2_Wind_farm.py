# Import required modules
import sys
import os

# Adding the path to the folder containing custom modules
sys.path.append('D:/GEOWORLDLOOK/OZE/Renewable_energy_optimum_location')

# Importing all functions from the custom module
from Renewable_energy_optimum_location_function import *

# Define paths for input and output
base_input_path = "D:/GEOWORLDLOOK/OZE/PILOT/Data"
base_output_path = "D:/GEOWORLDLOOK/OZE/PILOT/Step_2_Wind_Farm"

# Dictionary containing province codes, names, and identification numbers
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

# Iterate through each province, performing geospatial operations for wind farm locations
for key, (province, number) in provinces.items():
    """
    Looping through each province to perform various operations like creating buffers, merging layers,
    calculating areas, filtering, and calculating distances for optimal wind farm location.
    """

    # 1. Create output folder if it doesn't exist
    create_directory_if_not_exists(base_output_path)

    # 2. Create a buffer around areas of interest
    distance = 800  # Buffer distance in meters
    input_path = os.path.join(base_input_path, f"BDOT/PL.PZGiK.{number}.BDOT10k.{key}__OT_BUBD_A.shp")
    output_file_buffer = f"WIND_FARM_BUFFER_{province}.shp"

    buffer(base_output_path=base_output_path, input_path=input_path, output_file=output_file_buffer, distance=distance)

    # 3. Define paths for layers to merge (potential wind farm areas)
    layer_paths = [
        f"D:/GEOWORLDLOOK/OZE/PILOT/Data/BDOT/PL.PZGiK.{number}.BDOT10k.{key}__OT_PTGN_A.shp",
        f"D:/GEOWORLDLOOK/OZE/PILOT/Data/BDOT/PL.PZGiK.{number}.BDOT10k.{key}__OT_PTRK_A.shp",
        f"D:/GEOWORLDLOOK/OZE/PILOT/Data/BDOT/PL.PZGiK.{number}.BDOT10k.{key}__OT_PTTR_A_ROSLINOSC_TRAWIASTA.shp"
    ]

    # 4. Merge potential wind farm areas into one shapefile
    merge_areas = os.path.join("D:/GEOWORLDLOOK/OZE/PILOT/Step_1_Photovoltaic_farm", f"Merge_layers_area_{province}.shp")
    merge_vector_layers(layer_paths=layer_paths, base_output_path=base_output_path, output_file_name=merge_areas)

    # 5. Split merged areas into individual parts
    output_file_name_merge_area_split = f"merge_area_split_{province}.shp"
    split_into_single_parts(base_output_path=base_output_path, input_file_name=merge_areas, output_file_name=output_file_name_merge_area_split)

    # 6. Calculate the area of each part
    output_file_3 = f"calculate_area_split_{province}.shp"
    calculate_area(base_output_path=base_output_path, input_file=output_file_name_merge_area_split, output_file=output_file_3)

    # 7. Filter areas larger than 10,000 square meters
    output_file_4 = f"calculate_area_split_above_10000_{province}.shp"
    variable = '"AREA" > 10000'
    filter_areas(base_output_path=base_output_path, input_file=output_file_3, output_file=output_file_4, variable=variable)

    # 8. Group layers by common attributes
    group_layer_file = f"grouping_layer_in_diff_{province}.shp"
    group_layer(base_output_path=base_output_path, base_layer=output_file_4, output_layer_group=group_layer_file)

    # 9. Repair geometry of the grouped layers
    repair_layer_file = f"repair_layer_in_diff_{province}.shp"
    repair_geometry(base_output_path=base_output_path, base_layer=group_layer_file, output_layer_name_repair=repair_layer_file)

    # 10. Find the difference between buffered areas and repaired layers
    wind_farm_area = f"wind_farm_area_{province}.shp"
    variable_to_area = '"AREA" > 10000'
    difference_between_layers(base_output_path=base_output_path, base_layer=repair_layer_file,
                              overlay_layer=output_file_buffer, output_file_name=wind_farm_area, variable_to_area=variable_to_area)

    # 11. Split the resulting wind farm areas into single parts
    split_layer = f"split_layer_in_diff_{province}.shp"
    split_into_single_parts(base_output_path=base_output_path, input_file_name=wind_farm_area, output_file_name=split_layer)

    # 12. Calculate the area of each part again
    calculate_area_layer = f"calculate_area_in_diff_{province}.shp"
    calculate_area(base_output_path=base_output_path, input_file=split_layer, output_file=calculate_area_layer)

    # 13. Filter areas larger than 10,000 square meters again
    filter_area_layer = f"filter_area_in_diff_{province}.shp"
    filter_areas(base_output_path=base_output_path, input_file=calculate_area_layer, output_file=filter_area_layer, variable=variable_to_area)

    # 14. Add unique ID to the areas for further processing
    wind_farm_area_id = f"wind_farm_area_id_{province}.shp"
    add_id(base_output_path=base_output_path, input_file=filter_area_layer, output_file=wind_farm_area_id)

    # 15. Calculate the distance from wind farm areas to medium-voltage power lines
    medium_voltage_path = f"D:/GEOWORLDLOOK/OZE/PILOT/Step_1_Photovoltaic_farm"
    medium_power_line = f"medium_power_line_{province}.shp"
    medium_voltage_line = os.path.join(medium_voltage_path, medium_power_line)
    wind_farm_distance_to_line = f"distance_wind_farm_to_line_{province}.shp"
    calculate_distance(base_output_path=base_output_path, source_layer=wind_farm_area_id, destination_layer=medium_voltage_line, output_file_name=wind_farm_distance_to_line)

    # 16. Join calculated distances with wind farm areas by their unique IDs
    field_1 = 'ID'
    field_2 = 'ID'
    field_to_copy = 'distance'
    wind_farm_area_id_distance = f"wind_farm_area_id_distance_{province}.shp"
    join_attributes_with_distances(base_output_path=base_output_path, field_1=field_1, field_2=field_2, field_to_copy=field_to_copy,
                                   base_file=wind_farm_area_id, file_from_copy=wind_farm_distance_to_line, output_file_name=wind_farm_area_id_distance)

    # 17. Filter wind farm areas based on distance from power lines (e.g., areas within 800 meters of power lines)
    variable_wind_farm_line_distance = '"distance" < 800'
    wind_farm_area_with_distance_criterium = f"windfarm_area_{province}.shp"
    filter_areas(base_output_path=base_output_path, input_file=wind_farm_area_id_distance, output_file=wind_farm_area_with_distance_criterium, variable=variable_wind_farm_line_distance)
