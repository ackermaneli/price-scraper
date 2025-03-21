"""
This file provide helper functions / constants for the scrapers 
such as user-agent/sku's mapping/json file construction

"""
import logging
from rapidfuzz import fuzz, process  # for fuzzy matching
import json
import os
import shutil

logging.basicConfig(level=logging.DEBUG)

# randomizing the user-agent makes requests more reliable because, without it,
# requests might send a generic identifier that websites can detect as a bot
# note that this list composed of up-to-date, modern browsers (else it'll cause block problems, probably)
USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:115.0) Gecko/20100101 Firefox/115.0",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:116.0) Gecko/20100101 Firefox/116.0",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:117.0) Gecko/20100101 Firefox/117.0",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:118.0) Gecko/20100101 Firefox/118.0",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:119.0) Gecko/20100101 Firefox/119.0"
]



# sku -> URL of the product with this sku
SKU_URL_MAPPING = {
    "30061292": "https://www.rejectshop.com.au/p/palmolive-naturals-shampoo-coconut-cream-350ml",
    "30113527": "https://www.rejectshop.com.au/p/whiskas-jellymeat-400g",
    "30115549": "https://www.rejectshop.com.au/p/twisties-party-bag-cheese-270g",
    "30043588": "https://www.rejectshop.com.au/p/quilton-aloe-vera-tissue-3ply-95pk",
    "30087959": "https://www.rejectshop.com.au/p/jif-surface-cleaner-lemon-scent-500ml",
}

def fuzzy_matching_select(target_name, candidates, threshold=70):
    """
    uses RapidFuzz to find the best fuzzy match for `target_name` among the given `candidates`.
    each candidate is expected to be a dict with a "name" key.
    
    target_name: str, the string to match against candidate names
    candidates: list of dict, each with {"name": <product_name>, "url": <product_url>, ...}
    threshold: int, minimum similarity score to accept a match
    returns: dict or None
             - The candidate with the highest similarity to target_name if above threshold
             - None if no good match is found
    """
    if not candidates:
        return None
    
    try:
        # extract just the product names
        candidate_names = [c["name"] for c in candidates]
    
        # extractOne returns (best_match_name, score, index)
        best_match_name, best_score, best_idx = process.extractOne(
            query=target_name, 
            choices=candidate_names, 
            scorer=fuzz.WRatio  # in high-level description: a composite approach that tries multiple strategies
        )
    
        if best_score >= threshold:
            return candidates[best_idx]  # Return the dict for the best match
        else:
            return None
    except Exception as e:
        logging.error(f"Error during fuzzy matching: {e}")
        return None

def save_to_json(data, filename):
    """
    appends new data to an existing JSON file or creates a new one if it doesn't exist
    """
    existing_data = []
    if os.path.exists(filename):
        try:
            with open(filename, "r", encoding="utf-8") as f:
                existing_data = json.load(f)

            if isinstance(existing_data, dict):
                existing_data = [existing_data]  # Convert single dictionary into a list
            elif not isinstance(existing_data, list):
                raise ValueError(f"Unexpected JSON structure in {filename}")  # Force handling

        except (json.JSONDecodeError, ValueError) as e:
            logging.error(f"Error reading {filename}: {e}. Creating a backup and resetting.")

            # create a backup **only if the file has valid content**
            if os.path.getsize(filename) > 0:  # avoid backing up empty files
                backup_filename = f"backup_{filename}"
                shutil.copy(filename, backup_filename)
                logging.info(f"Backup created: {backup_filename}")

            existing_data = []  # Reset to an empty list

    # append new data and write back
    existing_data.extend(data)
    with open(filename, "w", encoding="utf-8") as f:
        json.dump(existing_data, f, indent=4, ensure_ascii=False)
    
    logging.info(f"Data successfully saved to {filename}")

def calculate_price_difference(price1, price2):
    """
    calculates the absolute price difference between two prices
    """
    
    price1 = float(price1.replace("$", "").strip()) if price1 and isinstance(price1, str) and "$" in price1 else None
    price2 = float(price2.replace("$", "").strip()) if price2 and isinstance(price2, str) and "$" in price2 else None
    
    if price1 is not None and price2 is not None:
        return f"${abs(price1 - price2):.2f}"
    
    return "N/A"

def load_skus_from_file(filename):
    """
    reads SKUs from a text file, ignoring empty lines and stripping spaces
    """
    try:
        with open(filename, "r", encoding="utf-8") as f:
            skus = [line.strip() for line in f if line.strip()]
        return skus
    except FileNotFoundError:
        print(f"Error: {filename} not found.")
        return None































# def remove_extra_descriptors(product_name: str):
#     """
#     simplify the product name by removing extra descriptive words
#     and keeping only critical tokens like brand (first word) and
#     any token containing a digit (sizes, pack counts, etc.).

#     those assumptions are still assumptions - they're not facts, thus, it's not true for all cases.

#     returns the simplified product name
#     """
#     if not product_name:
#         return ""

#     tokens = product_name.split()
#     if not tokens:
#         return ""

#     simplified_tokens = []

#     # keep the first token (brand guess)
#     simplified_tokens.append(tokens[0])

#     # keep any token that contains a digit (e.g. 350mL, 500g, x24, 2L, etc.)
#     for token in tokens[1:]:
#         if any(char.isdigit() for char in token):
#             simplified_tokens.append(token)

#     # Join them back into a simplified product name
#     return " ".join(simplified_tokens)