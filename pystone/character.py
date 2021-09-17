from typing import List, Optional, Tuple

from requests import Session

from pystone.definition import Definition


class Character:
    def __init__(self, *, definitions: List[Definition]):
        self.definitions = {(x.name): x for x in definitions}

    def __getattr__(self, name):
        if name in self.definitions:
            return self.definitions[name]

    def to_json(self):
        json = {}
        for definition in self.definitions.values():
            json.update(definition.to_json())
        return json
