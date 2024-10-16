import os
from datetime import datetime
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import mysql.connector
from mysql.connector import Error
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
import base64
import requests
import json
from exception import CustomException, setup_logger
import sys
from threading import Thread
import uvicorn

app = FastAPI()
logger = setup_logger("icbc", f"icbc")
# Login and filter page URLs
login_page_url = 'https://onlinebusiness.icbc.com/salvage/auth/Form-login.jsp'
filter_page_url = 'https://onlinebusiness.icbc.com/salvage/webServlet/Search?form=VehicleSales'

# Database configuration
db_config = {
    'host': 'localhost',  # Replace with your database host
    'user': 'root',  # Replace with your database user
    'password': '',  # Replace with your database password
    'database': 'scrap_data',  # Replace with your database name
    'port': 3307
}
# db_config = {
#    'host': 'localhost',                            # Replace with your database host
#    'user': 'icbc_scrapper',                        # Replace with your database user
#    'password': 'R3RhtTyGEjGD7pZV8WJY6N9oeWRXsAxZ', # Replace with your database password
#    'database': 'icbc_scrapper_DB',                 # Replace with your database name
#    'port': 3306
# }
chrome_options = Options()
chrome_options.add_argument("--headless")
chrome_options.add_argument("--disable-gpu")
chrome_options.add_argument("--no-sandbox")
chrome_options.add_argument("--disable-dev-shm-usage")
chrome_options.add_argument(
    "user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
)
chrome_options.add_argument("--disable-blink-features=AutomationControlled")
chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
chrome_options.add_experimental_option("useAutomationExtension", False)
chrome_options.add_argument("--window-size=1920x1080")
chrome_options.add_argument("--disable-extensions")
chrome_options.add_argument("--proxy-server='direct://'")
chrome_options.add_argument("--proxy-bypass-list=*")
chrome_options.binary_location = "/usr/bin/chromium-browser"
logger.info(f"{str(db_config)}\n{chrome_options.binary_location}")

driver = None
class LoginDetails(BaseModel):
    username: str = "B073902"
    password: str = "MUJEB786"
    b_year: str = "All"
    e_year: str = "All"
    
def connect_to_database():
    try:
        connection = mysql.connector.connect(**db_config)
        if connection.is_connected():
            print("Connected to the database.")
            logger.info("Connected to the database.")

            return connection
    except Exception as e:
        logger.info(f"Error Occurred at {CustomException(e, sys)}")
        print(CustomException(e, sys))
        print(f"Error connecting to database: {e}")
        logger.error(f"Error connecting to database: {e}")
        return None

def create_table_if_not_exists(connection):
    create_vehicle_table_query = """
    CREATE TABLE IF NOT EXISTS vehicle_data (
        lot_number VARCHAR(50),
        salvage_yard VARCHAR(100),
        asset_number VARCHAR(50),
        location VARCHAR(100),
        restrictions TEXT,
        vehicle_year INT,
        make VARCHAR(50),
        model_sub VARCHAR(50),      
        body_style VARCHAR(50),
        serial_number VARCHAR(50),
        previously_rebuilt VARCHAR(50),
        bc_assigned_vin VARCHAR(50),
        int_ext_colour VARCHAR(50),
        mileage VARCHAR(50),
        engine_size VARCHAR(50),
        transmission VARCHAR(50),
        seats VARCHAR(50),
        fuel_type VARCHAR(50),
        roof_options VARCHAR(50),
        power_equipment VARCHAR(50),
        keys_included VARCHAR(50),
        sound VARCHAR(50),
        us_vehicle VARCHAR(50),
        wheel_type VARCHAR(50),
        prior_damage_over_2000 VARCHAR(50),
        canopy VARCHAR(50),
        dismantle_only VARCHAR(50),
        special_equipment_or_damage TEXT,
        previously_registered_outside_bc VARCHAR(50),
        damage TEXT,
        warning TEXT,
        closing_date TEXT,
		status_code TEXT,
        PRIMARY KEY (lot_number)
    );
    """

    create_image_table_query = """
    CREATE TABLE IF NOT EXISTS vehicle_images (
        id INT AUTO_INCREMENT,
        lot_number VARCHAR(50),
        image LONGTEXT,
        url TEXT,
        PRIMARY KEY (id),
        FOREIGN KEY (lot_number) REFERENCES vehicle_data(lot_number) ON DELETE CASCADE
    );
    """

    try:
        cursor = connection.cursor()
        cursor.execute(create_vehicle_table_query)
        cursor.execute(create_image_table_query)
        connection.commit()
        print("Tables created or already exist.")
        logger.info("Tables created or already exist.")
    except Exception as e:
        logger.info(f"Error Occurred at {CustomException(e, sys)}")
        print(CustomException(e, sys))
        print(f"Error creating tables: {e}")
        logger.error(f"Error creating tables: {e}")
    finally:
        cursor.close()


def escape_single_quotes(value):
    return value.replace("'", "''")

def insert_data_to_database(data, images, status_code):
    connection = connect_to_database()
    if connection:
        create_table_if_not_exists(connection)
        cursor = connection.cursor()
        try:
            for entry in data:
                entry = {key: escape_single_quotes(value) if isinstance(
                    value, str) else value for key, value in entry.items()}

                vehicle_query = f"""
                INSERT INTO vehicle_data (
                    lot_number, salvage_yard, asset_number, location, restrictions,
                    vehicle_year, make, model_sub, body_style, serial_number,
                    previously_rebuilt, bc_assigned_vin, int_ext_colour, mileage,
                    engine_size, transmission, seats, fuel_type, roof_options,
                    power_equipment, keys_included, sound, us_vehicle, wheel_type,
                    prior_damage_over_2000, canopy, dismantle_only,
                    special_equipment_or_damage, previously_registered_outside_bc,
                    damage, warning ,closing_date,status_code
                ) VALUES (
                    '{entry.get('Lot #', '')}', '{entry.get('Salvage Yard', '')}', '{entry.get('Asset #', '')}', '{entry.get('Location', '')}', '{entry.get('Restrictions', '')}',
                    '{entry.get('Vehicle Year', '')}', '{entry.get('Make', '')}', '{entry.get('Model/Sub', '')}', '{entry.get('Body Style', '')}', '{entry.get('Serial Number', '')}',
                    '{entry.get('Previously Rebuilt', '')}', '{entry.get('BC Assigned VIN', '')}', '{entry.get('Int/Ext Colour', '')}', '{entry.get('Mileage', '')}',
                    '{entry.get('Engine Size', '')}', '{entry.get('Transmission', '')}', '{entry.get('Seats', '')}', '{entry.get('Fuel Type', '')}', '{entry.get('Roof Options', '')}',
                    '{entry.get('Power Equipment', '')}', '{entry.get('Keys Included', '')}', '{entry.get('Sound', '')}', '{entry.get('US Vehicle', '')}', '{entry.get('Wheel Type', '')}',
                    '{entry.get('Prior Damage Over $2000', '')}', '{entry.get('Canopy', '')}', '{entry.get('Dismantle Only', '')}',
                    '{entry.get('Special Equipment and/or Prior Damage Description', '')}', '{entry.get('Previously Registered Outside BC', '')}',
                    '{entry.get('Damage', '')}', '{entry.get('Warning', '')}', '{entry.get('Closing Date', '')}'
                    ,'{status_code}'
                )
                ON DUPLICATE KEY UPDATE
                    salvage_yard=VALUES(salvage_yard),
                    asset_number=VALUES(asset_number),
                    location=VALUES(location),
                    restrictions=VALUES(restrictions),
                    vehicle_year=VALUES(vehicle_year),
                    make=VALUES(make),
                    model_sub=VALUES(model_sub),
                    body_style=VALUES(body_style),
                    serial_number=VALUES(serial_number),
                    previously_rebuilt=VALUES(previously_rebuilt),
                    bc_assigned_vin=VALUES(bc_assigned_vin),
                    int_ext_colour=VALUES(int_ext_colour),
                    mileage=VALUES(mileage),
                    engine_size=VALUES(engine_size),
                    transmission=VALUES(transmission),
                    seats=VALUES(seats),
                    fuel_type=VALUES(fuel_type),
                    roof_options=VALUES(roof_options),
                    power_equipment=VALUES(power_equipment),
                    keys_included=VALUES(keys_included),
                    sound=VALUES(sound),
                    us_vehicle=VALUES(us_vehicle),
                    wheel_type=VALUES(wheel_type),
                    prior_damage_over_2000=VALUES(prior_damage_over_2000),
                    canopy=VALUES(canopy),
                    dismantle_only=VALUES(dismantle_only),
                    special_equipment_or_damage=VALUES(special_equipment_or_damage),
                    previously_registered_outside_bc=VALUES(previously_registered_outside_bc),
                    damage=VALUES(damage),
                    warning=VALUES(warning),
                    closing_date=VALUES(closing_date),
                    status_code=VALUES(status_code);
                """

                cursor.execute(vehicle_query)

                logger.info(f"""
                             '{entry.get('Lot #', '')}' --> added or updated
                             
                             """)

                for image in images:
                    try:
                        image_query = f"""
                        INSERT INTO vehicle_images (lot_number, image ,url)
                        VALUES ('{entry.get('Lot #', '')}', '{image[0]}', '{image[1]}');
                        """
                        cursor.execute(image_query)
                        logger.info(f"""
                             '{entry.get('Lot #', '')}' --> images added or updated
                             
                             """)
                    except Exception as e:
                        logger.error(f"Error Occurred at {CustomException(e, sys)}")
                        print(CustomException(e, sys))
                        print(f"Error inserting data: {e}")
                        logger.error(f"""
                             '{entry.get('Lot #', '')}' --> error in images added or updated
                             
                             """)
            connection.commit()
            print("Data inserted successfully.")
        except Exception as e:
            logger.info(f"Error Occurred at {CustomException(e, sys)}")
            print(CustomException(e, sys))
            print(f"Error inserting data: {e}")
            logger.error(f"""
                             '{entry.get('Lot #', '')}' --> error added or updated
                             
                             """)
        finally:
            cursor.close()
            connection.close()

def login(username, password):
    global driver
    driver = webdriver.Chrome(options=chrome_options)
    try:
        driver.get(login_page_url)
        print("Opened login page.")
        username_field = driver.find_element(By.NAME, 'j_username')
        username_field.send_keys(username)
        print("Entered username.")
        logger.info("Entered username.")
        password_field = driver.find_element(By.NAME, 'j_password')
        password_field.send_keys(password)
        print("Entered password.")
        logger.info("Entered password.")
        submit_button = driver.find_element(By.NAME, 'submit')
        submit_button.click()
        print("Clicked submit button.")
        logger.info("Clicked submit button.")

        # Handle session expiry and restart if necessary
        try:
            restart_link = driver.find_element(
                By.LINK_TEXT, 'Restart Salvage Web Session')
            restart_link.click()
            print("Clicked restart link.")
            logger.info("Clicked restart link.")
        except Exception as e:
            logger.info(f"Error Occurred at {CustomException(e, sys)}")
            print(CustomException(e, sys))
            print("No session restart needed.")
            logger.info("No session restart needed.")

        print("Login successful, proceeding to filter page.")
    except Exception as e:
        logger.error(f"Error Occurred at {CustomException(e, sys)}")
        print(CustomException(e, sys))
        print(f"An error occurred during login: {e}")
        logger.error(f"An error occurred during login: {e}")

def extract_structured_data_from_raw(raw_data_dict):
    keys = [
        'Lot #', 'Salvage Yard', 'Asset #', 'Location', 'Restrictions',
        'Vehicle Year', 'Make', 'Model/Sub', 'Body Style', 'Serial Number',
        'Previously Rebuilt', 'BC Assigned VIN', 'Int/Ext Colour', 'Mileage',
        'Engine Size', 'Transmission', 'Seats', 'Fuel Type', 'Roof Options',
        'Power Equipment', 'Keys Included', 'Sound', 'US Vehicle', 'Wheel Type',
        'Prior Damage Over $2000', 'Canopy', 'Dismantle Only',
        'Special Equipment and/or Prior Damage Description',
        'Previously Registered Outside BC', 'Damage', 'Warning']
    structured_data = {key: '' for key in keys}
    for key in raw_data_dict:
        value = raw_data_dict[key]
        if key in keys:
            structured_data[key] = value
        elif ':' in key:
            parts = key.split(':', 1)
            if len(parts) == 2:
                sub_key, sub_value = parts
                sub_key = sub_key.strip()
                sub_value = sub_value.strip()
                if sub_key in structured_data:
                    structured_data[sub_key] = sub_value
    return structured_data

def download_image_as_base64(image_url, cookies):
    try:
        print(f"Downloading image from URL: {image_url}")
        logger.info(f"Downloading image from URL: {image_url}")
        session = requests.Session()
        image_url = image_url.replace('size=1', 'size=2')
        # Add Selenium cookies to the session
        for cookie in cookies:
            session.cookies.set(cookie['name'], cookie['value'])

        # Download the image
        response = session.get(image_url)
        response.raise_for_status()
        image_content = response.content

        return base64.b64encode(image_content).decode('utf-8'), image_url
    except Exception as e:
        print(f"Error downloading image: {e}")
        logger.error(f"Error downloading image: {CustomException(e, sys)}")
        return '', image_url

def extract_structured_data(details):
    # Assuming details is a dictionary with raw scraped data, map to final JSON keys
    try:
        cars_type = "9"
        category = "car"
        make = f"""{details.get("Make", "").split("/")[0]}"""
        model = f"""{details.get("Model/Sub", "").split("/")[0]}"""
        year = f"""{details.get("Vehicle Year", "")}"""
        type = "Coupe" if "2DCPE" in f"""{details.get("Body Style", "")}""" else ""
        status = "21"
        vin = f"""{details.get("Serial Number", "")}"""
        fuel_type = f"""{details.get("Fuel Type", "")}"""
        transmission = f"""{details.get("Transmission", "")}"""
        engine = f"""{details.get("Engine Size", "")}"""
        cylinders = f"""{details.get("Engine Size", "").split(" ")[0].replace("CYL", "")}"""
        drive = ""
        kilometer = f"""{details.get("Mileage", "")}"""
        mileage_type = "KM"
        condition = f"""{details.get("Damage", "")}"""
        keys = f"""{str(0) if details.get("Keys Included") == "N" else str(1)}"""
        stock_number = f"""{details.get("Lot #", "")}"""
        interior_colour = f"""{details.get("Int/Ext Colour", "").split("/")[0]}"""
        exterior_colour = f"""{details.get("Int/Ext Colour", "").split("/")[1]}"""
        accessories = ""
        currency = "CAD"
        price = "1"
        country = "2"
        state = "4"
        location = details.get("Location", "")
        location_parts = location.split(", ")

        if len(location_parts) > 1:
            city_info = location_parts[1].split(" ")
            if len(city_info) > 1 and city_info[1] == "BC":
                city = city_info[0]
            else:
                city = location_parts[1]
        else:
            city = "Unknown"
        auction_date = f"""{details.get("Closing Date", "")}"""
        purchase_option = "0"
        hid_main_images = ""
        hid_addedtype = "2"
        hid_addedby = "47"
        h_inventory = "addinventory"
        hid_allimages = []
    except Exception as e:
        logger.error(f"Error Occurred at {CustomException(e, sys)}")
        print(CustomException(e, sys))
    d = {
        "cars_type": cars_type,
        "category": category,
        "make": make,
        "model": model,
        "year": year,
        "type": type,
        "status": status,
        "vin": vin,
        "fuel_type": fuel_type,
        "transmission": transmission,
        "engine": engine,
        "cylinders": cylinders,
        "drive": drive,
        "kilometer": kilometer,
        "mileage_type": mileage_type,
        "condition": condition,
        "keys": keys,
        "stock_number": stock_number,
        "interior_colour": interior_colour,
        "exterior_colour": exterior_colour,
        "accessories": accessories,
        "currency": currency,
        "price": price,
        "country": country,
        "state": state,
        "city": city,
        "auction_date": auction_date,
        "purchase_option": purchase_option,
        "hid_main_images": hid_main_images,
        "hid_addedtype": hid_addedtype,
        "hid_addedby": hid_addedby,
        "h_inventory": h_inventory,
        "hid_allimages": hid_allimages,
    }
    a= d
    del a['hid_allimages']
    print(a)
    return d

def call_api(data):
    try:
        headers = {'accept': 'application/json', 'Content-Type': 'application/json'}
        url = "https://americanauctionaccess.com/icbc-scrap-api"

        response = requests.post(url, headers=headers, data=data)
        print(response.status_code)
        if response.status_code == 200:
            logger.info("Data successfully sent to API")
            print("Data successfully sent to API")
            return f"successful status code - {response.status_code}"
        else:
            print(f"Failed to send data to API. Status code: {response.status_code}")
            return f"Failed status code - {response.status_code}"
    except Exception as e:
        logger.error(f"Error Occurred at {CustomException(e, sys)}")
        print(CustomException(e, sys))
        return "None"

def convert_date_format(date_str):
    # Parse the given date string to a datetime object
    date_object = datetime.strptime(date_str, '%B %d, %Y %I:%M %p')
    # Convert the datetime object to the desired format "YYYY-MM-DD"
    formatted_date = date_object.strftime('%Y-%m-%d')
    return formatted_date

def scrape_page(page_num, cookies):
    page_data = []
    try:
        detail_table_xpath = '/html/body/p[1]/table[1]/tbody[1]/tr[4]/td[1]/table[1]/tbody[1]/tr[1]/td[1]/table[1]'
        detail_table = driver.find_element(By.XPATH, detail_table_xpath)
        details = {}
        rows = detail_table.find_elements(By.TAG_NAME, 'tr')
        for row in rows:
            cols = row.find_elements(By.TAG_NAME, 'td')
            if len(cols) >= 4:
                details[cols[0].text.strip(':')] = cols[1].text
                details[cols[2].text.strip(':')] = cols[3].text
            elif len(cols) == 2:
                details[cols[0].text.strip(':')] = cols[1].text
        closing_date_xpath = '/html/body/p/table/tbody/tr[2]/td/span'
        closing_date_element = driver.find_element(
            By.XPATH, closing_date_xpath)
        closing_date_text = closing_date_element.text
        closing_date_text = convert_date_format(closing_date_text)
        details = extract_structured_data_from_raw(details)
        details['Closing Date'] = closing_date_text

        image_table = driver.find_element(
            By.XPATH, '/html/body/p[1]/table[1]/tbody[1]/tr[3]/td')
        image_elements = image_table.find_elements(By.TAG_NAME, 'img')
        images = [img.get_attribute('src') for img in image_elements if 'AssetImageAction' in img.get_attribute('src')]
        images = [download_image_as_base64(img, cookies) for img in images]
        details['Images'] = images
        page_data.append(details)
        data = extract_structured_data(details)
        fue_t = {
            "G": "Gas",
            "P": "Petrol",
            "D": "Diesel",
            "E": "Electric",
            "N": "None"
        }
        fuel = data.get("fuel_type")[0]
        data['fuel_type'] = fue_t.get(fuel, "")
        data['transmission'] = "Automatic" if data.get("transmission", "") == "AUTO" else data.get("transmission", "")
        print(data)
        data['hid_allimages'] = [f"""{img[0]}""" for img in images]
        print(f" Total Images {len(data['hid_allimages'])}")
        logger.info(f" Total Images {len(data['hid_allimages'])}")

        file_name = f"{data['stock_number']}.json"
        file_path = os.path.join("data/icbc", file_name)

        if not os.path.exists("data/icbc"):
            os.makedirs("data/icbc")

        with open(file_path, 'w') as json_file:
            json.dump(data, json_file, indent=4)
        # print(data)
        json_data = json.dumps(data)
        if len(data['hid_allimages'])>0:
            status_code = call_api(json_data)
            # logger.info(json_data)
            insert_data_to_database(page_data, images, str(status_code))
            print(f"VIN NUMBER {data['vin']} - stock Number {data['stock_number']} data appended to database.")
            logger.info(f"VIN NUMBER {data['vin']} - stock Number {data['stock_number']} data appended to database.")
            print(status_code)
        else:
            print(f"VIN NUMBER {data['vin']} - stock Number {data['stock_number']} has No Images")
            logger.info(f"VIN NUMBER {data['vin']} - stock Number {data['stock_number']} has No Image")
    except Exception as e:
        logger.info(f"Error Occurred at {CustomException(e, sys)}")
        print(CustomException(e, sys))
        print(f"Error scraping page {page_num}: {e}")
    return page_data


def navigate_and_submit_filter(cookies,b_years,e_years):
    try:
        driver.get(filter_page_url)
        print("Opened filter page.")
        logger.info("Opened filter page.")
        b_year = driver.find_element(By.NAME, 'by')
        b_year.send_keys(b_years)
        e_year = driver.find_element(By.NAME, 'ey')
        e_year.send_keys(e_years)
        submit_button = driver.find_element(By.NAME, 's2')
        submit_button.click()
        print("Clicked filter submit button.")
        logger.info("Clicked filter submit button.")
        total_found, first_page = get_total_pages()
        print(f"Total pages: {total_found}")
        logger.info(f"Total pages: {total_found}")
        for page_num in range(1, total_found + 2):
            print(f"Scraping page {page_num}...")
            logger.info(f"Scraping page {page_num}...")
            scrape_page(page_num, cookies)
            if page_num < total_found:
                next_page_url = get_next_page_url(first_page, page_num)
                driver.get(next_page_url)
    except Exception as e:
        logger.info(f"Error Occurred at {CustomException(e, sys)}")
        print(CustomException(e, sys))
        print(
            f"An error occurred during navigation and filter submission: {e}")

def get_total_pages():
    try:
        total_found_element = driver.find_element(
            By.XPATH, '/html/body/center/table/tbody/tr[2]/td[1]/table[1]/tbody/tr[2]/td/center/b[1]')
        total_found_text = total_found_element.text
        total_found = int(total_found_text.split()[0])
        first_page = driver.find_element(
            By.XPATH, '/html/body/center/table/tbody/tr[2]/td[1]/table[2]/tbody/tr[3]/td[1]/a')
        first_page = first_page.get_attribute('href')
        return total_found, first_page
    except Exception as e:
        logger.error(f"Error Occurred at {CustomException(e, sys)}")
        print(CustomException(e, sys))
        print(f"Error extracting total pages: {e}")
        return 1, ''

def get_next_page_url(first_page, rel):
    try:
        url_parts = first_page.split('rel=')
        return f"{url_parts[0]}rel={rel}"
    except Exception as e:
        logger.error(f"Error Occurred at {CustomException(e, sys)}")
        print(CustomException(e, sys))
        print(f"Error constructing next page URL: {e}")
        return ''

def close_browser(driver):
    if driver:
        driver.quit()
        print("Closed the browser.")
        logger.info("Closed the browser.")
        return "Stopping Scrapping"



from fastapi import FastAPI, HTTPException
from typing import List
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
import requests
import sys, os, json,re
from datetime import datetime
from time import sleep, time
import mysql.connector
from mysql.connector import Error
# Custom exception and logger_edge setup
from exception import CustomException, setup_logger
logger_edge = setup_logger("edgepipeline", "edgepipeline")
app = FastAPI()
# Database configuration
db_config_2 = {
    'host': 'localhost',  # Replace with your database host
    'user': 'root',  # Replace with your database user
    'password': '',  # Replace with your database password
    'database': 'scrap_data',  # Replace with your database name
    'port': 3307
}
# db_config_2 = {
#    'host': 'localhost',        # Replace with your database host
#    'user': 'icbc_scrapper',             # Replace with your database user
#    'password': 'R3RhtTyGEjGD7pZV8WJY6N9oeWRXsAxZ',             # Replace with your database password
#    'database': 'icbc_scrapper_DB',   # Replace with your database name
#    'port': 3306
# }
def convert_date_format_edge(date_str):
    try:
        input_date = datetime.strptime(date_str, '%a, %m/%d/%y')
        return input_date.strftime('%Y-%m-%d')
    except ValueError as e:
        logger_edge.error(f"Date conversion error: {e}")
#         return ''
driver2 = None
# Create database tables if they don't exist
def create_tables_edge():
    connection = mysql.connector.connect(
        host=db_config_2['host'],
        user=db_config_2['user'],
        password=db_config_2['password'],
        database=db_config_2['database'],
        port=db_config_2['port']
    )
    cursor = connection.cursor()

    create_vehicles_table = """
    CREATE TABLE IF NOT EXISTS vehicles__ (
        id INT AUTO_INCREMENT PRIMARY KEY,
        cars_type VARCHAR(50),
        category VARCHAR(50),
        make VARCHAR(50),
        model VARCHAR(50),
        year VARCHAR(4),
        type VARCHAR(50),
        status VARCHAR(50),
        vin VARCHAR(50) UNIQUE,
        fuel_type VARCHAR(50),
        transmission VARCHAR(50),
        engine VARCHAR(50),
        cylinders VARCHAR(50),
        drive VARCHAR(50),
        kilometer VARCHAR(50),
        mileage_type VARCHAR(50),
        `condition` VARCHAR(50),
        `keys` VARCHAR(100),
        stock_number VARCHAR(50),
        interior_colour VARCHAR(50),
        exterior_colour VARCHAR(50),
        accessories VARCHAR(100),
        currency VARCHAR(3),
        price VARCHAR(100),
        country VARCHAR(50),
        state VARCHAR(50),
        city VARCHAR(50),
        auction_date VARCHAR(100),
        purchase_option VARCHAR(100),
        hid_addedtype VARCHAR(50),
        hid_addedby VARCHAR(50),
        h_inventory VARCHAR(50),
        auction_name VARCHAR(100),
        drivable VARCHAR(100),
        engine_runs VARCHAR(100),
        title_status VARCHAR(50),
        run_no VARCHAR(50),
        pmr VARCHAR(50)
    );
    """

    create_vehicle_images_table = """
    CREATE TABLE IF NOT EXISTS vehicle_images__ (
        id INT AUTO_INCREMENT PRIMARY KEY,
        vin VARCHAR(50),
        image_base64 LONGTEXT,
        FOREIGN KEY (vin) REFERENCES vehicles__(vin) ON DELETE CASCADE
    );
    """

    cursor.execute(create_vehicles_table)
    cursor.execute(create_vehicle_images_table)
    connection.commit()
    cursor.close()
    connection.close()

# Initialize tables


# Set up Chrome WebDriver options
chrome_options = Options()
chrome_options.add_argument("--headless")
chrome_options.add_argument("--disable-gpu")
chrome_options.add_argument("--no-sandbox")
# Overcome limited resource problems
chrome_options.add_argument("--disable-dev-shm-usage")
chrome_options.add_argument(
    "user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
)
chrome_options.add_argument("--disable-blink-features=AutomationControlled")
chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
chrome_options.add_experimental_option("useAutomationExtension", False)
chrome_options.add_argument("--window-size=1920x1080")
chrome_options.add_argument("--disable-extensions")
chrome_options.add_argument("--proxy-server='direct://'")
chrome_options.add_argument("--proxy-bypass-list=*")
chrome_options.binary_location = "/usr/bin/chromium-browser"
logger_edge.info(f"{str(db_config_2)}\n{chrome_options.binary_location}")

# Function to extract text using explicit wait
def get_element_text_edge(driver2, selector, name):
    try:
        element = WebDriverWait(driver2, 5).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, selector))
        )
        return element.text
    except Exception as e:
        logger_edge.error(f"Error Occurred at {CustomException(e, sys)}")
        print(CustomException(e, sys))
        logger_edge.error(f"Error extracting {name}: {e}")
        return None

# Function to extract data from a single URL
def extract_data_from_url(driver2, url):
    data = {}
    start_time = time()
    try:
        driver2.get(url)
        driver2.set_window_size(1366, 768)
        sleep(4)

#vdp > div.overview > h1
        try:
        
            data['heading'] = WebDriverWait(driver2, 10).until(
                EC.presence_of_element_located((By.XPATH, '//*[@class="overview"]/h1'))
            ).text
            
        except Exception as e:
            logger_edge.error(f"Error Occurred at {CustomException(e, sys)}")
            print(CustomException(e, sys))
            logger_edge.error(f"Error extracting heading: {e}")
            data['heading'] = " "
        
        
        get_element_text_edge(driver2, "#vdp > div.overview > h1","heading")
        data['run'] = get_element_text_edge(driver2, "#vdp > div.overview > div.general-section > div.cell.run-number > span", "run")
        data['vin'] = get_element_text_edge(driver2, "#vdp > div.overview > div.general-section > div.cell.vin > span", "vin")
        data['pmr'] = get_element_text_edge(driver2, "#vdp > div.overview > div.general-section > div.cell.pmr > div > div > span", "pmr")
        data['kilometer'] = get_element_text_edge(driver2, "#vdp > div.overview > div.general-section > div.cell.odometer > span", "kilometer")

        data['details'] = extract_section_data_edge(driver2, "#vdp > div.sections > div.section.details.closed > div > div", 13)
        data['auction'] = extract_section_data_edge(driver2, "#vdp > div.sections > div.section-group > div.section.auction.closed > div > div", 6)
        data['declarations'] = extract_section_data_edge(driver2, "#vdp > div.sections > div.section-group > div.section.declarations.closed > div > div", 4)
        print(data)
        data['images_bs64'], data['images_links'] = get_image_sources_edge(driver2, 'images')

        elapsed_time = time() - start_time
        new = get_iframe_data_edge(driver2)
        data.update(new)
        logger_edge.info(f"Extracted data from {url} in {elapsed_time:.2f} seconds")
    except Exception as e:
        logger_edge.error(f"Error Occurred at {CustomException(e, sys)}")
        print(CustomException(e, sys))
        logger_edge.error(f"Error extracting data from {url}: {CustomException(e, sys)}")
    return data

# Function to extract data from specific sections
def extract_section_data_edge(driver2, section_selector, child_count):
    section_data = {}
    for i in range(1, child_count + 1):
        label_selector = f"{section_selector} > div:nth-child({i}) > label"
        value_selector = f"{section_selector} > div:nth-child({i}) > span"
        label_text = get_element_text_edge(driver2, label_selector, f"label_{i}")
        value_text = get_element_text_edge(driver2, value_selector, f"value_{i}")
        if label_text and value_text:
            section_data[label_text] = value_text
    return section_data

# Function to get image sources
def get_image_sources_edge(driver2, name):
    sources_bs64 = []
    sources = []
    try:
        element = WebDriverWait(driver2, 20).until(
            EC.presence_of_all_elements_located((By.CLASS_NAME, "fotorama__img"))
        )
        for ele in element:
            img_url = ele.get_attribute('src').replace('AweDc1Ow', 'YwMHgxMjAwOw')
            sources.append(img_url)
            sources_bs64.append(download_image_as_base64_edge(img_url))
        elements = WebDriverWait(driver2, 20).until(
            EC.presence_of_all_elements_located((By.CSS_SELECTOR, "div.fotorama__thumb.fotorama__loaded.fotorama__loaded--img > img"))
        )

        for element in elements:
            img_url = element.get_attribute('src').replace('AweDc1Ow', 'YwMHgxMjAwOw')
            sources.append(img_url)
            sources_bs64.append((img_url))
        return sources_bs64, sources
    except Exception as e:
        logger_edge.error(f"Error Occurred at {CustomException(e, sys)}")
        print(CustomException(e, sys))
        logger_edge.error(f"Error extracting {name}: {e}")
    return sources_bs64, sources

# Function to download image as base64
def download_image_as_base64_edge(image_url):
    try:
        logger_edge.info(f"Downloading image from URL: {image_url}")
        # response = requests.get(image_url)
        # response.raise_for_status()
        print('Done-->',image_url)
        return image_url  # base64.b64encode(response.content).decode('utf-8')
    except requests.exceptions.RequestException as e:
        logger_edge.error(f"Error downloading image: {CustomException(e, sys)}")
        return ''

def check_first_numeric_value_edge(input_string):
    numbers = re.findall(r'\d+', input_string)
    if numbers:
        return "1" if int(numbers[0]) > 0 else "0"
    else:
        return "0"


def get_iframe_data_edge(driver2):
    new = {}
    try:
        iframe = driver2.find_element(By.CLASS_NAME, 'cr-iframe')
        driver2.switch_to.frame(iframe)
        spotlight_fields = driver2.find_elements(By.CLASS_NAME, 'cr-spotlight-field')
        for spotlight_field in spotlight_fields:
            try:
                inner_divs = spotlight_field.find_elements(By.TAG_NAME, 'div')
                for div in inner_divs:
                    span_texts = []
                    spans = div.find_elements(By.TAG_NAME, 'span')
                    for span in spans:
                        span_texts.append(span.text)
                    div_text = div.text
                    for span_text in span_texts:
                        div_text = div_text.replace(span_text, '').strip()
                    if "Engine Runs" in span_texts or "Keys" in span_texts:
                        if"Keys" in span_texts:
                            div_text = check_first_numeric_value_edge(div_text)
                        new[span_text]=div_text
                        
                        
            except Exception as e:
                new['Engine runs']='0'
                new['Keys'] = '0'

        print(new)
        return new
    except Exception as e:
        
        print(HTTPException(status_code=500, detail=str(e)))
        new['Engine runs']='0'
        new['Keys'] = '0'
        return new

# Define a model for the request body
class RequestBody(BaseModel):
    id: str
    password: str
    links: List[str]
    
    
def format_data_edge(data):
    try:
        details = data.get('details', {})
        auction = data.get('auction', {})
        declarations = data.get('declarations', {})
        
        try :
            make = data.get('heading'," ").split()[1]
        except : 
            make  = " "
        
        try:
            model = data.get('heading'," ").split()[2]
        except:
            model =" "
        try:
            year = data.get('heading'," ").split()[0]
        except:
            year = " "
        try:
            type = data.get('heading'," ").split()[6]
        except:
            type = " "
        
        formatted_data = {
        "cars_type": "10",
        "category": "car",
        "make": make,
        "model": model,
        "year": year ,
        "type": type ,
        "status": "724",
        "vin": data.get('vin', ''),
        "fuel_type": details.get('Fuel Type', ''),
        "transmission": details.get('Transmission', ''),
        "engine": f"{details.get('Displacement', '')} {details.get('Cylinders', '').split(' ')[0].replace('CYL', '')}cyl",
        "cylinders": details.get('Cylinders', '').split(' ')[0].replace('CYL', ''),
        "drive": details.get('Drive Train', ''),
        "kilometer": ''.join(filter(str.isdigit, data.get('kilometer', ''))),
        "mileage_type": "Mile",
        "condition": "",
        "keys": "0" if data.get("Keys") == "0" else "1",
        "stock_number": auction.get('Stock Number', ''),
        "interior_colour": details.get('Interior Color / Material', '').split(' /')[0],
        "exterior_colour": details.get('Color', ''),
        "accessories": "",
        "currency": "USD",
        "price": "1",
        "country": "1",
        "state": auction.get('Location', '').split(", ")[1],
        "city": auction.get('Location', '').split(", ")[0],
        "auction_date": f"{convert_date_format_edge(auction.get('Sale Date', '').split(' (')[0])}",
        "purchase_option": "0",
        "hid_main_images": "",
        "hid_addedtype": "2",
        "hid_addedby": "47",
        "h_inventory": "addinventory",
        "auction_name": auction.get('Auction', ''),
        "drivable": '1' if str(declarations.get('Drivable', '')).lower()=='yes' else '0',
        "engine_runs" : '1' if data.get('Engine Runs', '').lower()=='yes' else '0',
        "title_status": declarations.get('Title Status', ''),
        "run_no": data.get('run', ''),
        "pmr": ''.join(filter(str.isdigit, data.get('pmr', ''))) ,
        "hid_allimages": data.get('images_links', [])}
        # print ('\n--------------------------------\n',formatted_data)
        return formatted_data
    except Exception as e:
        logger_edge.error(f"Error Occurred at {CustomException(e, sys)}")
        print(CustomException(e, sys))
        return {}
    # Define your API endpoint

def call_edge(driver2,id,password,links):
    try:
        parsed_data = []
        driver2.get('https://www.edgepipeline.com/components/login')  # Replace with the actual login URL
        # Find the username and password input elements and fill them
        username_input = driver2.find_element(By.ID, 'username')
        password_input = driver2.find_element(By.ID, 'password')
        username_input.send_keys(id)  # Replace with actual username
        password_input.send_keys(password)  # Replace with actual password
        # Submit the form
        submit_button = driver2.find_element(By.XPATH, "//input[@type='submit' and @value='Sign In']")
        submit_button.click()
        for link in links:
            try:
                print("\n\n===>Link--"+link+"\n\n")
                logger_edge.info("\n\n===>Link--"+link+"\n\n")
                yield "\n\n==>Link--"+link+"\n\n"
                data = extract_data_from_url(driver2, link)
                if data:
                    print(data.keys())
                    formatted_data = format_data_edge(data)
                    file_name = f"{formatted_data.get('vin','  ')}.json"
                    file_path = os.path.join("data/edge", file_name)

                    if not os.path.exists("data/edge"):
                        os.makedirs("data/edge")

                    with open(file_path, 'w') as json_file:
                        json.dump(formatted_data, json_file, indent=4)

                    parsed_data.append(formatted_data)
                    insert_data_edge(formatted_data)
                    call_api_edge(json.dumps(formatted_data))
                    # del formatted_data['hid_allimages']
                    print(f"\n\n {json.dumps(formatted_data)}\n")
                    logger_edge.info(f"\n\n {json.dumps(formatted_data)}\n")
                    yield(f"\n\n {json.dumps(formatted_data)}\n")
            except Exception as e:
                print("error")
                logger_edge.error("error")
                yield "error"
                logger_edge.error(f"Error Occurred at {CustomException(e, sys)}")
                print(CustomException(e, sys))
    finally:
        driver2.quit()
        logger_edge.info("\n\ncompleted")
        yield "\n\ncompleted"




    
# Function to call_edge an external API
def call_api_edge(data):
    try:
        headers = {'accept': 'application/json', 'Content-Type': 'application/json'}
        url = "https://americanauctionaccess.com/edge-scrap-api"
        response = requests.post(url, headers=headers, data=data)
        if response.status_code == 200:
            return response.json()
        else:
            raise Exception(f"Failed to send data to API. Status code: {response.status_code}")
    except requests.exceptions.RequestException as e:
        logger_edge.error(f"Error sending data to API: {CustomException(e, sys)}")
        print(f"Error sending data to API: {CustomException(e, sys)}")
# Function to insert data into the database
# Function to insert data into the database
def insert_data_edge(data):
    connection = None
    cursor = None
    create_tables_edge()
    try:
        connection = mysql.connector.connect(
            host=db_config_2['host'],
            user=db_config_2['user'],
            password=db_config_2['password'],
            database=db_config_2['database'],
            port=db_config_2['port']
        )
        cursor = connection.cursor()
        # Prepare data excluding images
        vehicle_data = {key: data[key] for key in data if key != 'hid_allimages'}
        
        insert_query = """
        INSERT INTO vehicles__ (
            cars_type, category, make, model, year, type, status, vin, fuel_type, transmission, engine, cylinders, drive,
            kilometer, mileage_type, `condition`, `keys`, stock_number, interior_colour, exterior_colour, accessories, currency, price, country, state, city,
            auction_date, purchase_option, hid_addedtype, hid_addedby, h_inventory, auction_name, drivable, engine_runs, title_status,
            run_no, pmr
        ) VALUES (
            %(cars_type)s, %(category)s, %(make)s, %(model)s, %(year)s, %(type)s, %(status)s, %(vin)s, %(fuel_type)s, %(transmission)s, 
            %(engine)s, %(cylinders)s, %(drive)s, %(kilometer)s, %(mileage_type)s, %(condition)s, %(keys)s, %(stock_number)s, 
            %(interior_colour)s, %(exterior_colour)s, %(accessories)s, %(currency)s, %(price)s, %(country)s, %(state)s, %(city)s, 
            %(auction_date)s, %(purchase_option)s, %(hid_addedtype)s, %(hid_addedby)s, %(h_inventory)s, %(auction_name)s, %(drivable)s, 
            %(engine_runs)s, %(title_status)s, %(run_no)s, %(pmr)s
        )
        ON DUPLICATE KEY UPDATE 
            category=VALUES(category), make=VALUES(make), model=VALUES(model), year=VALUES(year), type=VALUES(type), 
            status=VALUES(status), fuel_type=VALUES(fuel_type), transmission=VALUES(transmission), engine=VALUES(engine), cylinders=VALUES(cylinders), 
            drive=VALUES(drive), kilometer=VALUES(kilometer), mileage_type=VALUES(mileage_type), `condition`=VALUES(`condition`), 
            `keys`=VALUES(`keys`), stock_number=VALUES(stock_number), interior_colour=VALUES(interior_colour), exterior_colour=VALUES(exterior_colour), 
            accessories=VALUES(accessories), currency=VALUES(currency), price=VALUES(price), country=VALUES(country), state=VALUES(state), 
            city=VALUES(city), auction_date=VALUES(auction_date), purchase_option=VALUES(purchase_option),  
            hid_addedtype=VALUES(hid_addedtype), hid_addedby=VALUES(hid_addedby), h_inventory=VALUES(h_inventory), auction_name=VALUES(auction_name), 
            drivable=VALUES(drivable), engine_runs=VALUES(engine_runs), title_status=VALUES(title_status), run_no=VALUES(run_no), pmr=VALUES(pmr)
        """
        cursor.execute(insert_query, vehicle_data)
        
        # Insert images separately
        vehicle_vin = data.get('vin')
        for image_base64 in data.get('hid_allimages', []):
            cursor.execute("""
                INSERT INTO vehicle_images__ (vin, image_base64) VALUES (%s, %s)
            """, (vehicle_vin, image_base64))
        connection.commit()
        logger_edge.info(f"Inserted data for vehicle with VIN: {data.get('vin')}")
    except Error as e:
        logger_edge.error(f"Error Occurred at {CustomException(e, sys)}")
        print(CustomException(e, sys))
    finally:
        if cursor:
            cursor.close()
        if connection:
            connection.close()



@app.post("/ICBC_Scrape")
def login_endpoint(login_details: LoginDetails):
    global driver
    try:
        login(login_details.username, login_details.password)
        cookies = driver.get_cookies()
        navigate_and_submit_filter(cookies,login_details.b_year,login_details.e_year)
        return {"message": "Scraping completed."}
    except Exception as e:
        logger.error(f"Error Occurred at {CustomException(e, sys)}")
        print(CustomException(e, sys))

    finally:
        close_browser()


@app.post("/parse_links_edge/")
async def parse_links_edge(request_body: RequestBody):
    try:
        # call_edge(request_body.id,request_body.password)
        global driver2
        driver2 = webdriver.Chrome(options=chrome_options)

        return StreamingResponse(call_edge(driver2,request_body.id,request_body.password ,request_body.links), media_type="text/plain")
    except Exception as e:
                logger_edge.error(f"Error Occurred at {CustomException(e, sys)}")
                print(CustomException(e, sys))

@app.post("/stop-server-edge")
def stop_server():
    close_browser(driver2)
        


@app.post("/stop-server_icbc")
def stop_server():
    close_browser(driver=driver)


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=3033)
