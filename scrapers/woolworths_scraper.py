from re import search
from scrapers.base_scraper import BaseScraper
import logging
import time
import random
from urllib.parse import urljoin  # constructs an absolute URL from a base URL and a relative URL, handling edge cases
from urllib.parse import quote_plus  # URL-encodes query parameters
from utils import fuzzy_matching_select

logging.basicConfig(level=logging.DEBUG)

class WoolworthsScraper(BaseScraper):
    def __init__(self, base_url):
        # inherit initialization from BaseScraper.
        super().__init__(base_url)

    def close(self):
        """ closes browser context properly """
        super().close()  # call the parent close() method
    
    def construct_search_url(self, product_name):
        """
        constructs a search URL for Woolworths based on the given product name.
        search URL means a page that we arrived after searching for a product using a product name
        (might show multiple products in the search page)
        
        we use urllib.parse.quote_plus to URL-encode the product name so that it can be safely included 
        in the URL query parameters.
        
        Example URL:
          https://www.woolworths.com.au/shop/search/products?searchTerm=<encoded_product_name>
        """
        return f"https://www.woolworths.com.au/shop/search/products?searchTerm={quote_plus(product_name)}"

    def extract_candidates_via_locators(self):
        """
           Extracts product details from the search results using playwright locators.
           Retrieves the product name (from <a> text or <img> title), price, and URL 
           for each product tile (`wc-product-tile`).
           *tile, tags, and selectors were inspected manually on woolworths
           Returns a list of extracted product candidates.
        """
        candidates = []
        # locate all wc-product-tile elements (these represent individual products)
        tile_locator = self.driver.locator("wc-product-tile")
        count = tile_locator.count()
        logging.info(f"Found {count} wc-product-tile elements via locator.")
        for i in range(count):
            try:
                current_tile = tile_locator.nth(i)  # ith wc-product-tile (or ith product on the search page)
            
                # extract the <a> element from the current tile
                a_elements = current_tile.locator("a")
                if a_elements.count() == 0:  # no <a> tag -> no place to retrieve name and url
                    logging.warning(f"Tile {i}: No <a> element found.")
                    product_name = None
                    href = None
                else:
                    a_locator = a_elements.nth(0)
                    # try to get the visible text from the <a> element
                    product_name = a_locator.inner_text().strip()
                    # if that returns empty, try using the <img> title attribute inside the <a>
                    if not product_name:
                        img_locator = a_locator.locator("img")
                        if img_locator.count() > 0:
                            product_name = img_locator.first.get_attribute("title")
                            if product_name:
                                product_name = product_name.strip()
                            else:
                                product_name = None
                    href = a_locator.get_attribute("href")  # relative url
                   
                # extract the price using a locator
                price_elements = current_tile.locator(".product-tile-price .primary")
                if price_elements.count() > 0:
                    price_text = price_elements.first.inner_text().strip()
                else:
                    price_text = None

                # even if one missing, he's not relevant
                if product_name and href and price_text:
                    candidate = {
                        "name": product_name,
                        "price": price_text,
                        "url": urljoin(self.base_url, href)
                    }

                    # logging.info(f"Extracted candidate from tile {i}: {candidate['name']}, {candidate['price']}")
                    candidates.append(candidate)
                else:
                    logging.warning(f"Missing info in tile {i}: name: {product_name}, href: {href}, price: {price_text}")

            except Exception as e:
                logging.error(f"Error extracting candidate from tile {i}: {e}")
        return candidates
    
    def search_and_get_price(self, product_name):
        """
        searches for a product on woolworths using the product_name,
        extracts candidate information (product name and price) via locators,
        applies fuzzy matching to select the best candidate,
        and returns the candidate's name and price.

        """

        # CLOSE CURRENT CONTEXT PROPERLY
        self.close()  # this calls the inherited close() method

        # generate new user agent
        new_user_agent = self.get_random_user_agent()

        # create a fresh browser context
        self.context = BaseScraper._browser.new_context(
            user_agent=new_user_agent,
            viewport={'width': 1920, 'height': 1080}
        )
        self.driver = self.context.new_page()

        # clear cookies to simulate a fresh session for this search
        self.context.clear_cookies()

        search_url = self.construct_search_url(product_name)
        logging.info(f"Searching Woolworths for: {product_name}")
       
        search_html = self.fetch_page(search_url)

        if not search_html:
            # could not load search page at all OR the page is 'No Results' page
            logging.warning(f"Failed to fetch search results page for product: {product_name} (URL: {search_url})")
            return None, None

        # trigger lazy-loading by scrolling down and then up.
        self.driver.evaluate("window.scrollTo(0, document.body.scrollHeight)")
        time.sleep(3)
        self.driver.evaluate("window.scrollTo(0, 0)")
        time.sleep(4)

        # Get viewport size (assuming it's set in the context)
        viewport = self.driver.viewport_size
        # Pick random coordinates within the viewport
        x = random.randint(0, viewport['width'] - 1)
        y = random.randint(0, viewport['height'] - 1)
        # Move the mouse to those coordinates
        self.driver.mouse.move(x, y)

        # Extract candidates using the locator-based method
        candidates = self.extract_candidates_via_locators()
        # logging.debug(f"Extracted candidates via locators: {candidates}")
        
        # fuzzy matching 
        best_candidate = fuzzy_matching_select(product_name, candidates)
        if best_candidate:
            logging.info(f"Best match found for {product_name}: {best_candidate}")
            return best_candidate["name"], best_candidate["price"]

        logging.warning(f"No exact nor similar match for {product_name} in Woolworths")

        return None, None