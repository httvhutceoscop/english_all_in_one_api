import requests
from bs4 import BeautifulSoup
import json
import time
import os
from utils import save_to_json, HOST, HOST_MEDIA, remove_domain_from_url, get_text_or_empty

CATEGORY = "blog-tieng-anh-can-ban"
# CATEGORY = "blog-tieng-anh-trung-cap"
BASE_URL = "https://tienganhtflat.com/blog/cat/{}?page={}&per-page=18"


def crawl_all():
    page = 1
    all_contents = []
    count = 1

    while True:
        page_contents = []
        url = BASE_URL.format(CATEGORY, page)
        print(f"Crawling page {page}: {url}")

        response = requests.get(url)
        if response.status_code != 200:
            print("❌ Lỗi khi truy cập trang:", url)
            break

        soup = BeautifulSoup(response.text, "html.parser")
        contents = soup.select(".well .row.item")

        # Nếu không còn danh ngôn nào, dừng lại
        if not contents:
            print("✅ Không còn dữ liệu, dừng lại.")
            break

        for block in contents:
            title = get_text_or_empty(block, "h3 a")
            a_href = HOST + \
                remove_domain_from_url(
                    get_text_or_empty(block, "h3 a", "href"))
            img_thumb = HOST + \
                remove_domain_from_url(
                    get_text_or_empty(block, ".img-thumb", "src"))
            viewer = get_text_or_empty(block, "p span:nth-of-type(2)")
            detail_content = crawl_page_content(a_href)

            obj = {
                "id": count,
                "title": title,
                "a_href": a_href,
                "img_thumb": img_thumb,
                "viewer": viewer,
                "category": CATEGORY,
                "detail_content": detail_content,
                "page": page,
            }

            all_contents.append(obj)
            page_contents.append(obj)
            count += 1

        directory = f"api/blog/{CATEGORY}"
        save_to_json(page_contents, directory=directory,
                     filename=f"{page}.json")
        print(f"✅ Đã lưu {len(page_contents)} content từ trang {page}.")

        page += 1
        time.sleep(2)  # nghỉ 1s giữa các lần request để tránh bị chặn

        if CATEGORY and page > 5:
            print("✅ Đã lấy đủ danh ngôn cho danh mục:", CATEGORY)
            break

    return all_contents


def crawl_page_content(url):
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
    except requests.RequestException as e:
        print(f"❌ Lỗi khi truy cập trang {url}: {e}")
        return ""

    soup = BeautifulSoup(response.text, "html.parser")
    page_content = soup.select(".well .detail .content")

    if page_content:
        for link in page_content[0].find_all("a"):
            link.replace_with(link.text)
        return str(page_content[0])
    return ""


crawl_all()
# crawl_page_content(
#     "https://tienganhtflat.com/blog/30-mu-cau-dung-bt-chuyn-vi-tay")
