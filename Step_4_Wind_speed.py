import sys
import os
import processing
from Renewable_energy_optimum_location_function import create_directory_if_not_exists, buffer, process_sunlight_data, process_tif_files, wind_speed_farm_area

sys.path.append('D:/GEOWORLDLOOK/OZE/Renewable_energy_optimum_location')

def process_wind_speed_for_province(province_code, province_name, mask_number, base_input_path, base_output_path, months, distance=1):
    """
    Process wind speed data for a given province.

    Args:
        province_code (str): The code of the province.
        province_name (str): The name of the province.
        mask_number (str): The identifier number for the province mask.
        base_input_path (str): The base path where input data is located.
        base_output_path (str): The base path where output data will be saved.
        months (list): List of months to process wind speed data for.
        distance (int, optional): Buffer distance. Defaults to 1.

    Returns:
        None
    """
    # Create buffer for shape to cut
    mask_shapefile = os.path.join(base_input_path, f"MASK_TO_CUT/{province_name}.shp")
    buffer_output_directory = os.path.join(base_output_path, "MASK_TO_CUT_BUFFER")
    create_directory_if_not_exists(buffer_output_directory)

    buffer_output_file = os.path.join(buffer_output_directory, f"{province_name}_BUFFER.shp")
    buffer(base_output_path=base_output_path, input_path=mask_shapefile, output_file=buffer_output_file, distance=distance)

    # Define input and output folders for wind speed data
    wind_input_folder = os.path.join(base_input_path, "MEAN_WIND_SPEED")
    wind_output_folder = os.path.join(base_output_path, "CLIP_WIND_SPEED")
    create_directory_if_not_exists(wind_output_folder)

    # Process wind speed data for each month
    process_sunlight_data(months=months, input_folder=wind_input_folder, output_folder=wind_output_folder, mask_shapefile=buffer_output_file)

    # Convert wind speed raster data to vector format
    wind_speed_vector_output = f"wind_speed_vector_{province_name}"
    process_tif_files(base_input_path=wind_output_folder, base_output_path=base_output_path,
                      output_file_name=wind_speed_vector_output, field_name="Wind_speed", months=months)

    # Combine wind speed data with wind farm area for the province
    wind_farm_area_path = os.path.join(base_input_path, f"Step_2_Wind_Farm/windfarm_area_{province_name}.shp")
    wind_speed_vector_file = f"wind_speed_wind_farm_{province_name}.shp"
    wind_speed_farm_area(base_output_path=base_output_path, wind_area_path=wind_farm_area_path, province=province_name,
                         output_file_name=wind_speed_vector_file)


def main():
    base_input_path = "D:/GEOWORLDLOOK/OZE/PILOT/Data"
    base_output_path = "D:/GEOWORLDLOOK/OZE/PILOT/Step_4_wind_speed_vector/wind_speed_vector"
    create_directory_if_not_exists(base_output_path)

    months = [
        "january", "february", "march", "april",
        "may", "june", "july", "august",
        "september", "october", "november", "december"
    ]

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

    for province_code, (province_name, mask_number) in provinces.items():
        process_wind_speed_for_province(province_code, province_name, mask_number, base_input_path, base_output_path, months)


if __name__ == "__main__":
    main()
