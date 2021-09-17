from typing import Dict, Literal, Union, TypedDict

LangOptions = Literal['en']
Definition = Dict[str, Union[str, Dict[str, str]]]


class MetaDict(TypedDict):
    version: str
    userAgentDesktop: str
    userAgentMobile: str
    applicableUris: Dict[str, str]
