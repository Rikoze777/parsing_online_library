import json
import os

from jinja2 import Environment, FileSystemLoader, select_autoescape
from livereload import Server
from more_itertools import chunked


def on_load():
    env = Environment(
        loader=FileSystemLoader('.'),
        autoescape=select_autoescape(['html', 'xml'])
    )
    template = env.get_template('template.html')
    with open("books_dump.json", "r") as my_file:
        books_json = my_file.read()

    books = json.loads(books_json)
    books_per_page = 10
    books_chunked = list(chunked(books, books_per_page))
    pages_count = len(books_chunked)
    os.makedirs('pages/', exist_ok=True)
    for count, chunk in enumerate(books_chunked, 1):
        page_rows = 2
        page_chunk = list(chunked(chunk, page_rows))
        rendered_page = template.render(books=page_chunk,
                                        pages=pages_count,
                                        count=count)
        pages_path = os.path.join('pages/', f'index{count}.html')
        with open(pages_path, 'w', encoding="utf8") as file:
            file.write(rendered_page)


if __name__ == "__main__":
    on_load()

    server = Server()
    server.watch("template.html", on_load)
    server.serve(root=".")
