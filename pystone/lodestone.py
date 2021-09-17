from typing import Union, List
from pathlib import Path
from json import loads

from requests_cache import CachedSession as Session
# from requests import Session

from pystone.types import MetaDict
from pystone.definition import Definition
from pystone.character import Character

LODESTONE_BASE_URL = 'finalfantasyxiv.com/lodestone'


class Lodestone:
    def __init__(self, *, json_base: Union[str, Path]):
        if isinstance(json_base, str):
            json_base = Path(json_base)
        self.json_base: Path = json_base

        # read meta.json
        with open(json_base / 'meta.json') as f:
            self.meta: MetaDict = loads(f.read())
        self.session = Session()
        # self.session.headers.update({
        #     'User-Agent': self.meta['userAgentDesktop']
        # })

    def get_character_by_id(self, id: Union[str, int]) -> None:
        profile_json_files = (self.json_base / 'profile').expanduser().glob('*.json')
        definitions: List[Definition] = []

        for profile in profile_json_files:
            url = self.meta['applicableUris'][f'profile/{profile.name}']
            d = Definition(profile, url, session=self.session)
            d.process({'id': str(id)})
            definitions.append(d)

        return Character(definitions=definitions)
