from fastapi import FastAPI, HTTPException, BackgroundTasks
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
import time

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

# Setup Chrome options
chrome_options = Options()
chrome_options.add_argument("--headless")
chrome_options.add_argument("--disable-gpu")
chrome_options.add_argument("--no-sandbox")
driver = None

class LoginDetails(BaseModel):
    username: str
    password: str

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
    CREATE TABLE IF NOT EXISTS vehicle_data__ (
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
        PRIMARY KEY (lot_number)
    );
    """
    
    create_image_table_query = """
    CREATE TABLE IF NOT EXISTS vehicle_images__ (
        id INT AUTO_INCREMENT,
        lot_number VARCHAR(50),
        image LONGTEXT,
        url TEXT,
        PRIMARY KEY (id),
        FOREIGN KEY (lot_number) REFERENCES vehicle_data__(lot_number) ON DELETE CASCADE
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
                INSERT INTO vehicle_data__ (
                    lot_number, salvage_yard, asset_number, location, restrictions,
                    vehicle_year, make, model_sub, body_style, serial_number,
                    previously_rebuilt, bc_assigned_vin, int_ext_colour, mileage,
                    engine_size, transmission, seats, fuel_type, roof_options,
                    power_equipment, keys_included, sound, us_vehicle, wheel_type,
                    prior_damage_over_2000, canopy, dismantle_only,
                    special_equipment_or_damage, previously_registered_outside_bc,
                    damage, warning
                ) VALUES (
                    '{entry.get('Lot #', '')}', '{entry.get('Salvage Yard', '')}', '{entry.get('Asset #', '')}', '{entry.get('Location', '')}', '{entry.get('Restrictions', '')}',
                    '{entry.get('Vehicle Year', '')}', '{entry.get('Make', '')}', '{entry.get('Model/Sub', '')}', '{entry.get('Body Style', '')}', '{entry.get('Serial Number', '')}',
                    '{entry.get('Previously Rebuilt', '')}', '{entry.get('BC Assigned VIN', '')}', '{entry.get('Int/Ext Colour', '')}', '{entry.get('Mileage', '')}',
                    '{entry.get('Engine Size', '')}', '{entry.get('Transmission', '')}', '{entry.get('Seats', '')}', '{entry.get('Fuel Type', '')}', '{entry.get('Roof Options', '')}',
                    '{entry.get('Power Equipment', '')}', '{entry.get('Keys Included', '')}', '{entry.get('Sound', '')}', '{entry.get('US Vehicle', '')}', '{entry.get('Wheel Type', '')}',
                    '{entry.get('Prior Damage Over $2000', '')}', '{entry.get('Canopy', '')}', '{entry.get('Dismantle Only', '')}',
                    '{entry.get('Special Equipment and/or Prior Damage Description', '')}', '{entry.get('Previously Registered Outside BC', '')}',
                    '{entry.get('Damage', '')}', '{entry.get('Warning', '')}'
                );
                """
                
                cursor.execute(vehicle_query)
                
                for image in images:
                    image_query = f"""
                    INSERT INTO vehicle_images__ (lot_number, image ,url)
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
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)
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
        print(3)  # Wait for login to complete

        # Handle session expiry and restart if necessary
        try:
            restart_link = driver.find_element(By.LINK_TEXT, 'Restart Salvage Web Session')
            restart_link.click()
            print("Clicked restart link.")
            print(3)  # Wait for session restart to complete
        except Exception as e:
            print("No session restart needed.")
        
        print("Login successful, proceeding to filter page.")
    except Exception as e:
        print(f"An error occurred during login: {e}")

def extract_structured_data(raw_data_dict):
    keys = [
        'Lot #', 'Salvage Yard', 'Asset #', 'Location', 'Restrictions',
        'Vehicle Year', 'Make', 'Model/Sub', 'Body Style', 'Serial Number',
        'Previously Rebuilt', 'BC Assigned VIN', 'Int/Ext Colour', 'Mileage',
        'Engine Size', 'Transmission', 'Seats', 'Fuel Type', 'Roof Options',
        'Power Equipment', 'Keys Included', 'Sound', 'US Vehicle', 'Wheel Type',
        'Prior Damage Over $2000', 'Canopy', 'Dismantle Only',
        'Special Equipment and/or Prior Damage Description',
        'Previously Registered Outside BC', 'Damage', 'Warning'
    ]
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
        image_url = image_url.replace('size=1','size=2')
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
        details = extract_structured_data(details)
        print(details)
        image_table = driver.find_element(By.XPATH, '/html/body/p[1]/table[1]/tbody[1]/tr[3]/td')
        image_elements = image_table.find_elements(By.TAG_NAME, 'img')
        images = [img.get_attribute('src') for img in image_elements if 'AssetImageAction' in img.get_attribute('src')]
        images = [download_image_as_base64(img, cookies) for img in images]
        # print(images)
        details['Images'] = images
        page_data.append(details)
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
    driver.quit()
    print("Closed the browser.")

@app.post("/Scrape")
async def login_endpoint(login_details: LoginDetails, background_tasks: BackgroundTasks):
    
    try:
        login(login_details.username, login_details.password)
        cookies = driver.get_cookies()
        background_tasks.add_task(navigate_and_submit_filter, cookies)
        return {"message": "Login initiated, scraping in background."}
    except Exception as e:
        print("Exception",e)
    finally:
        if driver:
            close_browser()



if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
