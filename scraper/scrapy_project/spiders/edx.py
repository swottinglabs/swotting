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
        'LOG_LEVEL': 'DEBUG',  # Ensure detailed logging
        'CLOSESPIDER_ERRORCOUNT': 5,  # Allow more errors before stopping
        'CLOSESPIDER_TIMEOUT': 7200,  # 2 hours timeout
        'DOWNLOAD_TIMEOUT': 180,  # 3 minutes timeout for each request
        'RETRY_TIMES': 3,  # Retry failed requests 3 times
        'RETRY_HTTP_CODES': [500, 502, 503, 504, 522, 524, 408, 429],  # Retry on these status codes
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
        
        # Add counters for debugging
        self.sitemap_urls_found = 0
        self.urls_matched_pattern = 0
        self.requests_made = 0
        self.successful_parses = 0
        self.sitemap_files_processed = 0
        
        self.logger.info(f"EdxSpider initialized with TESTING={self.TESTING}, TEST_LIMIT={self.TEST_LIMIT}")
        
        # Print database settings from environment
        db_url = os.environ.get('DATABASE_URL', 'Not set in environment')
        self.logger.debug(f"Spider init - DATABASE_URL environment: {db_url}")

    def sitemap_filter(self, entries):
        count = 0
        total_entries = list(entries)
        self.sitemap_urls_found = len(total_entries)
        
        self.logger.info(f"Sitemap filter received {self.sitemap_urls_found} entries. Testing mode: {self.TESTING}")
        
        # Analyze URL patterns but log only at debug level
        url_patterns = {}
        for entry in total_entries:
            url = entry['loc']
            parts = url.replace(self.base_url, '').strip('/').split('/')
            if len(parts) >= 1:
                pattern = '/'.join(parts[:min(3, len(parts))])
                url_patterns[pattern] = url_patterns.get(pattern, 0) + 1
        
        # Log URL patterns at debug level only
        self.logger.debug(f"URL patterns found in sitemap:")
        for pattern, count in sorted(url_patterns.items(), key=lambda x: x[1], reverse=True)[:5]:  # Only log top 5
            self.logger.debug(f"  - Pattern: {pattern}, Count: {count}")
            
        # Move detailed alternative pattern analysis to debug level
        potential_course_urls = 0
        current_pattern = rf'^{re.escape(self.base_url)}/learn/[^/]+/[^/]+$'
        
        alternative_patterns = [
            r'/course/',
            r'/professional-certificate/',
            r'/xseries/',
            r'/micromasters/',
            r'/learn/.+/.+/.+',  # Deeper learn paths
        ]
        
        alternative_matches = {pattern: 0 for pattern in alternative_patterns}
        
        for entry in total_entries:
            url = entry['loc']
            
            if not re.match(current_pattern, url):
                for pattern in alternative_patterns:
                    if re.search(pattern, url):
                        # Remove individual URL logging
                        alternative_matches[pattern] += 1
                        potential_course_urls += 1
                        break
        
        # Log summary of alternative patterns at debug level
        self.logger.debug(f"Found {potential_course_urls} potential course URLs that don't match our current pattern")
        for pattern, count in alternative_matches.items():
            if count > 0:
                self.logger.debug(f"  - Alternative pattern '{pattern}' matched {count} URLs")
            
        # Continue with normal filtering
        for entry in total_entries:
            # If in testing mode and we've reached the limit, stop
            if self.TESTING and count >= self.TEST_LIMIT:
                self.logger.debug(f"Test limit reached ({self.TEST_LIMIT}), stopping sitemap filter")
                break
                
            url = entry['loc']
            pattern = rf'^{re.escape(self.base_url)}/learn/[^/]+/[^/]+$'
            
            if re.match(pattern, url):
                # Remove individual URL logging for matched URLs
                entry['loc'] = self._convert_to_json_url(entry['loc'])
                count += 1
                self.urls_matched_pattern += 1
                yield entry
            else:
                # Remove logging for non-matched URLs
                pass
        
        self.logger.info(f"Sitemap filter yielded {self.urls_matched_pattern} matching URLs out of {self.sitemap_urls_found} total")

    def start_requests(self):
        self.logger.info("Starting requests for EdxSpider")
        for request in SitemapSpider.start_requests(self):
            # Remove individual request URL logging
            self.requests_made += 1
            yield request.replace(
                url=request.url,
                dont_filter=True,
                meta={'dont_retry': False}
            )
        self.logger.info(f"Total initial requests scheduled: {self.requests_made}")

    def _parse_sitemap(self, response):
        self.sitemap_files_processed += 1
        self.logger.info(f"Parsing sitemap: {response.url} (sitemap #{self.sitemap_files_processed})")
        
        # Check if it's a sitemap index
        body = response.body
        if b'<sitemapindex' in body:
            # Count how many sitemaps are in this index
            sitemap_count = body.count(b'<sitemap>')
            self.logger.info(f"Sitemap index contains {sitemap_count} child sitemaps")
        elif b'<urlset' in body:
            # Count how many URLs are in this sitemap
            url_count = body.count(b'<url>')
            self.logger.info(f"Found urlset sitemap with {url_count} URLs")
            
            # Move sample URL logging to debug level and reduce to 2 samples
            import re
            urls = re.findall(b'<loc>([^<]+)</loc>', body)[:2]
            for url in urls:
                self.logger.debug(f"Sample URL from sitemap: {url.decode('utf-8')}")
        else:
            self.logger.warning(f"Unknown sitemap format at {response.url}")
        
        # Call parent method to ensure all functionality is preserved
        for result in super(EdxSpider, self)._parse_sitemap(response):
            yield result

    def _convert_to_json_url(self, course_url):
        """Convert course URL to corresponding page-data.json URL."""
        # Remove base URL
        path = course_url.replace(self.base_url, '')
        json_url = f"{self.base_url}/page-data{path}/page-data.json"
        # Remove individual URL conversion logging
        return json_url

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
        # Keep high-level parse logging for production
        self.logger.info(f"Parsing URL: {response.url}")
        try:
            json_data = response.json()
            course = json_data.get('result', {}).get('pageContext', {}).get('course', {})
            
            if not course:
                self.logger.warning(f"No course data found in response from {response.url}")
                return
            
            # Move detailed course info to debug level
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

            self.successful_parses += 1
            self.logger.info(f"Successfully parsed course: {course.get('title')} ({self.successful_parses} total)")
            
            yield {
                'type': 'learning_resource',
                'data': learning_resource
            }
            
        except Exception as e:
            # Keep detailed error logging for production
            self.logger.error(f"Error parsing JSON from {response.url}: {str(e)}")
            import traceback
            self.logger.error(f"Full error traceback: {traceback.format_exc()}")

    def closed(self, reason):
        """Handle spider cleanup"""
        self.logger.info(f"Spider closed: {reason}")
        self.logger.info(f"Final statistics:")
        self.logger.info(f"- Total sitemap files processed: {self.sitemap_files_processed}")
        self.logger.info(f"- Total sitemap URLs found: {self.sitemap_urls_found}")
        self.logger.info(f"- URLs matching pattern: {self.urls_matched_pattern}")
        self.logger.info(f"- Total requests made: {self.requests_made}")
        self.logger.info(f"- Successfully parsed courses: {self.successful_parses}")
        # super().closed(reason)