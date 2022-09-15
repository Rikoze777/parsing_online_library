import os
import requests
from pathvalidate import sanitize_filename
from bs4 import BeautifulSoup
import collections
collections.Callable = collections.abc.Callable
from urllib.parse import urljoin


def parse_book_prop(response, book_number, txt_folder, image_folder):
    url = f"https://tululu.org/b{book_number}/"
    soup = BeautifulSoup(response.text, 'lxml')
    soup_text = soup.find('body').find('h1')
    content_text = soup_text.text
    try:
        check_for_redirect(response)
        soup_img = soup.find(class_= 'bookimage').find('img')['src']
    except requests.exceptions.HTTPError:
        soup_img = "/images/nopic.gif"
    image_url = urljoin(url, soup_img)
    filename = "".join((content_text.split('::'))[0].strip())
    filename = (f"{sanitize_filename(filename)}")
    filepath = os.path.join(txt_folder, filename)
    imagename = "".join(image_url.split('/')[-1])
    imagepath = os.path.join(image_folder, imagename)
    return filepath, imagepath, image_url


def check_for_redirect(response):
    if response.history == []:
        pass
    else:
        raise requests.exceptions.HTTPError('main page')


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


def download_image(response, imagepath, image_url, folder="image/"):
    os.makedirs(folder, exist_ok=True)
    image_response = requests.get(image_url)
    image_response.raise_for_status()
    try:
        check_for_redirect(response)
        with open(imagepath, 'wb') as image:
            image.write(image_response.content)
    except requests.exceptions.HTTPError:
        print("Redirect to main")


def download_txt(response, filepath, folder="books/"):
    os.makedirs(folder, exist_ok=True)
    try:
        check_for_redirect(response)
        with open(filepath, 'w') as book:
            book.write(response.text)
    except requests.exceptions.HTTPError:
        print("Redirect to main")


def main():
    txt_folder = 'books/'
    image_folder = 'image/'
    books_count = 10
    for book_number in range(1, books_count+1):
        txt_response = fetch_download_response(book_number)
        page_response = fetch_page_response(book_number)
        txtpath, imagepath, image_url = parse_book_prop(page_response, book_number, txt_folder, image_folder)
        download_txt(txt_response, txtpath, txt_folder)
        download_image(page_response, imagepath, image_url, image_folder)


if __name__ == "__main__":
    main()
