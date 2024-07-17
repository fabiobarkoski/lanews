import re
from typing import Optional
from datetime import datetime
from dataclasses import dataclass

MONEY_CHECKER = re.compile(r"\$[\d+\.\,]+|[\d+\.\,]+\s(?:dollars|USD)")

@dataclass
class Picture:
    name: str
    link: str

@dataclass
class News:
    title: str
    date: datetime
    count: int
    contains_money: bool
    description: Optional[str] = None
    picture: Optional[Picture] = None

    @staticmethod
    def count_phrases(texts: list[str], phrases: str) -> int:
        count = 0
        for text in texts:
            if text is None:
                text = ""
            count += sum([1 for _ in re.findall(phrases+r"\b", text, re.I)])
        return count

    @staticmethod
    def contains_money(texts: list[str]) -> bool:
        have_money = False
        for text in texts:
            if text is None:
                text = ""
            if MONEY_CHECKER.findall(text):
                have_money = True
        return have_money

    def to_dict(self):
        return {
            "title": self.title,
            "description": self.description if self.description else "None",
            "date": self.date.isoformat(timespec="seconds"),
            "picture": self.picture.name if self.picture else "None",
            "count": str(self.count),
            "contains_money": str(self.contains_money)
        }