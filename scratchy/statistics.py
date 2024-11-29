class SpiderStatisticsManager:
    def __init__(self):
        self.stats = {
            'items_scraped': 0,
            'pages_crawled': 0,
            'errors': 0,
            'start_time': None,
            'end_time': None
        }

    def increment_stat(self, stat_name: str, value: int = 1):
        if stat_name in self.stats:
            self.stats[stat_name] += value

    def get_stat(self, stat_name: str):
        return self.stats.get(stat_name, 0)

    def set_stat(self, stat_name: str, value):
        self.stats[stat_name] = value 