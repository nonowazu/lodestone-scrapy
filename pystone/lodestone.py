from typing import Union, Optional
from pathlib import Path

from requests import session, codes as status_codes

from pystone.types import LangOptions

LODESTONE_BASE_URL = 'finalfantasyxiv.com/lodestone'


class Lodestone:
    def __init__(self, *, json_base: Union[str, Path], lang: LangOptions = 'en', base_url: str = LODESTONE_BASE_URL):
        if isinstance(json_base, str):
            json_base = Path(json_base)

        self.session = session()

        self.url = f'https://{lang}.{base_url}'

    def get_character_by_id(self, id: Union[str, int]) -> None:
        # https://na.finalfantasyxiv.com/lodestone/character/11561543/
        response = self.session.get(f'{self.url}/character/{id}')

        if response.status_code != status_codes.ok:
            # TODO: error
            return None
