import re
from pathlib import Path
import requests
import tqdm
import yaml

URL_RE = re.compile(r"url\(([^\)]+)\)")

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/15.6.1 Safari/605.1.15"
}

def get_fonts(family, target_folder):
    res = requests.get(f"https://fonts.googleapis.com/css", params={"family": family}, headers=HEADERS)
    res.raise_for_status()

    css = res.content.decode("utf-8")
    urls = set(URL_RE.findall(css))
    resources = []

    for url in tqdm.tqdm(urls):
        local_path = "/".join([url.split(".")[-1]] + url.split("/")[-3:])
        local_url = local_path
        resources.append("fonts/" + local_path)
        local_path = target_folder / local_path
        local_path.parent.mkdir(parents=True, exist_ok=True)

        res2 = requests.get(url, headers=HEADERS)
        res2.raise_for_status()
        content = res2.content
        with open(local_path, "wb") as outfile:
            outfile.write(content)

        css = css.replace(url, local_url)

    with open(target_folder / "fonts.css", "w") as outfile:
        outfile.write(css)

    print(yaml.dump(resources))

def main():
    get_fonts("Roboto:light,regular,italic,bold", Path("."))

if __name__ == "__main__":
    exit(main())
