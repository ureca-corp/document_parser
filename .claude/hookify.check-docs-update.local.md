---
name: check-docs-update
enabled: true
event: file
conditions:
  - field: file_path
    operator: regex_match
    pattern: ^src/.*\.py$
action: warn
---

📚 **문서 업데이트 확인 필요**

`src/` 디렉토리의 Python 파일이 수정됐습니다.

사용자가 코드 변경 시 문서를 함께 업데이트하도록 요청했습니다.

**다음을 확인하세요:**

- ✅ **공개 API 변경** → `docs/api-reference.md` 업데이트
  - `convert()` 함수 매개변수가 바뀌었나요?
  - 새로운 예외가 추가됐나요?

- ✅ **새 기능 추가** → 해당 가이드 문서 업데이트
  - `docs/guides/python-api.md` - 사용 예시 추가
  - `docs/guides/cli.md` - CLI 옵션 추가

- ✅ **새 포맷 지원** → 포맷 문서 추가
  - `docs/formats/` 디렉토리에 새 문서 생성
  - `mkdocs.yml` 네비게이션 업데이트

- ✅ **예제 코드** → 코드 스니펫 업데이트
  - docstring 예제 확인
  - README.md 퀵스타트 확인

**문서와 코드를 같은 커밋에 포함하세요.**
