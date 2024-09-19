import sys
import streamlit as st
from scraper import init_driver, login, scrape_links,otp__
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

            st.session_state['driver'] = driver
            login_successful,driver = login(driver, id, password)
            if login_successful:
                st.session_state['logged_in'] = True
                st.success("Login successful!")
            
        except Exception as e:
            st.error(f"Login failed: {CustomException(e,sys)}")

# Phase 2: Handle OTP

otp = st.text_input("Enter OTP:")
if st.button("Submit OTP"):
    try:
        st.success("OTP submitted successfully!")
        st.session_state['otp_entered'] = True
        # otp__(driver=driver,otp=otp)
        st.subheader("Scrape Data from URLs")
        urls_input = st.text_area("Enter URLs to scrape (one per line)")
        urls = eval(urls_input)
        print(type(urls))
        if isinstance(urls, list):
            if st.button("Scrape"):
                if urls:
                    try:
                        st.write("Scraping data from URLs...")
                        scraped_data = scrape_links(st.session_state['driver'], urls)
                        st.success("Scraping completed!")
                        st.write("\n".join(scraped_data))
                    except Exception as e:
                        st.error(f"Scraping error: {CustomException(e,sys)}")
                else:
                    st.warning("Please enter URLs to scrape.")
    except Exception as e:
        st.error(f"OTP submission failed: {CustomException(e,sys)}")

        st.error(f"OTP submission failed: {e}")

