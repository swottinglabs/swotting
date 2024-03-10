import csv
import json
import re
import time

import scrapy
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager


# Todo to run: active the virtual environment and run the following command python3 manage.py scrape classCentralProviders in the ubuntu
# TODO
# provider_name  is not working - DONE
# Save courses to a csv file. - DONE
# Write a function to get the link that is being requested. 
# make 1-5 sec delay between requests - Done
# make that it loops through all the pages. - Done


class ProvidersSpider(scrapy.Spider):
    name = "classCentralProviders"
    start_urls = [
        "https://www.classcentral.com/providers",
    ]
    custom_settings = {
        'USER_AGENT': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.150 Safari/537.36',
    }

    download_delay = 2.0

    def parse(self, response):
        # Delegate the processing of providers to the get_providers function
        return self.get_providers(response)

    def get_providers(self, response):
        providers = []

        # Loop through each provider in the list
        for provider in response.xpath('//li[contains(@class, "width-100 border-bottom border-box")]'):
            # Extract the name and URL of each provider
            name = provider.xpath('.//span[contains(@class, "text-1 line-tight color-charcoal weight-semi block")]/text()').get()
            relative_url = provider.xpath('./a/@href').get()
            url = response.urljoin(relative_url)  # Convert relative URL to absolute URL

            # Create a dictionary with the provider name and URL
            item = {
                'name': name,
                'url': url,
            }

            providers.append(item)

        # Call getAllLinksFromProviders and yield each request
        for request in self.getAllLinksFromProviders(providers):
            yield request
            
    def parse_course_data(self, response):
        # Extract the text content of the response object
        input_json_string = response.text  # or response.body.decode('utf-8') if you encounter encoding issues

        # Load the JSON string into a dictionary
        data = json.loads(input_json_string)

        # Extract the provider slug from the meta data
        provider_slug = response.meta['provider_slug']

        # Save the loaded JSON data to a file for testing
        with open('input_data.json', 'w') as file:
            json.dump(data, file, indent=4)

        # Proceed with parsing the HTML content
        soup = BeautifulSoup(data['table'], 'html.parser')

        # Initialize an empty list to store course information
        courses_info = []

        # Find all course elements in the parsed HTML
        courses = soup.find_all('li', class_='course-list-course')
        print("Found this many courses: ", len(courses))

        if not courses:
            print("No courses found")
            return
        
        for course in courses:
            # Extract course information as before
            course_name = course.find('h2', itemprop='name').text if course.find('h2', itemprop='name') else None
            course_url = course.find('a', itemprop='url')['href'] if course.find('a', itemprop='url') else None
            summary = course.find('p', class_='text-2 margin-bottom-xsmall').text.strip() if course.find('p', class_='text-2 margin-bottom-xsmall') else None
            duration = None
            duration_element = course.find('span', {'aria-label': 'Workload and duration'})
            if duration_element:
                duration = duration_element.text.strip()

            # Attempt to dynamically identify an entity link
            entity_url = None
            potential_entity_links = course.find_all('a', href=True)
            for link in potential_entity_links:
                if link['href'] != course_url and ('/course/' not in link['href']):
                    entity_url = link['href']
                    break  # Assuming the first matching link is the entity link
            
            # Get the final url
            end_url = self.get_end_url(course_url)
            
            # Append course information with the dynamic 'entity_url'
            courses_info.append({
                'course_name': course_name,
                'url_classCentral': course_url,
                'end_url': end_url,
                'provider_slug': provider_slug,
                'summary': summary,
                'duration': duration,
                'entity_url': entity_url,  # Dynamically found
                "type": "free",
                "source": "classCentral",
                "language": "en"
            })
        
        # for course in courses:
        #     # Extract course information
        #     course_name = course.find('h2', itemprop='name').text if course.find('h2', itemprop='name') else None
        #     course_url = course.find('a', itemprop='url')['href'] if course.find('a', itemprop='url') else None
        #     # provider_name = course.find('span', text='Provider').find_next_sibling('a').text if course.find('span', text='Provider') else None
        #     summary = course.find('p', class_='text-2 margin-bottom-xsmall').text.strip() if course.find('p', class_='text-2 margin-bottom-xsmall') else None
        #     duration = None
        #     duration_element = course.find('span', {'aria-label': 'Workload and duration'})
        #     if duration_element:
        #         duration = duration_element.text.strip()

        #     # Extract university URL
        #     university_element = course.find('a', href=lambda href: href and '/university/' in href)
        #     university_url = university_element['href'] if university_element else None

        #     # end_url = self.get_end_url(course_url)
        #     # print(f"End URL: {end_url}")

        #     # Rename 'course_url' to 'url_classCentral' and add 'university_url'
        #     courses_info.append({
        #         'course_name': course_name,
        #         'url_classCentral': course_url,
        #         # 'end_url': end_url,
        #         'provider_slug': provider_slug,
        #         'summary': summary,
        #         'duration': duration,
        #         "type": "free",
        #         "source": "classCentral",
        #         "language": "en",
        #         "university_url": university_url  # Add university_url here
        #     })

        print("Finished parsing course data and found this many courses: ", len(courses_info))

        # Read the existing CSV to check for duplicates
        existing_urls = set()
        try:
            with open('courses_info.csv', mode='r', newline='', encoding='utf-8') as csvfile:
                reader = csv.DictReader(csvfile)
                for row in reader:
                    existing_urls.add(row['url_classCentral'])
        except FileNotFoundError:
            # If the file does not exist, proceed to create it
            pass

        # Save the courses information to a CSV file, excluding duplicates
        with open('courses_info.csv', mode='a', newline='', encoding='utf-8') as csvfile:
            fieldnames = ['course_name', 'url_classCentral', 'end_url', 'provider_slug', 'summary', 'duration', "entity_url", "type", "source", "language"]
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            
            # Write the header only if the file is newly created
            if not existing_urls:
                writer.writeheader()

            for course in courses_info:
                if course['url_classCentral'] not in existing_urls:
                    # Replace newline characters in the 'summary' field with a space
                    course['summary'] = course['summary'].replace('\n', ' ').replace('\r', ' ')
                    writer.writerow(course)

        current_page = response.meta['current_page']
        print(f"Current page complete: {current_page}")
        # For testing if current page over 2 then stop
        if current_page > 2:
            return courses_info

        print('current_page', current_page)
        modified_url = f"https://www.classcentral.com/maestro/provider/{provider_slug}?page={current_page+1}&free=true&lang=english"
        print(f"Modified Url: {modified_url}")
        yield scrapy.Request(url=modified_url, callback=self.parse_course_data, meta={'provider_slug': provider_slug, 'current_page': current_page + 1})

    
    def extract_course_details(self, course_html):
        # This is a simplified extraction method
        # You'll need to parse HTML or use regex to extract the actual details
        # For example:
        name_match = re.search(r'data-track-props=\u0022(.*?)\u0022', course_html)
        if name_match:
            course_data = json.loads(name_match.group(1).replace('\u0026quot;', '"'))
            course = {
                'title': course_data.get('course_name'),
                'description': "Extract the description from the HTML using a similar approach",
                'link': f"https://www.classcentral.com/course/{course_data.get('course_slug')}",
            }
            return course
        return None


    def getAllLinksFromProviders(self, providers):

        print("Running getAllLinksFromProviders")


        for provider in providers:

            print("Provider: ", provider)

            if provider["name"] == "youtube" or provider["name"] == "Youtube" or provider["name"] == "YouTube": continue

            if provider["name"] != "edX": continue

            # Split the URL to get the provider name slug
            provider_slug = provider['url'].split('/')[-1]
            # Create the new URL format start at page 1 and only free courses
            modified_url = f"https://www.classcentral.com/maestro/provider/{provider_slug}?page=1&free=true&lang=english"

            print(f"Modified Url: {modified_url}")

            # Schedule a request to the modified URL
            # Use the callback parameter to specify the method that will handle the response
            yield scrapy.Request(url=modified_url, callback=self.parse_course_data, meta={'provider_slug': provider_slug, 'current_page': 1})



    # def get_end_url(self, url_slug, max_wait=20):
    #     # Configure Selenium to use Chrome in headless mode
    #     options = Options()
    #     options.headless = True
    #     options.add_argument("--window-size=1920,1080")

    #     # Initialize the WebDriver
    #     driver = webdriver.Chrome(options=options)

    #     start_url = f"https://www.classcentral.com{url_slug}/visit"

    #     # Open the URL
    #     driver.get(start_url)

    #     # Start time for the wait loop
    #     start_time = time.time()

    #     # Loop until the URL changes or max_wait time is reached
    #     while True:
    #         current_time = time.time()
    #         if driver.current_url != start_time or current_time - start_time > max_wait:
    #             break
    #         time.sleep(1)  # Wait for 1 second before checking again

    #     # You can add more logic here if you need to interact with the page or extract data

    #     end_url = driver.current_url
    #     print(f"End URL: {end_url}")

    #     # Print the current URL after waiting
    #     print("Current URL after waiting:", driver.current_url)

    #     # Close the browser
    #     driver.quit()

    #     if end_url == start_url:
    #         return None
        
    #     return end_url

    def get_end_url(self, url_slug, max_wait=20):
        # Configure Selenium to use Chrome in headless mode
        options = Options()
        # options.headless = True
        options.add_argument("--headless")
        options.add_argument("--window-size=1920,1080")
        options.add_argument("--no-sandbox")  # Add this if you are running in a container or restricted environment
        options.add_argument("--disable-dev-shm-usage")  # Add this to overcome limited resource problems

        # Initialize the WebDriver with webdriver-manager
        driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)

        start_url = f"https://www.classcentral.com{url_slug}/visit"

        # Open the URL
        driver.get(start_url)

        # Start time for the wait loop
        start_time = time.time()

        # Loop until the URL changes or max_wait time is reached
        while True:
            current_time = time.time()
            if driver.current_url != start_url and current_time - start_time > max_wait:
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
    


