# Path to folder with modules
import sys
sys.path.append('D:\GEOWORLDLOOK\OZE\Renewable_energy_optimum_location')

#import script
from Renewable_energy_optimum_location_function import *



#### WIND FARM PATH
base_input_path = "D:/GEOWORLDLOOK/OZE/PILOT/TEST_SKRYPTU"
base_output_path = "D:/GEOWORLDLOOK/OZE/PILOT/WIND_FARM"


#1 Tworzenie buforu

distance = 800
input_path = 'D:/GEOWORLDLOOK/OZE/PILOT/BDOT/PL.PZGiK.335.BDOT10k.20_OT_BUBD_A.shp'
output_file_buffer = 'WIND_FARM_BUFFOR.shp'

buffer(base_output_path = base_output_path, input_path = input_path, output_file=output_file_buffer,distance=distance)
#2 Split area

input_file_potencial_area='merge_layers.shp'
output_file_name_2 = "MERGE_ROZBITE_NA_POJEDYNCZE.shp"

split_into_single_parts(base_output_path = base_output_path, input_file_name=input_file_potencial_area, output_file_name = output_file_name_2)



#3 Calculate area
output_file_3 = "calculate_area_split.shp"
calculate_area(base_output_path = base_output_path, input_file = output_file_name_2, output_file =output_file_3)


#4 Filtr area above 10 000 m2

output_file_4 = "calculate_area_split_above_10000.shp"
variable ='"AREA" > 10000'
filter_areas(base_output_path = base_output_path,input_file = output_file_3,output_file = output_file_4, variable = variable)

# Użyj funkcji group_layer
group_layer_file = 'grouping_layer_in_diff.shp'
group_layer(base_output_path=base_output_path, base_layer=output_file_4, output_layer_group=group_layer_file)

repair_layer_file = 'repair_layer_in_diff.shp'
repair_geometry(base_output_path=base_output_path, base_layer=group_layer_file,
                output_layer_name_repair=repair_layer_file)

#5 areas based on BUFFOR AND AREA FREE FROM BDOT
wind_farm_area = 'wind_farm_area.shp'
variable_to_area = '"AREA" > 10000'
difference_between_layers(base_output_path = base_output_path, base_layer = repair_layer_file
                          , overlay_layer = output_file_buffer, output_file_name = wind_farm_area,variable_to_area=variable_to_area)


# split data##
split_layer = 'split_layer_in_diff.shp'
split_into_single_parts(base_output_path=base_output_path, input_file_name=wind_farm_area,
                            output_file_name=split_layer)

    # calculate area
calculate_area_layer = 'calculate_area_in_diff.shp'
calculate_area(base_output_path=base_output_path, input_file=split_layer, output_file=calculate_area_layer)

# filter area

filter_area_layer = 'filter_area_in_diff.shp'
filter_areas(base_output_path=base_output_path, input_file=calculate_area_layer, output_file=filter_area_layer,
                 variable=variable_to_area)


#6 Add id to column to select by id in next steps
wind_farm_area_id = 'wind_farm_area_id.shp'
add_id_column_to_filtered_data(base_output_path,input_file = filter_area_layer,output_file_10 = wind_farm_area_id)


#6 calculate distanse to power lines
medium_voltage_line = 'D:\GEOWORLDLOOK\OZE\PILOT\TEST_SKRYPTU\LINIE_SN.shp'
wind_farm_distance_to_line = "distance_wind_farm_to_line.shp"
calculate_distance(base_output_path,source_layer = wind_farm_area_id, destination_layer = medium_voltage_line,output_file_name = wind_farm_distance_to_line)


#13 Join to calculeted area by id
field_1 = 'ID'
field_2 ='ID'
field_to_copy = 'distance'
wind_farm_area_id_distance= "wind_farm_area_id_distance.shp"

join_attributes_with_distances(base_output_path = base_output_path,field_1 = field_1, field_2 = field_2, field_to_copy = field_to_copy
                               ,base_file=wind_farm_area_id,file_from_copy=wind_farm_distance_to_line,output_file_name =wind_farm_area_id_distance)

#14 Filter area by parametr
variable_wind_farm_line_distance = '"distance" < 800'
wind_farm_area_with_distance_criterium = "wind_farm_area_with_distance_criterium.shp"
column_distance_name = 'LINE_DISTANCE'
filter_area_distance(base_output_path = base_output_path, variable = variable_wind_farm_line_distance,column_distance_name = column_distance_name
                     ,layer_to_filter = wind_farm_area_id_distance, output_file_name = wind_farm_area_with_distance_criterium)

