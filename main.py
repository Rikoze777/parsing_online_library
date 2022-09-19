import os
import requests
from pathvalidate import sanitize_filename
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlencode
import argparse
import collections
collections.Callable = collections.abc.Callable


def parse_book_page(response):
    url = response.url
    soup = BeautifulSoup(response.text, 'lxml')
    soup_text = soup.find('body').find('h1')
    content_text = soup_text.text
    content = [" ".join(text.split()) for text in content_text.split('::')]
    title, author = content
    title = sanitize_filename(title)
    author = sanitize_filename(author)
    soup_genres = soup.find_all('span', class_='d_book')
    genres = [genre.text for genre in soup_genres]
    genres = ":".join(genres).lstrip('Жанр книги:').strip()
    soup_img = soup.find(class_='bookimage').find('img')['src']
    image_url = urljoin(url, soup_img)
    soup_comments = soup.find_all(class_='texts')
    decoded_comments = [comment.text for comment in soup_comments]
    raw_comments = []
    for comment in decoded_comments:
        comment = comment.split(')')
        raw_comments.append(comment[-1])
    comments = "\n".join(raw_comments)
    book_page = {
                 "title": title,
                 "author": author,
                 "genres": genres,
                 "image_url": image_url,
                 "comments": comments
                 }
    return book_page


def fetch_page_response(book_number):
    requests.packages.urllib3.disable_warnings(
        requests.packages.urllib3.exceptions.InsecureRequestWarning)
    url = f"https://tululu.org/b{book_number}/"
    response = requests.get(url, verify=False)
    response.raise_for_status()
    return response


def check_for_redirect(page_response):
    if page_response.history:
        raise requests.exceptions.HTTPError()


def download_comments(comments, book_number, folder):
    os.makedirs(folder, exist_ok=True)
    filename = f"{book_number}.txt"
    filepath = os.path.join(folder, filename)
    if comments:
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


def download_txt(book_number, title, folder):
    requests.packages.urllib3.disable_warnings(
        requests.packages.urllib3.exceptions.InsecureRequestWarning)
    main_url = f"https://tululu.org/txt.php"
    params = {
              "id": book_number,
              }
    encoded_params = urlencode(params)
    response = requests.get(main_url, params=encoded_params, verify=False)
    response.raise_for_status()
    os.makedirs(folder, exist_ok=True)
    filepath = os.path.join(folder, title)
    try:
        check_for_redirect(response)
        with open(filepath, 'w') as book:
            book.write(response.text)
        return response
    except requests.exceptions.HTTPError:
        print("Wrong url")


def main():
    parser = argparse.ArgumentParser(description="Arguments for parsing")
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
        page_response = fetch_page_response(book_number)
        try:
            check_for_redirect(page_response)
            book_page = parse_book_page(page_response)
            download_txt(book_number, book_page['title'], txt_folder)
            download_comments(book_page['comments'],
                              book_number, comments_folder)
            download_image(book_page['image_url'], image_folder)
            print("Заголовок: ", book_page['title'])
            print("Автор: ", book_page['author'])
            print("Жанр: ", book_page['genres'])
        except requests.exceptions.HTTPError:
            print("Wrong url")
        except requests.exceptions.ConnectionError:
            print("Connection error")


if __name__ == "__main__":
    main()
