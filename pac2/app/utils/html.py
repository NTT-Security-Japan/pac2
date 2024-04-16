from bs4 import BeautifulSoup


def remove_img_tag(html, src_host: str = None) -> str:
    soup = BeautifulSoup(html)
    for img_tag in soup.find_all('img', src=lambda s: 'graph.microsoft.com' in s if s else False):
        img_tag.decompose()

    return soup.__repr__()
