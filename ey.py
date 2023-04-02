from typing import Union, List, Dict
import httpx
import re
import sys
import os
from termcolor import cprint
from getkey import getkey
import json

with open('browser.json', 'r') as f:
    data = json.load(f)
    browser_cmd = data["browser_command"]
    u_agent = data["user_agent"]
    num_pages = data["num_pages"]

def search(query: str, num: int = num_pages, headers: Union[Dict[str, str], None] ={"User-Agent":
                u_agent}) -> List[Union[dict, str]]:

    results: List[Union[dict, str]] = []

    base_url: str = "https://www.google.com/search?q={}&num=30&hl=en"

    page: str = httpx.get(base_url.format(query), headers=headers).text

    web: str = '<div class="yuRUbf"><a href="(.*?)" data-jsarwt=".*?" ' \
                   'data-usg=".*?" data-ved=".*?"><br><h3 class="LC20lb MBeuO DKV0Md">(.*?)</h3>.*?' \
                   '<div class="VwiC3b yXK7lf MUxGbd yDYNvb lyLwlc lEBKkf" style="-webkit-line-clamp:2">' \
                   '<span>(.*?)</span></div>'

    for i in re.findall(pattern=web, string=page):
        results.append({
            "url": i[0],
            "title": i[1],
            "description": re.sub('<[^<>]+>', '', i[2])
        })

    return results[:num if len(results) > num else len(results)]

def chunks(lst, n):
    """Yield successive n-sized chunks from lst."""
    for i in range(0, len(lst), n):
        yield lst[i:i + n]

def trunc_desc(string):
    out = (string[:155] + '..') if len(string) > 157 else string
    return out

def print_item(item,i):
    cprint(f"{item['title']}", "blue")
    cprint(f"{trunc_desc(item['description'])}", "white")
    cprint(f"[{i}]: {item['url']}\n", "green")

def show_results(page):
    for i, res in enumerate(split_res[page]):
        print_item(res,i+1)

def show_page(page):
    global pagination
    os.system('clear')
    show_results(page)
    if len(split_res[page]) == 5:
        print(f"Showing results {page*5 + 1} - {page*5 + 5}")
    else:
        print(f"Showing results {page*5 + 1} - {page*5 + len(split_res[page])} (last entry)")

    print("Enter [1-5] to open link, [n/l] for next/last results, or [q] to quit")

    while True:
        key = getkey()
        if key.isdigit() and int(key) > 0 and int(key) < 6:
            break
        elif key in ('n', 'l', 'q'):
            break
        else:
            continue

    if key.isdigit():
        i = int(key)
      
        #print(f"Browser open: {split_res[page][i-1]['url']}")
        os.system('clear')
        os.system(f"{browser_cmd} {split_res[page][i-1]['url']}")

    elif key == 'n':
        pagination += 1
        if pagination > len(split_res)-1:
            pagination = len(split_res)-1
        show_page(pagination)
    elif key == 'l':
        pagination -= 1
        if pagination < 0:
            pagination = 0
        show_page(pagination)
    elif key == 'q':
        os.system('clear')
        exit(0)

pagination = 0
args = sys.argv
args.pop(0)
if len(args) > 0:
    query = " ".join(args)
    results = search(query)
    split_res = list(chunks(results,5))
    show_page(pagination)
else:
    print("Ey, you didn't ask me anything! Bye then...")