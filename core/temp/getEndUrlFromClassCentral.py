from pathlib import Path
import scrapy
import json
import re
import csv
from bs4 import BeautifulSoup
import time

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager


# From a CSV file that looks like this
# course_name,url_classCentral,end_url,provider_slug,summary,duration,entity_url,type,source,language
# Software Testing Simple (Software Quality Assurance QA),/course/udemy-software-testing-simple-36935,udemy,Easiest practical Testing course on the market that will explain you what is QA and testing and what QAs are doing!,3 hours 9 minutes,/provider/udemy,free,classCentral,en
# 
# Loop through each course
# If there is no end_url, then get it from the classCentral url by running the get_end_url
# Then update the csv file with the end_url

def get_end_urls_from_csv(csv_file):
    # Initialize an empty list to hold updated rows
    updated_rows = []
    headers = []

    # Read the CSV file and update rows as necessary
    with open(csv_file, newline='', mode='r') as csvfile:
        reader = csv.DictReader(csvfile)
        headers = reader.fieldnames  # Capture the headers for writing later

        for row in reader:
            print(row['url_classCentral'])
            if row['end_url'] == "":
                end_url = get_end_url(row['url_classCentral'])
                print(end_url)
                row['end_url'] = end_url
            updated_rows.append(row)

    # Write the updated rows back to the CSV file
    with open(csv_file, mode='w', newline='') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=headers)
        writer.writeheader()
        writer.writerows(updated_rows)



def get_end_url(url_slug, max_wait=20):
    # Configure Selenium to use Chrome in headless mode
    options = Options()
    # options.headless = True
    options.add_argument("--headless")
    options.add_argument("--window-size=1920,1080")
    options.add_argument("--no-sandbox")  # Add this if you are running in a container or restricted environment
    options.add_argument("--disable-dev-shm-usage")  # Add this to overcome limited resource problems

    start_url = f"https://www.classcentral.com{url_slug}/visit"

    # return none if the course is directly on classcentral (See example: https://www.classcentral.com/classroom/freecodecamp-flutter-course-for-beginners-37-hour-cross-platform-app-development-tutorial-104327)
    if start_url.startswith("https://www.classcentral.com/classroom"): 
        return None

    # Initialize the WebDriver with webdriver-manager
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)


    # Open the URL
    driver.get(start_url)

    # Start time for the wait loop
    start_time = time.time()

    # Loop until the URL changes or max_wait time is reached
    while True:
        current_time = time.time()
        if driver.current_url != start_url or current_time - start_time > max_wait:
            break
        time.sleep(1)  # Wait for 1 second before checking again

    
    end_url = driver.current_url


    # Remove everything from and including the "?"
    clean_url = end_url.split('?')[0]

    print(f"Clean URL: {clean_url}")

    # Close the browser
    driver.quit()

    if clean_url == start_url:
        return None
    
    return clean_url
    

# now run get_end_urls_from_csv for courses_info.csv
get_end_urls_from_csv("core/temp/courses_info.csv")
