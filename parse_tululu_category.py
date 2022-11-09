import os
import requests
import time
from pathvalidate import sanitize_filename
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlencode
import argparse
import collections
collections.Callable = collections.abc.Callable


# def parse_book_page(response):
#     url = response.url
#     soup = BeautifulSoup(response.text, 'lxml')
#     soup_text = soup.find('body').find('h1')
#     content_text = soup_text.text
#     content = [" ".join(text.split()) for text in content_text.split('::')]
#     title, author = content
#     title = sanitize_filename(title)
#     author = sanitize_filename(author)
#     soup_genres = soup.find_all('span', class_='d_book')
#     genres = [genre.text for genre in soup_genres]
#     book_genres = ":".join(genres).lstrip('Жанр книги:').strip()
#     soup_img = soup.find(class_='bookimage').find('img')['src']
#     image_url = urljoin(url, soup_img)
#     soup_comments = soup.find_all(class_='texts')
#     decoded_comments = [comment.text for comment in soup_comments]
#     raw_comments = []
#     for comment in decoded_comments:
#         comment = comment.split(')')
#         raw_comments.append(comment[-1])
#     comments = "\n".join(raw_comments)
#     book_page = {
#                  "title": title,
#                  "author": author,
#                  "genres": book_genres,
#                  "image_url": image_url,
#                  "comments": comments
#                  }
#     return book_page


# def check_for_redirect(page_response):
#     if page_response.history:
#         raise requests.exceptions.HTTPError()


# def fetch_comments(comments, book_number, folder):
#     os.makedirs(folder, exist_ok=True)
#     filename = f"{book_number}.txt"
#     filepath = os.path.join(folder, filename)
#     with open(filepath, 'w') as file:
#         file.write(comments)


# def download_image(image_url, folder):
#     os.makedirs(folder, exist_ok=True)
#     image_response = requests.get(image_url)
#     image_response.raise_for_status()
#     imagename = "".join(image_url.split('/')[-1])
#     imagepath = os.path.join(folder, imagename)
#     with open(imagepath, 'wb') as image:
#         image.write(image_response.content)


# def download_txt(title, download_response, folder):
#     os.makedirs(folder, exist_ok=True)
#     filepath = os.path.join(folder, title)
#     with open(filepath, 'w') as book:
#         book.write(download_response.text)


def main():
    requests.packages.urllib3.disable_warnings(
        requests.packages.urllib3.exceptions.InsecureRequestWarning)
    # parser = argparse.ArgumentParser(description='''This script allows you to
    #         download books, covers, comments, as well as get information about
    #         the book. To start, you must specify the start and end id of the
    #         books from the site https://tululu.org/''')
    # parser.add_argument('start_id', type=int,
    #                     help='ID of the book to start parsing from')
    # parser.add_argument('end_id', type=int,
    #                     help='ID of the book to finish parsing from')
    # args = parser.parse_args()
    # start_args = args.start_id
    # end_args = args.end_id
    # txt_folder = 'books/'
    # image_folder = 'image/'
    # comments_folder = 'comments/'
    # for book_number in range(start_args, end_args):
    while True:
        try:
            fantastic_url = "https://tululu.org/l55/"
            response = requests.get(fantastic_url, verify=False)
            response.raise_for_status()
            soup = BeautifulSoup(response.text, 'lxml')
            book_tag = soup.find(class_="bookimage").find('a')["href"]
            book_url = urljoin(fantastic_url, book_tag)
            print(book_url)
        except requests.exceptions.HTTPError:
            print("Wrong url")
        except requests.exceptions.ConnectionError:
            time.sleep(10)
        finally:
            break


if __name__ == "__main__":
    main()
