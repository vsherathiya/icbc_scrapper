import time,os
import requests
import json
import pandas as pd
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium import webdriver
from exception import CustomException, setup_logger
import sys

# Setup logger
logger = setup_logger("manheim", "manheim",stream=True)

# Initialize the WebDriver
def init_driver():
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

    
    return webdriver.Chrome(options=chrome_options)

# Function to download image
def download_image_as_base64(image_url):
    try:
        logger.info(f"Downloading image from URL: {image_url}")
        response = requests.get(image_url)
        response.raise_for_status()
        return image_url
    except requests.exceptions.RequestException as e:
        logger.error(f"Error downloading image: {CustomException(e, sys)}")
        return ""

# Function to scrape images from the webpage
def get_image_sources(driver):
    sources_bs64 = []
    sources = []
    try:
        target_div = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.XPATH, '//*[@id="fyusion-prism-viewer"]/div/div[2]/div/div'))
        )
        images = target_div.find_elements(By.TAG_NAME, "img")
        print(images)
        for image in images:
            img_url = image.get_attribute("src")
            if img_url:
                img_url = img_url.replace("?size=w86h64","")
                img_url = img_url.replace("_thumb","")
                sources.append(img_url)
                sources_bs64.append(download_image_as_base64(img_url))

        return sources_bs64, sources
    except Exception as e:
        logger.error(f"Error occurred: {CustomException(e, sys)}")
        return [], []  # Return empty lists on failure

# Function to handle login and OTP
def login(driver, id, password):
    try:
        logger.info("Starting login process")
        driver.get('https://search.manheim.com/results#/details/WA1VGAFP9FA018909/OVE')

        try:
            username_input = driver.find_element(By.ID, 'user_username')
            password_input = driver.find_element(By.ID, 'user_password')
        except Exception as e:
            logger.error(f"Error finding login fields: {CustomException(e, sys)}")
            return False, driver
        
        username_input.send_keys(id)
        password_input.send_keys(password)

        try:
            submit_button = driver.find_element(By.XPATH, '//*[@id="submit"]')
            submit_button.click()
        except Exception as e:
            logger.error(f"Error clicking the submit button: {CustomException(e, sys)}")
            return False, driver

        try:
            radio_button = WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable((By.XPATH, '//*[@id="186a7aba-c616-4c22-186a-7abac6164c22"]'))
            )
            radio_button.click()
        except Exception as e:
            logger.warning(f"Radio button not found or not clickable: {CustomException(e, sys)}")

        try:
            continue_button = WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable((By.XPATH, '//*[@id="buttoncontinue"]'))
            )
            continue_button.click()
        except Exception as e:
            logger.warning(f"Continue button not found or not clickable: {CustomException(e, sys)}")

        time.sleep(1.5)
        return True, driver
    
    except Exception as e:
        logger.error(f"General error during login: {CustomException(e, sys)}")
        return False, driver

def otp__(driver, otp=None):
    if otp:
        try:
            otp_input = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.XPATH, '//*[@id="OTP"]'))
            )
            otp_input.send_keys(otp)
            otp_submit_button = driver.find_element(By.XPATH, '//*[@id="submitButton"]')
            otp_submit_button.click()
            logger.info("OTP submitted")
            time.sleep(5)
            driver.get("https://search.manheim.com/results#/details/WA1VGAFP9FA018909/OVE")
        except Exception as e:
            logger.error(f"Error during OTP processing: {CustomException(e, sys)}")
            return False,driver
    return True,driver

# Function to extract data using XPaths
def extract_data_by_xpath(driver, xpath_dict):
    data = {}
    
    for key, xpath in xpath_dict.items():
        try:
            element = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.XPATH, xpath))
            )
            data[key] = element.text
        except Exception as e:
            logger.error(f"Error extracting data for {key}: {CustomException(e, sys)}")
            data[key] = None
    print(data)
    return data

# Function to scrape data and append it to a JSON file
# def scrape_links(driver, urls, json_file='scraped_data.json'):
#     scraped_data = []
#     print("\n\ncalled function")
    
#     for url in urls:
#         driver.get(url)
#         time.sleep(2)
#         # driver.refresh()
#         images_bs64, image_sources = get_image_sources(driver)
#         logger.info(f"Fetched {len(image_sources)} images from {url}")

#         data = extract_data_by_xpath(driver, xpaths)
#         logger.info(f"Extracted data from {url}: {data}")

#         result = {
#             'url': url,
#             'images': image_sources,
#             'data': data
#         }
#         scraped_data.append(result)

#     # Load existing data
#     try:
#         with open(json_file, 'r') as file:
#             existing_data = json.load(file)
#     except FileNotFoundError:
#         existing_data = []

#     # Append new data and save
#     existing_data.extend(scraped_data)
#     with open(json_file, 'w') as file:
#         json.dump(existing_data, file, indent=4)

#     return scraped_data

from datetime import datetime

def convert_to_yyyy_mm_dd(date_str):
    """
    Converts a date string in the format 'MM/DD - HH:MMam/pm' to 'YYYY-MM-DD' format with the current year.
    
    Args:
        date_str (str): Date string in the format 'MM/DD - HH:MMam/pm'.
        
    Returns:
        str: Date string in 'YYYY-MM-DD' format with the current year.
    """
    try:
        # Parse the date string assuming 'MM/DD - HH:MMam/pm'
        date_obj = datetime.strptime(date_str, "%m/%d - %I:%M%p")
        
        # Get the current year
        current_year = datetime.now().year
        
        # Replace the year in the date object with the current year
        date_obj = date_obj.replace(year=current_year)
        
        # Format the date object to 'YYYY-MM-DD'
        return date_obj.strftime("%Y-%m-%d")
    
    except ValueError as e:
        # Return an error message if the input date string doesn't match the expected format
        return f"Error: {str(e)}. Ensure the date format is 'MM/DD - HH:MMam/pm'."

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

def scrape_links(driver, city, state, urls, json_file='scraped_data.json'):
    scraped_data = []
    print("\n\ncalled function")

    for url in urls:
        driver.get(url)
        # time.sleep(1)
        # Add a page refresh
        driver.refresh()
        driver.refresh()
        time.sleep(3)

        # Extract images and data as before

        data = extract_data_by_xpath(driver, xpaths)
        logger.info(f"Extracted data from {url}: {data}")

        images_bs64, image_sources = get_image_sources(driver)
        print(image_sources)
        logger.info(f"Fetched {len(image_sources)} images from {url}")
        result = {
            'url': url,
            'images': image_sources,
            'data': data
        }

        # Safely extract each piece of data using try-except blocks
        d = {}
        try:
            d["cars_type"] = "11    "
        except Exception as e:
            logger.error(f"Error setting cars_type: {e}")
            d["cars_type"] = 'none'

        try:
            d["category"] = "car"
        except Exception as e:
            logger.error(f"Error setting category: {e}")
            d["category"] = 'none'

        try:
            d["make"] = result['data']['year_make_model_type'].split(" ")[1]
        except Exception as e:
            logger.error(f"Error setting make: {e}")
            d["make"] = 'none'

        try:
            d["model"] = result['data']['year_make_model_type'].split(" ")[2]
        except Exception as e:
            logger.error(f"Error setting model: {e}")
            d["model"] = 'none'

        try:
            d["year"] = result['data']['year_make_model_type'].split(" ")[0]
        except Exception as e:
            logger.error(f"Error setting year: {e}")
            d["year"] = 'none'

        try:
            d["type"] = result['data']['year_make_model_type'].split(" ")[3]
        except Exception as e:
            logger.error(f"Error setting type: {e}")
            d["type"] = 'none'

        try:
            d["status"] = "724"
        except Exception as e:
            logger.error(f"Error setting status: {e}")
            d["status"] = 'none'

        try:
            d["vin"] = result['data']['vin']
        except Exception as e:
            logger.error(f"Error setting vin: {e}")
            d["vin"] = 'none'

        try:
            d["fuel_type"] = result['data']['fuel']
        except Exception as e:
            logger.error(f"Error setting fuel_type: {e}")
            d["fuel_type"] = 'none'

        try:
            d["transmission"] = result['data']['transmission']
        except Exception as e:
            logger.error(f"Error setting transmission: {e}")
            d["transmission"] = 'none'
        try:
            d["cylinders"] = result['data']['cylinder'].lower().replace('cyl',"")
        except Exception as e:
            logger.error(f"Error setting cylinders: {e}")
            d["cylinders"] = 'none'

        try:
            d["engine"] = result['data']['engine'] + " "+d['cylinders']+"cyl"
        except Exception as e:
            logger.error(f"Error setting engine: {e}")
            d["engine"] = 'none'


        try:
            d["drive"] = result['data']['drive'].replace("•","")
        except Exception as e:
            logger.error(f"Error setting drive: {e}")
            d["drive"] = 'none'

        try:
            d["kilometer"] = "".join(filter(str.isdigit, result['data']['kilometer'].replace("•","").replace("mi","")))
        except Exception as e:
            logger.error(f"Error setting kilometer: {e}")
            d["kilometer"] = 'none'

        try:
            d["keys"] = str(int(result['data']['otherkey']) + int(result['data']['smartkey']))
        except Exception as e:
            logger.error(f"Error setting keys: {e}")
            d["keys"] = 'none'

        try:
            d["stock_number"] = 'stock_number'
        except Exception as e:
            logger.error(f"Error setting stock_number: {e}")
            d["stock_number"] = 'none'

        try:
            d["interior_colour"] = result['data']['int_color']
        except Exception as e:
            logger.error(f"Error setting interior_colour: {e}")
            d["interior_colour"] = 'none'

        try:
            d["exterior_colour"] = result['data']['ext_color']
        except Exception as e:
            logger.error(f"Error setting exterior_colour: {e}")
            d["exterior_colour"] = 'none'

        try:
            d["auction_date"] = convert_to_yyyy_mm_dd(result['data']['date'])
        except Exception as e:
            logger.error(f"Error setting auction_date: {e}")
            d["auction_date"] = 'none'

        try:
            d["title_status"] = result['data']['title_status']
        except Exception as e:
            logger.error(f"Error setting title_status: {e}")
            d["title_status"] = 'none'

        try:
            d["run_no"] = result['data']['run_no']
        except Exception as e:
            logger.error(f"Error setting run_no: {e}")
            d["run_no"] = 'none'

        # Additional keys
        d["currency"] = "USD"
        d["price"] = "1"
        d["country"] = "1"
        d["state"] = state
        d["city"] = city
        d["purchase_option"] = "0"
        d["hid_main_images"] = ""
        d["hid_addedtype"] = "2"
        d["hid_addedby"] = "47"
        d["h_inventory"] = "addinventory"
        d["drivable"] = ""
        d["engine_runs"] = ""
        d["pmr"] =  ''.join(filter(str.isdigit,result['data'].get('mmr','0')))
        d["hid_allimages"] = image_sources
        d["auction_name"] = result['data'].get('location', 'none')  # Adding a default value if key is missing
        d['mileage_type'] = "MILE"

        
        file_name = f"{d.get('vin','  ')}.json"
        file_path = os.path.join("data/man", file_name)

        if not os.path.exists("data/man"):
            os.makedirs("data/man")

        with open(file_path, "w") as json_file:
            json.dump(d, json_file, indent=4)
            
            
        print("\n================================",d,"================================\n")
        logger.info(f"\n================================{d}================================\n")
        call_api(json.dumps(d)) 

        scraped_data.append(d)

    # Load existing data and save the new data to the JSON file
    # try:
    #     with open(json_file, 'r') as file:
    #         existing_data = json.load(file)
    # except FileNotFoundError:
    #     existing_data = []

    # existing_data.extend(scraped_data)
    # with open(json_file, 'w') as file:
    #     json.dump(existing_data, file, indent=4)

    return scraped_data


# Define XPaths for data extraction
xpaths = {
    'vin'                  :'//*[@id="ae-main"]/div/div/div/div[3]/div[1]/div/div[2]/div[1]/span[1]',
    'engine'               :'//*[@id="ae-main"]/div/div/div/div[3]/div[1]/div/div[2]/div[1]/span[4]/span[2]',
    "cylinder"             : '//*[@id="ae-main"]/div/div/div/div[3]/div[1]/div/div[2]/div[1]/span[4]/span[3]',
    'year_make_model_type' :'//*[@id="ae-main"]/div/div/div/div[3]/div[1]/div/div[1]/div[1]/span',
    'fuel'                 :'//*[@id="ae-main"]/div/div/div/div[3]/div[1]/div/div[2]/div[1]/span[4]/span[5]',
    'transmission'         :'//*[@id="ae-main"]/div/div/div/div[3]/div[1]/div/div[2]/div[1]/span[4]/span[7]',
    'kilometer'            :'//*[@id="ae-main"]/div/div/div/div[3]/div[1]/div/div[2]/div[1]/span[2]',
    'drive'                :'//*[@id="ae-main"]/div/div/div/div[3]/div[1]/div/div[2]/div[1]/span[3]',
    'smartkey'             :'//*[@id="ae-main"]/div/div/div/div[3]/div[4]/div[3]/div[2]/div[3]/div/div/div/div[2]/div[2]/div[1]/div[2]/div',
    "otherkey"             :'//*[@id="ae-main"]/div/div/div/div[3]/div[4]/div[3]/div[2]/div[3]/div/div/div/div[2]/div[2]/div[2]/div[2]/div',
    'int_color'            :'//*[@id="ae-main"]/div/div/div/div[3]/div[4]/div[2]/div[2]/div[2]/div[1]/div[2]/div[2]',
    'ext_color'            :'//*[@id="ae-main"]/div/div/div/div[3]/div[4]/div[2]/div[2]/div[2]/div[1]/div[1]/div[2]',
    'title_status'         :'//*[@id="ae-main"]/div/div/div/div[3]/div[4]/div[2]/div[2]/div[2]/div[1]/div[14]/div[2]',
    'mmr'                  :'//*[@id="simWidget"]/div[2]/div[1]/span/span[4]/span/span[1]/span[2]/a',
    'location'             : '//*[@id="simWidget"]/div[2]/div[1]/span/span[12]/span',
    'date'                 : '//*[@id="simWidget"]/div[2]/div[1]/span/span[8]',
    'run_no'               :  '//*[@id="simWidget"]/div[2]/div[1]/span/span[10]'
}

# Streamlit application code
import streamlit as st
from exception import CustomException

# Initialize session state variables
if 'logged_in' not in st.session_state:
    st.session_state['logged_in'] = False
if 'otp_entered' not in st.session_state:
    st.session_state['otp_entered'] = False

st.title("Web Scraper with OTP Handling and URL Fetching")

# Phase 1: Log in to the website
st.subheader("Login")
id = st.text_input("Enter ID:")
password = st.text_input("Enter Password:", type="password")

if st.button("Login"):
    if id and password:
        st.write("Attempting to log in...")
        try:
            driver = init_driver()
            login_successful, driver = login(driver, id, password)
            st.session_state['driver'] = driver
            if login_successful:
                st.session_state['logged_in'] = True
                st.success("Login successful!")
            else:
                st.error("Login failed. Please check the logs for more details.")
        except Exception as e:
            st.error(f"Login failed: {CustomException(e, sys)}")

if st.session_state['logged_in']:
    otp = st.text_input("Enter OTP:")
    if st.button("Submit OTP"):
        try:
            if otp:
                st.success("OTP submitted successfully!")
                st.session_state['otp_entered'] = True
                otp_submitter,driver = otp__(driver=st.session_state['driver'], otp=otp)
                st.session_state['driver'] = driver
            else:
                st.error("Please enter the OTP.")
        except Exception as e:
            st.error(f"OTP submission failed: {CustomException(e, sys)}")

if st.session_state['logged_in'] and st.session_state['otp_entered']:
    st.subheader("Scrape Data from URLs")
    urls_input = st.text_area("Enter URLs to scrape (one per line)")

    city = st.text_area("Enter City")
    state = st.text_area("Enter State")
    if st.button("Scrape"):
        try:
            print("\n\n..")
            print(urls_input)
            # Convert URLs input into a list of strings
            urls = [url.strip() for url in urls_input.splitlines() if url.strip()]
            print(urls)
            if urls_input:
                # Log initial URL list
                st.write(f"Initial URLs list: {urls}")
                
                logger.info(f"Initial URLs list: {urls}")
                
                while urls:
                    try:
                        # Log current URL list before popping
                        logger.info(f"Current URL list before popping: {urls}")
                        st.write(f"Current URL list before popping: {urls}")

                        # Process the first URL in the list
                        url_to_scrape = urls.pop(0)  # Remove and get the first URL

                        # Log after popping the URL
                        logger.info(f"Processing URL: {url_to_scrape}")
                        logger.info(f"Remaining URLs after popping: {urls}")
                        
                        st.write(f"Scraping data from URL: {url_to_scrape}...")
                        scraped_data = scrape_links(st.session_state['driver'] ,city.splitlines()[0].strip(),state.splitlines()[0].strip(), [url_to_scrape])

                        st.success("Scraping completed!")
                        st.write("\n".join([json.dumps(data, indent=4) for data in scraped_data]))

                        # If no more URLs left to process
                        if not urls:
                            st.warning("All URLs have been processed. Please enter new URLs to scrape.")
                            break
                    except Exception as e:
                        st.error(f"Scraping error: {CustomException(e, sys)}")
                        logger.error(f"Scraping error for URL {url_to_scrape}: {CustomException(e, sys)}")
            else:
                st.warning("Please enter URLs to scrape.")
        except Exception as e:
            st.error(f"Scrape Data from URL failed: {CustomException(e, sys)}")
            
