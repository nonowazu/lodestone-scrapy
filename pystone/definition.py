from pathlib import Path
from typing import Dict, Union, Generic, TypeVar, Optional
from json import loads
from re import compile

from bs4 import BeautifulSoup
from requests import Session

T = TypeVar('T')


class Reference(Generic[T]):
    """Represents a reference to something which may not exist yet."""
    def __init__(self, initial_value: Optional[T] = None):
        self._value = initial_value

    @property
    def value(self) -> Optional[T]:
        return self._value

    @value.setter
    def value(self, new_value: T):
        self._value = new_value


class Element:
    """An element is something that has a selector property with other optional properties that refine that selection"""
    def __init__(self, name: str, data: Dict[str, str]):
        self.name = name
        self.selector = data['selector']  # I want this to error
        self.regex = None
        self.attribute = None

        if 'regex' in data:
            self.regex = compile(data['regex'])
        elif 'attribute' in data:
            self.attribute = data['attribute']

    def process(self, soup: BeautifulSoup) -> str:
        selection = soup.select_one(self.selector)
        if self.attribute is not None:
            # TODO: this is fragile; fix
            try:
                text = selection[self.attribute]
            except TypeError:  # NoneType
                text = ''
        else:
            try:
                text = selection.text
            except AttributeError:  # NoneType
                text = ''

        if self.regex is not None:
            # TODO: this is fragile; fix
            try:
                return self.regex.search(text).group(1)
            except AttributeError:  # NoneType
                return ''
        else:
            return text

    def __repr__(self):
        return f'<Element:{self.name}>'


class Container:
    """A container contains multiple elements or even other containers"""
    def __init__(self, name: str, soup_ref: Reference[BeautifulSoup] = Reference()):
        self.name = name
        self.entries = {}
        self.soup_ref = soup_ref
        self.selector_root = None

    def add(self, name: str, data: Union['Container', Element]):
        # TODO: raise error on overwriting key
        self.entries[name] = data

    def __getattr__(self, name):
        if name in self.entries:
            entry = self.entries[name]
            if isinstance(entry, Element):
                return entry.process(self.soup_ref.value)
            return self.entries[name]

    def __iter__(self):
        def internal_iterator():
            for entry in self.entries:
                yield entry
        return internal_iterator()

    def to_json(self):
        json = {self.name: {}}
        for entry in self.entries.values():
            if isinstance(entry, Element):
                json[self.name].update({entry.name: entry.process(self.soup_ref.value)})
            else:  # container
                json[self.name].update({entry.name: entry.to_json()})

        return json

    def set_selector_root(self, root):
        self.selector_root = root   

    def contains(self):
        """returns a list of everything this container contains"""
        return self.entries.keys()

    def __dir__(self):
        return self.entries.keys()

    def __repr__(self):
        return f'<Container:{self.name}>'


class Definition:
    """Takes in a json definition file and stores its name/definition"""
    def __init__(self, path: Union[str, Path], fmt_url: str, *, session: Optional[Session] = Session()):
        if isinstance(path, str):
            path = Path(path)
        if path.suffix != '.json':
            raise Exception('something is wrong.. why is this loading a non-json file?')
        self.fmt_url = fmt_url
        self.name = path.stem
        self.tree = Container(self.name)
        self.session = session

        with open(path.expanduser()) as f:
            json_data = loads(f.read())
            self._build_tree(json_data, self.tree)

    def _build_tree(self, json_data, root: Container):
        for k, v in json_data.items():
            if 'selector' in v:
                # we're making an element to add to our container
                root.add(k.lower(), Element(
                    k.lower(),
                    v
                ))
            else:
                # build a new Container and recurse
                c = Container(k.lower())
                # if 'ROOT' in k:
                #     selector_root = k['ROOT']['selector']

                self._build_tree(v, root=c)
                root.add(k.lower(), c)

    def process(self, vars: Dict[str, str]):
        response = self.session.get(
            self.fmt_url.format(
                **vars
            )
        )
        response.raise_for_status()
        with open(self.name + '.html', 'w') as f:
            f.write(response.text)
        self.tree.soup_ref.value = BeautifulSoup(response.text, features="html.parser")

    def to_json(self):
        return self.tree.to_json()

    def __getattr__(self, name):
        return getattr(self.tree, name)
