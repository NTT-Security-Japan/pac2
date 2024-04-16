import re
import uuid


def is_valid_url(url: str) -> bool:
    # 正規表現でhttpまたはhttpsのURLをマッチさせる
    pattern = re.compile(
        r'^(http|https)://(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+[A-Z]{2,6}\.?|localhost|\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})(?::\d+)?(?:/?|[/?]\S+)$', re.IGNORECASE)
    return bool(pattern.match(url))


def is_valid_flowmanagement_connection_id(id: str) -> bool:
    pattern = re.compile(
        r'shared-flowmanagemen-[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12}')
    return bool(pattern.match(id))


def is_valid_uuid(uuid_str: str) -> bool:
    try:
        # UUIDの文字列を解析して、それが正しい形式かどうかを確認する
        uuid_obj = uuid.UUID(uuid_str)
        return str(uuid_obj) == uuid_str
    except ValueError:
        return False


def is_valid_32chars_hex(string: str) -> bool:
    # 32文字の0-9, a-f, A-Fをマッチさせる正規表現
    pattern = re.compile(r'^[0-9a-fA-F]{32}$')
    return bool(pattern.match(string))


def is_valid_xorkey(key: str) -> bool:
    raise NotImplementedError("Not implemented yet.")
