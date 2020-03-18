import pandas as pd
import requests
from bs4 import BeautifulSoup
from splinter import Browser
from time import sleep

def init_browser():
    executable_path = {"executable_path": "/usr/local/bin/chromedriver"}
    return Browser("chrome", **executable_path, headless=False)

def scrape():
    # initialize return variable
    mars_data = {}

    # ## NASA Mars News

    nasa_mars_url = "https://mars.nasa.gov/news/"

    browser = init_browser()
    browser.visit(nasa_mars_url)
    sleep(5)
    soup = BeautifulSoup(browser.html, 'html.parser')

    news_title = soup.find_all("div", class_="content_title")[0].get_text()
    news_paragraph = soup.find_all("div", class_="article_teaser_body")[0].get_text()

    # close browser after scraping
    browser.quit()


    # ## JPL Mars Space Images - Featured Image

    jpl_url = "https://www.jpl.nasa.gov/spaceimages/?search=&category=Mars"

    browser = init_browser()
    browser.visit(jpl_url)

    browser.click_link_by_partial_text("FULL IMAGE")
    sleep(5) # add in lag to allow loading
    browser.click_link_by_partial_text("more info")
    browser.click_link_by_partial_text(".jpg")

    featured_image_url = browser.url

    # close browser after scraping
    browser.quit()


    # ## Mars Weather

    twitter_url = "https://twitter.com/marswxreport?lang=en"

    # use requests library to read in Twitter page
    twitter_page = requests.get(twitter_url)
    soup = BeautifulSoup(twitter_page.content, 'html.parser')

    # find first tweet and clean it
    first_tweet = soup.find_all("div", class_="js-tweet-text-container")[0]
    mars_weather_tweet = first_tweet.find("p").get_text().replace("\n","").split("pic.twitter.com")[0]


    # ## Mars Facts

    mars_facts_url = "https://space-facts.com/mars/"

    # use pandas to read table directly from URL
    mars_facts_df = pd.read_html(mars_facts_url)[1]

    # clean up resulting DataFrame
    mars_facts_df.columns = ["description", "value"]
    mars_facts_df["description"] = mars_facts_df["description"].str.replace(":","")
 
    # convert to HTML string
    mars_facts_df.set_index("description", inplace=True)
    mars_facts_html = mars_facts_df.to_html()


    # ## Mars Hemispheres

    usgs_url = "https://astrogeology.usgs.gov/search/results?q=hemisphere+enhanced&k1=target&v1=Mars"

    browser = init_browser()
    browser.visit(usgs_url)

    hemispheres = ["Cerberus","Schiaparelli","Syrtis","Valles"]
    hemisphere_image_urls = []

    # loop through each hemisphere and scrape the data
    for hemi in hemispheres:
        new_dict = {}

        browser.click_link_by_partial_text(hemi)
        usgs_html = browser.html
        soup = BeautifulSoup(usgs_html, 'html.parser')
        new_dict["title"] = soup.find("h2").get_text().replace("Enhanced","").strip()
        new_dict["img_url"] = soup.find_all("div", class_="downloads")[0].find_all("a")[0]["href"]
        hemisphere_image_urls.append(new_dict)
        
        # go back to original page with all the hemispheres
        browser.back()

    # close browser after scraping
    browser.quit()

    mars_data = {
        "nasa_mars_title":news_title,
        "nasa_mars_paragraph":news_paragraph,
        "jpl_image":featured_image_url,
        "mars_latest_tweet": mars_weather_tweet,
        "mars_facts":mars_facts_html,
        "mars_hemisphere":hemisphere_image_urls
    }

    return mars_data

if __name__ == "__main__":
    print(scrape())