import os
import requests
from pathvalidate import sanitize_filename
from bs4 import BeautifulSoup
import collections
collections.Callable = collections.abc.Callable


def get_filename(book_number):
    url = f"https://tululu.org/b{book_number}/"
    response = requests.get(url, verify=False)
    response.raise_for_status()
    soup = BeautifulSoup(response.text, 'lxml')
    soup_text = soup.find('body').find('h1')
    content_text = soup_text.text
    filename = "".join((content_text.split('::'))[0].strip())
    return filename


def get_filepath(filename, folder='books/'):
    filename = (f"{sanitize_filename(filename)}")
    filepath = os.path.join(folder, filename)
    return filepath


def check_for_redirect(response):
    if response.history == []:
        pass
    else:
        raise requests.exceptions.HTTPError('main')


def download_txt(folder, book_number):
    requests.packages.urllib3.disable_warnings(
        requests.packages.urllib3.exceptions.InsecureRequestWarning)
    os.makedirs(folder, exist_ok=True)
    url = f"https://tululu.org/txt.php?id={book_number}"
    response = requests.get(url, verify=False)
    response.raise_for_status()
    try:
        check_for_redirect(response)
        filename = get_filename(book_number)
        filepath = get_filepath(filename, folder='books/')
        with open(filepath, 'w') as book:
            book.write(response.text)
    except requests.exceptions.HTTPError:
        print("wrong url")


def main():
    folder = 'books'
    books_count = 10
    for book_number in range(1, books_count+1):
        download_txt(folder, book_number)


if __name__ == "__main__":
    main()
