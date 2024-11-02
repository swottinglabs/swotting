import re
from datetime import datetime
from urllib.parse import parse_qs, urlparse
from uuid import uuid4
import bs4

from .base_scraper import BaseScraper
from scrapy.spiders import SitemapSpider

# Improvements:
# Dynamically set the language based on the written out language on the website then get the iso code from that 
# Check Archived courses: https://www.edx.org/learn/social-science/mcgill-social-learning-for-social-impact
# The is_free and is_limited_free seems to work but needs to be verified on more examples

class EdxScraper(BaseScraper, SitemapSpider):
    name = 'edx_scraper'
    base_url = 'https://www.edx.org'
    sitemap_urls = [ base_url + '/sitemap-0.xml']

    # Constants
    IS_FREE = False
    IS_LIMITED_FREE = True
    LANGUAGE = ['en']
    FORMAT = "Video"
    

    def __init__(self, platform_id=None, *args, **kwargs):
        BaseScraper.__init__(self, platform_id, *args, **kwargs)
        SitemapSpider.__init__(self, *args, **kwargs)

    def sitemap_filter(self, entries):
        # Invalid: A url with only one '/' after the learn is a category page e.g. https://www.edx.org/learn/media-law
        # Invalid: A url with something else than learn after the base_url is an invalid url e.g. https://www.edx.org/certificates/professional-certificate/ucsandiegox-virtual-reality-app-development
        # Invalid: A two letter language iso code after the base is invalid for now e.g. https://www.edx.org/es/certificates/professional-certificate/ucsandiegox-virtual-reality-app-development
        # Valid: A url with 3 or more '/' after the base_url is a course e.g. https://www.edx.org/learn/statistics/university-of-adelaide-mathtrackx-statistics

        for entry in entries:
            url = entry['loc']
            
            pattern = rf'^{re.escape(self.base_url)}/learn/[^/]+/[^/]+$'
            if re.match(pattern, url):
                entry['loc'] = self._convert_to_json_url(entry['loc'])
                yield entry

    def start_requests(self):
        for request in SitemapSpider.start_requests(self):
            url = request.url

            yield request.replace(url=url)

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

    def parse(self, response):
        try:
            json_data = response.json()
            course = json_data.get('result', {}).get('pageContext', {}).get('course', {})
            active_run = course.get('activeCourseRun', {})
            clean_url = response.url.replace('page-data/', '').replace('page-data.json', '')
            
            seat_info = self._get_seat_info(
                active_run.get('seats', []),
                enrollment_start=active_run.get('enrollmentStart'),
                enrollment_end=active_run.get('enrollmentEnd')
            )
            
            course_data = {
                'name': course.get('title'),
                'url': clean_url,
                'scraped_timestamp': datetime.now().isoformat(),
                'uuid': str(uuid4()),
                'platform': 'edx',
                'description': self._clean_html_description(course.get('fullDescription')),
                'html_description': course.get('fullDescription'),
                'platform_course_id': course.get('uuid'),
                'language': course.get('language', self.LANGUAGE),
                'is_deleted': not active_run.get('isEnrollable', True),
                'is_free': seat_info['is_free'],
                'is_limited_free': seat_info['is_limited_free'],
                'dollar_price': seat_info['dollar_price'],
                'has_certificate': seat_info['has_certificate'],
                'short_description': self._clean_html_description(course.get('shortDescription')),
                'platform_last_update': course.get('updatedAt'),
                'platform_thumbnail_url': course.get('originalImage', {}).get('src'),
                'duration_h': self._calculate_duration_hours(active_run),
                'reviews_count': course.get('courseReview', {}).get('reviewCount'),
                'reviews_rating': course.get('courseReview', {}).get('avgCourseRating'),
                'level': course.get('levelType', None),
                'short_description': self._clean_html_description(course.get('shortDescription')),
                'enrollment_count': course.get('enrollmentCount', None),
                'is_active': active_run.get('isEnrollable', True),
                'tags': self._get_course_tags(course),
                'format': self.FORMAT
            }

            creators = [
                {
                    'platform_id': owner.get('uuid'),
                    'name': owner.get('name'),
                    'platform_thumbnail_url': owner.get('logoImageUrl')
                }
                for owner in course.get('owners', [])
            ]

            print(course_data)
            
        except Exception as e:
            self.logger.error(f"Error parsing JSON from {response.url}: {str(e)}")
