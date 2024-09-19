import json
import sys
import streamlit as st

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


def main():
    try:
        # if st.session_state.get('otp_entered', False):
            st.subheader("Scrape Data from URLs")
            urls_input = st.text_area("Enter URLs to scrape (one per line)")

            if st.button("Scrape"):
                if urls_input:
                    # Convert URLs input into a list of strings
                    urls = [url.strip() for url in urls_input.splitlines() if url.strip()]
                    print(urls, "\nURLs")

                    while urls:
                        try:
                            # Process the first URL in the list
                            url_to_scrape = urls.pop(0)  # Remove and get the first URL
                            st.write(f"Scraping data from URL: {url_to_scrape}...")
                            # Assuming scrape_links processes a single URL
                            time.sleep(4)
                            # scraped_data = scrape_links(st.session_state['driver'], [url_to_scrape])
                            st.success("Scraping completed for this URL!")
                            # st.write("\n".join([json.dumps(data, indent=4) for data in scraped_data]))

                            # If the URLs list is now empty, prompt the user to enter new URLs
                            if not urls:
                                st.warning("All URLs have been processed. Please enter new URLs to scrape.")
                                break

                        except Exception as e:
                            st.error(f"Scraping error: {CustomException(e, sys)}")
                            break  # Exit the loop in case of an error
                else:
                    st.warning("Please enter URLs to scrape.")
        # else:
        #     st.error("Please enter the OTP.")
    except Exception as e:
        st.error(f"OTP submission failed: {CustomException(e, sys)}")

# Assume otp__ and scrape_links functions are defined elsewhere

if __name__ == "__main__":
    main()
