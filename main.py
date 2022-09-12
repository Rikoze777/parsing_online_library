import os
import requests


def check_for_redirect(response):
    if response.history == []:
        pass
    else:
        raise requests.exceptions.HTTPError('main')


def get_books(book_path, books_count):
    requests.packages.urllib3.disable_warnings(
        requests.packages.urllib3.exceptions.InsecureRequestWarning)
    os.makedirs(book_path, exist_ok=True)
    for number_id in range(1, books_count+1):
        url = f"https://tululu.org/txt.php?id={number_id}"
        response = requests.get(url, verify=False)
        response.raise_for_status()
        try:
            check_for_redirect(response)
            filename = f"id{number_id}.txt"
            file_path = os.path.join(book_path, filename)
            with open(file_path, 'w') as book:
                book.write(response.text)
        except requests.exceptions.HTTPError:
            print("wrong url")


def main():
    book_path = 'books'
    books_count = 10
    get_books(book_path, books_count)


if __name__ == "__main__":
    main()
