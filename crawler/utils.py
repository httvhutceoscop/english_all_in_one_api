from urllib.parse import urlparse
import json
import os

HOST = "https://tienganhtflat.com"
HOST_MEDIA = "http://audio.tflat.vn"


def create_folder(path):
    """
    Tạo folder từ một đường dẫn được chỉ định.
    Nếu folder đã tồn tại, không làm gì cả.

    Args:
        path (str): Đường dẫn của folder cần tạo.
    """
    try:
        os.makedirs(path, exist_ok=True)
        print(f"✅ Folder '{path}' đã được tạo (hoặc đã tồn tại).")
    except Exception as e:
        print(f"❌ Lỗi khi tạo folder '{path}': {e}")


def save_to_json(data, directory="data", filename="all_quotes.json"):
    create_folder(directory)  # Tạo folder nếu chưa tồn tại
    filepath = os.path.join(directory, filename)
    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def remove_domain_from_url(url):
    """
    Kiểm tra xem chuỗi có phải là URL hay không và loại bỏ domain nếu đúng.

    Args:
        url (str): Chuỗi cần kiểm tra.

    Returns:
        str: Chuỗi không chứa domain nếu là URL, ngược lại trả về chuỗi ban đầu.
    """
    try:
        parsed_url = urlparse(url)
        # Kiểm tra nếu chuỗi là URL hợp lệ (có scheme và netloc)
        if parsed_url.scheme and parsed_url.netloc:
            return parsed_url.path  # Trả về phần path của URL
        return url  # Nếu không phải URL, trả về chuỗi ban đầu
    except Exception as e:
        print(f"❌ Lỗi khi xử lý URL '{url}': {e}")
        return url
