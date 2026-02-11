"""HWP table parsing — 3-phase table extraction from binary records."""

from __future__ import annotations

import struct

from ..models import Paragraph, Table, TableCell, TableRow
from .records import (
    CTRL_TABLE_ID,
    HWPTAG_CTRL_HEADER,
    HWPTAG_LIST_HEADER,
    HWPTAG_PARA_HEADER,
    HWPTAG_PARA_TEXT,
    HWPTAG_TABLE,
    RecordCursor,
)
from .text import extract_text, has_table_marker


def read_ctrl_id(data: bytes) -> int:
    """CTRL_HEADER 데이터에서 컨트롤 타입 ID(uint32 LE)를 읽는다."""
    if len(data) >= 4:
        return struct.unpack_from("<I", data, 0)[0]
    return 0


def find_table_ctrl(cursor: RecordCursor, para_level: int) -> int | None:
    """Phase 1: CTRL_HEADER(tbl) 레코드를 찾아 ctrl_level을 반환한다.

    테이블이 아니거나 다음 문단에 도달하면 None을 반환한다.
    """
    while cursor.has_next():
        rec = cursor.peek()
        if rec is None:
            break
        if rec.tag == HWPTAG_CTRL_HEADER and len(rec.data) >= 4:
            ctrl_id = read_ctrl_id(rec.data)
            if ctrl_id == CTRL_TABLE_ID:
                ctrl_level = rec.level
                cursor.advance()
                return ctrl_level
        # 같은/상위 레벨의 다음 문단을 만나면 중단
        if rec.tag == HWPTAG_PARA_HEADER and rec.level <= para_level:
            return None
        cursor.advance()
    return None


def read_table_dimensions(cursor: RecordCursor) -> tuple[int, int]:
    """Phase 2: HWPTAG_TABLE 레코드에서 (n_rows, n_cols)를 읽는다."""
    rec = cursor.peek()
    if rec is not None and rec.tag == HWPTAG_TABLE:
        tbl_data = rec.data
        cursor.advance()
        if len(tbl_data) >= 8:
            n_rows = struct.unpack_from("<H", tbl_data, 4)[0]
            n_cols = struct.unpack_from("<H", tbl_data, 6)[0]
            return n_rows, n_cols
    return 0, 0


def collect_table_cells(
    cursor: RecordCursor, ctrl_level: int, n_rows: int, n_cols: int
) -> Table:
    """Phase 3: LIST_HEADER + PARA_TEXT에서 셀 내용을 수집하여 Table을 빌드한다.

    셀 내부에 중첩 테이블 마커가 있으면 재귀적으로 파싱한다.
    """
    cell_contents: list[list[Paragraph | Table]] = []
    current_cell: list[Paragraph | Table] = []
    in_cell = False

    while cursor.has_next():
        rec = cursor.peek()
        if rec is None:
            break

        # 테이블 종료: ctrl_level 이하 레벨의 PARA_HEADER를 만남
        if rec.level <= ctrl_level and rec.tag == HWPTAG_PARA_HEADER:
            if in_cell:
                cell_contents.append(current_cell)
            break

        if rec.tag == HWPTAG_LIST_HEADER and rec.level == ctrl_level + 1:
            # 새 셀 시작
            if in_cell:
                cell_contents.append(current_cell)
            current_cell = []
            in_cell = True

        elif rec.tag == HWPTAG_PARA_TEXT and in_cell:
            # 중첩 테이블 마커 확인
            if has_table_marker(rec.data):
                para_level = rec.level
                cursor.advance()  # 현재 PARA_TEXT 소비
                nested = try_parse_table(cursor, para_level)
                if nested and nested.rows:
                    current_cell.append(nested)
                continue
            text = extract_text(rec.data).strip()
            if text:
                current_cell.append(Paragraph(text=text))

        cursor.advance()
    else:
        # 레코드 끝까지 도달
        if in_cell:
            cell_contents.append(current_cell)

    # 수집된 셀 내용으로 Table 객체 생성
    table = Table()
    cell_idx = 0
    for _ in range(n_rows):
        row = TableRow()
        for _ in range(n_cols):
            cell = TableCell()
            if cell_idx < len(cell_contents):
                cell.content = cell_contents[cell_idx]
            row.cells.append(cell)
            cell_idx += 1
        table.rows.append(row)

    return table


def try_parse_table(cursor: RecordCursor, para_level: int) -> Table | None:
    """테이블 파싱을 시도한다. 실패 시 None을 반환한다."""
    ctrl_level = find_table_ctrl(cursor, para_level)
    if ctrl_level is None:
        return None

    n_rows, n_cols = read_table_dimensions(cursor)
    if n_rows == 0 or n_cols == 0:
        return None

    return collect_table_cells(cursor, ctrl_level, n_rows, n_cols)
