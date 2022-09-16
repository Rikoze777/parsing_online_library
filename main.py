import os
import requests
from pathvalidate import sanitize_filename
from bs4 import BeautifulSoup
from urllib.parse import urljoin
import argparse
import collections
collections.Callable = collections.abc.Callable


def parse_book_page(response):
    soup = BeautifulSoup(response.text, 'lxml')
    soup_text = soup.find('body').find('h1')
    content_text = soup_text.text
    title = "".join((content_text.split('::'))[0].strip())
    title = f"{sanitize_filename(title)}"
    author = "".join((content_text.split('::'))[1].strip())
    author = f"{sanitize_filename(author)}"
    soup_genres = soup.find_all('span', class_='d_book')
    genres = [genre.text for genre in soup_genres]
    genres = ":".join(genres).lstrip('Жанр книги:').strip()
    parse_book = {
                  "title": title,
                  "author": author,
                  "genres": genres,
                  }
    return soup, parse_book


def check_for_redirect(download_response, page_response):
    url = "https://tululu.org/"
    if page_response.url != url and download_response.url != url:
        pass
    else:
        raise requests.exceptions.HTTPError()


def fetch_page_response(book_number):
    requests.packages.urllib3.disable_warnings(
        requests.packages.urllib3.exceptions.InsecureRequestWarning)
    url = f"https://tululu.org/b{book_number}/"
    response = requests.get(url, verify=False)
    response.raise_for_status()
    return response


def fetch_download_response(book_number):
    requests.packages.urllib3.disable_warnings(
        requests.packages.urllib3.exceptions.InsecureRequestWarning)
    url = f"https://tululu.org/txt.php?id={book_number}"
    response = requests.get(url, verify=False)
    response.raise_for_status()
    return response


def download_comments(soup, book_number, folder):
    os.makedirs(folder, exist_ok=True)
    soup_comments = soup.find_all(class_='texts')
    comments_list = [comment.text for comment in soup_comments]
    raw_comments = []
    for comment in comments_list:
        comment = comment.split(')')
        raw_comments.append(comment[-1])
    comments = "\n".join(raw_comments)
    filename = f"{book_number}.txt"
    filepath = os.path.join(folder, filename)
    if comments:
        with open(filepath, 'w') as file:
            file.write(comments)
    else:
        pass


def download_image(soup, book_number, folder):
    os.makedirs(folder, exist_ok=True)
    url = f"https://tululu.org/b{book_number}/"
    soup_img = soup.find(class_='bookimage').find('img')['src']
    image_url = urljoin(url, soup_img)
    image_response = requests.get(image_url)
    image_response.raise_for_status()
    imagename = "".join(image_url.split('/')[-1])
    imagepath = os.path.join(folder, imagename)
    with open(imagepath, 'wb') as image:
            image.write(image_response.content)


def download_txt(response, title, folder):
    os.makedirs(folder, exist_ok=True)
    filepath = os.path.join(folder, title)
    with open(filepath, 'w') as book:
        book.write(response.text)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('start_id',
                        help='Required argument')
    parser.add_argument('end_id',
                        help='Required argument')
    args = parser.parse_args()
    start_args = args.start_id
    end_args = args.end_id
    txt_folder = 'books/'
    image_folder = 'image/'
    comments_folder = 'comments/'
    for book_number in range(int(start_args), int(end_args) + 1):
        download_response = fetch_download_response(book_number)
        page_response = fetch_page_response(book_number)
        try:
            check_for_redirect(download_response, page_response)
            soup, parse_page = parse_book_page(page_response)
            download_txt(download_response, parse_page['title'], txt_folder)
            download_image(soup, book_number, image_folder)
            download_comments(soup, book_number, comments_folder)
            print("Заголовок: ", parse_page['title'])
            print("Автор: ", parse_page['author'])
            print("Жанр: ", parse_page['genres'])
        except:
            pass


if __name__ == "__main__":
    main()
