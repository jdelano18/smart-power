# smart-power
 
The goal of this project was to scrape all the data from lennar.com, a big home manufacturer, and the features in them. Eventually we wanted to be able to search through these attributes to answer questions like: how many homes does lennar have that have motion sensors? how do they display that to their customers? The use case for this information is confidential.

### roadmap

I started with homepage.ipynb to get all of the links relating to each one of the cities. These are found on lennar.com under the view all regions tab. This was a little hack-y but got the job done.

From there, I looked at specific-market.ipynb which was a case study for one city: huntsville, AL. This is where I discovered the data we wanted had to be loaded dynamically which required using the selenium package. This allows one to start-up a chrome window and control it through a python script. I needed to click buttons like the "accept cookies" pop-up window and then "load more homes". This work is in selenium.ipynb and the output is in huntsville-al.csv.

I then generalized this specific case to a loop that would go and visit all the cities (roadTrip.ipynb). I moved the work from selunium.ipynb into a module, tools.py. There were lots of data format issues and inconsistencies on this website -- pretty messy overall so this was a little tedious. In the main loop for roadTrip you can see a call to the scrapeItUp function where you can see how much of a mess this data was. The output from this file was the data folder with a csv for each city where each row was a unique home.

The next step was going from each row to pull the data we wanted for each home. This step I called trick-or-treat (it was right around halloween; a loop that goes from home-to-home in each neighborhood; you get it). This step required far less massaging than roadTrip -- I ran into a few data format issues but nothing that major. The output from this step is also in the data folder as individual json files -- one for each city where each row has basic home information (price, beds, baths, sqft, etc.) plus all the additional features we were interested in getting.

Finally, I combined these individual files into one big data source with bigData.ipynb and got to the analysis step in analysis.ipynb where I could search for keywords to answer a bunch of questions that we had.