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
# db_config_2 = {
#     'host': 'localhost',  # Replace with your database host
#     'user': 'root',  # Replace with your database user
#     'password': '',  # Replace with your database password
#     'database': 'scrap_data',  # Replace with your database name
#     'port': 3307
# }
db_config_2 = {
   'host': 'localhost',        # Replace with your database host
   'user': 'icbc_scrapper',             # Replace with your database user
   'password': 'R3RhtTyGEjGD7pZV8WJY6N9oeWRXsAxZ',             # Replace with your database password
   'database': 'icbc_scrapper_DB',   # Replace with your database name
   'port': 3306
}
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

@app.post("/stop-server")
def stop_server():
    close_browser(driver2)
        
    
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


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=3034)