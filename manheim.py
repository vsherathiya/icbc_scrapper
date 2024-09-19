# import streamlit as st
# from selenium import webdriver
# from selenium.webdriver.common.by import By
# from selenium.webdriver.support.ui import WebDriverWait
# from selenium.webdriver.support import expected_conditions as EC
# from selenium.webdriver.chrome.options import Options
# import time
# import mysql.connector
# from mysql.connector import Error
# from exception import CustomException
# from exception import CustomException, setup_logger
# import requests
# import sys
# import os
# import json
# import base64

# logger = setup_logger("manheim", "manheim")

# # Set up Chrome WebDriver options

# # Database configuration
# db_config = {
#     "host": "localhost",
#     "user": "root",
#     "password": "",
#     "database": "scrap_data",
#     "port": 3307,
# }
# # db_config = {
# #    'host': 'localhost',
# #    'user': 'icbc_scrapper',
# #    'password': 'R3RhtTyGEjGD7pZV8WJY6N9oeWRXsAxZ',
# #    'database': 'icbc_scrapper_DB',
# #    'port': 3306
# # }



# def create_tables():
#     connection = mysql.connector.connect(
#         host=db_config["host"],
#         user=db_config["user"],
#         password=db_config["password"],
#         database=db_config["database"],
#         port=db_config["port"],
#     )
#     cursor = connection.cursor()

#     create_vehicles_table = """
#     CREATE TABLE IF NOT EXISTS vehicles_ring (
#         id INT AUTO_INCREMENT PRIMARY KEY,
#         cars_type VARCHAR(50),
#         category VARCHAR(50),
#         make VARCHAR(50),
#         model VARCHAR(50),
#         year VARCHAR(4),
#         type VARCHAR(50),
#         status VARCHAR(50),
#         vin VARCHAR(50) UNIQUE,
#         fuel_type VARCHAR(50),
#         transmission VARCHAR(50),
#         engine VARCHAR(50),
#         cylinders VARCHAR(50),
#         drive VARCHAR(50),
#         kilometer VARCHAR(50),
#         mileage_type VARCHAR(50),
#         `condition` VARCHAR(50),
#         `keys` VARCHAR(100),
#         stock_number VARCHAR(50),
#         interior_colour VARCHAR(50),
#         exterior_colour VARCHAR(50),
#         accessories VARCHAR(100),
#         currency VARCHAR(3),
#         price VARCHAR(100),
#         country VARCHAR(50),
#         state VARCHAR(50),
#         city VARCHAR(50),
#         auction_date VARCHAR(100),
#         purchase_option VARCHAR(100),
#         hid_addedtype VARCHAR(50),
#         hid_addedby VARCHAR(50),
#         h_inventory VARCHAR(50),
#         auction_name VARCHAR(100),
#         drivable VARCHAR(100),
#         engine_runs VARCHAR(100),
#         title_status VARCHAR(50),
#         run_no VARCHAR(50),
#         pmr VARCHAR(50)
#     );
#     """

#     create_vehicle_images_table = """
#     CREATE TABLE IF NOT EXISTS vehicle_images_ring (
#         id INT AUTO_INCREMENT PRIMARY KEY,
#         vin VARCHAR(50),
#         image_base64 LONGTEXT,
#         FOREIGN KEY (vin) REFERENCES vehicles_ring(vin) ON DELETE CASCADE
#     );
#     """

#     cursor.execute(create_vehicles_table)
#     cursor.execute(create_vehicle_images_table)
#     connection.commit()
#     cursor.close()
#     connection.close()

# chrome_options = Options()
# # chrome_options.add_argument("--headless")
# chrome_options.add_argument("--disable-gpu")
# chrome_options.add_argument("--no-sandbox")
# # Overcome limited resource problems
# chrome_options.add_argument("--disable-dev-shm-usage")
# chrome_options.add_argument(
#     "user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
# )
# chrome_options.add_argument("--disable-blink-features=AutomationControlled")
# chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
# chrome_options.add_experimental_option("useAutomationExtension", False)
# chrome_options.add_argument("--window-size=1920x1080")
# chrome_options.add_argument("--disable-extensions")
# chrome_options.add_argument("--proxy-server='direct://'")
# chrome_options.add_argument("--proxy-bypass-list=*")
# # chrome_options.binary_location = "/usr/bin/chromium-browser"
# logger.info(f"{str(db_config)}\n{chrome_options.binary_location}")


# # Initialize the WebDriver
# driver = None

# def download_image_as_base64(image_url):
#     try:
#         logger.info(f"Downloading image from URL: {image_url}")
#         response = requests.get(image_url)
#         response.raise_for_status()
#         print("Done-->", image_url)
#         return image_url
#     except requests.exceptions.RequestException as e:
#         logger.error(f"Error downloading image: {CustomException(e, sys)}")
#         return ""

# def get_image_sources(driver, name):
#     sources_bs64 = []
#     sources = []
#     try:
#         images = WebDriverWait(driver, 20).until(
#             EC.presence_of_all_elements_located(
#                 (By.CSS_SELECTOR, "img.image-gallery-thumbnail-image")
#             )
#         )

#         for element in images:
#             img_url = element.get_attribute("src")
#             # img_url = img_url.replace("100x100", "800x600")
#             sources.append(img_url)
#             sources_bs64.append(download_image_as_base64(img_url))
#         return sources_bs64, sources
#     except Exception as e:
#         logger.error(f"Error Occurred at {CustomException(e, sys)}")
#         print(CustomException(e, sys))
#         logger.error(f"Error extracting {name}: {e}")
#     return "sources_bs64", "sources"



# def get_image_sources(driver, name):
#     sources_bs64 = []
#     sources = []
#     try:
#         # Wait until the target div is present
#         target_div = WebDriverWait(driver, 20).until(
#             EC.presence_of_element_located((By.CSS_SELECTOR, '/#fyusion-prism-viewer > div > div.svfy_carousel.svfy_noslct.svfy_btm > div > div'))
#         )

#         # Find all img elements within the target div
#         images = target_div.find_elements(By.TAG_NAME, "img")

#         # Process each image element
#         for element in target_div:
#             div_ = element.find_elements(By.TAG_NAME, "div")
#             images = div_.find_elements(By.TAG_NAME, "img")
#             img_url = images.get_attribute("src")
#             sources.append(img_url)
#             sources_bs64.append(download_image_as_base64(img_url))

#         return sources_bs64, sources
#     except Exception as e:
#         logger.error(f"Error occurred: {CustomException(e, sys)}")
#         print(CustomException(e, sys))
#         logger.error(f"Error extracting {name}: {e}")
#         return [], []  # Return empty lists on failure
# # Function to log in to the website
# def login(driver, id, password):
#     driver.get('https://search.manheim.com/results#/details/WA1VGAFP9FA018909/OVE')  # Replace with the actual login URL
#     username_input = driver.find_element(By.ID, 'user_username')
#     password_input = driver.find_element(By.ID, 'user_password')
#     username_input.send_keys(id)
#     password_input.send_keys(password)
#     submit_button = driver.find_element(By.XPATH, '//*[@id="submit"]')
#     submit_button.click()
#     time.sleep(0.5) 
#     radio_button = WebDriverWait(driver, 10).until(
#         EC.element_to_be_clickable((By.XPATH, '//*[@id="186a7aba-c616-4c22-186a-7abac6164c22"]')))
#     radio_button.click()

#     # Click "Continue" button
#     continue_button = WebDriverWait(driver, 10).until(
#         EC.element_to_be_clickable((By.XPATH, '//*[@id="buttoncontinue"]')))
#     continue_button.click()
#     # Wait for login
    
#     st.subheader("OTP Handling")
#     otp = st.text_input("Enter OTP:")
#     WebDriverWait(driver, 10).until(
#         EC.presence_of_element_located((By.XPATH, '//*[@id="OTP"]')))
#     otp_input = driver.find_element(By.XPATH, '//*[@id="OTP"]')
#     otp_input.send_keys(otp)
#     otp_submit_button = driver.find_element(By.XPATH, '//*[@id="submitButton"]')
#     otp_submit_button.click()

#     driver.get('https://search.manheim.com/results#/details/WA1VGAFP9FA018909/OVE')
#     time.sleep(0.5) 

# # Function to handle OTP input

# # Function to scrape data from links using session cookies
# def scrape_links(driver, numbers):
#     scraped_data = []
#     for number in numbers:
#         # Generate the link based on the number
#         link = number  # Replace with the actual URL format
#         driver.get(link)
        
#         time.sleep(1)  # Wait for page load
#         # Extract data (replace with actual extraction logic)
#         a,b = get_image_sources(driver,"image")
#         print(a)
#         print(b)
#         title = '\n\n'
#         scraped_data.append(f"Title of {link}: {title}")
#     return scraped_data


# # Initialize session state variables
# if 'logged_in' not in st.session_state:
#     st.session_state['logged_in'] = False

# if 'otp_entered' not in st.session_state:
#     st.session_state['otp_entered'] = False

# if 'target_url' not in st.session_state:
#     st.session_state['target_url'] = ""



# # Streamlit UI
# st.title("Web Scraper with Radio Button, Continue, and OTP Handling")

# # Phase 1: Log in to the website
# if not st.session_state['logged_in']:
#     st.subheader("Login")

#     id = st.text_input("Enter ID:")
#     password = st.text_input("Enter Password:", type="password")

#     if st.button("Login"):
#         if id and password:
#             driver = webdriver.Chrome(options=chrome_options)
#             st.write("Attempting to log in...")
#             try:
#                 login(driver, id, password)
#                 st.success("Login successful!")
#                 st.session_state['logged_in'] = True
#             except Exception as e:
#                 st.error(f"Login failed: {e}")
#         else:
#             st.warning("Please fill in both fields.")

# # Phase 2: Handle OTP and make the links text box visible

# # Phase 3: Scrape data from links
# if st.session_state['otp_entered']:
#     st.subheader("Scrape Data from Links")
#     numbers = st.text_area("Enter numbers to scrape (one per line)")

#     if st.button("Scrape"):
#         numbers = eval(numbers)
#         if numbers:
#             st.write("Scraping data from numbers...")
#             try:
                
#                 scraped_data = scrape_links(driver, numbers)
                
#                 st.success("Scraping completed!")
#                 st.write("\n".join(scraped_data))
#             except Exception as e:
#                 st.error(f"Scraping error: {e}")
#         else:
#             st.warning("Please enter some numbers to scrape.")


import streamlit as st
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
import time
import mysql.connector
from mysql.connector import Error
from exception import CustomException, setup_logger
import requests
import sys
import os
import json
import base64

logger = setup_logger("manheim", "manheim")

# Database configuration
db_config = {
    "host": "localhost",
    "user": "root",
    "password": "",
    "database": "scrap_data",
    "port": 3307,
}

# Initialize the WebDriver
chrome_options = Options()
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

driver = None

def download_image_as_base64(image_url):
    try:
        logger.info(f"Downloading image from URL: {image_url}")
        response = requests.get(image_url)
        response.raise_for_status()
        return image_url
    except requests.exceptions.RequestException as e:
        logger.error(f"Error downloading image: {CustomException(e, sys)}")
        return ""



def get_image_sources(driver, name):
    sources_bs64 = []
    sources = []
    try:
        # Wait until the target div is present
        target_div = WebDriverWait(driver, 20).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, '/#fyusion-prism-viewer > div > div.svfy_carousel.svfy_noslct.svfy_btm > div > div'))
        )

        # Find all img elements within the target div
        images = target_div.find_elements(By.TAG_NAME, "img")

        # Process each image element
        for element in target_div:
            div_ = element.find_elements(By.TAG_NAME, "div")
            images = div_.find_elements(By.TAG_NAME, "img")
            img_url = images.get_attribute("src")
            sources.append(img_url)
            sources_bs64.append(download_image_as_base64(img_url))

        return sources_bs64, sources
    except Exception as e:
        logger.error(f"Error occurred: {CustomException(e, sys)}")
        print(CustomException(e, sys))
        logger.error(f"Error extracting {name}: {e}")
        return [], []  # Return empty lists on failure
    
def login(driver, id, password):
    logger.info("Starting login process")
    driver.get('https://search.manheim.com/results#/details/WA1VGAFP9FA018909/OVE')  # Replace with actual login URL
    username_input = driver.find_element(By.ID, 'user_username')
    password_input = driver.find_element(By.ID, 'user_password')
    username_input.send_keys(id)
    password_input.send_keys(password)
    submit_button = driver.find_element(By.XPATH, '//*[@id="submit"]')
    submit_button.click()
    logger.info("Login credentials submitted")
    # Select radio button and click Continue
    radio_button = WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable((By.XPATH, '//*[@id="186a7aba-c616-4c22-186a-7abac6164c22"]')))
    radio_button.click()
    logger.info("Radio button selected")
    continue_button = WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable((By.XPATH, '//*[@id="buttoncontinue"]')))
    continue_button.click()
    logger.info("Continue button clicked")
    otp = st.text_input("Enter OTP:")
    otp_input = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.XPATH, '//*[@id="OTP"]'))
    )
    otp_input.send_keys(otp)
    otp_submit_button = driver.find_element(By.XPATH, '//*[@id="submitButton"]')
    otp_submit_button.click()
    logger.info("OTP submitted")
    st.success("OTP submitted successfully!")
    
    # Wait for 5 seconds before fetching URLs
    time.sleep(5)
    logger.info("Waited for 5 seconds after OTP submission")

    

def scrape_links(driver, urls):
    scraped_data = []
    for url in urls:
        driver.get(url)
        images_bs64, image_sources = get_image_sources(driver, "image")
        logger.info(f"Fetched {len(image_sources)} images from {url}")
        scraped_data.append(f"Images from {url}: {image_sources}")
    return scraped_data

# Initialize session state variables
if 'logged_in' not in st.session_state:
    st.session_state['logged_in'] = False
if 'otp_entered' not in st.session_state:
    st.session_state['otp_entered'] = False

# Streamlit UI
st.title("Web Scraper with OTP Handling and URL Fetching")

# Phase 1: Log in to the website
if not st.session_state['logged_in']:
    st.subheader("Login")

    id = st.text_input("Enter ID:")
    password = st.text_input("Enter Password:", type="password")

    if st.button("Login"):
        if id and password:
            driver = webdriver.Chrome(options=chrome_options)
            st.write("Attempting to log in...")
            try:
                login(driver, id, password)
                st.session_state['logged_in'] = True
                st.success("Login successful!")
            except Exception as e:
                st.error(f"Login failed: {e}")
                logger.error(f"Login failed: {e}")
        else:
            st.warning("Please fill in both fields.")

# Phase 2: Handle OTP and URL fetching

# Phase 3: Scrape data from URLs
if st.session_state['logged_in']:
    st.subheader("Scrape Data from URLs")
    urls_input = st.text_area("Enter URLs to scrape (one per line)")
    urls =eval(urls_input)

    if st.button("Scrape"):
        if type(urls)==list:
            try:
                st.write("Scraping data from URLs...")
                scraped_data = scrape_links(driver, urls)
                st.success("Scraping completed!")
                st.write("\n".join(scraped_data))
                logger.info("Scraping completed successfully")
            except Exception as e:
                st.error(f"Scraping error: {e}")
                logger.error(f"Scraping error: {e}")
        else:
            st.warning("Please enter URLs to scrape.")
