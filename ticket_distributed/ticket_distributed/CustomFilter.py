from scrapy_redis.dupefilter import RFPDupeFilter
class CustomFilter(RFPDupeFilter):
    def request_seen(self, request):
        return False