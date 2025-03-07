
#### Trying out selenium
import re
import pandas as pd
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
import time

with open("password.txt", "r") as file:
    PASSWORD = file.read()


opt = webdriver.EdgeOptions()
opt.add_argument("--window-size=1920,1080")
opt.add_argument("--enable-javascript")
opt.add_argument("disable-infobars")
opt.add_argument("--disable-extensions")
# opt.add_argument("--headless")
opt.add_argument("enable-automation")

driver = webdriver.Edge(options=opt)

# driver.get(
#     "https://wallha.com/wallpaper/beige-car-car-crossover-car-ford-ecosport-suv-subcompact-car-1158548"
# )

# time.sleep(1.5)
# driver.get(
#     "https://www.carscoops.com/2019/09/beige-2009-mercedes-slr-mclaren-roadster-is-one-of-a-kind-thankfully/"
# )

time.sleep(1.5)

driver.get(
    "https://www.geocaching.com/account/signin?returnUrl=https%3A%2F%2Fwww.geocaching.com%2Fseek%2Fnearest.aspx"
)

time.sleep(4)

driver.find_element("id","CybotCookiebotDialogBodyLevelButtonLevelOptinAllowAll").click()


driver.find_element("id", "UsernameOrEmail").send_keys("Team_Dorito_Chip")
driver.find_element("id", "Password").send_keys(PASSWORD)
driver.find_element("id", "SignIn").click()

# URLs for the different states
utah_caches = "https://www.geocaching.com/seek/nearest.aspx?state_id=45&ex=0&cFilter=9a79e6ce-3344-409c-bbe9-496530baf758&children=n"
cali_caches = "https://www.geocaching.com/seek/nearest.aspx?state_id=5&ex=0&cFilter=9a79e6ce-3344-409c-bbe9-496530baf758&children=n"

driver.get(cali_caches)

content = driver.page_source

soup = BeautifulSoup(content, "html.parser")

# Finding the total number of pages in the search results

span_20 = soup.findAll("div", {"class": "span-20 last"})
page_content = span_20[0].findAll("div", {"id": "ctl00_ContentBody_PageContent"})
pagesearch = page_content[0].findAll("div", {"id": "ctl00_ContentBody_ResultsPanel"})
table = pagesearch[0].find("table", {"class": "NoBottomSpacing"}).findAll("b")
totalnumpages = int(table[2].text)

# Instantiating some lists to store the data
ids = []
difficulties = []
terrains = []
dates = []
favorites = []
# totalnumpages = 500
# Looping through all the search results
for page in range(1, totalnumpages):
    dirty_info = soup.findAll(
        "tr",
        {
            "class": [
                "SolidRow Data BorderTop",
                "BeginnerRow Data BorderTop",
                "AlternatingRow Data BorderTop",
            ]
        },
    )
    # Looping through each cache on the page
    for info in dirty_info:
        favorite = info.find("span", attrs={"class": "favorite-rank"}).text

        important_info = info.findAll("span", attrs={"class": "small"})

        cache_id = important_info[1]
        cache_difficulty = important_info[2]
        date_hidden = important_info[3]

        ### Cleaning the ID ###
        #######################
        text = cache_id.text
        # Split the text into lines
        lines = text.split("\n")
        # Loop through each line
        for line in lines:
            # Strip leading and trailing whitespace
            line = line.strip()
            # If the line starts with 'G', it's the ID you're looking for
            if line.startswith("G"):
                id = line
                break

        ### Cleaning the difficulty ###
        ###############################
        text = cache_difficulty.text
        # Split the text on the '/' character
        parts = text.split("/")
        # The first part is the difficulty
        difficulty = parts[0].strip()
        # The second part is the terrain
        terrain = parts[1].strip()

        ### Cleaning the date hidden ###
        ################################
        date_hidden = date_hidden.text

        ids.append(id)
        difficulties.append(difficulty)
        terrains.append(terrain)
        dates.append(date_hidden)
        favorites.append(favorite)


    # Clicking to the next page
    nextPage = len(
        soup.find("div", {"id": "ctl00_ContentBody_ResultsPanel"})
        .find("table", {"class": "NoBottomSpacing"})
        .findAll("a")
    )
    time.sleep(2)
    driver.find_element(
        By.XPATH,
        "//*[@id='ctl00_ContentBody_ResultsPanel']/table[1]/tbody/tr/td[2]/a[{}]".format(
            nextPage
        ),
    ).click()
    # Getting info from the next page
    content = driver.page_source
    soup = BeautifulSoup(content, "html.parser")
    dirty_info = soup.findAll(
        "tr",
        {
            "class": [
                "SolidRow Data BorderTop",
                "BeginnerRow Data BorderTop",
                "AlternatingRow Data BorderTop",
            ]
        },
    )



### Making these into a DataFrame ####
######################################

df = pd.DataFrame(
    {
        "id": ids,
        "difficulty": difficulties,
        "terrain": terrains,
        "date_hidden": dates,
        "favorites": favorites,
    }
)

df.to_csv("cali_geocaches.csv", index=False)
