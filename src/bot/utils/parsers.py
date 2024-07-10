# TODO: remake everything here
from bs4 import BeautifulSoup
import httpx


def get_group_title(html: str) -> str | None:
    soup = BeautifulSoup(html, 'html.parser')
    try:
        title = soup.find('meta', property='og:title')['content']  # type: ignore
    except Exception:
        return None
    return str(title)


def get_group_description(html: str) -> str | None:
    soup = BeautifulSoup(html, 'html.parser')
    try:
        description = soup.find('meta', property='og:description')['content']  # type: ignore
    except Exception:
        return None
    return str(description)


async def parse_telegram_webpage(url: str) -> tuple[str | None, str | None]:
    """Returns group title, description from url"""
    async with httpx.AsyncClient() as client:
        response = await client.get(url)
        if response.status_code != 200:
            raise httpx.HTTPError(message=f'Error occured when tried to get response from {url}')
        group_title = get_group_title(response.content.decode())
        group_descrpiption = get_group_description(response.content.decode())
    return group_title, group_descrpiption
