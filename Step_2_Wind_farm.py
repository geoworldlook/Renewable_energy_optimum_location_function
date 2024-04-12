# Path to folder with modules
import sys
sys.path.append('D:\GEOWORLDLOOK\OZE\Renewable_energy_optimum_location')

#import script
from Renewable_energy_optimum_location_function import *



#### WIND FARM PATH
base_input_path = "D:/GEOWORLDLOOK/OZE/PILOT/Data"
base_output_path = "D:/GEOWORLDLOOK/OZE/PILOT/Step_2_Wind_Farm"

provinces = {
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


    #create_output_folder
    create_directory_if_not_exists(base_output_path)

    #1 Tworzenie buforu

    distance = 800
    input_path = os.path.join(base_input_path, f"BDOT/PL.PZGiK.{number}.BDOT10k.{key}__OT_BUBD_A.shp")
    output_file_buffer = f"WIND_FARM_BUFFOR_{province}.shp"

    buffer(base_output_path = base_output_path, input_path = input_path, output_file=output_file_buffer,distance=distance)
    #2 Split area

    #3 Define layers which use to looking for photovoltaic areas
    #Topographic Object Database

    layer_paths = [
                    f"D:/GEOWORLDLOOK/OZE/PILOT/Data/BDOT/PL.PZGiK.{number}.BDOT10k.{key}__OT_PTGN_A.shp",
                   f"D:/GEOWORLDLOOK/OZE/PILOT/Data/BDOT/PL.PZGiK.{number}.BDOT10k.{key}__OT_PTRK_A.shp",
                   f"D:/GEOWORLDLOOK/OZE/PILOT/Data/BDOT/PL.PZGiK.{number}.BDOT10k.{key}__OT_PTTR_A_ROSLINOSC_TRAWIASTA.shp"
    ]
    #1 Merge layers potencial area
    #Output file name


    merge_areas = os.path.join("D:/GEOWORLDLOOK/OZE/PILOT/Step_1_Photovoltaic_farm", f"Merge_layers_area_{province}.shp")
    #merge_areas = 'Merge_layers_area.shp'
    #merge_vector_layers(layer_paths = layer_paths,base_output_path = base_output_path,output_file_name = merge_areas)


    input_file_potencial_area = merge_areas
    output_file_name_merge_area_split = f"merge_area_split_{province}.shp"

    split_into_single_parts(base_output_path = base_output_path, input_file_name=input_file_potencial_area, output_file_name = output_file_name_merge_area_split)



    #3 Calculate area
    output_file_3 = f"calculate_area_split_{province}.shp"
    calculate_area(base_output_path = base_output_path, input_file = output_file_name_merge_area_split, output_file =output_file_3)


    #4 Filtr area above 10 000 m2

    output_file_4 = f"calculate_area_split_above_10000_{province}.shp"
    variable ='"AREA" > 10000'
    filter_areas(base_output_path = base_output_path,input_file = output_file_3,output_file = output_file_4, variable = variable)

    # Użyj funkcji group_layer
    group_layer_file = f"grouping_layer_in_diff_{province}.shp"
    group_layer(base_output_path=base_output_path, base_layer=output_file_4, output_layer_group=group_layer_file)

    repair_layer_file = f"repair_layer_in_diff_{province}.shp"
    repair_geometry(base_output_path=base_output_path, base_layer=group_layer_file,
                    output_layer_name_repair=repair_layer_file)

    #5 areas based on BUFFOR AND AREA FREE FROM BDOT
    wind_farm_area = f"wind_farm_area_{province}.shp"
    variable_to_area = '"AREA" > 10000'
    difference_between_layers(base_output_path = base_output_path, base_layer = repair_layer_file
                              , overlay_layer = output_file_buffer, output_file_name = wind_farm_area,variable_to_area=variable_to_area)


    # split data##
    split_layer = f"split_layer_in_diff_{province}.shp"
    split_into_single_parts(base_output_path=base_output_path, input_file_name=wind_farm_area,
                                output_file_name=split_layer)

        # calculate area
    calculate_area_layer = f"calculate_area_in_diff_{province}.shp"
    calculate_area(base_output_path=base_output_path, input_file=split_layer, output_file=calculate_area_layer)

    # filter area

    filter_area_layer = f"filter_area_in_diff_{province}.shp"
    filter_areas(base_output_path=base_output_path, input_file=calculate_area_layer, output_file=filter_area_layer,
                     variable=variable_to_area)


    #6 Add id to column to select by id in next steps
    wind_farm_area_id = f"wind_farm_area_id_{province}.shp"
    add_id(base_output_path,input_file = filter_area_layer,output_file = wind_farm_area_id)

    
    #6 calculate distanse to power lines
    medium_voltage_path = f"D:/GEOWORLDLOOK/OZE/PILOT/Step_1_Photovoltaic_farm"
    medium_power_line = f"medium_power_line_{province}.shp"
    medium_voltage_line = os.path.join(medium_voltage_path,medium_power_line)
    wind_farm_distance_to_line = f"distance_wind_farm_to_line_{province}.shp"
    calculate_distance(base_output_path = base_output_path,source_layer = wind_farm_area_id, destination_layer = medium_voltage_line,output_file_name = wind_farm_distance_to_line)


    #13 Join to calculeted area by id
    field_1 = 'ID'
    field_2 ='ID'
    field_to_copy = 'distance'
    wind_farm_area_id_distance= f"wind_farm_area_id_distance_{province}.shp"

    join_attributes_with_distances(base_output_path = base_output_path,field_1 = field_1, field_2 = field_2, field_to_copy = field_to_copy
                                   ,base_file=wind_farm_area_id,file_from_copy=wind_farm_distance_to_line,output_file_name =wind_farm_area_id_distance)

    #14 Filter area by parametr
    filter_layer = 'filter_area_distance.shp'
    variable_wind_farm_line_distance = '"distance" < 800'
    wind_farm_area_with_distance_criterium = f"windfarm_area_{province}.shp"
    column_distance_name = 'LINE_DISTANCE'
    filter_areas(base_output_path = base_output_path,input_file=wind_farm_area_id_distance
                 , output_file= wind_farm_area_with_distance_criterium,variable=variable_wind_farm_line_distance)



