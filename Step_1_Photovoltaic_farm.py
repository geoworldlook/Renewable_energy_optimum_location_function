# Path to folder with modules
import sys
sys.path.append('D:/GEOWORLDLOOK/OZE/Renewable_energy_optimum_location')

from Renewable_energy_optimum_location_function import *

# Define base input and output paths
base_input_path = "D:/GEOWORLDLOOK/OZE/PILOT/Data"
base_output_path = "D:/GEOWORLDLOOK/OZE/PILOT/Step_1_Photovoltaic_farm"

# Create the output folder if it does not exist
create_directory_if_not_exists(base_output_path)

# 1. Define layers used for identifying potential photovoltaic areas
# Topographic Object Database (BDOT10k)

layer_paths_2 = [
    'D:/GEOWORLDLOOK/OZE/PILOT/Data/BDOT/PL.PZGiK.335.BDOT10k.20_OT_PTGN_A.shp',
    'D:/GEOWORLDLOOK/OZE/PILOT/Data/BDOT/PL.PZGiK.335.BDOT10k.20_OT_PTRK_A.shp',
    'D:/GEOWORLDLOOK/OZE/PILOT/Data/BDOT/PL.PZGiK.335.BDOT10k.20_OT_PTTR_A_ROSLINOSC_TRAWIASTA.shp'
]

# Provinces and their corresponding codes
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

# Loop through each province to perform operations
for key, (province, number) in provinces.items():
    # Layer paths for each province
    layer_paths = [
        f"D:/GEOWORLDLOOK/OZE/PILOT/Data/BDOT/PL.PZGiK.{number}.BDOT10k.{key}__OT_PTGN_A.shp",
        f"D:/GEOWORLDLOOK/OZE/PILOT/Data/BDOT/PL.PZGiK.{number}.BDOT10k.{key}__OT_PTRK_A.shp",
        f"D:/GEOWORLDLOOK/OZE/PILOT/Data/BDOT/PL.PZGiK.{number}.BDOT10k.{key}__OT_PTTR_A_ROSLINOSC_TRAWIASTA.shp"
    ]

    # Print the paths (for debugging purposes)
    print(layer_paths_2)
    print(layer_paths)

    # Merge the layers for each province
    merge_areas = f"Merge_layers_area_{province}.shp"
    output_path_1 = os.path.join(base_output_path, merge_areas)
    processing.run("native:mergevectorlayers", {
        'LAYERS': layer_paths,
        'CRS': QgsCoordinateReferenceSystem('EPSG:2180'),
        'OUTPUT': output_path_1
    })

    # Repair the merged layer geometry
    repair_layer_file = f"repair_layer_{province}.shp"
    repair_geometry(base_output_path=base_output_path, base_layer=merge_areas,
                    output_layer_name_repair=repair_layer_file)

    # Split the repaired geometry into individual parts
    split_potencial_area_repair = f"repair_layer_split_{province}.shp"
    split_into_single_parts(base_output_path=base_output_path, input_file_name=repair_layer_file, output_file_name=split_potencial_area_repair)

    # 2. Terrain aspect calculation
    input_folder_aspect = base_input_path + "/NMT/"
    input_file_aspect = f"{province}_geotif.tif"
    output_folder_aspect = base_output_path + "/TERRAIN_ASPECT/"
    output_file_aspect = f"{province}_aspect.tif"

    # Calculate terrain aspect
    calculate_terrain_aspect(input_folder=input_folder_aspect, input_file_name=input_file_aspect,
                             output_folder=output_folder_aspect, output_file_name=output_file_aspect)

    # 3. Convert terrain aspect to vector data
    output_folder_raster = base_output_path + "/EXPOSURE_WS_S_ES/"
    output_raster_file = f"RASTER_WS_S_ES_{province}.tif"
    output_vector_folder = base_output_path + "/VECTOR_EXPOSURE/"
    output_vector_file = f"EXPOSURE_VECTOR_{province}.shp"

    # Raster to vector conversion
    raster_to_vector_conversion(raster_input=output_folder_aspect + output_file_aspect, output_folder_raster=output_folder_raster,
                                output_raster_filename=output_raster_file, output_vector_folder=output_vector_folder, output_vector_file=output_vector_file)

    # 4. Filter areas that meet the specified criteria
    filter_value = '"DN" = 1'
    output_file_filter = f"EXPOSURE_VECTOR_TRUE_{province}.shp"
    filter_values_condition_1(filter_value=filter_value, base_input_path=output_vector_folder, input_filename=output_vector_file,
                              base_output_path=base_output_path, output_file=output_file_filter)

    # 5. Select areas that fit criteria and overlay them with BDOT data
    output_potencial_area = f"POTENCIAL_PHOTOVOLTAIC_AREA_{province}.shp"
    intersection_exposure_bdot(base_output_path=base_output_path, base_layer=output_file_filter, overlay_layer=split_potencial_area_repair,
                               output_file_name=output_potencial_area)

    # 6. Split potential areas into individual parts
    split_potencial_area = f"SPLIT_POTENCIAL_AREA_{province}.shp"
    split_into_single_parts(base_output_path=base_output_path, input_file_name=output_potencial_area, output_file_name=split_potencial_area)

    # 7. Calculate area of split parts
    calculate_split_area = f"calculate_split_area_{province}.shp"
    calculate_area(base_output_path=base_output_path, input_file=split_potencial_area, output_file=calculate_split_area)

    # 8. Filter areas larger than the given value
    filter_area_more_than = f"filter_area_by_area_condition_{province}.shp"
    condition = '"AREA" > 20000'
    filter_areas(base_output_path=base_output_path, input_file=calculate_split_area, output_file=filter_area_more_than, variable=condition)

    # 9. Add ID column to the filtered areas for future selections
    add_id_to_file = f"area_id_{province}.shp"
    add_id(base_output_path=base_output_path, input_file=filter_area_more_than, output_file=add_id_to_file)

    # 10. Select medium power lines from BDOT data
    input_voltage_path_11 = base_input_path + f"/BDOT/PL.PZGiK.{number}.BDOT10k.{key}__OT_SULN_L.shp"
    medium_power_line = f"medium_power_line_{province}.shp"
    select_from_layer(base_output_path=base_output_path, input_path=input_voltage_path_11, output_file_name=medium_power_line)

    # 11. Calculate distance to power lines
    distance_to_line = f"distance_to_line_{province}.shp"
    calculate_distance(base_output_path=base_output_path, source_layer=add_id_to_file, destination_layer=medium_power_line, output_file_name=distance_to_line)

    # 12. Join calculated distances to area data by ID
    field_1 = 'ID'
    field_2 = 'ID'
    field_to_copy = 'distance'
    area_with_distance_to_power_line = f"area_with_distance_to_power_line_{province}.shp"
    join_attributes_with_distances(base_output_path=base_output_path, field_1=field_1, field_2=field_2, field_to_copy=field_to_copy,
                                   base_file=add_id_to_file, file_from_copy=distance_to_line, output_file_name=area_with_distance_to_power_line)

    # 13. Filter areas based on distance criteria (distance < 500m)
    variable_14 = '"distance" < 500'
    area_in_distance_criterium_to_line = f"area_distance_criterium_line_{province}.shp"
    filter_areas(base_output_path=base_output_path, input_file=area_with_distance_to_power_line, output_file=area_in_distance_criterium_to_line, variable=variable_14)

    # 14. Rename distance column to LINE_DISTANCE
    new_name = 'LINE_DISTANCE'
    field_to_rename = 'distance'
    area_distance_criterium_line_rename = f"area_distance_criterium_line_rename_{province}.shp"
    rename_column(base_output_path=base_output_path, input_file=area_in_distance_criterium_to_line, output_file=area_distance_criterium_line_rename,
                  current_field=field_to_rename, new_field=new_name)

    # 16. Calculate distance to roads
    distance_to_road = f"distance_to_road_{province}.shp"
    road_file_path = base_input_path + f"/BDOT/PL.PZGiK.{number}.BDOT10k.{key}__OT_SKJZ_L.shp"

    # Calculate the distance from areas to roads
    calculate_distance(base_output_path=base_output_path,
                       source_layer=area_distance_criterium_line_rename,
                       destination_layer=road_file_path,
                       output_file_name=distance_to_road)

    # 17. Select and join the distance column by ID from the road distance data to the area data
    select_column_distance_road = f"select_column_distance_to_road_{province}.shp"
    field_1 = 'ID'
    field_2 = 'ID'
    field_to_copy = 'distance'

    # Join the road distance column to the area layer
    join_attributes_with_distances(field_1=field_1, field_2=field_2, field_to_copy=field_to_copy,
                                   base_output_path=base_output_path, base_file=area_distance_criterium_line_rename,
                                   file_from_copy=distance_to_road, output_file_name=select_column_distance_road)

    # 18. Rename the distance column to 'ROAD_DISTANCE'
    photovoltaic_area = f"photovoltaic_area_{province}.shp"
    rename_column(base_output_path=base_output_path, file_to_rename=select_column_distance_road,
                  field_to_rename='distance', new_name='ROAD_DISTANCE', output_file_name=photovoltaic_area)
