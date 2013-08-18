from scrapy.spider import BaseSpider
from scrapy.selector import HtmlXPathSelector, XPathSelector
from scrapy.http import Request
from scrapy.utils.python import unicode_to_str
import libxml2

class MainSpider(BaseSpider):
  name = "main"
  allowed_domains = ["delta-braking.com"]
  base_url = "http://delta-braking.com/htm/brakepads.php?selectedBp="
  start_urls = [
    "{base_url}{break_pad_name}".format(base_url=base_url,
                                        break_pad_name="DB1110"),
  ]

  def _generate_next(self, sel, brake_pad_name):
    brake_pads = sel.select("table/tr/td/form/table/tr/td/select/option/text()")
    for i, p in enumerate(brake_pads):
      name = p.extract()
      if name != brake_pad_name:
        continue
      try:
        return "{base_url}{break_pad_name}".format(base_url=self.base_url,
                                        break_pad_name=brake_pads[i+1].extract())
      except IndexError:
        pass

  def parse(self, response):
    sel = XPathSelector(response)
    container_main = sel.select('//div[@id="containermain"]')
    table = container_main.select('table/tr/td/table')[0]

    print "Encoding: {}".format(response.encoding)
    unicoded_str = table.extract().encode('utf-8')

    doc = libxml2.htmlParseDoc(unicoded_str, 'utf-8')
    tr_nodes = doc.xpathEval("/html/body/table/tr")
    first = tr_nodes[0]
    first.parent.setProp('width', "536")
    first.setProp('bgcolor', "#A0A0A0")
    first.last.setProp('width', "60")
    first.last.setContent("")
    first.last.newChild(None, "strong", "F=Front R=rear\nFL=front left FR=front right")

    for i, node in enumerate(tr_nodes):
      children = node.xpathEval("td")
      for j, child in enumerate(children):
        if len(children) == 1:
          continue
        if (i != 0 and j == 4) or j == 0:
          child.unlinkNode()
          child.freeNode()

    brake_pad_name = unicode(response.url.split("=")[-1])
    open("{0}.html".format(brake_pad_name), "wb").write(str(doc))

    next_url = self._generate_next(container_main, brake_pad_name)
    yield Request(next_url, callback=self.parse)
