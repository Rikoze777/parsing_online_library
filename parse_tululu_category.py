import argparse
import collections
import json
import os
import time
from pathlib import Path
from urllib.parse import urljoin

import requests
from bs4 import BeautifulSoup
from pathvalidate import sanitize_filename

from main import check_for_redirect, download_image, download_txt

collections.Callable = collections.abc.Callable


def parse_book_page(response):
    url = response.url
    soup = BeautifulSoup(response.text, 'lxml')

    header_selector = ".ow_px_td h1"
    header_content = soup.select_one(header_selector)
    content_text = header_content.text
    content = [" ".join(text.split()) for text in content_text.split('::')]
    book_title, book_author = content
    book_title = sanitize_filename(book_title)
    book_author = sanitize_filename(book_author)

    genres_selector = "span.d_book a"
    genres_content = soup.select(genres_selector)
    genres = [genre.string for genre in genres_content]
    book_genres = " : ".join(genres).lstrip('Жанр книги:').strip()

    image_selector = "div.bookimage img"
    image_content = soup.select_one(image_selector)['src']
    image_url = urljoin(url, image_content)

    comments_selector = "#content .texts .black"
    comments_content = soup.select(comments_selector)
    decoded_comments = [comment.text for comment in comments_content]
    comments = "\n".join(decoded_comments)
    book_page = {
                 "title": book_title,
                 "author": book_author,
                 "genres": book_genres,
                 "image_url": image_url,
                 "comments": comments
                 }
    return book_page


def create_argparse():
    parser = argparse.ArgumentParser(description='''This script will download
            fantasy books for you from https://tululu.org/''')
    parser.add_argument('--start_page', type=int,
                        help='Start page to start parsing from')
    parser.add_argument('--end_page', nargs='?', type=int,
                        help='End page to finish parsing from')
    parser.add_argument('--dest_folder', nargs='?', type=str,
                        default=Path.cwd(),
                        help='Folder with parsing results')
    parser.add_argument('--skip_imgs', action="store_true", default=False,
                        help='Skip parsing images')
    parser.add_argument('--skip_txt', action="store_true", default=False,
                        help='Skip parsing textfiles')
    parser.add_argument('--json_path', action="store_true", default=Path.cwd(),
                        help='Folder with parsing json results')
    return parser


def main():
    requests.packages.urllib3.disable_warnings(
        requests.packages.urllib3.exceptions.InsecureRequestWarning)
    parser = create_argparse()
    args = parser.parse_args()
    start_page = args.start_page
    end_page = args.end_page
    dest_folder = args.dest_folder
    skip_imgs = args.skip_imgs
    skip_txt = args.skip_txt
    json_folder = args.json_path
    books_dump = []
    txt_folder = Path(dest_folder, 'books/')
    image_folder = Path(dest_folder, 'images/')
    if json_folder:
        os.makedirs(json_folder, exist_ok=True)
    if not skip_imgs:
        image_folder.mkdir(parents=True, exist_ok=True)
    if not skip_txt:
        txt_folder.mkdir(parents=True, exist_ok=True)
    if not end_page:
        end_page = start_page + 1
    for page in range(start_page, end_page):
        while True:
            fantastic_url = f"https://tululu.org/l55/{page}"
            download_url = "https://tululu.org/txt.php"
            url = "https://tululu.org/"
            response = requests.get(fantastic_url, verify=False)
            response.raise_for_status()
            soup = BeautifulSoup(response.text, 'lxml')
            selector = ".d_book a[href^='/b']"
            links = [content["href"] for content in soup.select(selector)]
            page_links = list(dict.fromkeys(links))
            for link in page_links:
                try:
                    book_number = int(str(link)[2:-1])
                    book_url = urljoin(url, link)
                    params = {
                            "id": book_number,
                    }
                    book_response = requests.get(book_url, verify=False)
                    book_response.raise_for_status()
                    download_response = requests.get(download_url,
                                                     params=params,
                                                     verify=False)
                    download_response.raise_for_status()
                    check_for_redirect(book_response)
                    check_for_redirect(download_response)
                    book_page = parse_book_page(book_response)
                    if not skip_txt:
                        download_txt(book_page['title'],
                                     download_response, txt_folder)
                    if not skip_imgs:
                        download_image(book_page['image_url'], image_folder)
                    books_dump.append(book_page)
                except requests.exceptions.HTTPError:
                    print("Wrong url")
                    continue
                except requests.exceptions.ConnectionError:
                    time.sleep(10)
                    continue
            break
    json_path = os.path.join(json_folder, "books_dump.json")
    with open(json_path, 'w') as file:
        json.dump(books_dump,
                  file,
                  ensure_ascii=False,
                  indent=4)


if __name__ == "__main__":
    main()
