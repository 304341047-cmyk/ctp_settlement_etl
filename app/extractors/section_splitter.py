import re
from dataclasses import dataclass


@dataclass
class SectionBlock:
    key: str
    title: str
    content: str


SECTION_PATTERNS = [
    ("account_summary", r"资金状况"),
    ("transaction_record", r"成交记录"),
    ("exercise_statement", r"行权明细"),
    ("position_closed", r"平仓明细"),
    ("positions_detail", r"持仓明细"),
    ("positions", r"持仓汇总"),
]


def split_sections(text: str) -> dict[str, SectionBlock]:
    found = []

    for key, pattern in SECTION_PATTERNS:
        match = re.search(pattern, text)
        if match:
            found.append(
                {
                    "key": key,
                    "title": match.group(0),
                    "start": match.start(),
                }
            )

    found.sort(key=lambda x: x["start"])

    sections: dict[str, SectionBlock] = {}

    for i, item in enumerate(found):
        start = item["start"]
        end = found[i + 1]["start"] if i + 1 < len(found) else len(text)
        content = text[start:end]

        sections[item["key"]] = SectionBlock(
            key=item["key"],
            title=item["title"],
            content=content,
        )

    return sections


def require_section(sections: dict[str, SectionBlock], key: str) -> SectionBlock:
    if key not in sections:
        raise ValueError(f"未找到区块: {key}")
    return sections[key]