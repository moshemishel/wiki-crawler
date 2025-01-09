import os
from os.path import abspath, dirname, exists, isfile, isdir
import requests
from bs4 import BeautifulSoup
from tqdm import tqdm
import random
from urllib.parse import urljoin
from PIL import Image
from io import BytesIO

def delete_folder(folder_path):
    for item in os.listdir(folder_path):
        item_path = os.path.join(folder_path, item)
        if isfile(item_path):
            os.unlink(item_path)  
        elif isdir(item_path):
            delete_folder(item_path)  
    os.rmdir(folder_path)  

def get_soup(url):
    response = requests.get(url)
    return BeautifulSoup(response.text, 'html.parser')

def get_img(soup):
    min_width, min_height = 75, 75
    img = []
    for img_tag in soup.find_all('img'):
        img_url = img_tag.get('src')
        img_class = img_tag.get('class')
        img_width = img_tag.get('width') 
        img_height = img_tag.get('height')
        img_class = img_class[0] if img_class is not None else ""
        img_width = int(img_width) if img_width is not None else 0
        img_height = int(img_height) if img_height is not None else 0
        if img_class == 'mw-file-element' and \
        img_width >= min_width and img_height >= min_height:
            img.append(img_url)
    return img


def save_img(img, main_dir, title):
    img_dir = os.path.join(main_dir, title)
    os.makedirs(img_dir, exist_ok=True) 
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36'
    }

    for img_path in img:
        full_path = urljoin("https:", img_path)

        try:
            response = requests.get(full_path, headers=headers, timeout=5)
            if response.status_code != 200:
                print(f"Failed to download {full_path}, status code: {response.status_code}")
                continue
            img_data = Image.open(BytesIO(response.content))
            file_name = img_path.rsplit('/', 1)[-1][:15] + ".png"
            save_path = os.path.join(img_dir, file_name)     
            img_data.save(save_path, format="PNG")

        except Exception as e:
            print(f"Error processing {full_path}: {e}")


def get_links(soup, width, visited):
    links = []
    base_url = "https://en.wikipedia.org"

    for link_tag in soup.find_all('a'):
        link = link_tag.get('href')
        if link is None:
            continue 
        link = urljoin(base_url, link)

        if not link.startswith('https://en.wikipedia.org/wiki/'):
            continue
        if ':' in link[len('https://en.wikipedia.org/wiki/'):]:
            continue
        if link in visited:
            continue

        links.append(link)

    return random.sample(links, min(width, len(links)))
     

def crawler(width, depth, url, main_dir, progress_bar, visited = None):
    visited = set() if visited is None else visited
    visited.add(url)

    soup = get_soup(url)

    img = get_img(soup)
    title = soup.title.string
    save_img(img, main_dir, title)
    progress_bar.update(1)

    if depth > 0:
        links = get_links(soup, width, visited)
        for link in links:
            crawler(width, depth -1, link, main_dir, progress_bar, visited)


def main():
    width = int(input("Please enter a number for width search: "))
    assert width > 0, "width must be a positive number."
    depth = int(input("Please enter a number for depth search: "))
    assert depth >= 0, "width must be a none negative number."
    main_dir = f"{dirname(abspath(__file__))}/result" 
    if exists(main_dir):
        delete_folder(main_dir)
    os.mkdir(main_dir)
    random_url =  "https://en.wikipedia.org/wiki/Special:Random"
    response = requests.get(random_url)
    assert response.status_code == 200, "The connection fail."
    init_url = response.url
    progress_bar = tqdm(total= width**depth, desc= 'crawling now')

    crawler(width, depth, init_url, main_dir, progress_bar)

    progress_bar.close()


if __name__ == "__main__":
    main()
  


    







    


