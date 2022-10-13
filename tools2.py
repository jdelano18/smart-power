import os



def cleanURL(url):
    """
    Takes lennar url as in all the csv files and returns the updated version ready to scrape
    returns: String (url)
    """
    
    ## get rid of code if the last part of url starts with a digit
    if url.split('/')[-1][0].isdigit():
        tmp = url.split('/')[:-1]
        url = '/'.join(tmp)
    
    final_url = url + '/included?print=true'
    return final_url


def __init__():
    pass