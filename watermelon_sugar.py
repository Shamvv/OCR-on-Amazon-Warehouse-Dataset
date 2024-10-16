# -*- coding: utf-8 -*-
!pip install paddlepaddle-gpu==2.6.2 paddleocr

from google.colab import drive
drive.mount('/content/drive')

from paddleocr import PaddleOCR, draw_ocr
import matplotlib.pyplot as plt
from PIL import Image
import cv2

ocr = PaddleOCR(use_angle_cls=True, lang='en')  # Use English model

"""#HANDLE VARIABLE `n` IN THE FOLLOWING BLOCK WITH EXTREME CARE!!!!! IT SETS HOW MANY IMAGES YOU WILL DOWNLOAD AND TEST!!!"""

import pandas as pd

# Read the dataset
df = pd.read_csv("test.csv")

# Select rows from index 17975 to 34999 (since Python indexing is zero-based)
df1 = df.iloc[35000:60000]

# Extract relevant columns into lists from the sliced dataframe
list_of_image_paths = df1['image_link'].to_list()
e_name = df1['entity_name'].to_list()
index = df1['index'].to_list()
g_id = df1['group_id'].to_list()

# number of input images (from the sliced dataset)
n = len(list_of_image_paths)

# Now you can proceed with further analysis on the sliced data

import requests
for i in range(n):

  # Image URL
  url = list_of_image_paths[i]

  # Send GET request
  response = requests.get(url)
  img_path = 'image'+str(i)+'.jpg'
  # Save the image to a file
  if response.status_code == 200:
      with open(img_path, 'wb') as file:
          file.write(response.content)
  else:
      print("Failed to retrieve image.")

import os

# Directory where images are saved (in Colab)
image_dir = '/content/'

# List all files in the directory that match the pattern "image*.jpg"
image_files = [f for f in os.listdir(image_dir) if f.startswith('image') and f.endswith('.jpg')]

# Extract the numbers from the filenames and convert them to integers
image_numbers = [int(f.replace('image', '').replace('.jpg', '')) for f in image_files]

# Find the maximum number
if image_numbers:
    max_downloaded = max(image_numbers)
    print(f"The highest image number downloaded is: {max_downloaded}")

    # Check if all images from 0 to max_downloaded are present
    missing_images = [i for i in range(max_downloaded + 1) if i not in image_numbers]

    if not missing_images:
        print(f"All images from 0 to {max_downloaded} are downloaded in sequence.")
    else:
        print(f"Missing images: {missing_images}")
else:
    print("No images found.")

def extract_text_from_image(image_path):
    # Perform OCR on the image
    result = ocr.ocr(image_path, cls=True)
    temp = []
    if result[0] is None:
      return "Not Found"
    for i in range(len(result[0])):
      temp.append(result[0][i][-1][0])
    return "".join(temp)

import re

# Define regex patterns for different elements with updated unit lists
patterns = {
    "item_weight": r"(\d+(\.\d+)?)(\s?(mg|g|kg|lb|lbs|pounds|oz|ounce|ounces|ton|microgram))",
    "item_volume": r"(\d+(\.\d+)?)(\s?(ml|l|liters?|fl oz|fluid ounce|milliliter|liter|ounce|cubic foot|microlitre|cup|centilitre|imperial gallon|pint|decilitre|quart|cubic inch|gallon))",
    "height": r"(\d+(\.\d+)?)(\s?(cm|m|in|inch|inches|feet|ft|centimeter|meter|foot|\"|mm|millimetre|yard))",
    "depth": r"(\d+(\.\d+)?)(\s?(cm|m|in|inch|inches|feet|ft|centimeter|meter|foot|\"|mm|millimetre|yard))",
    "width": r"(\d+(\.\d+)?)(\s?(cm|m|in|inch|inches|feet|ft|centimeter|meter|foot|\"|mm|millimetre|yard))",
    "voltage": r"(\d+(\.\d+)?)(\s?(V|volts?|kilovolt|millivolt))",
    "wattage": r"(\d+(\.\d+)?)(\s?(W|watts?|kilowatt))",
}

# Map abbreviations to full forms
unit_mappings = {
    "mg": "milligram",
    "g": "gram",
    "kg": "kilogram",
    "lb": "pound",
    "lbs": "pound",
    "pounds": "pound",
    "oz": "ounce",
    "ounce": "ounce",
    "ounces": "ounce",
    "ml": "millilitre",
    "l": "liter",
    "liters": "liter",
    "fl oz": "fluid ounce",
    "fl": "fluid ounce",
    " fl": "fluid ounce",
    "cm": "centimetre",
    "m": "meter",
    "in": "inch",
    "inch": "inch",
    "inches": "inch",
    "ft": "foot",
    "feet": "foot",
    "mm": "millimetre",
    "millimetre": "millimetre",
    "yard": "yard",
    " cm": "centimetre",
    " m": "metre",
    " in": "inch",
    "inch": "inch",
    "inches": "inch",
    "ft": "foot",
    "feet": "foot",
    " mm": "millimetre",
    "mm": "millimetre",
    "millimetre": "millimetre",
    "yard": "yard",
    "V": "volt",
    "v": "volt",
    " v": "volt",
    " V": "volt",
    "volts": "volt",
    "W": "watt",
    "w": "watt",
    " W": "watt",
    " w": "watt",
    "V": "volt",
    "volts": "volt",
    "W": "watt",
    " w": "watt",
    " W": "watt",
    "w": "watt",
    "watts": "watt",
    "kilovolt": "kilovolt",
    "millivolt": "millivolt",
    "kilowatt": "kilowatt",
    "ton": "ton",
    "microgram": "microgram",
    "cubic foot": "cubic foot",
    "microlitre": "microlitre",
    "cup": "cup",
    "centilitre": "centilitre",
    "imperial gallon": "imperial gallon",
    "pint": "pint",
    "decilitre": "decilitre",
    "quart": "quart",
    "cubic inch": "cubic inch",
    "gallon": "gallon",
    ' "' : "inch",
    '"': "inch"
}

# Unit conversion to grams for weights
unit_conversion = {
    "mg": 0.001,
    "g": 1,
    "kg": 1000,
    "lb": 453.592,
    "lbs": 453.592,
    "pounds": 453.592,
    "oz": 28.3495,
    "ounce": 28.3495,
    "ounces": 28.3495,
    "ton": 1000000,
    "microgram": 0.000001
}

def format_decimal(value):
    """Ensure the number has one decimal place only if it doesn't already have decimals."""
    if "." not in value:
        return f"{value}.0"
    return value

def replace_units_with_full_form(match):
    """Helper function to replace abbreviations with full-form units."""
    value = match[0]  # Access the value part of the tuple
    unit = match[3].lower()  # Access the unit part for the element

    # Replace unit with its full form using the mapping
    full_unit = unit_mappings.get(unit, unit)

    # For height, width, depth, weight, and voltage, ensure the value has one decimal
    if full_unit in ["centimetre", "meter", "inch", "foot", "gram", "kilogram", "ounce", "volt"]:
        value = format_decimal(value)

    return f"{value} {full_unit}"

def find_highest_weight(matches):
    """
    Helper function to find the highest weight in the list of matches.
    If both grams and ounces are present, ounces are preferred.
    """
    max_weight = 0
    result = ""
    found_ounce = None

    for match in matches:
        try:
            weight = float(match[0])  # The numeric value
            unit = match[3].lower()   # The unit, like mg, g, kg, etc.

            # If ounce is found, prefer it over grams
            if unit in ["oz", "ounce", "ounces"]:
                found_ounce = match  # Store ounce value, continue to find if there's any larger weight
            weight_in_grams = weight * unit_conversion[unit]  # Convert to grams

            if weight_in_grams > max_weight:
                max_weight = weight_in_grams
                result = replace_units_with_full_form(match)
        except ValueError:
            continue  # Skip if there's an error converting the weight

    # If ounce was found, prefer it
    if found_ounce:
        result = replace_units_with_full_form(found_ounce)

    return result

def sort_matches_by_value(matches):
    """Helper function to sort matches by numeric value."""
    return sorted(matches, key=lambda x: float(x[0]), reverse=True)

def find_element(text, element):
    """
    Function to extract the relevant information for a given element from the text.
    :param text: Extracted text from the image
    :param element: The element to find (e.g., "item_weight", "height").
    :return: The matched value with units or 'Not Found'.
    """
    # Treat maximum_weight_recommendation as item_weight
    if element == "maximum_weight_recommendation":
        element = "item_weight"

    if element not in patterns:
        return "Invalid element provided"

    # Get the regex pattern for the requested element
    pattern = patterns[element]

    # Search for the pattern in the extracted text
    matches = re.findall(pattern, text, re.IGNORECASE)

    if element == "item_weight" and matches:
        return find_highest_weight(matches)

    if matches:
        # If multiple matches, sort them in descending order
        sorted_matches = sort_matches_by_value(matches)

        # If height is requested, return the largest value
        if element == "height":
            return replace_units_with_full_form(sorted_matches[0])

        # If width is requested and there are multiple matches, return the second largest
        if element == "width" and len(sorted_matches) > 1:
            return replace_units_with_full_form(sorted_matches[1])

        # For wattage, handle special cases like 0.45W vs. 65W
        if element == "wattage":
            # Filter out incorrect wattage matches (like IP65)
            correct_wattage = [m for m in sorted_matches if "W" in m[3] or "watt" in m[3]]
            if correct_wattage:
                return replace_units_with_full_form(correct_wattage[0])
            return replace_units_with_full_form(sorted_matches[0])

        # For other elements or single matches, return the first match
        return replace_units_with_full_form(sorted_matches[0])

    return ""

def main():
    final = []
    # Iterate for each image
    for i in range(25000):
        print(f"\nProcessing Image {i}:")
        img_path = 'image'+str(i)+'.jpg'
        # Ask for the extracted text
        extracted_text = extract_text_from_image(img_path)
        # Ask for the element to find
        element_to_find = e_name[i]

        # Find the element in the text
        result = find_element(extracted_text, element_to_find)
        final.append(result)
    return final

import pandas as pd

# Call the main function to get predictions
final = main()

# Create an index that matches the length of final
index = list(range(1, len(final) + 1))  # Assuming the index starts from 1

# Ensure that 'index' and 'final' are of the same length
if len(index) == len(final):
    # Create the DataFrame
    data = {
        "index": index,
        "prediction": final,
    }

    df_final = pd.DataFrame(data)
    print(df_final)  # Display the DataFrame
else:
    print("Error: The length of 'index' and 'final' must match.")

df_final.to_csv('test_out.csv')

from google.colab import files
files.download('test_out.csv')
