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
import numpy as np

def closeCookies(driver):
    """
    finds the accept cookies window and clicks if it is there
    """
    try:
        driver.find_element(By.XPATH, "/html/body/div[3]/div[2]/div/div/div[2]/div/div/button").click()
        print("\t Closed cookies window. Continue...")
    except NoSuchElementException:
        try:
            driver.find_element(By.XPATH, "/html/body/div[2]/div[2]/div/button").click()
            print("\t Closed cookies window. Continue...")
        except NoSuchElementException:
            try:
                driver.find_element(By.XPATH, "/html/body/div[2]/div[2]/div/div/div[2]/div/div/button").click()
                print("\t Closed cookies window. Continue...")
            except NoSuchElementException:
                print("\t No cookies window. Continue...")
    except:
        print("wtf")
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
            # print("hi")
            result = driver.find_element(By.XPATH, 
                            f'//*[@id="main"]/div/div[1]/div[2]/div/div[3]/div/div[2]/div[{index}]').text.splitlines()
            # print(result)

            ## skip over the Ads
            ## OLD AD: if index == 2 and 'Year-End Sales Event' in result[0]
            if "Summer's on!" in result[0]:
                index += 1
                continue
            
            if result[0].startswith('Check out'):
                index += 1
                continue
                
            if result[0].startswith('Final') and result[0].endswith('remain'):
                index += 1
                continue
            
            if result[0].startswith('BIG SAVINGS'):
                index += 1
                continue
            
            if result[0].startswith('Start your path'):
                index += 1
                continue
                
            if result[0].startswith('Preview the homes'):
                index += 1
                continue
                
            if result[0].startswith('Cirrus'):
                index += 1
                continue
                
            if result[0].startswith('Save on move'):
                index += 1
                continue
            
            if result[0].startswith('Take advantage of'):
                index += 1
                continue
                
            if result[0].startswith('Move-in ready homes available now'):
                index += 1
                continue
            
            if result[0].startswith('New Home National Sales Event'):
                index += 1
                continue
                
            if result[0].startswith('Sales Event Extended'):
                index += 1
                continue
                
            if result[0].startswith('Why buy new'):
                index += 1
                continue
                
            if result[0].startswith('HUGE'):
                index += 1
                continue
                
            if result[0].startswith('Hello Autumn'):
                index += 1
                continue
            
            ## drop all the stupid tags that are in the top right corner:
            for _ in range(3):
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
                


            ## Rearranging columns for data
            if result[0] == "Future release":
                # result.pop(1)
                # result.insert(5, "N/A")
                result = ['Future release']+[np.NaN]*6

                
            # final check
            assert len(result) == 7 
            
            ## get link
            html = driver.find_element(By.XPATH, 
                            f'//*[@id="main"]/div/div[1]/div[2]/div/div[3]/div/div[2]/div[{index}]').get_attribute('innerHTML')
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
    df['Beds'] = df['Beds'].replace('Studio', '0 bd')
    df['Beds'] = df[~df['Beds'].isna()]['Beds'].apply(lambda x : float(x.replace(" bd","")))
    df['Baths'] = df[~df['Baths'].isna()]['Baths'].apply(lambda x : float(x.replace(" ba","")))
    df['Sqft'] = df[~df['Sqft'].isna()]['Sqft'].apply(lambda x : float(x.replace(" ft²", "").replace(",","")))
    # df['Price'] = df.Price.replace('\D', '', regex=True).astype(int)
    # df['Price'] = df.apply(lambda row: row['Price'] if row['Availability'] != 'Future release' 
    #                     else row['Price']*1000, axis=1)
    
    return df
    
def __init__():
    pass