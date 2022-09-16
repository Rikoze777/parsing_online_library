import os
import requests
from pathvalidate import sanitize_filename
from bs4 import BeautifulSoup
import collections
collections.Callable = collections.abc.Callable
from urllib.parse import urljoin


def parse_book_page(response):
    soup = BeautifulSoup(response.text, 'lxml')
    soup_text = soup.find('body').find('h1')
    content_text = soup_text.text
    title = "".join((content_text.split('::'))[0].strip())
    title = (f"{sanitize_filename(title)}")
    print(title)
    return soup, title


def check_for_redirect(response):
    if response.history == []:
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


def download_comments(soup):
    soup_comments = soup.find_all(class_='texts')
    comments_list = [comment.text for comment in soup_comments]
    raw_comments = []
    for comment in comments_list:
        comment = comment.split(')')
        raw_comments.append(comment[-1])
    comments = "\n".join(raw_comments)
    print(comments)


def download_image(soup, book_number, folder):
    os.makedirs(folder, exist_ok=True)
    url = f"https://tululu.org/b{book_number}/"
    soup_img = soup.find(class_= 'bookimage').find('img')['src']
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
    txt_folder = 'books/'
    image_folder = 'image/'
    books_count = 10
    for book_number in range(1, books_count+1):
        txt_response = fetch_download_response(book_number)
        page_response = fetch_page_response(book_number)
        try:
            check_for_redirect(page_response)
            soup, title = parse_book_page(page_response)
            download_txt(txt_response, title, txt_folder)
            download_image(soup, book_number, image_folder)
            download_comments(soup)
        except:
            pass


if __name__ == "__main__":
    main()
