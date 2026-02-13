from olx_data_app.scraper import OlxShopScraper


HTML = """
<html>
  <body>
    <div>
      <a href="/d/ad/ratan-stol-ID123.html">Ратан стол</a>
      <span>120 лв.</span>
      <span>гр. София</span>
    </div>
    <div>
      <a href="https://www.olx.bg/d/ad/ratan-masa-ID456.html">Ратан маса</a>
      <span>250 лв.</span>
      <span>гр. Пловдив</span>
    </div>
  </body>
</html>
"""


def test_parse_listings_extracts_expected_fields() -> None:
    items = OlxShopScraper.parse_listings(HTML, "https://estestvenratan.olx.bg/home/")

    assert len(items) == 2
    assert items[0].title == "Ратан стол"
    assert items[0].url == "https://estestvenratan.olx.bg/d/ad/ratan-stol-ID123.html"
    assert items[0].price is None
    assert items[0].location is None
