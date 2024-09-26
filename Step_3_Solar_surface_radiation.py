import sys
import os
import processing
from Renewable_energy_optimum_location_function import create_directory_if_not_exists, buffer, process_sunlight_data, \
    process_tif_files, solar_radiation_photovoltaic_area

# Add path to the folder containing modules
sys.path.append('D:/GEOWORLDLOOK/OZE/Renewable_energy_optimum_location')

# Base input/output paths
BASE_INPUT_PATH = "D:/GEOWORLDLOOK/OZE/PILOT/Data/"
BASE_OUTPUT_PATH = "D:/GEOWORLDLOOK/OZE/PILOT/Step_3_Solar_surface_radiation/solar_radiation_vector"
create_directory_if_not_exists(BASE_OUTPUT_PATH)

# List of months to process
MONTHS = [
    "january", "february", "march", "april",
    "may", "june", "july", "august",
    "september", "october", "november", "december"
]

# Dictionary of provinces and corresponding buffer distances
PROVINCES = {
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


def process_province_data(key, province, number):
    """
    Process solar radiation data for a specific province.

    Args:
        key (str): Province key.
        province (str): Name of the province.
        number (str): Number associated with the province.
    """
    # 1. Create a buffer for the shape to cut (since solar radiation vector data doesn't cover the whole area)
    distance = 1
    mask_shapefile = os.path.join(BASE_INPUT_PATH, f"MASK_TO_CUT/{province}.shp")
    output_buffer_dir = os.path.join(BASE_OUTPUT_PATH, "MASK_TO_CUT_BUFFER")
    create_directory_if_not_exists(output_buffer_dir)

    output_buffer = os.path.join(output_buffer_dir, f"{province}_BUFFOR.shp")
    buffer(base_output_path=BASE_OUTPUT_PATH, input_path=mask_shapefile, output_file=output_buffer, distance=distance)

    # 2. Process sunlight data
    input_folder = os.path.join(BASE_INPUT_PATH, "SURFACE_RADIATION_1991_2020")
    output_folder = os.path.join(BASE_OUTPUT_PATH, "CLIP_RADIATION")
    process_sunlight_data(months=MONTHS, input_folder=input_folder, output_folder=output_folder,
                          mask_shapefile=output_buffer)

    # 3. Convert raster to vector
    output_file_name = f"solar_radiation_vector_{province}"
    field_name = "Solar_surface_radiation_[Wm2]"
    process_tif_files(base_input_path=output_folder, base_output_path=BASE_OUTPUT_PATH,
                      output_file_name=output_file_name, field_name=field_name, months=MONTHS)

    # 4. Create solar radiation to photovoltaic area for each month
    photovoltaic_area_path = f"D:/GEOWORLDLOOK/OZE/PILOT/Step_1_Photovoltaic_farm/photovoltaic_area_{province}.shp"
    solar_radiation_vector_file = f"solar_radiation_photovoltaic_area_{province}.shp"
    solar_radiation_photovoltaic_area(base_output_path=BASE_OUTPUT_PATH, photovoltaic_area_path=photovoltaic_area_path,
                                      province=province, output_file_name=solar_radiation_vector_file)


# Iterate through all provinces and process data
for key, (province, number) in PROVINCES.items():
    process_province_data(key, province, number)
