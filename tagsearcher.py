from bs4 import BeautifulSoup
from selenium import webdriver
import time
from selenium.webdriver.common.by import By
from selenium.webdriver import DesiredCapabilities

#Defined Exceptions

class TagNotFound(Exception):
    pass

class InvalidOptions(Exception):
    pass

class InvalidLink(Exception):
    pass

#TagSearcher Object
class TagSearcher:

    def __init__(self, link: str, html: str) -> None:
        self._link = link.strip()
        self._html = html.strip()
        self._val = ""
        self._saved_index = -1 
        self._driver = None
        self._options = None
        self._elementString = None
        self._last_tag_txt = None
        self._tag_attributes = None

    #Default webscraping options, or pass in a list of options
    def _setOptions(self, options = []):
        self._options = webdriver.ChromeOptions()
        if (len(options) == 0):
            self._options.add_argument("--headless")
            self._options.add_argument("--disable-gpu")
            self._options.add_argument("--window-size=1920,1080")
            agent = 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/60.0.3112.50 Safari/537.36'
            self._options.add_argument(f"user-agent={agent}")
            self._options.page_load_strategy = "none"
        else:
            for arg in options:
                self._options.add_argument(arg)

    #Finds provided tag information
    def _findTagInfo(self) -> None:
        parser = BeautifulSoup(self._html, "html.parser")
        tags = parser.find_all()
        
        if(not tags):
            raise TagNotFound("No tag found")
        
        tag = tags[0]
        self._elementString = tag.name
        self._last_tag_txt = tag.text
        self._tag_attributes = tag.attrs
        
    #Begins the scraping process
    #Returns 0 if successful, error string based on error
    def start(self, options = []) -> int: #Or error string
        
        try:
            self._setOptions(options)
        except InvalidOptions:
            return "Invalid options arguments: Try passing a list of strings"

        try:
            self._findTagInfo()
        except TagNotFound:
            return "Tag not found"
        
        if("class" in self._tag_attributes):
            for i in self._tag_attributes["class"]:
                self._elementString += "." + i
        else:
            return "No class found"

        try:
            self._driver = webdriver.Chrome(options=self._options)
        except:
            return "Driver could not start"

        try:
            self._driver.get(self._link)
        except InvalidLink:
            return "Invalid link"

        #Provides 60 seconds for the page to load
        time.sleep(60)
        self._driver.get_screenshot_as_file("screenshot.png")

        try:
            self._searchPageFindIndex()
        except TagNotFound:
            return "Could not find tag on page"

        return 0

    #Searches page for tag for the first time, logs saved index
    def _searchPageFindIndex(self) -> None:
        try:
            all_tags = self._driver.find_elements(By.CSS_SELECTOR, self._elementString)
            self._saved_index = 0
            if(len(all_tags) == 0):
                raise TagNotFound("Not found")
            for tag in all_tags:
                if(tag.text != "" and tag.text == self._last_tag_txt):
                    break
                self._saved_index += 1
            self._val = all_tags[self._saved_index].text        
        except TagNotFound:
            self._saved_index = -1
            raise TagNotFound("Could not find tag on page")

    #Searches page for tag using saved index
    def searchWithIndexandElementString(self, options = [], index = None, elementString = None) -> None:

        if(index != None):
            self._saved_index = index
        if(elementString != None):
            self._elementString = elementString

        try:
            self._setOptions(options)
        except InvalidOptions:
            raise InvalidOptions("Invalid options arguments: Try passing a list of strings")
        

        try:
            self._driver = webdriver.Chrome(options=self._options)
        except:
            raise Exception("Driver could not start")
        
        try:
            self._driver.get(self._link)
        except InvalidLink:
            raise InvalidLink("Invalid link")

        #Provides 60 seconds for the page to load
        time.sleep(60)
        #self._driver.get_screenshot_as_file("screenshot.png")

        try:
            all_tags = self._driver.find_elements(By.CSS_SELECTOR, self._elementString)
            if(len(all_tags) == 0):
                raise TagNotFound("Not found")
            self._val = all_tags[self._saved_index].text
            return self._val        
        except TagNotFound:
            raise TagNotFound("Could not find tag on page")



    def setLink(self, link: str):
        self._link = link

    def setHTML(self, html: str):
        self._html = html.strip()

    def getHTML(self):
        return self._html
    
    def getLink(self):
        return self._link
    
    def getVal(self):
        return self._val
    
    def getSavedIndex(self):
        return self._saved_index
    
    def setSavedIndex(self, index: int):
        self._saved_index = index

    def getElementString(self):
        return self._elementString
    
    def setElementString(self, elementString: str):
        self._elementString = elementString
    

if __name__ == "__main__":
    pass
    
    
    






