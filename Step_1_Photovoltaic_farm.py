# Path to folder with modules
import sys
sys.path.append('D:\GEOWORLDLOOK\OZE\Renewable_energy_optimum_location')

from Renewable_energy_optimum_location_function import *


# Przykładowe wywołanie funkcji:
base_input_path = "D:/GEOWORLDLOOK/OZE/PILOT/Data"
base_output_path = "D:/GEOWORLDLOOK/OZE/PILOT/Step_1_Photovoltaic_farm"

#create_output_folder
create_directory_if_not_exists(base_output_path)


#1 Define layers which use to looking for photovoltaic areas
#Topographic Object Database

layer_paths_2 = [
    'D:/GEOWORLDLOOK/OZE/PILOT/Data/BDOT/PL.PZGiK.335.BDOT10k.20_OT_PTGN_A.shp',
    'D:/GEOWORLDLOOK/OZE/PILOT/Data/BDOT/PL.PZGiK.335.BDOT10k.20_OT_PTRK_A.shp',
    'D:/GEOWORLDLOOK/OZE/PILOT/Data/BDOT/PL.PZGiK.335.BDOT10k.20_OT_PTTR_A_ROSLINOSC_TRAWIASTA.shp'
]
#1 Merge layers
#Output file name




provinces = wojewodztwa = {
    "02":("dolnoslaskie", "337"),
    "04":("kujawsko_pomorskie", "994"),
    "06":("lubelskie", "3700"),
    "08": ("lubuskie", "333"),
    "10":("lodzkie", "340"),
    "12":("malopolskie", "283"),
    "14":("mazowieckie", "330"),
    "16":("opolskie", "1833"),
    "18":("podkarpackie", "332"),
    "20":("podlaskie", "335"),
    "22":("pomorskie", "336"),
    "24":("slaskie", "238"),
    "26":("swietokrzyskie", "370"),
    "28":("warminsko_mazurskie", "341"),
    "30":("wielkopolskie", "308"),
    "32":("zachodniopomorskie", "339")
}

for key,(province,number) in provinces.items():





    layer_paths = [
        f"D:/GEOWORLDLOOK/OZE/PILOT/Data/BDOT/PL.PZGiK.{number}.BDOT10k.{key}__OT_PTGN_A.shp",
        f"D:/GEOWORLDLOOK/OZE/PILOT/Data/BDOT/PL.PZGiK.{number}.BDOT10k.{key}__OT_PTRK_A.shp",
        f"D:/GEOWORLDLOOK/OZE/PILOT/Data/BDOT/PL.PZGiK.{number}.BDOT10k.{key}__OT_PTTR_A_ROSLINOSC_TRAWIASTA.shp"
    ]
    print(layer_paths_2)
    print(layer_paths)
    merge_areas = f"Merge_layers_area_{province}.shp"
    output_path_1 = os.path.join(base_output_path, merge_areas)
    processing.run("native:mergevectorlayers", {
        'LAYERS': [f"D:/GEOWORLDLOOK/OZE/PILOT/Data/BDOT/PL.PZGiK.{number}.BDOT10k.{key}__OT_PTGN_A.shp",
                   f"D:/GEOWORLDLOOK/OZE/PILOT/Data/BDOT/PL.PZGiK.{number}.BDOT10k.{key}__OT_PTRK_A.shp",
                   f"D:/GEOWORLDLOOK/OZE/PILOT/Data/BDOT/PL.PZGiK.{number}.BDOT10k.{key}__OT_PTTR_A_ROSLINOSC_TRAWIASTA.shp"],
        'CRS': QgsCoordinateReferenceSystem('EPSG:2180'), 'OUTPUT': output_path_1})


    repair_layer_file = f"repair_layer_{province}.shp"
    repair_geometry(base_output_path=base_output_path, base_layer=merge_areas,
                    output_layer_name_repair=repair_layer_file)

    split_potencial_area_repair = f"repair_layer_split_{province}.shp"
    split_into_single_parts(base_output_path = base_output_path,input_file_name=repair_layer_file ,output_file_name = split_potencial_area_repair)

    #2 Terrain aspect

    # Input paths
    input_folder_aspect = base_input_path + "/NMT/"
    input_file_aspect = f"{province}_geotif.tif"

    # Output paths
    output_folder_aspect = base_output_path + "/TERRAIN_ASPECT/"
    output_file_aspect = f"{province}_aspect.tif"


    calculate_terrain_aspect(input_folder = input_folder_aspect,input_file_name = input_file_aspect,
                             output_folder = output_folder_aspect, output_file_name = output_file_aspect)


    #3 Convert terrain aspect to vector data


    output_folder_raster = base_output_path + "/EXPOSURE_WS_S_ES/"
    output_raster_file = f"RASTER_WS_S_ES_{province}.tif"

    output_vector_folder = base_output_path + "/VECTOR_EXPOSURE/"
    output_vector_file = f"EXPOSURE_VECTOR_{province}.shp"

    # Perform raster to vector conversion
    raster_to_vector_conversion(raster_input = output_folder_aspect + output_file_aspect, output_folder_raster = output_folder_raster
                                , output_raster_filename = output_raster_file, output_vector_folder = output_vector_folder, output_vector_file=output_vector_file)


    #4 Filter value, where area fit to cryterium
    filter_value = '"DN" = 1'

    output_file_filter = f"EXPOSURE_VECTOR_TRUE_{province}.shp"

    filter_values_condition_1(filter_value = filter_value, base_input_path= output_vector_folder ,input_filename=output_vector_file, base_output_path = base_output_path
                              ,output_file = output_file_filter)




    #5 Select area fit to cryterium and to free area from bdot

    input_filename = output_vector_file
    output_file_5 = output_file_filter
    output_potencial_area = f"POTENCIAL_PHOTOVOLTAIC_AREA_{province}.shp"


    intersection_exposure_bdot(base_output_path = base_output_path ,base_layer = output_file_filter
                               ,overlay_layer=split_potencial_area_repair, output_file_name = output_potencial_area)

    #6 Split to single parts
    split_potencial_area = f"SPLIT_POTENCIAL_AREA_{province}.shp"

    split_into_single_parts(base_output_path = base_output_path,input_file_name=output_potencial_area ,output_file_name = split_potencial_area)

    #7 calculate area
    calculate_split_area= f"calculate_split_area_{province}.shp"
    calculate_area(base_output_path = base_output_path ,input_file = split_potencial_area,output_file = calculate_split_area)

    #8 Select area more than value (individual parametr)
    filter_area_more_than = f"filter_area_by_area_condition_{province}.shp"
    condition ='"AREA" > 20000'
    filter_areas(base_output_path = base_output_path,input_file = calculate_split_area,output_file = filter_area_more_than, variable = condition)

    #9 Add id to column to select by id in next steps
    add_id_to_file = f"area_id_{province}.shp"
    add_id(base_output_path = base_output_path,input_file= filter_area_more_than ,output_file   = add_id_to_file)

    #10
    input_voltage_path_11 = base_input_path + f"/BDOT/PL.PZGiK.{number}.BDOT10k.{key}__OT_SULN_L.shp"
    medium_power_line = f"medium_power_line_{province}.shp"
    #11 select specific voltage lines
    select_from_layer(base_output_path = base_output_path,input_path = input_voltage_path_11,  output_file_name = medium_power_line)


    #12 calculate distanse to power lines
    distance_to_line = f"distance_to_line_{province}.shp"
    calculate_distance(base_output_path = base_output_path,source_layer = add_id_to_file, destination_layer = medium_power_line,output_file_name = distance_to_line)


    #13 Join to calculeted area by id
    field_1 = 'ID'
    field_2 ='ID'
    field_to_copy = 'distance'
    area_with_distance_to_power_line = f"area_with_distance_to_power_line_{province}.shp"

    join_attributes_with_distances(base_output_path = base_output_path,field_1 = field_1, field_2 = field_2, field_to_copy = field_to_copy
                                   ,base_file=add_id_to_file,file_from_copy=distance_to_line,output_file_name =area_with_distance_to_power_line)

    #14 Filter area by parametr
    #distance in meters
    variable_14 = '"distance" < 500'
    area_in_distance_criterium_to_line = f"area_distance_criterium_line_{province}.shp"
    filter_areas(base_output_path = base_output_path,input_file = area_with_distance_to_power_line
                 ,output_file = area_in_distance_criterium_to_line, variable = variable_14)

    #15 Rename distance to voltage column
    new_name = 'LINE_DISTANCE'
    field_to_rename ='distance'
    area_distance_criterium_line_rename = f"area_distance_criterium_line_rename_{province}.shp"
    rename_column(base_output_path = base_output_path, file_to_rename=area_in_distance_criterium_to_line,field_to_rename = field_to_rename
    , new_name= new_name, output_file_name = area_distance_criterium_line_rename)

    #16

    distance_to_road = f"distance_to_road_{province}.shp"
    road_file_path = base_input_path + f"/BDOT/PL.PZGiK.{number}.BDOT10k.{key}__OT_SKJZ_L.shp"


    calculate_distance(base_output_path = base_output_path,source_layer=area_distance_criterium_line_rename
                       ,destination_layer =road_file_path ,output_file_name = distance_to_road)

    #17 Select column by id from vector with distance to new column in area data
    select_column_distance_road = f"select_column_distance_to_road_{province}.shp"
    field_1 = 'ID'
    field_2 = 'ID'
    field_to_copy = 'distance'
    join_attributes_with_distances(field_1,field_2
        ,field_to_copy,base_output_path,base_file= area_distance_criterium_line_rename, file_from_copy=distance_to_road,output_file_name =select_column_distance_road)


    #18 Rename column with distance to road
    photovoltaic_area = f"photovoltaic_area_{province}.shp"
    rename_column(base_output_path=base_output_path,file_to_rename=select_column_distance_road,field_to_rename = 'distance'
                  ,new_name='ROAD_DISTANCE',output_file_name = photovoltaic_area)