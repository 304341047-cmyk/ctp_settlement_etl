from __future__ import annotations

import re
from dataclasses import dataclass


@dataclass
class Section:
    name: str
    title: str
    content: str


SECTION_PATTERNS = [
    ("account_summary", r"资金状况"),
    ("deposit_withdrawal", r"出入金明细"),
    ("transaction_record", r"成交记录"),
    ("exercise_statement", r"行权明细"),
    ("position_closed", r"平仓明细"),
    ("positions_detail", r"持仓明细"),
    ("positions", r"持仓汇总"),
]


def split_sections(full_text: str) -> dict[str, Section]:
    matches = []

    for name, pattern in SECTION_PATTERNS:
        for m in re.finditer(pattern, full_text):
            matches.append(
                {
                    "name": name,
                    "title": m.group(0),
                    "start": m.start(),
                    "end": m.end(),
                }
            )

    matches.sort(key=lambda x: x["start"])

    sections: dict[str, Section] = {}
    for i, item in enumerate(matches):
        start = item["start"]
        end = matches[i + 1]["start"] if i + 1 < len(matches) else len(full_text)

        content = full_text[start:end].strip()
        sections[item["name"]] = Section(
            name=item["name"],
            title=item["title"],
            content=content,
        )

    return sections