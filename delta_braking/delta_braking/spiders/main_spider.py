from scrapy.spider import BaseSpider
from scrapy.selector import HtmlXPathSelector

class MainSpider(BaseSpider):
  name = "main"
  allowed_domains = ["delta-braking.com"]
  start_urls = [
    "http://delta-braking.com/htm/brakepads.php?selectedBp=DB2220",
  ]

  def parse(self, response):
    sel = HtmlXPathSelector(response)
    table = sel.select('//div[@id="containermain"]/table')
    print "***\n\n\n"
    print table[0].doc
    print "\n\n\n***"

    filename = response.url.split("/")[-1]
    filename = filename.split("?")[0]
    open(filename, "wb").write(str(table.extract()))
