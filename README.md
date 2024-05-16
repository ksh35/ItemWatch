ItemWatch is a website tag tracking platform. A user can enter website links and corresponding html tags to track. 

For example, a user can setup a tag tracker to track price changes, image changes, and more.

The program will monitor these tags and check their value every 3 hours for changes. Users can have multiple concurrent tracked tags.  

This program works for any html tag, so any website element is trackable. An example use of this program could be to track the price of an item.

The program waits 60 seconds when checking tags to give time for Javascript content to load.

Features a browser based UI using flask. Uses Selenium to webscrape.  

SQLlite is used for data storage.  

Sends notification when a tracked tag's value is altered.  

Frontend updates in progress

**Instructions:**
<code>
1. Install Anaconda if you don't have it
2. conda env create -f environment.yml  
3. conda activate ItemWatch  
4. python app.py</code>
