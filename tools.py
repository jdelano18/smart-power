from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
import time
from selenium.webdriver.chrome.service import Service
import requests
from bs4 import BeautifulSoup
import json
import pandas as pd


def closeCookies(driver):
    """
    finds the accept cookies window and clicks if it is there
    """
    try:
        driver.find_element(By.XPATH, "/html/body/div[2]/div[2]/div/button").click()
    except:
        print("No cookies window. Continue...")

    time.sleep(5)

def loadMoreHomes(driver):
    """
    keeps clikcing on the load more homes button on a page until theres no more
    """
    more_homes = True
    while more_homes:
        try:
            load_more = driver.find_element(By.XPATH, '//button[normalize-space()="Load more homes"]')
            driver.execute_script("arguments[0].click();", load_more)
            time.sleep(5)
        except:
            print("No more homes to load... Scraping text")
            more_homes = False

def myHTMLParser(s):
    """
    chops up the url and returns the proper url as a String
    """
    i = s.find('href=\"')
    newString = s[i+6:]
    i2 = newString.find('\"')
    return newString[:i2]
            
            
def scrapeItUp(driver):
    """
    function that pulls basic info + the link to each home on the page
    
    returns: pandas DataFrame, df
    """
    keep_scraping = True
    index = 1
    data = []
    while keep_scraping:
        
        ## skip over the stupid Year-end sales event ad that they have on each page
        if index == 2:
            index += 1
            continue

        try:
            ## current home
            result = driver.find_element(By.XPATH, 
                            f'//*[@id="main"]/div/div[1]/div[2]/div/div[2]/div/div[2]/div[{index}]').text.splitlines()

            ## data format error
            if len(result) != 7:

                ## flex-cash indicator -- just drop it, irrelevant
                if result[0] == 'Flex Cash':
                    result = result[1:]

                ## weird thing where sometimes a half bath is a separate column.
                ## grab that and add it to the total baths (divide by 2)
                if 'half ba' in result[4]:
                    i = int(result[4][0]) / 2
                    b = int(result[3][0])
                    result[3] = str(i+b) + " ba"
                    result.pop(4)
                
                # well, still likely something could go wrong here
                else:
                    raise Exception("Some other data format issue -- debug this")

            ## correct data format error with rearranging columns
            if result[0] == "Future release":
                result.insert(5, result.pop(1))

            ## get link
            html = driver.find_element(By.XPATH, 
                            f'//*[@id="main"]/div/div[1]/div[2]/div/div[2]/div/div[2]/div[{index}]').get_attribute('innerHTML')
            url = 'https://www.lennar.com' + myHTMLParser(html)
            result.append(url)

            data.append(result)
            index += 1

        except:
            print("Done Scraping info")
            keep_scraping = False

    df = pd.DataFrame(data, columns = ["Availability", "Price", "Beds", "Baths", "Sqft", "Address", "Community", "URL"])
    return df

def cleanItUp(df):
    """
    *** needs to be fixed, but here for now
    """
    df['Beds'] = df['Beds'].apply(lambda x : float(x.replace(" bd","")))
    df['Baths'] = df['Baths'].apply(lambda x : float(x.replace(" ba","")))
    df['Sqft'] = df['Sqft'].apply(lambda x : float(x.replace(" ft²", "").replace(",","")))
    df['Price'] = df.Price.replace('\D', '', regex=True).astype(int)
    df['Price'] = df.apply(lambda row: row['Price'] if row['Availability'] != 'Future release' 
                        else row['Price']*1000, axis=1)
    
    return df
    
def __init__():
    pass