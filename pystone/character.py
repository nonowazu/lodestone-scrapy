from typing import List

from bs4 import BeautifulSoup as bs

from pystone.types import Definitions


class Character:
    def __init__(self, *, html: str, definitions: List[Definitions]):
        self._soup = bs(html)

