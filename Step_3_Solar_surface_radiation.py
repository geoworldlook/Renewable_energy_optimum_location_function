# Path to folder with modules
import sys
sys.path.append('D:\GEOWORLDLOOK\OZE\Renewable_energy_optimum_location')
from Renewable_energy_optimum_location_function import *
import os
import processing

base_input_path = "D:/GEOWORLDLOOK/OZE/PILOT/Data"
base_output_path = "D:/GEOWORLDLOOK/OZE/PILOT/Step_3_Solar_surface_radiation/solar_radiation_vector"
create_directory_if_not_exists(base_output_path)

#1 Cut sunlight data base on mask for each month
months = [
    "january", "february", "march", "april",
    "may", "june", "july", "august",
    "september", "october", "november", "december"
    ]

#create buffor to shape to cut, beacause solar radiation vector data don't cover whole area
distance = 1
mask_shapefile = base_input_path + "/MASK_TO_CUT/PODLASKIE_SHP.shp"

output_file_buffer_directory = os.path.join(base_output_path, "MASK_TO_CUT_BUFFER")
create_directory_if_not_exists(output_file_buffer_directory)

output_file_buffer = os.path.join(output_file_buffer_directory, "podlaskie_BUFFOR.shp")

buffer(base_output_path = base_output_path, input_path = mask_shapefile, output_file=output_file_buffer,distance=distance)


# Paths to the input and output data folders


input_folder = base_input_path + "/SURFACE_RADIATION_1991_2020/"
output_folder = base_output_path + "/CLIP_RADIATION"


# Process sunlight data
process_sunlight_data(months = months, input_folder= input_folder, output_folder = output_folder, mask_shapefile = output_file_buffer)

#2 Change raster to vector
output_file_name = "solar_radiation_vector"
field_name = "Solar_surface_radiation_[Wm2]"
process_tif_files(base_input_path = output_folder , 
base_output_path = base_output_path , output_file_name =output_file_name , field_name = field_name, months = months)


#3 Create solar radiation to photovoltaic area each month

# Path to folder with modules
#base path to input files
base_input_path = "D:/GEOWORLDLOOK/OZE/PILOT/"

#base output path
base_output_path = "D:/GEOWORLDLOOK/OZE/PILOT/Step_3_Solar_surface_radiation/solar_radiation_vector"

#path to data from step 1
photovoltaic_area_path = "D:/GEOWORLDLOOK/OZE/PILOT/Step_1_Photovoltaic_farm/photovoltaic_area.shp"

#folder to step 3
solar_radiation_vector_path = "Step_3_Solar_surface_radiation"

#final output file name with photovoltaic area and solar radiation for each month
solar_radiation_vector_file = 'solar_radiation_photovoltaic_area.shp'
output_file_name = "solar_radiation_photovoltaic_area.shp"

solar_radiation_photovoltaic_area(base_output_path = base_output_path, photovoltaic_area_path = photovoltaic_area_path
                                  ,output_file_name = solar_radiation_vector_file)



