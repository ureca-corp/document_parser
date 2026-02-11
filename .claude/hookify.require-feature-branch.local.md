---
name: require-feature-branch
enabled: true
event: bash
pattern: git\s+commit
action: warn
---

⚠️ **Feature 브랜치 확인 필요**

`git commit` 명령을 실행하려고 합니다.

**현재 main 브랜치가 아닌지 확인하세요!**

사용자가 모든 작업을 feature 브랜치에서 하도록 요청했습니다.

**권장 워크플로우:**
1. 현재 브랜치 확인: `git branch --show-current`
2. main에 있다면: `git checkout -b feature/descriptive-name`
3. Feature 브랜치에서 커밋 진행
4. PR을 통해 main에 merge

**예시:**
```bash
git checkout -b feature/add-pdf-support
git add .
git commit -m "feat: PDF 파서 추가"
git push origin feature/add-pdf-support
# GitHub에서 PR 생성
```
