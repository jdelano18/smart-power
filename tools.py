from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
import time
from selenium.webdriver.chrome.service import Service
from selenium.common.exceptions import NoSuchElementException
import requests
from bs4 import BeautifulSoup
import json
import pandas as pd
import sys

def closeCookies(driver):
    """
    finds the accept cookies window and clicks if it is there
    """
    try:
        driver.find_element(By.XPATH, "/html/body/div[2]/div[2]/div/button").click()
        print("\t Closed cookies window. Continue...")
    except:
        print("\t No cookies window. Continue...")

    time.sleep(5)

def loadMoreHomes(driver):
    """
    keeps clikcing on the load more homes button on a page until theres no more
    """
    more_homes = True
    print("\t Loading homes", end="")
    while more_homes:
        try:
            load_more = driver.find_element(By.XPATH, '//button[normalize-space()="Load more homes"]')
            driver.execute_script("arguments[0].click();", load_more)
            time.sleep(3)
            print(".", end="")
        except:
            # print("No more homes to load...")
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
    print("\n\t Scraping", end="")
    keep_scraping = True
    index = 1
    data = []
    while keep_scraping:
        if index % 10 == 0:
            print(".", end='')

        try:
            result = driver.find_element(By.XPATH, 
                            f'//*[@id="main"]/div/div[1]/div[2]/div/div[2]/div/div[2]/div[{index}]').text.splitlines()

            ## skip over the Ad
            ## OLD AD: if index == 2 and 'Year-End Sales Event' in result[0]:
            if index == 2 and 'Limited time incentives' in result[0]:
                index += 1
                continue

            ## drop all the stupid tags that are in the top right corner:
            if result[0] not in ['Move-in ready', 'Under construction', 'Future release', 'Coming soon']:
                result = result[1:]

            
            ## reduced price
            if result[1][0] == '$' and result[2][0] == '$':
                result.pop(2)

            ## crossed out price and new low/mid/high estimate
            if '$' in result[1] and '$' in result[2]:
                result.pop(2)
            
            ## weird thing where sometimes a half bath is a separate column.
            ## grab that and add it to the total baths (divide by 2)
            if 'half ba' in result[4]:
                i = int(result[4][0]) / 2
                b = int(result[3][0])
                result[3] = str(i+b) + " ba"
                result.pop(4)
                

            assert len(result) == 7 

            ## Rearranging columns for data
            if result[0] == "Future release":
                result.pop(1)
                result.insert(5, "N/A")

            ## get link
            html = driver.find_element(By.XPATH, 
                            f'//*[@id="main"]/div/div[1]/div[2]/div/div[2]/div/div[2]/div[{index}]').get_attribute('innerHTML')
            url = 'https://www.lennar.com' + myHTMLParser(html)
            result.append(url)

            data.append(result)
            index += 1
        except AssertionError:
            print("**** Some other data format issue ****")
            keep_scraping = False
        except NoSuchElementException:
            print(f"{len(data)}. Done!")
            keep_scraping = False
        except:
            print("Shit is broken")
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
    # df['Price'] = df.Price.replace('\D', '', regex=True).astype(int)
    # df['Price'] = df.apply(lambda row: row['Price'] if row['Availability'] != 'Future release' 
    #                     else row['Price']*1000, axis=1)
    
    return df
    
def __init__():
    pass