# Path to folder with modules
import sys
sys.path.append('D:\GEOWORLDLOOK\OZE\Renewable_energy_optimum_location')
from Renewable_energy_optimum_location_function import *
import os
import processing

base_input_path = "D:/GEOWORLDLOOK/OZE/PILOT/Data"
base_output_path = "D:/GEOWORLDLOOK/OZE/PILOT/Step_3_Solar_surface_radiation/solar_radiation_vector"

#1 Cut sunlight data base on mask for each month
months = [
    "january", "febuary", "march", "april",
    "may", "june", "july", "august",
    "september", "october", "november", "december"
    ]

# Paths to the input and output data folders
input_folder = base_input_path + "/SURFACE_RADIATION_1991_2020/"
output_folder = base_output_path + "/CLIP_RADIATION"
mask_shapefile = base_input_path + "/MASK_TO_CUT/PODLASKIE_SHP.shp"

# Process sunlight data
process_sunlight_data(months = months, input_folder= input_folder, output_folder = output_folder, mask_shapefile = mask_shapefile)

#2 Change raster to vector
output_file_name = "solar_radiation_vector"
field_name = "Solar_surface_radiation_[Wm2]"
process_tif_files(base_input_path = output_folder , 
base_output_path = base_output_path , output_file_name =output_file_name , field_name = field_name, months = months)


