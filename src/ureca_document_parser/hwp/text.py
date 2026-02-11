"""HWP character scanning and text extraction utilities."""

from __future__ import annotations

import struct
from collections.abc import Iterator
from dataclasses import dataclass

# ---------------------------------------------------------------------------
# PARA_TEXT character codes
# ---------------------------------------------------------------------------
# Extended control characters occupy 8 uint16 = 16 bytes total.
EXTENDED_CTRL_CHARS = frozenset(range(0, 9)) | {11, 12} | frozenset(range(14, 24))
EXTENDED_CTRL_SIZE = 16  # bytes (8 × uint16)

CHAR_TAB = 9
CHAR_LINE_BREAK = 10
CHAR_TABLE_OBJECT = 11  # GSO (table, image 등) marker
CHAR_PARAGRAPH_END = 13
PRINTABLE_THRESHOLD = 32


@dataclass(slots=True)
class CharInfo:
    """Character information extracted from PARA_TEXT bytes."""

    code: int  # uint16 character code
    offset: int  # byte offset within PARA_TEXT data
    size: int  # bytes consumed by this character (2 or 16)


def read_bstr(data: bytes, offset: int) -> tuple[str, int]:
    """Read an HWP BSTR (UINT16 length + UTF-16LE chars) from *data*.

    Returns (decoded_string, new_offset).
    """
    if offset + 2 > len(data):
        return "", offset
    n_chars = struct.unpack_from("<H", data, offset)[0]
    offset += 2
    byte_len = n_chars * 2
    if offset + byte_len > len(data):
        return "", offset
    text = data[offset : offset + byte_len].decode("utf-16-le", errors="ignore")
    return text, offset + byte_len


def scan_para_chars(data: bytes) -> Iterator[CharInfo]:
    """HWPTAG_PARA_TEXT 바이트를 순회하며 CharInfo를 yield한다.

    확장 제어문자(16바이트)와 일반 문자(2바이트)를 올바르게 구분한다.
    """
    offset = 0
    length = len(data)
    while offset + 1 < length:
        code = struct.unpack_from("<H", data, offset)[0]
        if code in EXTENDED_CTRL_CHARS:
            yield CharInfo(code=code, offset=offset, size=EXTENDED_CTRL_SIZE)
            offset += EXTENDED_CTRL_SIZE
        else:
            yield CharInfo(code=code, offset=offset, size=2)
            offset += 2


def extract_text(data: bytes) -> str:
    """PARA_TEXT 바이트에서 사람이 읽을 수 있는 텍스트를 추출한다."""
    chars: list[str] = []
    for info in scan_para_chars(data):
        if info.code == CHAR_TAB:
            chars.append("\t")
        elif info.code == CHAR_LINE_BREAK:
            chars.append("\n")
        elif info.code >= PRINTABLE_THRESHOLD:
            chars.append(chr(info.code))
    return "".join(chars)


def has_table_marker(data: bytes) -> bool:
    """파라그래프에 테이블/GSO 마커(char 11)가 있는지 확인한다."""
    return any(info.code == CHAR_TABLE_OBJECT for info in scan_para_chars(data))
