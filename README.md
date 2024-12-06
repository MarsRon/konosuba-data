# KonoSuba Data

Text data of KonoSuba: God's Blessing on This Wonderful World! Light Novel
Volume 1 to 17 + short stories (English fan translation).

> Note:\
> Most of the unrelated metadata/TL note have been removed.\
> This might have accidentally removed some lines from the light novel, but the damage should be minimal.\
> Feel free to create an issue if there are some lines that have been accidentally removed.

## Context

KonoSuba: God's Blessing on This Wonderful World!, often referred to simply as KonoSuba,
is a Japanese light novel series written by Natsume Akatsuki.
The series follows Kazuma Satou, a boy who is sent to a fantasy world with MMORPG elements
following his death, where he forms a dysfunctional adventuring party with a goddess, an archwizard, and a crusader.

Source: https://en.wikipedia.org/wiki/KonoSuba

## Usage

Download the files below.

| File | Lines | Size | Description |
|-|-|-|-|
| [`konosuba.txt`](./konosuba.txt) | 47573 | 4.5MB | 17 volumes of KonoSuba light novel condensed into 1 file. Both dialogue and monologue are included. |
| [`konosuba-dialogue.txt`](./konosuba-dialogue.txt) | 18689 | 2.3MB | Contains only dialogues in between quotes (`“”`). Monologue is excluded. |
| [`konosuba-dataset.json`](./konosuba-dataset.json) | 18688 | 5.8MB | JSON array of dialogues between `user` and `assistant` to fine-tune LLMs. Data from [`konosuba-dialogue.txt`](./konosuba-dialogue.txt) Example: { [user: 1st line, assistant: 2nd line], [user: 2nd line, assistant: 3rd line], [user: 3rd line, assistant: 4th line], ... } |

Shameless self-plug:

- Wanna make a Markov chain random sentence generator? Check out
  [`aqua`](https://github.com/MarsRon/aqua).
- Wanna make a AI chatbot? Check out
  [`kazuma`](https://github.com/MarsRon/kazuma).

## I wanna DIY

If you want to manually generate the data yourself, I recommend using a proxy/VPN before running the webscraper.

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

This will create a `./data` directory which temporarily stores each chapter from Volume 1 to Volume 17 in text form.

Then, the script will merge all the posts into `konosuba.txt` and also generate `konosuba-dialogue.txt` only from speeches.

### Dataset creation

Run the dataset creation script.

```sh
python dataset.py
```

This will create `konosuba-dataset.json` which can then be used to fine-tune LLMs such as Llama-3.2 3B.

You can edit the bottom of the script to choose compact JSON format (default), pretty-print JSON format or CSV format.

## Acknowledgements

The data is scraped from [cgtranslations.me](https://cgtranslations.me/konosuba)
and [crimsonmagic.me](https://crimsonmagic.me/konosuba/volumes-10-plus/).

## License

Distributed under the MIT License.
See [`LICENSE.md`](./LICENSE.md) for more information.

## Contact

MarsRon - marsron204@gmail.com - [marsron.name.my](https://marsron.name.my)
