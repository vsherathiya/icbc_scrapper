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
logger = setup_logger("copart", "copart",stream=False)

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
        target_div =driver.find_elements(By.CLASS_NAME, 'thumbImgblock')
        # print(target_div)
        # images = target_div.find_elements(By.TAG_NAME, "img")
        # print(images)
        for image in target_div:
            imag = image.find_element(By.TAG_NAME, "img")
            img_url = imag.get_attribute("src")
            if img_url:
                img_url = img_url.replace("_thb","_ful")
                # img_url = img_url.replace("_thumb","")
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
        driver.get('https://www.copart.ca/login/')

        # Locate the username input field
        try:
            username_input = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.XPATH, '//*[@id="username"]'))
            )
            print(f"Username input field found: {username_input}")
        except Exception as e:
            logger.error(f"Error finding username field: {CustomException(e, sys)}")
            return False, driver

        # Locate the password input field
        try:
            password_input = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.XPATH, '//*[@id="password"]'))  # Fixed XPATH typo here
            )
            print(f"Password input field found: {password_input}")
        except Exception as e:
            logger.error(f"Error finding password field: {CustomException(e, sys)}")
            return False, driver

        # Send login credentials
        username_input.send_keys(id)
        password_input.send_keys(password)

        # Locate the submit button
        try:
            submit_button = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.XPATH, '//*[@id="show"]/div[4]/button'))
            )
            print(f"Submit button found: {submit_button}")
            submit_button.click()
        except Exception as e:
            logger.error(f"Error clicking the submit button: {CustomException(e, sys)}")
            return False, driver

        # time.sleep(1.5) can be replaced by WebDriverWait if needed

        return True, driver
    
    except Exception as e:
        logger.error(f"General error during login: {CustomException(e, sys)}")
        return False, driver

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
    # print(data)
    return data


from datetime import datetime
def convert_to_yyyy_mm_dd(date_str):
    # print("\n\n\n\n\n\n",date_str,"\n\n\n\n\n\n")
    date_str = date_str.split("\n")[0].split(". ")[1]
    # print("\n\n\n\n",date_str,"\n\n\n\n")
 
    try:
        # print(date_str)
        # Parse the datetime string according to the input format
        parsed_date = datetime.strptime(date_str, "%b %d, %Y")

        # Format the date object to 'YYYY-MM-DD'
        formatted_date = parsed_date.strftime("%Y-%m-%d")
        
        return formatted_date
    
    except ValueError as e:
        # Return an error message if the input date string doesn't match the expected format
        return"None"
    
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
    try:
        scraped_data = []
        print("\n\ncalled function")

        for url in urls:
            driver.get(url)


            data = extract_data_by_xpath(driver, xpaths)
            logger.info(f"Extracted data from {url}: {data}")

            images_bs64, image_sources = get_image_sources(driver)
            # print(image_sources)
            logger.info(f"Fetched {len(image_sources)} images from {url}")
            result = {
                'url': url,
                'images': image_sources,
                'data': data
            }

            # Safely extract each piece of data using try-except blocks
            d = {}
            try:
                d["cars_type"] = "14"
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
                d["vin"] = ''.join(filter(str.isalnum,result['data']['vin']))
            except Exception as e:
                logger.error(f"Error setting vin: {e}")
                d["vin"] = 'none'

            try:
                d["fuel_type"] = result['data']['fuel']
            except Exception as e:
                logger.error(f"Error setting fuel_type: {e}")
                d["fuel_type"] = 'none'

            try:
                d["transmission"] =  result['data']['transmission'].replace("Transmission:\n","" )
            except Exception as e:
                logger.error(f"Error setting transmission: {e}")
                d["transmission"] = 'none'
            try:
                d["cylinders"] = result['data']['engine'][-1]
            except Exception as e:
                logger.error(f"Error setting cylinders: {e}")
                d["cylinders"] = 'none'

            try:
                d["engine"] = result['data']['engine'] +"cyl"
            except Exception as e:
                logger.error(f"Error setting engine: {e}")
                d["engine"] = 'none'


            try:
                drive = result['data']['drive']
                drive_map = {"Front-wheel Drive":"FWD",
                             "All wheel drive":"AWD",
                             "Rear-wheel drive":"RWD",
                             "4x4 w/Rear Wheel Drv":"4x4"}
                
                drive = drive_map.get(drive,drive)
                
                d["drive"] = drive
            except Exception as e:
                logger.error(f"Error setting drive: {e}")
                d["drive"] = 'none'

            try:
                d["kilometer"] = "".join(filter(str.isdigit, result['data']['kilometer']))
            except Exception as e:
                logger.error(f"Error setting kilometer: {e}")
                d["kilometer"] = 'none'
            d['mileage_type'] = "MILE"
            try:
                d["keys"] = '1' if  result['data']['key']=='YES' else '0'
            except Exception as e:
            
                logger.error(f"Error setting keys: {e}")
                d["keys"] = 'none'

            try:
                d["stock_number"] = result['data']['lot']
            except Exception as e:
                logger.error(f"Error setting stock_number: {e}")
                d["stock_number"] = 'none'
                
            try:
                element = driver.find_element(By.XPATH, '//*[@id="sale-information-block"]/div[2]/div[3]/div/div/p/span').text
                d["auction_date"] = convert_to_yyyy_mm_dd(element)
            except Exception as e:
    
                logger.error(f"Error extracting data: {e}")
                d["auction_date"] = "None"


            # Additional keys
            d["currency"] = "CAD"
            d["price"] = "1"
            d["country"] = "2"
            d["state"] = state
            d["city"] = city
            d["purchase_option"] = "0"
            d["hid_main_images"] = ""
            d["hid_addedtype"] = "2"
            d["hid_addedby"] = "47"
            d["h_inventory"] = "addinventory"
            
            try:
                element = driver.find_element(By.XPATH, '//*[@data-uname="lotdetailEstimatedretailvalue"]').text
                # print(element)
                d["pmr"]  =str(int(float(''.join(filter(lambda x: x.isdigit() or x == '.', element)))))
                
                
            except Exception as e:
            
                logger.error(f"Error extracting data: {e}")
                d["pmr"] = "None"
                
                
            try:
                element = driver.find_element(By.XPATH, '//*[@id="sale-information-block"]/div[2]/div[2]/span').text
                d["auction_name"] = element
            except Exception as e:
                
                    logger.error(f"Error extracting data: {e}")
                    d["auction_name"] = "None"
            try:
                # element = driver.find_element(By.XPATH, '//*[@id="simWidget"]/div[2]/div[1]/span/span[10]').text
                d["run_no"] = ""
            # except Exception as e:
                # try:
                #     element = driver.find_element(By.XPATH, '//*[@id="simWidget"]/div[2]/div[1]/span/span[10]').text
                #     d["run_no"] = element
                # # except Exception as e:
                #     try:
                #         element = WebDriverWait(driver, 10).until(
                #             EC.presence_of_element_located((By.XPATH, '//*[@id="simWidget"]/div[2]/div[1]/span/span[10]'))
                #         ).text
                #         d["run_no"] = element
                #     except Exception as e:
                #         try:
                #             element = WebDriverWait(driver, 10).until(
                #                 EC.presence_of_element_located((By.XPATH,'//*[@id="bidWidget"]/div[2]/div[1]/span/span[10]'))
                #             ).text
                #             d["run_no"] = element
            except Exception as e:
                logger.error(f"Error extracting data: {e}")
                d["run_no"] = "None"
            try:
                # element = driver.find_element(By.XPATH, '//*[@id="ae-main"]/div/div/div/div[3]/div[4]/div[2]/div[2]/div[2]/div[1]/div[14]/div[2]').text
                d["title_status"] = ""
            except Exception as e:
                logger.error(f"Error extracting data: {e}")
                d["title_status"] = "None"
                
                            
            try:                                         
                element = driver.find_element(By.XPATH, '//*[@data-uname="lotdetailColorvalue"]').text
                d["exterior_colour"] = element
            except Exception as e:
    
                logger.error(f"Error extracting data: {e}")
                d["exterior_colour"] = "None"
                
                
            try:
                # element = driver.find_element(By.XPATH, '///*[@id="ae-main"]/div/div/div/div[3]/div[4]/div[2]/div[2]/div[2]/div[1]/div[2]/div[2]').text
                d["interior_colour"] = ""
            except Exception as e:
    
                logger.error(f"Error extracting data: {e}")
                d["interior_colour"] = "None"
                
            try:    
                print("=============")                                     
                element = driver.find_elements(By.CSS_SELECTOR, ".lot-details-desc.highlights-popover-cntnt")
                h = ''
                for ele in element:
                    h+=' '+ele.text
                print(element,h)
                d["highlight"] = h
            except Exception as e:
    
                logger.error(f"Error extracting data: {e}")
                d["highlight"] = "None"
                                
            d["drivable"] = 'Yes' if 'drive' in d['highlight'].lower() else 'No'
            d["engine_runs"] = 'Yes' if 'run' in d['highlight'].lower() else 'No'
                            
            d["hid_allimages"] = image_sources

            
            file_name = f"{d.get('vin','  ')}.json"
            file_path = os.path.join("data/copart", file_name)

            if not os.path.exists("data/copart"):
                os.makedirs("data/copart")

            with open(file_path, "w") as json_file:
                json.dump(d, json_file, indent=4)
                
                
            print("\n================================",d,"================================\n")
            logger.info(f"\n================================{d}================================\n")
            call_api(json.dumps(d)) 
            
            

            scraped_data.append(d)

        return scraped_data
    except Exception as e:
        logger.error(f"Error sending data to API: {CustomException(e, sys)}")
        print(f"Error sending data to API: {CustomException(e, sys)}")

    return {}


# Define XPaths for data extraction
xpaths = {
    'vin'                  :'//*[@id="lot-details"]/div/div[2]/div/div/div[1]/div[1]/div[1]/div[2]/div[1]/div/div[2]/div/div/div[2]/div/div/div/span/span',
    'lot'                  : '//*[@data-uname="lotdetailVinvalue"]',
    'engine'               :'//*[@data-uname="lotdetailEnginetype"]',
    "cylinder"             :'//*[@data-uname="lotdetailCylindervalue"]',
    'year_make_model_type' :'//*[@id="lot-details"]/div/div[1]/div/div/div/div/div/div/h1',
    'fuel'                 :'//*[@data-uname="lotdetailFuelvalue"]',
    'transmission'         :'//*[@class="d-flex pt-5 border-top-gray"]',
    'kilometer'            :'//*[@data-uname="lotdetailOdometervalue"]',
    'drive'                :'//*[@data-uname="DriverValue"]',
    'key'                  :'//*[@data-uname="lotdetailKeyvalue"]'
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
            driver.set_window_size(1366, 768)
            login_successful, driver = login(driver, id, password)
            st.session_state['driver'] = driver
            # login_successful = True
            if login_successful:
                st.session_state['logged_in'] = True
                st.success("Login successful!")
            else:
                st.error("Login failed. Please check the logs for more details.")
        except Exception as e:
            st.error(f"Login failed: {CustomException(e, sys)}")


if st.session_state['logged_in'] :
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
            
