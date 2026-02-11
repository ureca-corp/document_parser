"""HWP binary record parsing — low-level record stream handling.

A record header is a 4-byte (uint32 LE) value:
    [tag_id: 10 bits][level: 10 bits][size: 12 bits]
If size == 0xFFF (EXTENDED_SIZE_SENTINEL), the next 4 bytes hold the real size.
"""

from __future__ import annotations

import struct
from dataclasses import dataclass

# ---------------------------------------------------------------------------
# Record header bit layout
# ---------------------------------------------------------------------------
TAG_BITS = 10
LEVEL_BITS = 10

TAG_MASK = (1 << TAG_BITS) - 1  # 0x3FF
LEVEL_MASK = (1 << LEVEL_BITS) - 1  # 0x3FF
SIZE_MASK = (1 << 12) - 1  # 0xFFF
EXTENDED_SIZE_SENTINEL = SIZE_MASK  # 0xFFF — "real size in next 4 bytes"

# ---------------------------------------------------------------------------
# HWP tag IDs  (HWPTAG_BEGIN = 16)
# ---------------------------------------------------------------------------
HWPTAG_STYLE = 26  # HWPTAG_BEGIN + 10
HWPTAG_PARA_HEADER = 66
HWPTAG_PARA_TEXT = 67
HWPTAG_CTRL_HEADER = 71
HWPTAG_LIST_HEADER = 72
HWPTAG_TABLE = 77  # HWPTAG_BEGIN + 61

# ---------------------------------------------------------------------------
# Control type ID
# ---------------------------------------------------------------------------
CTRL_TABLE_ID = struct.unpack(">I", b"tbl ")[0]  # 0x74626c20


@dataclass(slots=True)
class Record:
    """A single parsed HWP binary record."""

    tag: int
    level: int
    data: bytes


class RecordCursor:
    """레코드 리스트를 순회하는 커서."""

    def __init__(self, records: list[Record], start: int = 0) -> None:
        self._records = records
        self._pos = start

    @property
    def pos(self) -> int:
        return self._pos

    @pos.setter
    def pos(self, value: int) -> None:
        self._pos = value

    def has_next(self) -> bool:
        return self._pos < len(self._records)

    def peek(self) -> Record | None:
        return self._records[self._pos] if self.has_next() else None

    def advance(self) -> Record:
        rec = self._records[self._pos]
        self._pos += 1
        return rec


def parse_records(data: bytes) -> list[Record]:
    """바이너리 레코드 스트림을 Record 리스트로 파싱한다."""
    records: list[Record] = []
    offset = 0
    data_len = len(data)

    while offset + 4 <= data_len:
        header = struct.unpack_from("<I", data, offset)[0]
        tag = header & TAG_MASK
        level = (header >> TAG_BITS) & LEVEL_MASK
        size = (header >> (TAG_BITS + LEVEL_BITS)) & SIZE_MASK
        offset += 4

        if size == EXTENDED_SIZE_SENTINEL:
            if offset + 4 > data_len:
                break
            size = struct.unpack_from("<I", data, offset)[0]
            offset += 4

        if offset + size > data_len:
            break

        records.append(Record(tag=tag, level=level, data=data[offset : offset + size]))
        offset += size

    return records
