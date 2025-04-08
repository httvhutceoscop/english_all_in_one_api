import requests
from bs4 import BeautifulSoup
import time
from utils import save_to_json, HOST, HOST_MEDIA, remove_domain_from_url, get_text_or_empty

TOTAL_PAGE = 6
CATEGORY = "english-adventure-words"
BASE_URL = "https://tienganhtflat.com/blog/cat/{}?page={}&per-page=18"
API_DIR = f"api/{CATEGORY}"


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

        if not contents:
            print("✅ Không còn dữ liệu, dừng lại.")
            break

        for block in contents:
            a_href = HOST + \
                remove_domain_from_url(
                    get_text_or_empty(block, "h3 a", "href"))
            words_list = crawl_vocab(a_href)
            img_thumb = HOST + \
                remove_domain_from_url(
                    get_text_or_empty(block, ".img-thumb", "src"))
            title = get_text_or_empty(block, "h3 a")
            title_vi = get_text_or_empty(block, "div p:nth-of-type(1)")
            viewer = get_text_or_empty(block, "div p span:nth-of-type(2)")
            # detail_content = crawl_page_content(a_href)

            obj = {
                "id": count,
                "a_href": a_href,
                "img_thumb": img_thumb,
                "title": title,
                "title_vi": title_vi,
                "viewer": viewer,
                "category": CATEGORY,
                "vocab": words_list,
                "page": page,
            }

            all_contents.append(obj)
            page_contents.append(obj)
            count += 1

        save_to_json(page_contents, directory=API_DIR,
                     filename=f"{page}.json")
        print(f"✅ Đã lưu {len(page_contents)} content từ trang {page}.")

        page += 1
        print(f"✅ Nghỉ 5s giữa các lần request để tránh bị chặn.")
        time.sleep(5)  # nghỉ 1s giữa các lần request để tránh bị chặn

        if CATEGORY and page > TOTAL_PAGE:
            print("✅ Đã lấy đủ danh ngôn cho danh mục:", CATEGORY)
            break

    return all_contents


def crawl_vocab(url):
    """Thu thập từ vựng từ URL và trả về danh sách từ vựng."""
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
    except requests.RequestException as e:
        print(f"❌ Lỗi khi truy cập trang {url}: {e}")
        return []

    soup = BeautifulSoup(response.text, "html.parser")
    words_list = soup.select(".well .words-list .item-content")

    words = []
    count = 1
    for word in words_list:
        img_thumb = HOST_MEDIA + \
            remove_domain_from_url(
                get_text_or_empty(word, ".img-thumb", "src"))
        pronunciation = word.select_one(
            "div p a").next_sibling.strip() if word.select_one("div p a") else ""
        word_type = word.select_one(
            "div p b").next_sibling.strip() if word.select_one("div p b") else ""
        word_type = word_type.replace("\n", "").replace(":", "")
        explain = word.select_one("div p:nth-of-type(2) b:nth-of-type(1)").next_sibling.strip(
        ) if word.select_one("div p:nth-of-type(2) b:nth-of-type(1)") else ""
        text_en = get_text_or_empty(word, "div p b")
        text_vi = get_text_or_empty(word, "div p i")
        audio = HOST_MEDIA + \
            remove_domain_from_url(get_text_or_empty(word, "div p a", "href"))

        # Lấy ví dụ nếu có
        example_block = word.select_one("div p:nth-of-type(2)")
        example_en = example_block.select_one(
            "b:nth-of-type(2)").next_sibling.strip() if word.select_one("b:nth-of-type(2)") else ""
        example_vi = get_text_or_empty(example_block, "i")

        words.append({
            "id": count,
            "img_thumb": img_thumb,
            "text_en": text_en,
            "word_type": word_type,
            "text_vi": text_vi,
            "pronunciation": pronunciation,
            "audio": audio,
            "explain": explain,
            "example_en": example_en,
            "example_vi": example_vi
        })

        count += 1

    return words


crawl_all()
# a = crawl_vocab("https://tienganhtflat.com/blog/toeic-words-media")
# print(a)
