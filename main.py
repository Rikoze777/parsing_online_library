import argparse
import collections
import os
import time
from urllib.parse import urlencode, urljoin

import requests
from bs4 import BeautifulSoup
from pathvalidate import sanitize_filename

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


def check_for_redirect(page_response):
    if page_response.history:
        raise requests.exceptions.HTTPError()


def fetch_comments(comments, book_number, folder):
    os.makedirs(folder, exist_ok=True)
    filename = f"{book_number}.txt"
    filepath = os.path.join(folder, filename)
    with open(filepath, 'w') as file:
        file.write(comments)


def download_image(image_url, folder):
    os.makedirs(folder, exist_ok=True)
    image_response = requests.get(image_url)
    image_response.raise_for_status()
    imagename = "".join(image_url.split('/')[-1])
    imagepath = os.path.join(folder, imagename)
    with open(imagepath, 'wb') as image:
        image.write(image_response.content)


def download_txt(title, download_response, folder):
    os.makedirs(folder, exist_ok=True)
    filepath = os.path.join(folder, title)
    with open(filepath, 'w') as book:
        book.write(download_response.text)


def main():
    requests.packages.urllib3.disable_warnings(
        requests.packages.urllib3.exceptions.InsecureRequestWarning)
    parser = argparse.ArgumentParser(description='''This script allows you to
            download books, covers, comments, as well as get information about
            the book. To start, you must specify the start and end id of the
            books from the site https://tululu.org/''')
    parser.add_argument('start_id', type=int,
                        help='ID of the book to start parsing from')
    parser.add_argument('end_id', type=int,
                        help='ID of the book to finish parsing from')
    args = parser.parse_args()
    start_args = args.start_id
    end_args = args.end_id
    txt_folder = 'books/'
    image_folder = 'image/'
    comments_folder = 'comments/'
    for book_number in range(start_args, end_args):
        while True:
            try:
                book_url = f"https://tululu.org/b{book_number}/"
                book_response = requests.get(book_url, verify=False)
                book_response.raise_for_status()
                download_url = "https://tululu.org/txt.php"
                params = {
                        "id": book_number,
                        }
                encoded_params = urlencode(params)
                download_response = requests.get(download_url,
                                                 params=encoded_params,
                                                 verify=False)
                download_response.raise_for_status()
                check_for_redirect(book_response)
                check_for_redirect(download_response)
                book_page = parse_book_page(book_response)
                download_txt(book_page['title'], download_response, txt_folder)
                if book_page['comments']:
                    fetch_comments(book_page['comments'],
                                   book_number, comments_folder)
                download_image(book_page['image_url'], image_folder)
                print("Заголовок: ", book_page['title'])
                print("Автор: ", book_page['author'])
                print("Жанр: ", book_page['genres'])
            except requests.exceptions.HTTPError:
                print("Wrong url")
            except requests.exceptions.ConnectionError:
                time.sleep(10)
            finally:
                break


if __name__ == "__main__":
    main()
