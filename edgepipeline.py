# # from fastapi import FastAPI, HTTPException
# # from typing import List
# # from pydantic import BaseModel
# # from selenium import webdriver
# # from selenium.webdriver.common.by import By
# # from selenium.webdriver.support.ui import WebDriverWait
# # from selenium.webdriver.support import expected_conditions as EC
# # from selenium.webdriver.chrome.options import Options
# # from time import sleep
# # import requests,base64,os,sys

# # from exception import CustomException, setup_logger
# # logger = setup_logger("edgepipeline", f"edgepipeline")

# # app = FastAPI()

# # # Set up Chrome WebDriver options
# # chrome_options = Options()
# # chrome_options.add_argument("--headless")
# # chrome_options.add_argument("--disable-gpu")
# # chrome_options.add_argument("--no-sandbox")

# # # Function to extract data from a single URL

# # # Define a function to extract text using explicit wait
# # def get_element_text(driver, selector, name):
# #     try:
# #         element = WebDriverWait(driver, .05).until(
# #             EC.presence_of_element_located((By.CSS_SELECTOR, selector))
# #         )
# #         text = element.text
# #     except Exception as e:
# #         print(f"Error extracting {name}: {e}")
# #         text = None
# #     return text

# # def extract_data_from_url(url):
# #     data = {}
# #     driver = webdriver.Chrome(options=chrome_options)

# #     try:
# #         driver.get(url)
# #         sleep(1)  # Ensure page loads completely

# #         # Function to extract text from an element
# #         def get_element_text(driver, selector, name):
# #             try:
# #                 element = WebDriverWait(driver, .05).until(
# #                     EC.presence_of_element_located((By.CSS_SELECTOR, selector))
# #                 )
# #                 text = element.text
# #             except Exception as e:
# #                 print(f"Error extracting {name}: {e}")
# #                 text = None
# #             return text

# #         # Extract necessary data from the page
# #         data['heading'] = get_element_text(driver, "h1.description","heading")
# #         data['run'] = get_element_text(driver, "#vdp > div.overview > div.general-section > div.cell.run-number > span","run")
# #         data['vin'] = get_element_text(driver, "#vdp > div.overview > div.general-section > div.cell.vin > span","vin")
# #         data['pmr'] = get_element_text(driver, "#vdp > div.overview > div.general-section > div.cell.pmr > div > div > span","pmr")
# #         data['kilometer'] = get_element_text(driver, "#vdp > div.overview > div.general-section > div.cell.odometer > span","kilometer")

# #         # Additional extraction functions can be added here for specific sections

# #         # Extracting details, auction, and declarations sections
# #         data['details'] = extract_section_data(driver, "#vdp > div.sections > div.section.details.closed > div > div", 13)
# #         data['auction'] = extract_section_data(driver, "#vdp > div.sections > div.section-group > div.section.auction.closed > div > div", 6)
# #         data['declarations'] = extract_section_data(driver, "#vdp > div.sections > div.section-group > div.section.declarations.closed > div > div", 4)

# #         data['images_bas64'],data['images_links'] = get_image_sources(driver=driver,name='images')


# #     finally:
# #         driver.quit()

# #     return data

# # # Function to extract data from specific sections
# # def extract_section_data(driver, section_selector, child_count):
# #     section_data = {}
# #     for i in range(1, child_count + 1):
# #         label_selector = f"{section_selector} > div:nth-child({i}) > label"
# #         value_selector = f"{section_selector} > div:nth-child({i}) > span"
# #         label_text = get_element_text(driver, label_selector,i)
# #         value_text = get_element_text(driver, value_selector,i)
# #         if label_text and value_text:
# #             section_data[label_text] = value_text
# #     return section_data

# # def get_image_sources(driver, name):
# #     sources = []
# #     sources_bs64 = []
# #     try:
# #         elements = WebDriverWait(driver, 20).until(
# #             EC.presence_of_all_elements_located((By.CSS_SELECTOR, "div.fotorama__thumb.fotorama__loaded.fotorama__loaded--img > img"))
# #         )


# #         for element in elements:
# #             l = element.get_attribute('src')
# #             l = l.replace('AweDc1Ow', 'YwMHgxMjAwOw')
# #             sources.append(l)
# #             sources_bs64.append(download_image_as_base64(l))
# #         return sources_bs64,sources
# #     except Exception as e:
# #         print(f"Error extracting {name}: {e}")
# #     return sources_bs64,sources


# # def download_image_as_base64(image_url):
# #     try:
# #         print(f"Downloading image from URL: {image_url}")
# #         logger.info(f"Downloading image from URL: {image_url}")
# #         # Download the image
# #         response = requests.get(image_url)
# #         response.raise_for_status()
# #         image_content = response.content

# #         return base64.b64encode(image_content).decode('utf-8')
# #     except requests.exceptions.RequestException as e:
# #         print(f"Error downloading image: {e}")
# #         logger.error(f"Error downloading image: {CustomException(e, sys)}")
# #         return ''


# # # Define a model for the request body
# # class RequestBody(BaseModel):
# #     links: List[str]

# # # Define your API endpoint
# # @app.post("/parse_links/")
# # def parse_links(request_body: RequestBody):
# #     parsed_data = []

# #     for link in request_body.links:
# #         try:
# #             data = extract_data_from_url(link)
# #             print(data)
# #             formatted_data = format_data(data)
# #             parsed_data.append(formatted_data)
# #         except Exception as e:
# #             # Handle any errors that might occur during extraction
# #             print(f"Error extracting data from {link}: {e}")
# #             continue

# #     return {"data": parsed_data}

# # # Function to format the extracted data as specified
# # def format_data(data):
# #     details = data.get('details', {})
# #     auction = data.get('auction',{})
# #     declarations = data.get('declarations',{})
# #     formatted_data = {
# #         "cars_type": "10",
# #         "category": "car",
# #         "make": data.get('heading').split()[1],
# #         "model": data.get('heading').split()[2],
# #         "year": data.get('heading').split()[0],
# #         "type": data.get('heading').split()[6],
# #         "status": "Non Brand",
# #         "vin": f"{details.get('VIN', '')}",
# #         "fuel_type": f"{details.get('Fuel Type', '')}",
# #         "transmission": f"{details.get('Transmission', '')}",
# #         "engine": f"{details.get('Displacement', '')} " +  f"{details.get('Cylinders', '').split(' ')[0].replace('CYL', '')}" + "cyl",
# #         "cylinders": f"{details.get('Cylinders', '').split(' ')[0].replace('CYL', '')}",
# #         "drive": f"{details.get('Drive Train', '')}",
# #         "kilometer": ''.join([char for char in f"{data.get('kilometer', '')}" if char.isdigit()]),
# #         "mileage_type": "Mile",
# #         "condition": "",
# #         "keys": "0" if details.get("Keys Included") == "N" else "1",
# #         "stock_number":  f"{auction.get('Stock Number', '')}",
# #         "interior_colour": f"{details.get('Interior Color / Material', '').split(' /')[0]}",
# #         "exterior_colour": f"{details.get('Color', '')}",
# #         "accessories": "",
# #         "currency": "USD",
# #         "price": "1",
# #         "country": "USA",
# #         "state": f"{auction.get('Location', '')}".split(", ")[1],
# #         "city" : f"{auction.get('Location', '')}".split(", ")[0],
# #         "auction_name":f"{auction.get('Auction', '')} "  ,
# #         "title_status": f"{declarations.get('Title Status', '')}",
# #         "run_no": f"{data.get('run', '')}",
# #         "pmr": f"{data.get('pmr', '')}",
# #         "images_links" : f"{data.get('images_links',[])}",
# #         "images_bs64" : f"{data.get('images_bas64',[])}"

# #     }
# #     return formatted_data

# # if __name__ == "__main__":
# #     import uvicorn
# #     uvicorn.run(app, host="0.0.0.0", port=8000)


# # =====================================================================
# # =====================================================================


# from fastapi import FastAPI, HTTPException
# from typing import List
# from pydantic import BaseModel
# from selenium import webdriver
# from selenium.webdriver.common.by import By
# from selenium.webdriver.support.ui import WebDriverWait
# from selenium.webdriver.support import expected_conditions as EC
# from selenium.webdriver.chrome.options import Options
# from time import sleep, time
# import requests
# import sys,os,json
# import base64
# from concurrent.futures import ThreadPoolExecutor, as_completed
# import logging
# from exception import CustomException, setup_logger

# logger = setup_logger("edgepipeline", f"edgepipeline.log")

# app = FastAPI()

# # Set up Chrome WebDriver options
# chrome_options = Options()
# chrome_options.add_argument("--headless")
# chrome_options.add_argument("--disable-gpu")
# chrome_options.add_argument("--no-sandbox")

# # Function to extract text using explicit wait


# def get_element_text(driver, selector, name):
#     try:
#         element = WebDriverWait(driver, 0.5).until(
#             EC.presence_of_element_located((By.CSS_SELECTOR, selector))
#         )
#         return element.text
#     except Exception as e:
#         logger.error(f"Error extracting {name}: {e}")
#         return None

# # Function to extract data from a single URL


# def extract_data_from_url(url):
#     data = {}
#     start_time = time()
#     driver = webdriver.Chrome(options=chrome_options)
#     try:
#         driver.get(url)
#         sleep(1)  # Ensure page loads completely

#         data['heading'] = get_element_text(driver, "h1.description", "heading")
#         data['run'] = get_element_text(
#             driver, "#vdp > div.overview > div.general-section > div.cell.run-number > span", "run")
#         data['vin'] = get_element_text(
#             driver, "#vdp > div.overview > div.general-section > div.cell.vin > span", "vin")
#         data['pmr'] = get_element_text(
#             driver, "#vdp > div.overview > div.general-section > div.cell.pmr > div > div > span", "pmr")
#         data['kilometer'] = get_element_text(
#             driver, "#vdp > div.overview > div.general-section > div.cell.odometer > span", "kilometer")

#         data['details'] = extract_section_data(
#             driver, "#vdp > div.sections > div.section.details.closed > div > div", 13)
#         data['auction'] = extract_section_data(
#             driver, "#vdp > div.sections > div.section-group > div.section.auction.closed > div > div", 6)
#         data['declarations'] = extract_section_data(
#             driver, "#vdp > div.sections > div.section-group > div.section.declarations.closed > div > div", 4)

#         data['images_bs64'], data['images_links'] = get_image_sources(
#             driver=driver, name='images')

#         elapsed_time = time() - start_time
#         logger.info(f"Extracted data from {url} in {elapsed_time:.2f} seconds")
#     except Exception as e:
#         logger.error(
#             f"Error extracting data from {url}: {CustomException(e, sys)}")
#     finally:
#         driver.quit()
#     return data

# # Function to extract data from specific sections


# def extract_section_data(driver, section_selector, child_count):
#     section_data = {}
#     for i in range(1, child_count + 1):
#         label_selector = f"{section_selector} > div:nth-child({i}) > label"
#         value_selector = f"{section_selector} > div:nth-child({i}) > span"
#         label_text = get_element_text(driver, label_selector, f"label_{i}")
#         value_text = get_element_text(driver, value_selector, f"value_{i}")
#         if label_text and value_text:
#             section_data[label_text] = value_text
#     return section_data

# # Function to get image sources


# def get_image_sources(driver, name):
#     sources_bs64 = []
#     sources = []
#     try:
#         elements = WebDriverWait(driver, 20).until(
#             EC.presence_of_all_elements_located(
#                 (By.CSS_SELECTOR, "div.fotorama__thumb.fotorama__loaded.fotorama__loaded--img > img"))
#         )

#         for element in elements:
#             l = element.get_attribute('src')
#             l = l.replace('AweDc1Ow', 'YwMHgxMjAwOw')
#             sources.append(l)
#             sources_bs64.append(download_image_as_base64(l))
#         return sources_bs64, sources
#     except Exception as e:
#         logger.error(f"Error extracting {name}: {e}")
#     return sources_bs64, sources

# # Function to download image as base64


# def download_image_as_base64(image_url):
#     try:
#         logger.info(f"Downloading image from URL: {image_url}")
#         response = requests.get(image_url)
#         response.raise_for_status()
#         image_content = response.content
#         return base64.b64encode(image_content).decode('utf-8')
#     except requests.exceptions.RequestException as e:
#         logger.error(f"Error downloading image: {CustomException(e, sys)}")
#         return ''

# # Define a model for the request body


# class RequestBody(BaseModel):
#     links: List[str]

# # Define your API endpoint


# @app.post("/parse_links/")
# async def parse_links(request_body: RequestBody):
#     parsed_data = []
#     with ThreadPoolExecutor(max_workers=5) as executor:
#         futures = [executor.submit(extract_data_from_url, link)
#                    for link in request_body.links]
#         for future in as_completed(futures):
#             try:
#                 data = future.result()
#                 if data:
#                     formatted_data = format_data(data)
#                     parsed_data.append(formatted_data)
#             except Exception as e:
#                 logger.error(
#                     f"Error processing URL: {CustomException(e, sys)}")
#     return {"data": parsed_data}


# def call_api(data):
#     try:
#         headers = {'accept': 'application/json',
#                    'Content-Type': 'application/json'}
#         url = "http://localhost:8080/add_car_info"
#         response = requests.post(url, headers=headers, data=data)
#         print(response.status_code)
#         if response.status_code == 200:
#             logger.info("Data successfully sent to API")
#             print("Data successfully sent to API")
#             return f"successful status code - {response.status_code}"
#         else:
#             print(
#                 f"Failed to send data to API. Status code: {response.status_code}")
#             return f"Failed status code - {response.status_code}"
#     except Exception as e:
#         logger.error(f"Error Occurred at {CustomException(e, sys)}")
#         print(CustomException(e, sys))
#         return "None"

# # Function to format the extracted data


# from datetime import datetime

# def convert_date_format(date_str):
#     # Parse the input date string
#     input_date = datetime.strptime(date_str, '%a, %m/%d/%y')
    
#     # Format the date to the desired output format
#     output_date = input_date.strftime('%Y-%m-%d')
    
#     return output_date

# def format_data(data):
#     details = data.get('details', {})
#     auction = data.get('auction', {})
#     declarations = data.get('declarations', {})
#     formatted_data = {
#         "cars_type": "10",
#         "category": "car",
#         "make": data.get('heading').split()[1],
#         "model": data.get('heading').split()[2],
#         "year": data.get('heading').split()[0],
#         "type": data.get('heading').split()[6],
#         "status": "Non Brand",
#         "vin": f"{details.get('VIN', '')}",
#         "fuel_type": f"{details.get('Fuel Type', '')}",
#         "transmission": f"{details.get('Transmission', '')}",
#         "engine": f"{details.get('Displacement', '')} {details.get('Cylinders', '').split(' ')[0].replace('CYL', '')}cyl",
#         "cylinders": f"{details.get('Cylinders', '').split(' ')[0].replace('CYL', '')}",
#         "drive": f"{details.get('Drive Train', '')}",
#         "kilometer": ''.join([char for char in f"{data.get('kilometer', '')}" if char.isdigit()]),
#         "mileage_type": "Mile",
#         "condition": "",
#         "keys": "0" if details.get("Keys Included") == "N" else "1",
#         "stock_number": f"{auction.get('Stock Number', '')}",
#         "interior_colour": f"{details.get('Interior Color / Material', '').split(' /')[0]}",
#         "exterior_colour": f"{details.get('Color', '')}",
#         "accessories": "",
#         "currency": "USD",
#         "price": "1",
#         "country": "USA",
#         "state": f"{auction.get('Location', '')}".split(", ")[1],
#         "city": f"{auction.get('Location', '')}".split(", ")[0],
#         "auction_date": f"{convert_date_format(auction.get('Sale Date', '').split(' (')[0])}",
#         "purchase_option": "0",
#         "hid_main_images": "",
#         "hid_addedtype": "2",
#         "hid_addedby": "47",
#         "h_inventory": "addinventory",
#         "auction_name": f"{auction.get('Auction', '')}",
#         "title_status": f"{declarations.get('Title Status', '')}",
#         "run": f"{data.get('run', '')}",
#         "pmr": f"{data.get('pmr', '')}",
#         "hid_allimages": data.get('images_bs64', [])
#     }
    
#     file_name = f"{data['stock_number']}.json"
#     file_path = os.path.join("data/edge", file_name)

#     if not os.path.exists("data/edge"):
#         os.makedirs("data/edge")

#     with open(file_path, 'w') as json_file:
#         json.dump(formatted_data, json_file, indent=4)
#     # print(data)
#     json_data = json.dumps(formatted_data)
#     if len(formatted_data['hid_allimages'])>0:
#         status_code = call_api(json_data)
    
#     return [formatted_data,status_code]


# # Initialize the WebDriver
# driver = webdriver.Chrome(options=chrome_options)

# if __name__ == "__main__":
#     import uvicorn
#     uvicorn.run(app, host="0.0.0.0", port=8000)

from fastapi import FastAPI, HTTPException
from typing import List
from pydantic import BaseModel
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
import requests
import sys, os, json
import base64
from concurrent.futures import ThreadPoolExecutor, as_completed
import logging
from datetime import datetime
from exception import CustomException, setup_logger
from time import sleep,time
logger = setup_logger("edgepipeline", f"edgepipeline")

app = FastAPI()

# Database configuration
db_config = {
    'host': 'localhost',  # Replace with your database host
    'user': 'root',  # Replace with your database user
    'password': '',  # Replace with your database password
    'database': 'scrap_data',  # Replace with your database name
    'port': 3307
}
# db_config = {
#    'host': 'localhost',        # Replace with your database host
#    'user': 'icbc_scrapper',             # Replace with your database user
#    'password': 'R3RhtTyGEjGD7pZV8WJY6N9oeWRXsAxZ',             # Replace with your database password
#    'database': 'icbc_scrapper_DB',   # Replace with your database name
#    'port': 3306
# }

# Set up Chrome WebDriver options
chrome_options = Options()
chrome_options.add_argument("--headless")
chrome_options.add_argument("--disable-gpu")
chrome_options.add_argument("--no-sandbox")
chrome_options.binary_location = "/usr/bin/chromium-browser"  # Adjust this path if necessary
logger.info(f"{str(db_config)}'\n'{chrome_options.binary_location}")

# Function to extract text using explicit wait
def get_element_text(driver, selector, name):
    try:
        element = WebDriverWait(driver, 0.5).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, selector))
        )
        return element.text
    except Exception as e:
        logger.error(f"Error extracting {name}: {e}")
        return None

# Function to extract data from a single URL
def extract_data_from_url(driver, url):
    data = {}
    start_time = time()
    try:
        driver.get(url)
        sleep(1)
        
        data['heading'] = get_element_text(driver, "h1.description", "heading")
        data['run'] = get_element_text(driver, "#vdp > div.overview > div.general-section > div.cell.run-number > span", "run")
        data['vin'] = get_element_text(driver, "#vdp > div.overview > div.general-section > div.cell.vin > span", "vin")
        data['pmr'] = get_element_text(driver, "#vdp > div.overview > div.general-section > div.cell.pmr > div > div > span", "pmr")
        data['kilometer'] = get_element_text(driver, "#vdp > div.overview > div.general-section > div.cell.odometer > span", "kilometer")

        data['details'] = extract_section_data(driver, "#vdp > div.sections > div.section.details.closed > div > div", 13)
        data['auction'] = extract_section_data(driver, "#vdp > div.sections > div.section-group > div.section.auction.closed > div > div", 6)
        data['declarations'] = extract_section_data(driver, "#vdp > div.sections > div.section-group > div.section.declarations.closed > div > div", 4)

        data['images_bs64'], data['images_links'] = get_image_sources(driver, 'images')

        elapsed_time = time() - start_time
        logger.info(f"Extracted data from {url} in {elapsed_time:.2f} seconds")
    except Exception as e:
        logger.error(f"Error extracting data from {url}: {CustomException(e, sys)}")
    return data

# Function to extract data from specific sections
def extract_section_data(driver, section_selector, child_count):
    section_data = {}
    for i in range(1, child_count + 1):
        label_selector = f"{section_selector} > div:nth-child({i}) > label"
        value_selector = f"{section_selector} > div:nth-child({i}) > span"
        label_text = get_element_text(driver, label_selector, f"label_{i}")
        value_text = get_element_text(driver, value_selector, f"value_{i}")
        if label_text and value_text:
            section_data[label_text] = value_text
    return section_data

# Function to get image sources
def get_image_sources(driver, name):
    sources_bs64 = []
    sources = []
    try:
        elements = WebDriverWait(driver, 20).until(
            EC.presence_of_all_elements_located((By.CSS_SELECTOR, "div.fotorama__thumb.fotorama__loaded.fotorama__loaded--img > img"))
        )

        for element in elements:
            img_url = element.get_attribute('src').replace('AweDc1Ow', 'YwMHgxMjAwOw')
            sources.append(img_url)
            sources_bs64.append(download_image_as_base64(img_url))
        return sources_bs64, sources
    except Exception as e:
        logger.error(f"Error extracting {name}: {e}")
    return sources_bs64, sources

# Function to download image as base64
def download_image_as_base64(image_url):
    try:
        logger.info(f"Downloading image from URL: {image_url}")
        response = requests.get(image_url)
        response.raise_for_status()
        return base64.b64encode(response.content).decode('utf-8')
    except requests.exceptions.RequestException as e:
        logger.error(f"Error downloading image: {CustomException(e, sys)}")
        return ''

# Define a model for the request body
class RequestBody(BaseModel):
    links: List[str]

# Define your API endpoint
@app.post("/parse_links/")
async def parse_links(request_body: RequestBody):
    parsed_data = []
    driver = webdriver.Chrome(options=chrome_options)
    try:
        with ThreadPoolExecutor(max_workers=5) as executor:
            futures = [executor.submit(extract_data_from_url, driver, link) for link in request_body.links]
            for future in as_completed(futures):
                try:
                    data = future.result()
                    if data:
                        formatted_data = format_data(data)
                        parsed_data.append(formatted_data)
                except Exception as e:
                    logger.error(f"Error processing URL: {CustomException(e, sys)}")
    finally:
        driver.quit()
    return parsed_data

# Function to call an external API
def call_api(data):
    try:
        headers = {'accept': 'application/json', 'Content-Type': 'application/json'}
        url = "http://localhost:8080/add_car_info"
        response = requests.post(url, headers=headers, data=data)
        if response.status_code == 200:
            logger.info("Data successfully sent to API")
            return f"successful status code - {response.status_code}"
        else:
            logger.error(f"Failed to send data to API. Status code: {response.status_code}")
            return f"Failed status code - {response.status_code}"
    except Exception as e:
        logger.error(f"Error Occurred at {CustomException(e, sys)}")
        return "None"

# Function to format the extracted data
def convert_date_format(date_str):
    try:
        input_date = datetime.strptime(date_str, '%a, %m/%d/%y')
        return input_date.strftime('%Y-%m-%d')
    except ValueError as e:
        logger.error(f"Date conversion error: {e}")
        return ''

def format_data(data):
    details = data.get('details', {})
    auction = data.get('auction', {})
    declarations = data.get('declarations', {})
    formatted_data = {
        "cars_type": "10",
        "category": "car",
        "make": data.get('heading').split()[1],
        "model": data.get('heading').split()[2],
        "year": data.get('heading').split()[0],
        "type": data.get('heading').split()[6],
        "status": "Non Brand",
        "vin": details.get('VIN', ''),
        "fuel_type": details.get('Fuel Type', ''),
        "transmission": details.get('Transmission', ''),
        "engine": f"{details.get('Displacement', '')} {details.get('Cylinders', '').split(' ')[0].replace('CYL', '')}cyl",
        "cylinders": details.get('Cylinders', '').split(' ')[0].replace('CYL', ''),
        "drive": details.get('Drive Train', ''),
        "kilometer": ''.join(filter(str.isdigit, data.get('kilometer', ''))),
        "mileage_type": "Mile",
        "condition": "",
        "keys": "0" if details.get("Keys Included") == "N" else "1",
        "stock_number": auction.get('Stock Number', ''),
        "interior_colour": details.get('Interior Color / Material', '').split(' /')[0],
        "exterior_colour": details.get('Color', ''),
        "accessories": "",
        "currency": "USD",
        "price": "1",
        "country": "USA",
        "state": auction.get('Location', '').split(", ")[1],
        "city": auction.get('Location', '').split(", ")[0],
        "auction_date": f"{convert_date_format(auction.get('Sale Date', '').split(' (')[0])}",
        "purchase_option": "0",
        "hid_main_images": "",
        "hid_addedtype": "2",
        "hid_addedby": "47",
        "h_inventory": "addinventory",
        "auction_name": auction.get('Auction', ''),
        "title_status": declarations.get('Title Status', ''),
        "run": data.get('run', ''),
        "pmr": data.get('pmr', ''),
        "hid_allimages": data.get('images_bs64', [])
    }
    
    file_name = f"{formatted_data['stock_number']}.json"
    file_path = os.path.join("data/edge", file_name)

    if not os.path.exists("data/edge"):
        os.makedirs("data/edge")

    with open(file_path, 'w') as json_file:
        json.dump(formatted_data, json_file, indent=4)

    if formatted_data['hid_allimages']:
        status_code = call_api(json.dumps(formatted_data))
    
    return formatted_data

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=3034)
