from scrapy.dupefilters import RFPDupeFilter
class CustomFilter(RFPDupeFilter):
    def request_seen(self, request):
        return False