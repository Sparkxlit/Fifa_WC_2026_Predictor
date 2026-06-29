import os
import requests

flags = {
    "Argentina": "ar",
    "England": "gb-eng",
    "Morocco": "ma",
    "Japan": "jp",
    "Spain": "es",
    "Netherlands": "nl",
    "Norway": "no",
    "Algeria": "dz",
    "France": "fr",
    "Senegal": "sn",
    "Croatia": "hr",
    "Germany": "de",
    "Brazil": "br",
    "Belgium": "be",
    "Portugal": "pt",
    "Austria": "at",
    "Ivory Coast": "ci",
    "Iran": "ir",
    "Colombia": "co",
    "Canada": "ca",
    "Turkey": "tr",
    "Mexico": "mx",
    "South Korea": "kr",
    "Paraguay": "py",
    "Switzerland": "ch",
    "Haiti": "ht",
    "Czech Republic": "cz",
    "Uruguay": "uy",
    "DR Congo": "cd",
    "Australia": "au",
    "Ecuador": "ec",
    "Egypt": "eg",
    "Curaçao": "cw",
    "Uzbekistan": "uz",
    "South Africa": "za",
    "New Zealand": "nz",
    "Panama": "pa",
    "Sweden": "se",
    "Tunisia": "tn",
    "Scotland": "gb-sct",
    "Cape Verde": "cv",
    "Ghana": "gh",
    "United States": "us",
    "Bosnia and Herzegovina": "ba",
    "Jordan": "jo",
    "Saudi Arabia": "sa",
    "Iraq": "iq",
    "Qatar": "qa"
}

os.makedirs("flags", exist_ok=True)

for team, code in flags.items():
    url = f"https://flagcdn.com/w320/{code}.png"
    r = requests.get(url)

    if r.status_code == 200:
        with open(f"flags/{team}.png", "wb") as f:
            f.write(r.content)
        print(f"Downloaded {team}")
    else:
        print(f"Failed {team}")