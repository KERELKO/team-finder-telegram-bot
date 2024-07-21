from bs4 import BeautifulSoup
import httpx


def get_group_title(html: str) -> str | None:
    soup = BeautifulSoup(html, 'html.parser')
    result = soup.find('meta', property='og:title')
    if not result:
        return None
    description = result['content']  # type: ignore
    return str(description)


def get_group_description(html: str) -> str | None:
    soup = BeautifulSoup(html, 'html.parser')
    result = soup.find('meta', property='og:description')
    if not result:
        return None
    description = result['content']  # type: ignore
    return str(description)


async def parse_telegram_webpage(url: str) -> tuple[str | None, str | None]:
    """Returns group title, group description from the url"""
    async with httpx.AsyncClient() as client:
        response = await client.get(url)
        response.raise_for_status()
        group_title = get_group_title(response.content.decode())
        group_descrpiption = get_group_description(response.content.decode())
    return group_title, group_descrpiption
