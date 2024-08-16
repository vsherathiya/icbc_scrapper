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
# db_config = {
#     'host': 'localhost',  # Replace with your database host
#     'user': 'root',  # Replace with your database user
#     'password': '',  # Replace with your database password
#     'database': 'scrap_data',  # Replace with your database name
#     'port': 3307
# }
db_config = {
   'host': 'localhost',        # Replace with your database host
   'user': 'icbc_scrapper',             # Replace with your database user
   'password': 'R3RhtTyGEjGD7pZV8WJY6N9oeWRXsAxZ',             # Replace with your database password
   'database': 'icbc_scrapper_DB',   # Replace with your database name
   'port': 3306
}

# Setup Chrome options
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
    except requests.exceptions.RequestException as e:
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

    return {
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


def close_browser():
    if driver:
        driver.quit()
        print("Closed the browser.")
        logger.info("Closed the browser.")
        return "Stopping Scrapping"


@app.post("/Scrape")
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
        raise HTTPException(
            status_code=500, detail="An error occurred during scraping.")
    finally:
        close_browser()


@app.post("/stop-server")
def stop_server():
    close_browser()


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=3033)
