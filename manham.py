import time
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
import streamlit as st
import os
# Setup logger
logger = setup_logger("manheim", "manheim")

# Initialize the WebDriver
def init_driver():
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
        target_div = WebDriverWait(driver, 20).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, '#fyusion-prism-viewer > div > div.svfy_carousel.svfy_noslct.svfy_btm > div > div'))
        )
        images = target_div.find_elements(By.TAG_NAME, "img")

        for image in images:
            img_url = image.get_attribute("src")
            if img_url:
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
        except Exception as e:
            logger.error(f"Error during OTP processing: {CustomException(e, sys)}")
            return False
    return True

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
    return data

# Function to scrape data and append it to a JSON file
def scrape_links(driver, urls, json_file='scraped_data.json'):
    scraped_data = []
    for url in urls:
        driver.get(url)
        images_bs64, image_sources = get_image_sources(driver)
        logger.info(f"Fetched {len(image_sources)} images from {url}")

        data = extract_data_by_xpath(driver, xpaths)
        logger.info(f"Extracted data from {url}: {data}")

        result = {
            'url': url,
            'images': image_sources,
            'data': data
        }
        file_name = f"{result['data'].get('vin','  ')}{result['data'].get('vin_4','  ')}.json"
        file_path = os.path.join("data/man", file_name)
        if not os.path.exists("data/man"):
            os.makedirs("data/man")

        with open(file_path, "w") as json_file:
            json.dump(result, json_file, indent=4)
        scraped_data.append(result)

    # Load existing data
    try:
        with open(json_file, 'r') as file:
            existing_data = json.load(file)
    except FileNotFoundError:
        existing_data = []

    # Append new data and save
    existing_data.extend(scraped_data)
    with open(json_file, 'w') as file:
        json.dump(existing_data, file, indent=4)

    return scraped_data

# Define XPaths for data extraction
xpaths = {
    'vin'                  : """//*[@id="ae-main"]/div/div/div/div[3]/div[1]/div/div[2]/div[1]/span[1]/text()""",
    "vin_4"                : """//*[@id="ae-main"]/div/div/div/div[3]/div[1]/div/div[2]/div[1]/span[1]/b""",
    'engine'               : """//*[@id="ae-main"]/div/div/div/div[3]/div[1]/div/div[2]/div[1]/span[4]/span[2]""",
    'year_make_model_type' : """//*[@id="ae-main"]/div/div/div/div[3]/div[1]/div/div[1]/div[1]/span""",
    'fuel'                 : """//*[@id="ae-main"]/div/div/div/div[3]/div[1]/div/div[2]/div[1]/span[4]/span[5]""",
    'transmission'         : """//*[@id="ae-main"]/div/div/div/div[3]/div[1]/div/div[2]/div[1]/span[4]/span[7]""",
    'kilometer'            : """//*[@id="ae-main"]/div/div/div/div[3]/div[1]/div/div[2]/div[1]/span[2]""",
    'drive'                : """//*[@id="ae-main"]/div/div/div/div[3]/div[4]/div[2]/div[2]/div[2]/div[1]/div[6]/div[2]""",
    'smartkey'             : """//*[@id="ae-main"]/div/div/div/div[3]/div[4]/div[3]/div[2]/div[3]/div/div/div/div[2]/div[2]/div[1]/div[2]/div"]""",
    "otherkey"             :"""//*[@id="ae-main"]/div/div/div/div[3]/div[4]/div[3]/div[2]/div[3]/div/div/div/div[2]/div[2]/div[2]/div[2]/div"]""",
    'int_color'            : """//*[@id="ae-main"]/div/div/div/div[3]/div[4]/div[2]/div[2]/div[2]/div[1]/div[1]/div[2]""",
    'ext_color'            : """//*[@id="ae-main"]/div/div/div/div[3]/div[4]/div[2]/div[2]/div[2]/div[1]/div[1]/div[2]""",
    'title_status'         : """//*[@id="ae-main"]/div/div/div/div[3]/div[4]/div[2]/div[2]/div[2]/div[1]/div[14]/div[2]""",
    'mmr'                  : """//*[@id="bidWidget"]/div[2]/div[1]/span/span[4]/span/span[1]/span[2]/a""",
    'location'             : """//*[@id="bidWidget"]/div[2]/div[1]/span/span[10]/span"""
}

# Streamlit application code
def main():
    st.title("Web Scraper with Continuous Scraping")

    if 'logged_in' not in st.session_state:
        st.session_state['logged_in'] = False
    if 'otp_entered' not in st.session_state:
        st.session_state['otp_entered'] = False
    if 'driver' not in st.session_state:
        st.session_state['driver'] = None
    if 'scraping_started' not in st.session_state:
        st.session_state['scraping_started'] = False
    if 'scraping' not in st.session_state:
        st.session_state['scraping'] = False

    # Phase 1: Log in to the website
    if not st.session_state['logged_in']:
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

    # Phase 2: Handle OTP
    if st.session_state['logged_in']:
        otp = st.text_input("Enter OTP:")

        if st.button("Submit OTP"):
            try:
                if otp:
                    opt_s = otp__(driver=driver, otp=otp)
                    st.session_state['otp_entered'] = opt_s
                    st.success("OTP submitted successfully!")
                else:
                    st.error("Please enter the OTP.")
            except Exception as e:
                st.error(f"OTP submission failed: {CustomException(e, sys)}")

    # Phase 3: Start Continuous Scraping
    if st.session_state['logged_in'] and st.session_state['otp_entered']:
        st.subheader("Scrape Data from URLs")
        urls_input = st.text_area("Enter URLs to scrape (one per line)")
        
        urls = eval

        if st.button("Start Scraping"):
            if urls:
                st.session_state['scraping_started'] = True
                st.session_state['scraping'] = True
                st.write("Scraping data from URLs...")
                while st.session_state['scraping']:
                    try:
                        scraped_data = scrape_links(st.session_state['driver'], urls)
                        st.success("Scraping completed!")
                        st.write("\n".join([json.dumps(data, indent=4) for data in scraped_data]))
                    except Exception as e:
                        st.error(f"Scraping error: {CustomException(e, sys)}")
                    time.sleep(10)  # Wait before the next scrape cycle
            else:
                st.warning("Please enter URLs to scrape.")

        if st.button("Quit"):
            st.session_state['scraping'] = False
            st.success("Scraping stopped.")
        
    # Clean up and close driver if necessary
    if not st.session_state['scraping_started']:
        if st.session_state['driver']:
            st.session_state['driver'].quit()
            st.session_state['driver'] = None
            st.session_state['logged_in'] = False
            st.session_state['otp_entered'] = False
            st.session_state['scraping_started'] = False

if __name__ == "__main__":
    main()
