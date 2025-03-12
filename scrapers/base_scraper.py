# for browser control to render dynamic HTML content;
# using sync api rather than async api for simplicity
from playwright.sync_api import sync_playwright
import logging  # to log events and errors for debugging
import random  # to randomize user-agent selection
import time  # to add delays between requests
from utils import USER_AGENTS

class BaseScraper:
    _playwright = None  # class-level shared playwright instance (due to async loop)
    _browser = None  # shared browser instance

    def __init__(self, base_url):
        #  stores the main URL of the website we're scraping, not used here, a placeholder for subclasses
        self.base_url = base_url
        
        # set up logging for debugging and tracking issues.
        self.setup_logging()

        # http headers with a random user-agent
        self.request_http_headers = {
            'User-Agent': self.get_random_user_agent()
        }

        # initialize the playwright driver (browser/ context)
        self.init_driver()
    
    def init_driver(self):
        """
        initializes playwright and the browser instance only once.
        each scraper gets its own browser context (isolated session).

        """
        # ensure playwright and browser are initialized only once
        if not BaseScraper._playwright:
            # start playwright (allow interaction with browesers)
            BaseScraper._playwright = sync_playwright().start()  
            # launch a headless (so it'll not open a window) firefox browser session
            BaseScraper._browser = BaseScraper._playwright.firefox.launch(headless=True)
        
        # create an **isolated context** for this scraper instance
        self.context = BaseScraper._browser.new_context(
            user_agent=self.request_http_headers['User-Agent'],
            viewport={'width': 1920, 'height': 1080}
        )
        # open a new page (browser tab) within this context
        self.driver = self.context.new_page()

    def close(self):
        """
        closes the browser context for this scraper instance.
        
        """
        try:
            self.context.close()
        except Exception as e:
            logging.error(f"Error closing browser context: {e}")

    @classmethod
    def shutdown_playwright(cls):
        """
        closes the shared browser and Playwright instance.
        """
        try:
            if cls._browser:
                cls._browser.close()
                cls._browser = None
        except Exception as e:
            logging.error(f"Error closing browser: {e}")

        try:
            if cls._playwright:
                cls._playwright.stop()
                cls._playwright = None
        except Exception as e:
            logging.error(f"Error stopping playwright: {e}")

    def get_random_user_agent(self):
        """
        returns a random user-agent string from a predefined list.
        rotating the User-Agent helps avoid anti-scraping blocks.
        """

        if not USER_AGENTS:
            logging.warning("USER_AGENTS list is empty, using a default User-Agent.")
            return "Mozilla/5.0 (Windows NT 6.1; WOW64; rv:30.0) Gecko/20100101 Firefox/30.0"
        
        return random.choice(USER_AGENTS)
    
    def setup_logging(self):
        """
        configures the logging settings to output informational messages.
        info/warning/error/critical

        *CHANGE LATER - set to INFO after completing Debugging
        """
        logging.basicConfig(level=logging.DEBUG)
    
    def fetch_page(self, url, wait_until="load", timeout=30):
        """
        uses playwright to navigate to the given URL, 
        optionally waiting until some event is fired. Default is 'load'
        mimics human behavior by introducing a random delay.

        returns:
            str: the HTML content of the page after dynamic content has been rendered.
        """
        try:
            # navigate to the URL. the timeout is specified in milliseconds
            # if the page takes longer than timeout it will throw a timeout error   
            
            if wait_until:
                self.driver.goto(url, timeout=timeout * 1000, wait_until=wait_until)
            else:
                self.driver.goto(url, timeout=timeout * 1000)
            
            # delay to mimic human browsing behavior
            sleep_time = random.uniform(2, 8)
            logging.info(f"Sleeping for {sleep_time:.2f} seconds before the next request.")
            time.sleep(sleep_time)
            
            # return the full HTML content of the page
            return self.driver.content()
        except Exception as e:
            logging.error(f"(fetch_page) Error fetching {url}: {e}")
            return None

    def parse_page(self, html):
        """
        This method should be implemented by subclasses
        Parameters:
            html (str): The HTML content of a webpage
        Raises:
            NotImplementedError: if the subclass does not override this method
        """
        raise NotImplementedError("Subclasses must implement the parse_page method. Define how to extract data from HTML.")