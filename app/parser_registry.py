from app.parsers.ctp_settlement_parser import CtpSettlementParser


class ParserRegistry:
    def __init__(self) -> None:
        self.parsers = [
            CtpSettlementParser(),   # 👈 必须实例化
        ]

    def get_parser(self, file_path):
        for parser in self.parsers:
            if parser.can_parse(file_path):
                return parser
        return None