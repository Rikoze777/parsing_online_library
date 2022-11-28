import argparse
import collections
import json
import os
import time
from pathlib import Path
from urllib.parse import urljoin

import requests
from bs4 import BeautifulSoup

from main import (check_for_redirect, download_image, download_txt,
                  parse_book_page)

collections.Callable = collections.abc.Callable


def create_argparse():
    parser = argparse.ArgumentParser(description='''This script will download
            fantasy books for you from https://tululu.org/''')
    parser.add_argument('--start_page', type=int, default=1,
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
    download_url = "https://tululu.org/txt.php"
    url = "https://tululu.org/"
    parser = create_argparse()
    args = parser.parse_args()
    start_page = args.start_page
    end_page = args.end_page
    dest_folder = args.dest_folder
    skip_imgs = args.skip_imgs
    skip_txt = args.skip_txt
    json_folder = args.json_path
    books_dump = []
    if json_folder:
        os.makedirs(json_folder, exist_ok=True)
    if not end_page:
        end_page = start_page + 1
    for page in range(start_page, end_page):
        try:
            fantastic_url = f"https://tululu.org/l55/{page}"
            response = requests.get(fantastic_url, verify=False)
            response.raise_for_status()
            check_for_redirect(response)
            soup = BeautifulSoup(response.text, 'lxml')
            selector = ".d_book"
            page_links = [content.a["href"] for content
                          in soup.select(selector)]
        except requests.exceptions.HTTPError:
            print("Wrong url")
        except requests.exceptions.ConnectionError:
            print("Connection error")
            time.sleep(10)
        finally:
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
                        book_path = download_txt(book_page['title'],
                                                 download_response,
                                                 dest_folder)
                        book_page['book_path'] = book_path
                    if not skip_imgs:
                        image_path = download_image(book_page['image_url'],
                                                    dest_folder)
                        book_page['img_src'] = image_path
                    books_dump.append(book_page)
                except requests.exceptions.HTTPError:
                    print("Wrong url")
                except requests.exceptions.ConnectionError:
                    print("Connection error")
                    time.sleep(10)
    json_path = os.path.join(json_folder, "books_dump.json")
    with open(json_path, 'w') as file:
        json.dump(books_dump,
                  file,
                  ensure_ascii=False,
                  indent=4)


if __name__ == "__main__":
    main()
