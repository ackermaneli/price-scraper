"""
main entry point
"""

# TO DO - should i add args / kwargs?
# how should one look at it from github and run?
# maybe a shell sequencial running?

import logging
from utils import save_to_json, calculate_price_difference, load_skus_from_file
from scrapers.base_scraper import BaseScraper as BS
from scrapers.rejectshop_scraper import RejectShopScraper
from scrapers.woolworths_scraper import WoolworthsScraper

logging.basicConfig(level=logging.INFO)

def main():
    # Initialize both scrapers
    rejectshop_scraper = RejectShopScraper("https://www.rejectshop.com.au")
    woolworths_scraper = WoolworthsScraper("https://www.woolworths.com.au")

    phase1_data = []
    phase2_data = []

    search_counter = 0
    
    try:
        skus = load_skus_from_file("skus.txt")
        if not skus:
            logging.info("no SKUs found in skus.txt. Exiting.")
            return

        for sku in skus:
            # due to anti-bot measures from woolworths we restart playwright every 3 searches
            if search_counter >= 3:
                logging.info("Restarting playwright to reset anti-bot tracking...")

                # close old scrapers before restarting
                rejectshop_scraper.close()
                woolworths_scraper.close()
                BS.shutdown_playwright()
                
                # reinitialize scrapers
                rejectshop_scraper = RejectShopScraper("https://www.rejectshop.com.au")
                woolworths_scraper = WoolworthsScraper("https://www.woolworths.com.au")

                search_counter = 0  # reset counter

            # **phase 1: get data from the reject shop**
            rs_data = rejectshop_scraper.scrape_product_by_sku(sku)
            if not rs_data:
                logging.info(f"Skipping SKU {sku}: No data found.")
                continue  # Skip this SKU if we couldn't retrieve data

            # Save Phase 1 data
            phase1_data.append(rs_data)

            # **Phase 2: find and compare with woolworths**
            product_name_rs = rs_data["Product Name"]
            candidate_name, price_woolworths = woolworths_scraper.search_and_get_price(product_name_rs)
        
            price_diff = calculate_price_difference(rs_data["Price"], price_woolworths)

            # construct final data for phase 2
            comparison_data = {
                "SKU": sku,
                "Product Name The Reject Shop": product_name_rs,
                "Price_RejectShop": rs_data["Price"],
                "Product Name Woolworths": candidate_name,
                "Price_Woolworths": price_woolworths if price_woolworths else "Not Found",
                "Price Difference": price_diff,
                "Date": rs_data["Date"]
            }
            phase2_data.append(comparison_data)
    
        # save as JSON
        save_to_json(phase1_data, "phase1_results.json")
        save_to_json(phase2_data, "phase2_results.json")

    finally:
        # close scrapers individual browser contexts
        rejectshop_scraper.close()
        woolworths_scraper.close()
        logging.info("closed scrapers successfully (browsers)")

        if hasattr(BS, "shutdown_playwright"):
            BS.shutdown_playwright()
            logging.info("shutdown playwright went successfully")
        else:
            print("shutdown_playwright does NOT exist in BaseScraper!")

if __name__ == '__main__':
    main()