# KonoSuba Data

Webscrapes KonoSuba Light Novel from Volume 1-17 + short stories (English fan
translation) from [cgtranslations.me](https://cgtranslations.me/konosuba) and
[crimsonmagic.me](https://crimsonmagic.me/konosuba/volumes-10-plus/).

## Usage

The full data is located at
[`konosuba.txt`](https://github.com/MarsRon/konosuba-data/blob/main/konosuba.txt).
Just download it or whatever.

### I wanna DIY

If you want to manually generate the data yourself, I recommend using a proxy/VPN
before running the webscraper.

Clone the project.
```sh
git clone https://github.com/MarsRon/konosuba-data
```

Create a Python virtual environment.
```sh
python3 -m venv venv
source venv/bin/activate
```

Install libraries.
```sh
pip install -r requirements.txt
```

Run the webscraper.
```sh
python scrape.py
```
