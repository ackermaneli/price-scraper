# Products Scraper & Price Comparison

This project is a **web scraping tool** that extracts product prices from two websites and compares them.  
It is designed to scrape data from **The Reject Shop** and **Woolworths**, matching products by name and reporting the price difference.

---

## Features

- **Phase 1:** Scrapes product details (SKU, name, and price) from **The Reject Shop**.
- **Phase 2:** Searches for the same product on **Woolworths** and compares prices.
- Saves results in **JSON format**.
- Handles **anti-scraping measures** like **randomized user agents**, **retry and reconnect mechanism**, and **delays**.
- Uses **OOP principles** for modular and reusable code.

---

## Project Structure

```
priceScraper/
│── scrapers/
│   ├── base_scraper.py        # Base scraper with shared logic
│   ├── rejectshop_scraper.py  # Scraper for The Reject Shop
│   ├── woolworths_scraper.py  # Scraper for Woolworths
│── notebooks/
│   ├── scraper_experiments.ipynb  # Jupyter notebook for testing
│── data/                    # (Empty) Directory for future use
│── phase1_results.json       # Output of Phase 1
│── phase2_results.json       # Output of Phase 2
│── skus.txt                  # List of SKUs to scrape
│── utils.py                   # Helper functions (user agents, file handling, etc.)
│── scraper.py                 # Main script
│── requirements.txt           # Dependencies (TBD)
│── README.md                  # This file
│── .gitignore                 # Ignore unnecessary files
```

---

## Setup & Installation

### **🔹 Prerequisites**
- Python **3.11** (recommended)
- **pip** or **micromamba** for managing dependencies
- **Google Chrome** or **Firefox** (for Playwright)
- **Note:** You may encounter **HTTP2 errors** using Chrome.  
  One way to handle it is by adding this argument:  
  ```python
  args=['--disable-http2']
  ```
  in the **Playwright `goto` function**.

---

### **🔹 Install Dependencies**

```sh
pip install -r requirements.txt
```

or if using **micromamba**:

```sh
micromamba install --file requirements.txt
```

---

### **🔹 Install Playwright Browsers**

```sh
playwright install
```

---

## Usage

### **Step 1: Add SKUs to `skus.txt`**
Add a list of SKUs (one per line) that you want to scrape from **The Reject Shop**.

Example:
```
30061292
30113527
30115549
```

---

### **Step 2: Run the Scraper**
```sh
python scraper.py
```
The script will:
1. Scrape each SKU from **The Reject Shop**.
2. Search for a matching product on **Woolworths**.
3. Save results in **JSON files**.

---

## Example Output

### **🔹 Phase 1 (`phase1_results.json`)**
```json
[
    {
        "SKU": "30061292",
        "Product Name": "Palmolive Shampoo Intensive Coconut Cream 350mL",
        "Price": "$3.75",
        "Date": "2025-03-12"
    }
]
```

### **🔹 Phase 2 (`phase2_results.json`)**
```json
[
    {
        "SKU": "30061292",
        "Product Name The Reject Shop": "Palmolive Shampoo Intensive Coconut Cream 350mL",
        "Price_RejectShop": "$3.75",
        "Product Name Woolworths": "Palmolive Shampoo Naturals Intensive Moisture 350ml",
        "Price_Woolworths": "$3.00",
        "Price Difference": "$0.75",
        "Date": "2025-03-12"
    }
]
```

---

## How It Works

### **🔹 Scraper Architecture**
- **`BaseScraper`** (Parent class):  
  Handles **Playwright setup**, **fetching pages**, and **user agents**.
- **`RejectShopScraper`**:  
  Scrapes product details from **The Reject Shop**.
- **`WoolworthsScraper`**:  
  Searches for the product on **Woolworths** and extracts price.

### **🔹 Anti-Bot Measures**
- **Random User-Agent** rotation
- **Delays** between requests
- **Browser restarts** every few searches

---

## Notes

- This script is for **educational purposes**.
- The **website structures** might change over time, requiring updates.
- **Respect website terms of service** when scraping.

---

## Author

- **Eli Ackerman**


