# dentalstall-scraper

## Overview

`dentalstall-scraper` is a web scraping tool designed to extract data from the Dental Stall website. It collects information such as product title, prices, and images, and stores it in a structured format for further analysis.

## Features

- Scrapes product details including title, price, and images.
- Stores scraped data in a JSON file (Configurable storage support is there).
- Configurable settings for target URLs and output file paths.

# Pre Requisites

1. Make sure you have redis installed on your system.

## Installation

To install the necessary dependencies, run:

```bash
pip install pipenv
pipenv install --dev
```

# Start server

To start the server once dependencies are installes run:

```bash
uvicorn app.main:app --reload --port 9800
```

## Configuration

You can configure the scraper by editing the `config.py` file. Here you can set the target URLs and output file paths.

## Usage and example

<!-- ```bash -->

1. Endpoint -> http://localhost:9800/v1/scrape/

2. Request Headers should have following header for api authentication:
   Authorization: token

3. Body:
   ```bash
   {
       "page_limit": 1,
       "proxy": ""
   }
   ```
4. Params Descriptions ->
   page limit is optional (in that default is `1`) which defines the number of pages to scrape.
   Proxy is optional (in that case will scrape data from 'www.dentalstall.com/shop/') which defines any particular proxy page to target inside the dentalstall website.

5. Proxy handlings have been done for the following cases:

   a. Any particular category proxy -> `product-category/corona-safety/covid-19-test-kits/`

   b. Any filters applied proxy -> `product-category/corona-safety/covid-19-test-kits/?min_price=914&max_price=920`

   c. Any particular start page proxy -> `shop/page/4/` (will start scrapping from page 4 till limit)

   d. Any particular product detail page proxy handling -> `product/angelus-interlig-single-patient-strip/`

6. Response:

   ```bash
   {
       "message": "Scraping completed successfully",
       "scraped_products_count": 48,
       "created_new_products_count": 0,
       "updated_existing_products_count": 0
   }
   ```

7. Also a notification on console can be seen once request is processed.
