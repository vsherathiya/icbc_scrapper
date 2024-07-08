from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Optional
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

app = FastAPI()

# Login and filter page URLs
login_page_url = 'https://onlinebusiness.icbc.com/salvage/auth/Form-login.jsp'
filter_page_url = 'https://onlinebusiness.icbc.com/salvage/webServlet/Search?form=VehicleSales'

# Database configuration
db_config = {
    'host': 'localhost',        # Replace with your database host
    'user': 'root',             # Replace with your database user
    'password': '',             # Replace with your database password
    'database': 'scrap_data',   # Replace with your database name
    'port': 3307
}

# db_config = {
#     'host': 'localhost',        # Replace with your database host
#     'user': 'icbc_scrapper',             # Replace with your database user
#     'password': 'R3RhtTyGEjGD7pZV8WJY6N9oeWRXsAxZ',             # Replace with your database password
#     'database': 'icbc_scrapper_DB',   # Replace with your database name
#     'port': 3306
#}

# Setup Chrome options
chrome_options = Options()
chrome_options.add_argument("--headless")
chrome_options.add_argument("--disable-gpu")
chrome_options.add_argument("--no-sandbox")
# chrome_options.binary_location = "/usr/bin/chromium-browser"  # Adjust this path if necessary

driver = None

class LoginDetails(BaseModel):
    username: str = "B073902"
    password: str = "MUJEB786"

def connect_to_database():
    try:
        connection = mysql.connector.connect(**db_config)
        if connection.is_connected():
            print("Connected to the database.")
            return connection
    except Error as e:
        print(f"Error connecting to database: {e}")
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
    except Error as e:
        print(f"Error creating tables: {e}")
    finally:
        cursor.close()

def escape_single_quotes(value):
    return value.replace("'", "''")

def insert_data_to_database(data, images):
    connection = connect_to_database()
    if connection:
        create_table_if_not_exists(connection)
        cursor = connection.cursor()
        try:
            for entry in data:
                entry = {key: escape_single_quotes(value) if isinstance(value, str) else value for key, value in entry.items()}
                
                vehicle_query = f"""
                INSERT INTO vehicle_data (
                    lot_number, salvage_yard, asset_number, location, restrictions,
                    vehicle_year, make, model_sub, body_style, serial_number,
                    previously_rebuilt, bc_assigned_vin, int_ext_colour, mileage,
                    engine_size, transmission, seats, fuel_type, roof_options,
                    power_equipment, keys_included, sound, us_vehicle, wheel_type,
                    prior_damage_over_2000, canopy, dismantle_only,
                    special_equipment_or_damage, previously_registered_outside_bc,
                    damage, warning ,closing_date
                ) VALUES (
                    '{entry.get('Lot #', '')}', '{entry.get('Salvage Yard', '')}', '{entry.get('Asset #', '')}', '{entry.get('Location', '')}', '{entry.get('Restrictions', '')}',
                    '{entry.get('Vehicle Year', '')}', '{entry.get('Make', '')}', '{entry.get('Model/Sub', '')}', '{entry.get('Body Style', '')}', '{entry.get('Serial Number', '')}',
                    '{entry.get('Previously Rebuilt', '')}', '{entry.get('BC Assigned VIN', '')}', '{entry.get('Int/Ext Colour', '')}', '{entry.get('Mileage', '')}',
                    '{entry.get('Engine Size', '')}', '{entry.get('Transmission', '')}', '{entry.get('Seats', '')}', '{entry.get('Fuel Type', '')}', '{entry.get('Roof Options', '')}',
                    '{entry.get('Power Equipment', '')}', '{entry.get('Keys Included', '')}', '{entry.get('Sound', '')}', '{entry.get('US Vehicle', '')}', '{entry.get('Wheel Type', '')}',
                    '{entry.get('Prior Damage Over $2000', '')}', '{entry.get('Canopy', '')}', '{entry.get('Dismantle Only', '')}',
                    '{entry.get('Special Equipment and/or Prior Damage Description', '')}', '{entry.get('Previously Registered Outside BC', '')}',
                    '{entry.get('Damage', '')}', '{entry.get('Warning', '')}', '{entry.get('Closing Date', '')}'
                );
                """
                
                cursor.execute(vehicle_query)
                
                for image in images:
                    image_query = f"""
                    INSERT INTO vehicle_images (lot_number, image ,url)
                    VALUES ('{entry.get('Lot #', '')}', '{image[0]}', '{image[1]}');
                    """
                    cursor.execute(image_query)
                    
            connection.commit()
            print("Data inserted successfully.")
        except Error as e:
            print(f"Error inserting data: {e}")
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
        password_field = driver.find_element(By.NAME, 'j_password')
        password_field.send_keys(password)
        print("Entered password.")
        submit_button = driver.find_element(By.NAME, 'submit')
        submit_button.click()
        print("Clicked submit button.")

        # Handle session expiry and restart if necessary
        try:
            restart_link = driver.find_element(By.LINK_TEXT, 'Restart Salvage Web Session')
            restart_link.click()
            print("Clicked restart link.")
        except Exception as e:
            print("No session restart needed.")
        
        print("Login successful, proceeding to filter page.")
    except Exception as e:
        print(f"An error occurred during login: {e}")

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
        return '', image_url
    

def extract_structured_data(details):
    # Assuming details is a dictionary with raw scraped data, map to final JSON keys
    return {
        "cars_type": "9",
        "category": "car",
        "make": details.get("Make", "").split("/")[0],
        "model": details.get("Model/Sub", "").split("/")[0],
        "year": details.get("Vehicle Year", ""),
        "type": "Coupe" if "2DCPE" in details.get("Body Style", "") else "",
        "status": "Damaged",
        "vin": details.get("Serial Number", ""),
        "fuel_type": details.get("Fuel Type", ""),
        "transmission": details.get("Transmission", ""),
        "engine": details.get("Engine Size", ""),
        "cylinders": details.get("Engine Size", "").split(" ")[0].replace("CYL", ""),
        "drive": "",
        "kilometer": details.get("Mileage", ""),
        "mileage_type": "KM",
        "condition": details.get("Damage",""),
        "keys": str(0) if details.get("Keys Included") == "N" else str(1),
        "stock_number": details.get("Lot #", ""),
        "interior_colour": details.get("Int/Ext Colour", "").split("/")[0],
        "exterior_colour": details.get("Int/Ext Colour", "").split("/")[1],
        "accessories": "",
        "currency": "CAD",
        "price": "1",
        "country": "Canada",
        "state": "British Columbia",
        "city": str(details.get("Location", "").split(", ")[1]) ,
        "auction_date": details.get("Closing Date", ""),
        "purchase_option": "0",
        "hid_main_images": "",
        "hid_addedtype": "2",
        "hid_addedby": "47",
        "h_inventory": "addinventory",
        "hid_allimages": []
    }
    
def call_api(data):
    url = "https://americanauctionaccess.com/scrap-api"
        # Convert data to JSON string
    data_json = json.dumps(data)

    response = requests.post(url, json=data_json)
    if response.status_code == 200:
        print("Data successfully sent to API")
    else:
        print(f"Failed to send data to API. Status code: {response.status_code}")

from datetime import datetime

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
        closing_date_element = driver.find_element(By.XPATH, closing_date_xpath)
        closing_date_text = closing_date_element.text
        closing_date_text = convert_date_format(closing_date_text)
        details = extract_structured_data_from_raw(details)
        details['Closing Date'] = closing_date_text
        
        print(details)
        
        image_table = driver.find_element(By.XPATH, '/html/body/p[1]/table[1]/tbody[1]/tr[3]/td')
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
        data['fuel_type'] = fue_t.get(fuel,"")
        data['transmission'] = "Automatic" if data.get("transmission","")=="AUTO" else data.get("transmission","")
        import os
        data['hid_allimages'] = [str(img[0])for img in  images]
        file_name = f"{data['stock_number']}.json"
        file_path = os.path.join("data/d", file_name)
        
        if not os.path.exists("data/d"):
            os.makedirs("data/d")
        
        with open(file_path, 'w') as json_file:
            json.dump(data, json_file, indent=4)
        print(data)
        call_api(json.dumps(data)) 
        
        insert_data_to_database(page_data, images)
        print(f"Page {page_num} data appended to database.")
    except Exception as e:
        print(f"Error scraping page {page_num}: {e}")
    return page_data

def navigate_and_submit_filter(cookies):
    try:
        driver.get(filter_page_url)
        print("Opened filter page.")
        submit_button = driver.find_element(By.NAME, 's2')
        submit_button.click()
        print("Clicked filter submit button.")
        total_found, first_page = get_total_pages()
        print(f"Total pages: {total_found}")
        for page_num in range(1, total_found + 2):
            print(f"Scraping page {page_num}...")
            scrape_page(page_num, cookies)
            if page_num < total_found:
                next_page_url = get_next_page_url(first_page, page_num)
                driver.get(next_page_url)
    except Exception as e:
        print(f"An error occurred during navigation and filter submission: {e}")

def get_total_pages():
    try:
        total_found_element = driver.find_element(By.XPATH, '/html/body/center/table/tbody/tr[2]/td[1]/table[1]/tbody/tr[2]/td/center/b[1]')
        total_found_text = total_found_element.text
        total_found = int(total_found_text.split()[0])
        first_page = driver.find_element(By.XPATH, '/html/body/center/table/tbody/tr[2]/td[1]/table[2]/tbody/tr[3]/td[1]/a')
        first_page = first_page.get_attribute('href')
        return total_found, first_page
    except Exception as e:
        print(f"Error extracting total pages: {e}")
        return 1, ''

def get_next_page_url(first_page, rel):
    try:
        url_parts = first_page.split('rel=')
        return f"{url_parts[0]}rel={rel}"
    except Exception as e:
        print(f"Error constructing next page URL: {e}")
        return ''

def close_browser():
    if driver:
        driver.quit()
        print("Closed the browser.")

@app.post("/Scrape")
async def login_endpoint(login_details: LoginDetails):
    global driver
    try:
        login(login_details.username, login_details.password)
        cookies = driver.get_cookies()
        navigate_and_submit_filter(cookies)
        return {"message": "Scraping completed."}
    except Exception as e:
        print("Exception", e)
        raise HTTPException(status_code=500, detail="An error occurred during scraping.")
    finally:
        close_browser()

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=3033)
