from bs4 import BeautifulSoup  # parses and extracts data from HTML pages
from datetime import datetime  # to timestamp scraped data
import logging
from utils import SKU_URL_MAPPING
from scrapers.base_scraper import BaseScraper

logging.basicConfig(level=logging.DEBUG)

class RejectShopScraper(BaseScraper):
    def __init__(self, base_url):
        # initialize the BaseScraper (the base_url here is a placeholder for future adjustments, 
        # # e.g. dynamic URL search)
        super().__init__(base_url)

    def close(self):
        """ closes browser context properly """
        super().close()  # call the parent close() method
    
    def construct_product_url(self, sku):
        """
        constructs the full URL for a product given its SKU.
        
        Note: currently we look up the SKU in a predefined mapping.
        this implementation can be replaced with a dynamic search mechanism to retrieve the product URL.
        the method returns the product URL regardless of how it's obtained, keeping the interface consistent.
        """
        try:
            return SKU_URL_MAPPING[sku]
        except KeyError:
            logging.error(f"SKU {sku} not found in the URL mapping.")
            return None
    
    def parse_page(self, html, sku):
        """
        parses the HTML content of a product page to extract details.
        Parameters:
            html (str): the HTML content of the product page.
            sku (str): the SKU parameter provided for reference.
        Returns:
            dict: a dictionary containing the SKU, product name, price, and current date.
        """
        soup = BeautifulSoup(html, 'html.parser')
        try:
            # Note: The selectors below (e.g., data-testid for product title, class names for SKU and price) 
            # were determined by manually inspecting the website's HTML structure (which is rendered).
            # It might be worth to check if a Machine Learning (NLP) approach would work to automate this (if there's a lot of websites to scrape)
            
            # extract product name using the data-testid attribute
            product_name_element = soup.find("h1", {"data-testid": "product-title"})
            product_name = product_name_element.get_text(strip=True) if product_name_element else "Unknown Product"
            logging.debug(f"Extracted product name: {product_name}")
            
            # extract the SKU from the <p> tag with class "pdp-sku except-phone"
            # we extract the SKU even though we get it as a parameter for validation
            sku_element = soup.find("p", class_="jsx-ac1f85233799a587 pdp-sku except-phone")            
            if sku_element:
                sku_text = sku_element.get_text(strip=True)
                # Remove the "SKU:" prefix and extra spaces
                extracted_sku = sku_text.replace("SKU:", "").strip()
            else:
                extracted_sku = "SKU Not Found"
            logging.debug(f"Extracted SKU: {extracted_sku}")
            
            # extract the product price from the <div> with class "product-price"
            price_container = soup.find("div", class_="jsx-c5b8eb4ab4d5ad55 product-price")
            if price_container:
                # combine the text from all spans (e.g., "$", "3", ".45") and remove extra spaces
                raw_price_text = price_container.get_text(strip=True)
                product_price = raw_price_text
            else:
                product_price = "Price Not Found"
            logging.debug(f"Extracted product price: {product_price}")
            
            # get the current date in YYYY-MM-DD format
            current_date = datetime.now().strftime("%Y-%m-%d")
            
            return {
                "SKU": extracted_sku,
                "Product Name": product_name,
                "Price": product_price,
                "Date": current_date
            }
        except Exception as e:
            logging.error(f"Error parsing HTML for SKU {sku}: {e}")
            return None
    
    def scrape_product_by_sku(self, sku):
        """
        scrapes the product page for a given SKU and returns the extracted data.
        Parameters:
            sku (str): The product SKU to scrape.
        Returns:
            dict: The extracted product details or None if scraping fails.
        """
        product_url = self.construct_product_url(sku)
        if not product_url:
            logging.error(f"No valid product URL found for SKU {sku}")
            return None
        logging.info(f"Scraping product URL: {product_url}")
        
        # fetch the page content using the BaseScraper fetch_page method
        html_content = self.fetch_page(product_url)
        if html_content:
            product_data = self.parse_page(html_content, sku)
            if product_data:
                logging.info(f"Successfully scraped data for SKU {sku}")
            else:
                logging.error(f"Failed to parse product data for SKU {sku}")
            return product_data
        else:
            logging.error(f"Failed to fetch page for SKU {sku}")
            return None
