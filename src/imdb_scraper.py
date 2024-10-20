import time
import warnings

import pandas as pd
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from tqdm import tqdm

from src.constants import IMDB_TOP_1000_URL
from src.utils import *

warnings.filterwarnings("ignore")


def initialize_chrome_driver():
    """
    Initialize a Chrome WebDriver and navigate to the IMDb Top 1000 movies page.

    This function sets up a Chrome WebDriver instance, navigates to the IMDb Top 1000
    movies page, and simulates scrolling down the page to load more content. It then
    returns the initialized WebDriver instance.

    Returns:
    webdriver.Chrome: The initialized Chrome WebDriver instance.
    """
    driver = webdriver.Chrome()
    time.sleep(1)   # Wait for 1 second before proceeding
    driver.get(IMDB_TOP_1000_URL)   # Navigate to the specified URL
    time.sleep(1)   # Wait for 1 second to ensure the page has loaded
    time.sleep(1)   # Wait for 1 second before proceeding

    # Find the body element of the page using CSS selector
    body = driver.find_element(By.CSS_SELECTOR, 'body')

    # Simulate pressing the PAGE_DOWN key to scroll down the page
    body.send_keys(Keys.PAGE_DOWN)
    time.sleep(1)   # Wait for 1 second before proceeding
    body.send_keys(Keys.PAGE_DOWN)   # Scroll down the page again
    time.sleep(1)   # Wait for 1 second before proceeding
    body.send_keys(Keys.PAGE_DOWN)   # Scroll down the page again
    return driver


def get_page_elements(items):
    """
    Extract and return movie details from a list of movie elements.

    This function iterates over a list of movie elements, extracts various pieces
    of information for each movie (title, rating, introduction, vote count, Metascore, year,
    duration, and age restriction), and appends the extracted data to a list.

    Parameters:
    items (list): A list of movie elements to extract information from. Each element
                  should be a WebElement object containing movie details.

    Returns:
    list: A list of lists where each inner list contains the extracted details for a movie.
          The details include title, rating, vote count, Metascore (or None if not available),
          year, duration, age restriction, and introduction.
    """
    output_list = []

    # Iterate over each movie element in the item_list
    for movie in tqdm(items):
        # Extract the movie title using the class name 'ipc-title__text'
        title = movie.find_element(By.CLASS_NAME, 'ipc-title__text').text
        rating = movie.find_element(By.CLASS_NAME, 'ipc-rating-star--rating').text
        intro = movie.find_element(By.CLASS_NAME, 'ipc-html-content-inner-div').text
        vote_count = movie.find_element(By.CLASS_NAME, 'ipc-rating-star--voteCount').text

        # Try to extract the Metascore if available, handle exceptions such as if it is a new movie if not found
        try:
            meta_score = movie.find_element(By.CSS_SELECTOR, ".metacritic-score-box").text
        except:
            meta_score = None

        # Extract the year, duration, and age restriction using the CSS selector '.dli-title-metadata'
        year, duration, age_restriction = movie.find_element(By.CSS_SELECTOR, ".dli-title-metadata").text.split("\n")

        # Append the extracted data to the output list as a list of values
        output_list.append([title, rating, vote_count, meta_score, year, duration, age_restriction, intro])
    return output_list


chrome_driver = initialize_chrome_driver()
# Find all elements with the class name "ipc-metadata-list-summary-item"
item_list = chrome_driver.find_elements(By.CLASS_NAME, "ipc-metadata-list-summary-item")
output = get_page_elements(item_list)

# Create a pandas dataframe
movies = pd.DataFrame(output, columns=["title", "rating", "vote_count", "meta_score", "year", "duration",
                                       "age_restriction", "intro"])

# Cleaning 'year' column
movies['year'] = movies['year'].str.extract('(\d+)').astype(int)

# Cleaning 'duration' column
movies['duration'] = movies['duration'].apply(lambda x: convert_to_minutes(x))

# Cleaning 'metascore' column
movies['meta_score'] = movies['meta_score'].str.extract('(\d+)')
# convert it to float and if there are dashes turn it into NaN
movies['meta_score'] = pd.to_numeric(movies['meta_score'], errors='coerce')

# Cleaning 'vote_count' column
movies['vote_count'] = movies['vote_count'].apply(lambda x: convert_to_integer(x))

# Cleaning 'rating' column
movies['rating'] = movies['rating'].astype(float)

# Cleaning 'title' column
movies['title'] = movies['title'].apply(lambda x: remove_prefix(x))

# Save data to a file
movies.to_csv('../data/movies.csv', index=False)

# Close the driver
chrome_driver.close()
