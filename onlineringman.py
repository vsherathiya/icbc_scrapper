from fastapi import FastAPI
from typing import List
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
import requests
import sys
import os
import json
import base64
from datetime import datetime
import mysql.connector
from mysql.connector import Error
from exception import CustomException, setup_logger

logger = setup_logger("ringman", "ringman")
app = FastAPI()


# Database configuration
# db_config = {
#     "host": "localhost",
#     "user": "root",
#     "password": "",
#     "database": "scrap_data",
#     "port": 3307,
# }
db_config = {
   'host': 'localhost',
   'user': 'icbc_scrapper',
   'password': 'R3RhtTyGEjGD7pZV8WJY6N9oeWRXsAxZ',
   'database': 'icbc_scrapper_DB',
   'port': 3306
}


def convert_date_format(date_str):
    try:
        input_date = datetime.strptime(date_str, "%a, %m/%d/%y")
        return input_date.strftime("%Y-%m-%d")
    except ValueError as e:
        logger.error(f"Date conversion error: {e}")


#         return ''
driver = None
# Create database tables if they don't exist


def create_tables():
    connection = mysql.connector.connect(
        host=db_config["host"],
        user=db_config["user"],
        password=db_config["password"],
        database=db_config["database"],
        port=db_config["port"],
    )
    cursor = connection.cursor()

    create_vehicles_table = """
    CREATE TABLE IF NOT EXISTS vehicles_ring (
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
    CREATE TABLE IF NOT EXISTS vehicle_images_ring (
        id INT AUTO_INCREMENT PRIMARY KEY,
        vin VARCHAR(50),
        image_base64 LONGTEXT,
        FOREIGN KEY (vin) REFERENCES vehicles_ring(vin) ON DELETE CASCADE
    );
    """

    cursor.execute(create_vehicles_table)
    cursor.execute(create_vehicle_images_table)
    connection.commit()
    cursor.close()
    connection.close()


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


class RequestBody(BaseModel):
    id: str = "hello@americanauctionaccess.com"
    password: str = "Marhaba@450"
    links: List[str]

def download_image_as_base64(image_url):
    try:
        logger.info(f"Downloading image from URL: {image_url}")
        response = requests.get(image_url)
        response.raise_for_status()
        print("Done-->", image_url)
        return base64.b64encode(response.content).decode("utf-8")
    except requests.exceptions.RequestException as e:
        logger.error(f"Error downloading image: {CustomException(e, sys)}")
        return ""

def get_image_sources(driver, name):
    sources_bs64 = []
    sources = []
    try:
        images = WebDriverWait(driver, 20).until(
            EC.presence_of_all_elements_located(
                (By.CSS_SELECTOR, "img.image-gallery-thumbnail-image")
            )
        )

        for element in images:
            img_url = element.get_attribute("src").replace("thumbnail", "large")
            img_url = img_url.replace("100x100", "800x600")
            sources.append(img_url)
            sources_bs64.append(download_image_as_base64(img_url))
        return sources_bs64, sources
    except Exception as e:
        logger.error(f"Error Occurred at {CustomException(e, sys)}")
        print(CustomException(e, sys))
        logger.error(f"Error extracting {name}: {e}")
    return "sources_bs64", "sources"


def insert_data(data):
    connection = None
    cursor = None
    create_tables()
    try:
        connection = mysql.connector.connect(
            host=db_config["host"],
            user=db_config["user"],
            password=db_config["password"],
            database=db_config["database"],
            port=db_config["port"],
        )
        cursor = connection.cursor()
        # Prepare data excluding images
        vehicle_data = {key: data[key] for key in data if key != "hid_allimages"}

        insert_query = """
        INSERT INTO vehicles_ring (
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
        vehicle_vin = data.get("vin")
        for image_base64 in data.get("hid_allimages", []):
            cursor.execute(
                """
                INSERT INTO vehicle_images_ring (vin, image_base64) VALUES (%s, %s)
            """,
                (vehicle_vin, image_base64),
            )
        connection.commit()
        logger.info(f"Inserted data for vehicle with VIN: {data.get('vin')}")
    except Error as e:
        logger.error(f"Error Occurred at {CustomException(e, sys)}")
        print(CustomException(e, sys))
    finally:
        if cursor:
            cursor.close()
        if connection:
            connection.close()
            
            
def drive_type_mapper(drive_type):
    # Define the mapping dictionary
    mapping = {
        "FRONT WHEEL": "FWD",
        "REAR WHEEL": "RWD",
        "ALL WHEEL": "AWD",
        "4-WHEEL": "4WD"
    }
    
    # Convert the input to uppercase for consistent mapping
    drive_type_upper = drive_type.upper()
    
    # Get the corresponding abbreviation from the dictionary
    return mapping.get(drive_type_upper, "Unknown")  

def to_sentence_case(text):
    
    if not text:
        return text
    words = text.split()
    words[0] = words[0].capitalize()
    sentence_case_text = words[0] + ' ' + ' '.join(word.lower() for word in words[1:])
    return sentence_case_text

def call(driver, id, password, links):
    try:
        parsed_data = []
        driver.get("https://onlineringman.com/")

        # Wait for the username and password fields to be present
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.ID, "adornment-email"))
        )

        username_input = driver.find_element(By.ID, "adornment-email")
        username_input.send_keys(id)

        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.ID, "adornment-password"))
        )

        password_input = driver.find_element(By.ID, "adornment-password")
        password_input.send_keys(password)

        # Wait for the submit button to be clickable
        submit_button = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable(
                (
                    By.XPATH,
                    "/html/body/div/div/main/div/div[1]/div[2]/div[2]/div/div[2]/form/div/button",
                )
            )
        )
        submit_button.click()

        print("Login successful")

        for link in links:
            try:
                yield f"\n\nlink -->  {link}"
                
                driver.get(link)
                # Wait for the body style element to be present
                try:
                    auction_house = WebDriverWait(driver, 10).until(
                        EC.presence_of_element_located(
                            (
                                By.CSS_SELECTOR,
                                "body > div:nth-child(2) > div:nth-child(1) > main:nth-child(4) > div:nth-child(2) > div:nth-child(1) > div:nth-child(2) > div:nth-child(1) > \
                        div:nth-child(2) > div:nth-child(1) > div:nth-child(1) > div:nth-child(2) > p:nth-child(2)",
                            )
                        )
                    ).text
                except:
                    auction_house = " "
                try:
                    run_no = WebDriverWait(driver, 10).until(
                        EC.presence_of_element_located(
                            (
                                By.CSS_SELECTOR,
                                "body > div:nth-child(2) > div:nth-child(1) > main:nth-child(4) > div:nth-child(2) > div:nth-child(1) > div:nth-child(2) > div:nth-child(1) > div:nth-child(2) > div:nth-child(1) > div:nth-child(1) > div:nth-child(3) > p:nth-child(2)",
                            )
                        )
                    ).text
                except:
                    run_no = " "
                try:
                    stock_number = WebDriverWait(driver, 10).until(
                        EC.presence_of_element_located(
                            (
                                By.CSS_SELECTOR,
                                "body > div:nth-child(2) > div:nth-child(1) > main:nth-child(4) > div:nth-child(2) > div:nth-child(1) > div:nth-child(2) > div:nth-child(1) > div:nth-child(2) > div:nth-child(1) > div:nth-child(1) > div:nth-child(1) > p:nth-child(2)",
                            )
                        )
                    ).text
                except:
                    stock_number = " "


                try:
                    heading = WebDriverWait(driver, 10).until(
                        EC.presence_of_element_located(
                            (
                                By.CSS_SELECTOR,
                                ".MuiTypography-root.MuiTypography-h5.css-1rz0m2l",
                            )
                        )
                    ).text
                except:
                    heading = " "
                try:
                    vin = WebDriverWait(driver, 10).until(
                        EC.presence_of_element_located(
                            (By.CSS_SELECTOR, 'div[data-testid="Vin-value"]')
                        )
                    ).text
                except:
                    vin = " "
                try:
                    keys = WebDriverWait(driver, 10).until(
                        EC.presence_of_element_located(
                            (By.CSS_SELECTOR, 'div[data-testid="Keys-value"]')
                        )
                    ).text
                except:
                    keys = " "
                try:
                    interior_color = WebDriverWait(driver, 10).until(
                        EC.presence_of_element_located(
                            (By.CSS_SELECTOR, "div[data-testid='interior color-value']")
                        )
                    ).text
                except:
                    interior_color = " "
                try:
                    milage = WebDriverWait(driver, 10).until(
                        EC.presence_of_element_located(
                            (By.CSS_SELECTOR, "div[data-testid='Mileage-value']")
                        )
                    ).text
                except:
                    milage =" "

                try:
                    exterior_color = WebDriverWait(driver, 10).until(
                        EC.presence_of_element_located(
                            (By.CSS_SELECTOR, "div[data-testid='exterior color-value']")
                        )
                    ).text
                except:
                    exterior_color = " "
                try:
                    engine = WebDriverWait(driver, 10).until(
                        EC.presence_of_element_located(
                            (By.CSS_SELECTOR, "div[data-testid='Engine-value']")
                        )
                    ).text
                except:
                    engine =" "
                try:
                    fuel_type = WebDriverWait(driver, 10).until(
                        EC.presence_of_element_located(
                            (By.CSS_SELECTOR, "div[data-testid='fuel type-value']")
                        )
                    ).text
                except:
                    fuel_type = " "
                try:
                    transmission = (WebDriverWait(driver, 10).until(
                        EC.presence_of_element_located(
                            (By.CSS_SELECTOR, "div[data-testid='Transmission-value']")
                        )
                    )).text
                    
                except:
                    transmission = " "
                try:    
                    body_style = WebDriverWait(driver, 10).until(
                        EC.presence_of_element_located(
                            (By.CSS_SELECTOR, "div[data-testid='body style-value']")
                        )
                    ).text
                except :
                    body_style = " "
                    
                try:    
                    title = WebDriverWait(driver, 10).until(
                        EC.presence_of_element_located(
                            (By.CSS_SELECTOR, "div[data-testid='Title-value']")
                        )
                    ).text
                except:
                    title = " "
                try:
                    drive = WebDriverWait(driver, 10).until(
                        EC.presence_of_element_located(
                            (By.CSS_SELECTOR, "div[data-testid='Drive-value']")
                        )
                    ).text
                except:
                    drive = " "        
            
                # Assuming get_image_sources is defined elsewhere and works as expected
                images, images_links = get_image_sources(driver, "images")

                try:
                    formatted_data = {
                        "cars_type": "11",
                        "category": "car",
                        "make": heading.split(" ")[1],
                        "model": " ".join(heading.split(" ")[2:4]),
                        "year": heading.split(" ")[0],
                        "type": body_style.split(" ")[1],
                        "status": "724",
                        "vin": vin,
                        "fuel_type": to_sentence_case(fuel_type),
                        "transmission":  to_sentence_case(transmission).split(" ")[0] if transmission!=" " else " ",
                        "engine": engine,
                        "cylinders": "".join(
                            filter(str.isdigit, engine.split(" ")[1])
                        ),
                        "drive": drive_type_mapper(drive),
                        "kilometer": "".join(filter(str.isdigit, milage)),
                        "mileage_type": "Mile",
                        "condition": "",
                        "keys": keys,
                        "stock_number": stock_number,
                        "interior_colour": interior_color,
                        "exterior_colour": exterior_color,
                        "accessories": "",
                        "currency": "USD",
                        "price": "1",
                        "country": "1",
                        "state": "",
                        "city": "",
                        "auction_date": "",
                        "purchase_option": "0",
                        "hid_main_images": "",
                        "hid_addedtype": "2",
                        "hid_addedby": "47",
                        "h_inventory": "addinventory",
                        "auction_name": auction_house,
                        "drivable": "",
                        "engine_runs": "",
                        "title_status": title,
                        "run_no": run_no,
                        "pmr": "",
                        "hid_allimages": images_links,
                    }
                    print((formatted_data))
                    yield f"\n\n{json.dumps(formatted_data)}"
                    file_name = f"{formatted_data.get('vin','  ')}.json"
                    file_path = os.path.join("data/ring", file_name)

                    if not os.path.exists("data/ring"):
                        os.makedirs("data/ring")

                    with open(file_path, "w") as json_file:
                        json.dump(formatted_data, json_file, indent=4)

                    insert_data(formatted_data)
                    call_api(json.dumps(formatted_data))
                    logger.info(f"{json.dumps(formatted_data)}")
                except Exception as e:
                    logger.error(f"Error Occurred at {CustomException(e, sys)}")
                    print(CustomException(e, sys))

            except Exception as e:
                print("Error while processing link:", link)
                logger.error(f"Error while processing link: {link}")
                logger.error(f"Exception: {CustomException(e,sys)}")
                yield "Error"

    except Exception as e:
        print("Error during login process")
        logger.error(f"Error during login process: {e}")

    finally:
        driver.quit()
        logger.info("Process completed")
        yield "Process completed"


@app.post("/parse_links/")
async def parse_links(request_body: RequestBody):
    try:
        # call(request_body.id,request_body.password)
        global driver
        driver = webdriver.Chrome(options=chrome_options)

        return StreamingResponse(
            call(driver, request_body.id, request_body.password, request_body.links),
            media_type="text/plain",
        )
    except Exception as e:
        logger.error(f"Error Occurred at {CustomException(e, sys)}")
        print(CustomException(e, sys))


def close_browser():
    if driver:
        driver.quit()
        print("Closed the browser.")
        logger.info("Closed the browser.")
        return "Stopping Scrapping"


@app.post("/stop-server")
def stop_server():
    close_browser()


# Function to call an external API


def call_api(data):
    try:
        headers = {"accept": "application/json", "Content-Type": "application/json"}
        url = "https://americanauctionaccess.com/edge-scrap-api"
        response = requests.post(url, headers=headers, data=data)
        if response.status_code == 200:
            return response.json()
        else:
            raise Exception(
                f"Failed to send data to API. Status code: {response.status_code}"
            )
    except requests.exceptions.RequestException as e:
        logger.error(f"Error sending data to API: {CustomException(e, sys)}")
        print(f"Error sending data to API: {CustomException(e, sys)}")


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=3035)


