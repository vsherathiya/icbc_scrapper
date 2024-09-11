# from fastapi import FastAPI, HTTPException
# from typing import List
# from fastapi.responses import StreamingResponse
# from pydantic import BaseModel
# from selenium import webdriver
# from selenium.webdriver.common.by import By
# from selenium.webdriver.support.ui import WebDriverWait
# from selenium.webdriver.support import expected_conditions as EC
# from selenium.webdriver.chrome.options import Options
# import requests
# import sys, os, json,re
# import base64
# from concurrent.futures import ThreadPoolExecutor, as_completed
# import logging
# from datetime import datetime
# from time import sleep, time
# import mysql.connector
# from mysql.connector import Error
# # Custom exception and logger setup
# from exception import CustomException, setup_logger
# logger = setup_logger("edgepipeline", "edgepipeline")
# app = FastAPI()
# # Database configuration
# # db_config = {
# #     'host': 'localhost',  # Replace with your database host
# #     'user': 'root',  # Replace with your database user
# #     'password': '',  # Replace with your database password
# #     'database': 'scrap_data',  # Replace with your database name
# #     'port': 3307
# # }
# db_config = {
#    'host': 'localhost',        # Replace with your database host
#    'user': 'icbc_scrapper',             # Replace with your database user
#    'password': 'R3RhtTyGEjGD7pZV8WJY6N9oeWRXsAxZ',             # Replace with your database password
#    'database': 'icbc_scrapper_DB',   # Replace with your database name
#    'port': 3306
# }
# def convert_date_format(date_str):
#     try:
#         input_date = datetime.strptime(date_str, '%a, %m/%d/%y')
#         return input_date.strftime('%Y-%m-%d')
#     except ValueError as e:
#         logger.error(f"Date conversion error: {e}")
# #         return ''
# driver = None
# # Create database tables if they don't exist

# # Initialize tables


# # Set up Chrome WebDriver options
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

# # Function to extract text using explicit wait
# def get_element_text(driver, selector, name):
#     try:
#         element = WebDriverWait(driver, 5).until(
#             EC.presence_of_element_located((By.CSS_SELECTOR, selector))
#         )
#         return element.text
#     except Exception as e:
#         logger.error(f"Error Occurred at {CustomException(e, sys)}")
#         print(CustomException(e, sys))
#         logger.error(f"Error extracting {name}: {e}")
#         return None

# # Function to extract data from a single URL
# def extract_data_from_url(driver, url):
#     data = {}
#     start_time = time()
#     try:
#         driver.get(url)
#         sleep(1.5)


#         print(data)

#         elapsed_time = time() - start_time
#         logger.info(f"Extracted data from {url} in {elapsed_time:.2f} seconds")
#     except Exception as e:
#         logger.error(f"Error Occurred at {CustomException(e, sys)}")
#         print(CustomException(e, sys))
#         logger.error(f"Error extracting data from {url}: {CustomException(e, sys)}")
#     return data

# # Function to extract data from specific sections







# # Define a model for the request body
                                                                                            
#     # Define your API endpoint

# def call(driver,id,password,links):
#     try:
#         parsed_data = []
#         driver.get('https://api.manheim.com/auth/authorization.oauth2?adaptor=manheim_customer&client_id=25xk9b3322exa7ar4tdazrr4&redirect_uri=https%3A%2F%2Fsearch.manheim.com%2Fcallback&response_type=code&scope=email+profile+openid+offline_access&state=%2Fresults#/details/WA1VGAFP9FA018909/OVE')  # Replace with the actual login URL
#         # Find the username and password input elements and fill them
#         username_input = driver.find_element(By.ID, 'user_username')
#         password_input = driver.find_element(By.ID, 'user_password')
#         username_input.send_keys(id)  # Replace with actual username
#         password_input.send_keys(password)  # Replace with actual password
#         # Submit the form
#         submit_button = driver.find_element(By.XPATH, '//*[@id="submit"]')
#         submit_button.click()
#         print('log in')
        
#          # Navigate to the specific page URL
#         # driver.get("https://search.manheim.com/results#/details/WA1VGAFP9FA018909/OVE")

#         # Wait until the page is fully loaded and locate the radio button
#         radio_button = WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.XPATH, '//*[@id="186a7aba-c616-4c22-186a-7abac6164c22"]')))
        
#         # Click the radio button
#         radio_button.click()

#         # Locate the "Continue" button
#         continue_button = WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.XPATH, '//*[@id="buttoncontinue"]')))
        
#         # Click the "Continue" button
#         continue_button.click()

#         print("Radio button selected and 'Continue' button clicked successfully.")
        
#         WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.XPATH, '//*[@id="OTP"]')))
        
#         # Manually input OTP here
#         otp_code = input("Please enter the OTP received: ")
#         otp_input = driver.find_element(By.XPATH, '//*[@id="OTP"]')
#         otp_input.send_keys(otp_code)
        
#         # Click the submit button for OTP
#         otp_submit_button = driver.find_element(By.XPATH, '//*[@id="submitButton"]')
#         otp_submit_button.click()
#         print('OTP entered and submitted')
#         return(f"\n\dhfdfh\n")
          
#     finally:
#         driver.quit()
#         logger.info("\n\ncompleted")
#         yield "\n\ncompleted"

# def close_browser():
#     if driver:
#         driver.quit()
#         print("Closed the browser.")
#         logger.info("Closed the browser.")
#         return "Stopping Scrapping"
# class RequestBody(BaseModel):
#     id: str
#     password: str
#     links: List[str]
    

# @app.post("/parse_links/")
# async def parse_links(request_body: RequestBody):
#     try:
#         # call(request_body.id,request_body.password)
#         global driver
#         driver = webdriver.Chrome(options=chrome_options)

#         return StreamingResponse(call(driver,request_body.id,request_body.password ,request_body.links), media_type="text/plain")
#     except Exception as e:
#                 logger.error(f"Error Occurred at {CustomException(e, sys)}")
#                 print(CustomException(e, sys))

# @app.post("/stop-server")
# def stop_server():
#     close_browser()
        
    
# # Function to call an external API
# def call_api(data):
#     try:
#         headers = {'accept': 'application/json', 'Content-Type': 'application/json'}
#         url = "https://americanauctionaccess.com/edge-scrap-api"
#         response = requests.post(url, headers=headers, data=data)
#         if response.status_code == 200:
#             return response.json()
#         else:
#             raise Exception(f"Failed to send data to API. Status code: {response.status_code}")
#     except requests.exceptions.RequestException as e:
#         logger.error(f"Error sending data to API: {CustomException(e, sys)}")
#         print(f"Error sending data to API: {CustomException(e, sys)}")
# # Function to insert data into the database
# # Function to insert data into the database

# if __name__ == "__main__":
#     import uvicorn
#     uvicorn.run(app, host="0.0.0.0", port=3036)

# import streamlit as st
# from selenium import webdriver
# from selenium.webdriver.common.by import By
# from selenium.webdriver.support.ui import WebDriverWait
# from selenium.webdriver.support import expected_conditions as EC
# from selenium.webdriver.chrome.options import Options
# import time

# # Set up Chrome WebDriver options
# chrome_options = Options()
# chrome_options.add_argument("--disable-gpu")
# chrome_options.add_argument("--no-sandbox")
# chrome_options.add_argument("--disable-dev-shm-usage")
# chrome_options.add_argument("--disable-blink-features=AutomationControlled")
# chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
# chrome_options.add_experimental_option("useAutomationExtension", False)
# chrome_options.add_argument("--window-size=1920x1080")
# chrome_options.add_argument("--disable-extensions")

# # Initialize the WebDriver
# driver = None

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
#     time.sleep(0.5) 


# # Function to handle radio button and continue
# def handle_radio_and_continue(driver):
#     # Wait for the radio bu
#     pass

# # Function to handle OTP input
# def enter_otp(driver, otp):
#     WebDriverWait(driver, 10).until(
#         EC.presence_of_element_located((By.XPATH, '//*[@id="OTP"]')))
#     otp_input = driver.find_element(By.XPATH, '//*[@id="OTP"]')
#     otp_input.send_keys(otp)
#     otp_submit_button = driver.find_element(By.XPATH, '//*[@id="submitButton"]')
#     otp_submit_button.click()

# # Function to scrape data from links
# def scrape_links(driver, links):
#     scraped_data = []
#     for link in links:
#         driver.get(link)
#         time.sleep(2)  # Wait for page load
#         # Extract data (replace with actual extraction logic)
#         title = driver.title
#         scraped_data.append(f"Title of {link}: {title}")
#     return scraped_data

# # Initialize session state variables
# if 'logged_in' not in st.session_state:
#     st.session_state['logged_in'] = False

# if 'radio_handled' not in st.session_state:
#     st.session_state['radio_handled'] = False

# if 'otp_entered' not in st.session_state:
#     st.session_state['otp_entered'] = False

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

# # Phase 3: Handle OTP and Scrape Data
# if st.session_state['logged_in'] and not st.session_state['otp_entered']:
#     st.subheader("OTP Handling")
#     otp = st.text_input("Enter OTP:")
#     if st.button("Submit OTP"):
#         if otp:
#             st.write("Submitting OTP...")
#             try:
#                 enter_otp(driver, otp)
#                 st.success("OTP submitted!")
#                 st.session_state['otp_entered'] = True
#             except Exception as e:
#                 st.error(f"Error: {e}")
#         else:
#             st.warning("Please enter OTP.")


# # Phase 4: Scrape data from links
# if st.session_state['otp_entered']:
#     st.subheader("Scrape Data from Links")
#     links = st.text_area("Enter links to scrape (one per line)").splitlines()

#     if st.button("Scrape"):
#         if links:
#             st.write("Scraping data from links...")
#             try:
#                 scraped_data = scrape_links(driver, links)
#                 st.success("Scraping completed!")
#                 st.write("\n".join(scraped_data))
#             except Exception as e:
#                 st.error(f"Scraping error: {e}")
#         else:
#             st.warning("Please enter some links to scrape.")

import streamlit as st
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
import time

# Set up Chrome WebDriver options
chrome_options = Options()
chrome_options.add_argument("--disable-gpu")
chrome_options.add_argument("--no-sandbox")
chrome_options.add_argument("--disable-dev-shm-usage")
chrome_options.add_argument("--disable-blink-features=AutomationControlled")
chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
chrome_options.add_experimental_option("useAutomationExtension", False)
chrome_options.add_argument("--window-size=1920x1080")
chrome_options.add_argument("--disable-extensions")

# Initialize the WebDriver
driver = None

# Function to log in to the website
def login(driver, id, password):
    driver.get('https://search.manheim.com/results#/details/WA1VGAFP9FA018909/OVE')  # Replace with the actual login URL
    username_input = driver.find_element(By.ID, 'user_username')
    password_input = driver.find_element(By.ID, 'user_password')
    username_input.send_keys(id)
    password_input.send_keys(password)
    submit_button = driver.find_element(By.XPATH, '//*[@id="submit"]')
    submit_button.click()
    time.sleep(0.5) 
    radio_button = WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable((By.XPATH, '//*[@id="186a7aba-c616-4c22-186a-7abac6164c22"]')))
    radio_button.click()

    # Click "Continue" button
    continue_button = WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable((By.XPATH, '//*[@id="buttoncontinue"]')))
    continue_button.click()
    # Wait for login
    time.sleep(0.5) 

# Function to handle OTP input
def enter_otp(driver, otp, target_url):
    WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.XPATH, '//*[@id="OTP"]')))
    otp_input = driver.find_element(By.XPATH, '//*[@id="OTP"]')
    otp_input.send_keys(otp)
    otp_submit_button = driver.find_element(By.XPATH, '//*[@id="submitButton"]')
    otp_submit_button.click()
    # Wait until URL changes after OTP submission
    WebDriverWait(driver, 10).until(
        EC.url_changes(driver.current_url))
    # Navigate to the target URL after OTP submission
    driver.get(target_url)
    # Store session cookies
    cookies = driver.get_cookies()
    st.session_state['cookies'] = cookies

# Function to scrape data from links using session cookies
def scrape_links(driver, numbers):
    scraped_data = []
    for number in numbers:
        # Generate the link based on the number
        link = f"https://example.com/details/{number}"  # Replace with the actual URL format
        driver.get(link)
        time.sleep(2)  # Wait for page load
        # Extract data (replace with actual extraction logic)
        title = driver.title
        scraped_data.append(f"Title of {link}: {title}")
    return scraped_data

# Function to initialize driver with cookies
def initialize_driver_with_cookies():
    driver = webdriver.Chrome(options=chrome_options)
    driver.get('https://search.manheim.com/results#/details/WA1VGAFP9FA018909/OVE')  # Replace with an actual URL
    cookies = st.session_state.get('cookies', [])
    for cookie in cookies:
        driver.add_cookie(cookie)
    driver.refresh()
    return driver

# Initialize session state variables
if 'logged_in' not in st.session_state:
    st.session_state['logged_in'] = False

if 'otp_entered' not in st.session_state:
    st.session_state['otp_entered'] = False

if 'target_url' not in st.session_state:
    st.session_state['target_url'] = ""

if 'cookies' not in st.session_state:
    st.session_state['cookies'] = []

# Streamlit UI
st.title("Web Scraper with Radio Button, Continue, and OTP Handling")

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
                st.success("Login successful!")
                st.session_state['logged_in'] = True
            except Exception as e:
                st.error(f"Login failed: {e}")
        else:
            st.warning("Please fill in both fields.")

# Phase 2: Handle OTP and make the links text box visible
if st.session_state['logged_in'] and not st.session_state['otp_entered']:
    st.subheader("OTP Handling")
    otp = st.text_input("Enter OTP:")
    target_url = st.text_input("Enter the URL to navigate to after OTP:")

    if st.button("Submit OTP"):
        if otp and target_url:
            st.write("Submitting OTP...")
            try:
                enter_otp(driver, otp, target_url)
                st.success("OTP submitted and navigated to URL!")
                st.session_state['otp_entered'] = True
                # Reinitialize the driver with cookies
                driver.quit()
                driver = initialize_driver_with_cookies()
            except Exception as e:
                st.error(f"Error: {e}")
        else:
            st.warning("Please enter both OTP and target URL.")

# Phase 3: Scrape data from links
if st.session_state['otp_entered']:
    st.subheader("Scrape Data from Links")
    numbers = st.text_area("Enter numbers to scrape (one per line)").splitlines()

    if st.button("Scrape"):
        if numbers:
            st.write("Scraping data from numbers...")
            try:
                scraped_data = scrape_links(driver, numbers)
                st.success("Scraping completed!")
                st.write("\n".join(scraped_data))
            except Exception as e:
                st.error(f"Scraping error: {e}")
        else:
            st.warning("Please enter some numbers to scrape.")
