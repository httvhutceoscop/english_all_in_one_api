import requests
from bs4 import BeautifulSoup
import json
import time
import os
from utils import save_to_json, HOST, HOST_MEDIA, remove_domain_from_url

BASE_URL = "https://tienganhtflat.com/danh-ngon?page={}&per-page=18"
CAT_TINH_YEU = "tinh-yeu"
CAT_CUOC_SONG = "cuoc-song"
CAT_GIA_DINH = "gia-dinh"
CAT_TINH_BAN = "tinh-ban"
CAT_CONG_VIEC = "cong-viec"
DANH_NGON = {
    "tinh-yeu": "https://tienganhtflat.com/danhngon/cat/tinh-yeu?page={}&per-page=18",
    "cuoc-song": "https://tienganhtflat.com/danhngon/cat/cuoc-song?page={}&per-page=18",
    "gia-dinh": "https://tienganhtflat.com/danhngon/cat/gia-dinh?page={}&per-page=18",
    "tinh-ban": "https://tienganhtflat.com/danhngon/cat/tinh-ban?page={}&per-page=18",
    "cong-viec": "https://tienganhtflat.com/danhngon/cat/cong-viec?page={}&per-page=18"
}


def crawl_all_quotes(category):
    page = 1
    all_quotes = []

    while True:
        quotes = []
        BASE_URL = DANH_NGON[category]
        url = BASE_URL.format(page)
        print(f"Crawling page {page}: {url}")

        response = requests.get(url)
        if response.status_code != 200:
            print("❌ Lỗi khi truy cập trang:", url)
            break

        soup = BeautifulSoup(response.text, "html.parser")
        quote_blocks = soup.select(".well .row.item")

        # Nếu không còn danh ngôn nào, dừng lại
        if not quote_blocks:
            print("✅ Không còn dữ liệu, dừng lại.")
            break

        for block in quote_blocks:
            a_href = block.select_one(
                "h3 a")["href"] if block.select_one("h3 a") else ""
            a_href = remove_domain_from_url(a_href)
            a_href = HOST + a_href
            words_list = crawl_vocab(a_href)
            img_thumb = block.select_one(
                ".img-thumb")["src"] if block.select_one(".img-thumb") else ""
            img_thumb = remove_domain_from_url(img_thumb)
            img_thumb = HOST + img_thumb
            text_en = block.select_one("h3 a").get_text(
                strip=True) if block.select_one("h3 a") else ""

            text_vi = block.select_one(
                "p.hide-mobile").get_text(strip=True) if block.select_one("p.hide-mobile") else ""

            author = block.select_one("p.hide-mobile span i").get_text(
                strip=True) if block.select_one("p.hide-mobile span i") else ""
            if not author:
                author = block.select_one("p.hide-mobile span").get_text(
                    strip=True) if block.select_one("p.hide-mobile span") else ""

            viewer = block.select_one("p.hide-mobile span i.fa.fa-user").next_sibling.strip(
            ) if block.select_one("p.hide-mobile span i.fa.fa-user") else ""

            quote = {
                "a_href": a_href,
                "img_thumb": img_thumb,
                "text_en": text_en,
                "text_vi": text_vi,
                "author": author,
                "viewer": viewer,
                "category": category,
                "page": page,
                "vocab": words_list,
            }

            all_quotes.append(quote)
            quotes.append(quote)

        directory = f"api/danhngon/{category}"
        save_to_json(quotes, directory=directory, filename=f"{page}.json")
        print(f"✅ Đã lưu {len(quotes)} danh ngôn từ trang {page}.")

        page += 1
        time.sleep(1)  # nghỉ 1s giữa các lần request để tránh bị chặn
        if category and page > 4:
            print("✅ Đã lấy đủ danh ngôn cho danh mục:", category)
            break
        # break

    return all_quotes


def crawl_vocab(url):
    response = requests.get(url)
    if response.status_code != 200:
        print("❌ Lỗi khi truy cập trang:", url)
        return
    # Phân tích cú pháp HTML của trang

    soup = BeautifulSoup(response.text, "html.parser")
    words_list = soup.select(".words-list .item-content")
    words = []
    for word in words_list:
        img_thumb = word.select_one(
            ".img-thumb")["src"] if word.select_one(".img-thumb") else ""
        img_thumb = remove_domain_from_url(img_thumb)
        img_thumb = HOST_MEDIA + img_thumb
        word_type = word.select_one(
            "div p b").next_sibling.strip() if word.select_one("div p b") else ""
        word_type = word_type.replace("\n", "")
        pronoun = word.select_one(
            "div p a").next_sibling.strip() if word.select_one("div p a") else ""
        text_en = word.select_one(
            "div p b").get_text(strip=True) if word.select_one("div p b") else ""
        text_vi = word.select_one(
            "div p i").get_text(strip=True) if word.select_one("div p i") else ""
        audio = word.select_one(
            "div p a")["href"] if word.select_one("div p a") else ""
        audio = remove_domain_from_url(audio)
        audio = HOST_MEDIA + audio
        # Lấy ví dụ
        example_block = word.select_one("div p:nth-of-type(2)")
        ex_en = example_block.select_one("b").next_sibling.strip(
        ) if example_block and example_block.select_one("b") else ""
        ex_vi = example_block.select_one("i").get_text(
            strip=True) if example_block and example_block.select_one("i") else ""

        words.append({
            "img_thumb": img_thumb,
            "text_en": text_en,
            "word_type": word_type,
            "text_vi": text_vi,
            "pronoun": pronoun,
            "audio": audio,
            "ex_en": ex_en,
            "ex_vi": ex_vi
        })

    return words

# for category in DANH_NGON.keys():
    # crawl_all_quotes(category)

crawl_all_quotes(CAT_TINH_YEU)
# crawl_all_quotes(CAT_CUOC_SONG)
# crawl_all_quotes(CAT_GIA_DINH)
# crawl_all_quotes(CAT_TINH_BAN)
# crawl_all_quotes(CAT_CONG_VIEC)

# crawl_vocab(
#     "https://tienganhtflat.com/danhngon/the-way-to-get-started-is-to-quit-talking-and-begin-doing")
