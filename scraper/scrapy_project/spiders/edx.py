import re
from datetime import datetime
from urllib.parse import parse_qs, urlparse
from uuid import uuid4
import bs4
from scrapy.spiders import SitemapSpider
from scraper.scrapy_project.spiders.base_scraper import BaseSpider
import logging
import os


# Set this to False for production runs
TESTING = False 
# If testing is enabled, limit number of processed items
TEST_LIMIT = 10

# Improvements:
# Dynamically set the language based on the written out language on the website then get the iso code from that 
# Check Archived courses: https://www.edx.org/learn/social-science/mcgill-social-learning-for-social-impact
# The is_free and is_limited_free seems to work but needs to be verified on more examples

class EdxSpider(SitemapSpider, BaseSpider):
    name = 'edx'
    base_url = 'https://www.edx.org'
    sitemap_urls = [base_url + '/sitemap.xml']
    custom_settings = {
        'CONCURRENT_REQUESTS': 4,  # Reduced from 8 for more stability
        'DOWNLOAD_DELAY': 2,
        'RANDOMIZE_DOWNLOAD_DELAY': True,
    }

    # Constants
    TESTING = TESTING  # Use global setting for testing mode
    TEST_LIMIT = TEST_LIMIT  # Use global setting for test limit
    IS_FREE = False
    IS_LIMITED_FREE = True
    LANGUAGE = ['en']
    FORMAT = "Video"
    
    def __init__(self, *args, **kwargs):
        # Set default platform_id if not provided
        platform_id = kwargs.pop('platform_id', 'edx')
        # Initialize both parent classes properly
        SitemapSpider.__init__(self, platform_id, *args, **kwargs)
        BaseSpider.__init__(self, platform_id, *args, **kwargs)
        
        # Add debug logging
        self.logger.setLevel(logging.DEBUG)
        self.logger.debug(f"EdxSpider initialized. TESTING mode: {self.TESTING}, TEST_LIMIT: {self.TEST_LIMIT}")
        
        # Print database settings from environment
        db_url = os.environ.get('DATABASE_URL', 'Not set in environment')
        self.logger.debug(f"Spider init - DATABASE_URL environment: {db_url}")

    def sitemap_filter(self, entries):
        count = 0
        
        self.logger.info(f"Sitemap filter received {len(list(entries))} entries. Testing mode: {self.TESTING}")
        
        for entry in entries:
            # If in testing mode and we've reached the limit, stop
            if self.TESTING and count >= self.TEST_LIMIT:
                self.logger.debug(f"Test limit reached ({self.TEST_LIMIT}), stopping sitemap filter")
                break
                
            url = entry['loc']
            pattern = rf'^{re.escape(self.base_url)}/learn/[^/]+/[^/]+$'
            
            if re.match(pattern, url):
                self.logger.debug(f"URL matched pattern: {url}")
                entry['loc'] = self._convert_to_json_url(entry['loc'])
                count += 1
                yield entry
            else:
                self.logger.debug(f"URL did not match pattern: {url}")
        
        self.logger.info(f"Sitemap filter yielded {count} entries")

    def start_requests(self):
        self.logger.info("Starting requests for EdxSpider")
        for request in SitemapSpider.start_requests(self):
            self.logger.debug(f"Sending request to: {request.url}")
            yield request.replace(
                url=request.url,
                dont_filter=True,
                meta={'dont_retry': False}
            )

    def _convert_to_json_url(self, course_url):
        """Convert course URL to corresponding page-data.json URL."""
        # Remove base URL
        path = course_url.replace(self.base_url, '')
        return f"{self.base_url}/page-data{path}/page-data.json"

    def _clean_html_description(self, html_description):
        """Remove <p> tags and newlines from HTML description."""
        if not html_description:
            return ""
        soup = bs4.BeautifulSoup(html_description, 'html.parser')
        return ' '.join(soup.stripped_strings)

    def _get_seat_info(self, seats, enrollment_start=None, enrollment_end=None):
        """
        Extract pricing and certificate information from course seats.
        Also considers enrollment dates for determining free access.
        """
        if not seats:
            return {
                'is_free': False,
                'is_limited_free': False,
                'dollar_price': None,
                'has_certificate': False
            }
        
        audit_seat = next((seat for seat in seats if seat.get('type') == 'audit'), None)
        verified_seat = next((seat for seat in seats if seat.get('type') == 'verified'), None)
        
        has_free_audit = bool(audit_seat and audit_seat.get('price') == '0.00')
        has_enrollment_start = enrollment_start is not None
        has_no_enrollment_start = enrollment_start is None
        has_no_enrollment_end = enrollment_end is None
        
        return {
            'is_free': has_free_audit and has_enrollment_start and has_no_enrollment_end,
            'is_limited_free': has_free_audit and has_no_enrollment_start and has_no_enrollment_end,
            'dollar_price': float(verified_seat.get('price', 0)) if verified_seat else None,
            'has_certificate': bool(verified_seat)
        }

    def _calculate_duration_hours(self, active_run):
        """
        Calculate total duration in hours based on effort per week and total weeks.
        
        Args:
            active_run (dict): Dictionary containing course run information
            
        Returns:
            float or None: Total duration in hours, or None if data is insufficient
        """
        min_effort = active_run.get('minEffort')
        max_effort = active_run.get('maxEffort')
        weeks_to_complete = active_run.get('weeksToComplete')
        
        if not all([min_effort, max_effort, weeks_to_complete]):
            return None
            
        avg_effort = (min_effort + max_effort) / 2
        return avg_effort * weeks_to_complete

    def _get_course_tags(self, course):
        """
        Combine skill names and subject names into a single list of tags.
        
        Args:
            course (dict): Course data containing skillNames and subjects
            
        Returns:
            list: Combined list of skill names and subject names
        """
        # Get skill names (direct list of strings)
        skill_names = course.get('skillNames', [])
        
        # Get subject names (list of objects with 'name' key)
        subject_names = [
            subject.get('name') 
            for subject in course.get('subjects', []) 
            if subject.get('name')
        ]
        
        # Combine both lists
        return skill_names + subject_names

    def _standardize_level(self, level):
        """
        Standardize course level to one of: Beginner, Intermediate, or Advanced.
        
        Args:
            level (str): Raw level from EdX
            
        Returns:
            str: Standardized level or None if no match
        """
        level_mapping = {
            'introductory': 'Beginner',
            'intermediate': 'Intermediate',
            'advanced': 'Advanced',
            'beginner': 'Beginner'
        }
        
        if not level:
            return None
            
        normalized_level = level.lower().strip()
        return level_mapping.get(normalized_level)

    def parse(self, response):
        self.logger.info(f"Parsing URL: {response.url}")
        try:
            json_data = response.json()
            course = json_data.get('result', {}).get('pageContext', {}).get('course', {})
            
            if not course:
                self.logger.warning(f"No course data found in response from {response.url}")
                return
            
            self.logger.debug(f"Found course: {course.get('title')}")
            
            active_run = course.get('activeCourseRun', {})
            clean_url = response.url.replace('page-data/', '').replace('page-data.json', '')

            
            seat_info = self._get_seat_info(
                active_run.get('seats', []),
                enrollment_start=active_run.get('enrollmentStart'),
                enrollment_end=active_run.get('enrollmentEnd')
            )
            
            learning_resource = {
                'creators': [
                    {
                        'name': owner.get('name'),
                        'platform_id': 'edx',
                        'platform_creator_id': owner.get('uuid'),
                        'url': owner.get('marketingUrl'),
                        'platform_thumbnail_url': owner.get('logoImageUrl'),
                        'description': ''
                    }
                    for owner in course.get('owners', [])
                ],
                'name': course.get('title'),
                'url': clean_url,
                'scraped_timestamp': datetime.now().isoformat(),
                'platform_id': 'edx',
                'description': self._clean_html_description(course.get('fullDescription')),
                'html_description': course.get('fullDescription'),
                'platform_course_id': course.get('uuid'),
                'languages': course.get('language', self.LANGUAGE),
                'is_free': seat_info['is_free'],
                'is_limited_free': seat_info['is_limited_free'],
                'dollar_price': float(seat_info['dollar_price']) if seat_info['dollar_price'] else None, # should be improved e.g. does not work for this page https://www.edx.org/learn/business-administration/acca-business-and-technology
                'has_certificate': seat_info['has_certificate'],
                'short_description': self._clean_html_description(course.get('shortDescription')),
                'platform_last_update': course.get('updatedAt'),
                'platform_thumbnail_url': course.get('originalImage', {}).get('src'),
                'duration_h': self._calculate_duration_hours(active_run),
                'plarform_reviews_count': course.get('courseReview', {}).get('reviewCount'),
                'platform_reviews_rating': round(float(course.get('courseReview', {}).get('avgCourseRating', 0)), 2) if course.get('courseReview', {}).get('avgCourseRating') else None,
                'level': self._standardize_level(course.get('levelType')),
                'short_description': self._clean_html_description(course.get('shortDescription')),
                'enrollment_count': course.get('enrollmentCount', None),
                'is_active': active_run.get('isEnrollable', True),
                'tags': self._get_course_tags(course),
                'format': self.FORMAT,
            }

            self.logger.info(f"Successfully parsed course: {learning_resource['name']}")
            self.logger.debug(f"Yielding learning resource: {learning_resource['name']} with ID {learning_resource['platform_course_id']}")
            yield {
                'type': 'learning_resource',
                'data': learning_resource
            }
            
        except Exception as e:
            self.logger.error(f"Error parsing JSON from {response.url}: {str(e)}")
            import traceback
            self.logger.error(f"Full error traceback: {traceback.format_exc()}")

    def closed(self, reason):
        """Handle spider cleanup"""
        self.logger.info(f"Spider closed: {reason}")
        # super().closed(reason)