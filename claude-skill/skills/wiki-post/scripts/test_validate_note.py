#!/usr/bin/env python3
import importlib.util
import tempfile
import unittest
from pathlib import Path


MODULE_PATH = Path(__file__).with_name("validate-note.py")
SPEC = importlib.util.spec_from_file_location("validate_note", MODULE_PATH)
validate_note = importlib.util.module_from_spec(SPEC)
assert SPEC and SPEC.loader
SPEC.loader.exec_module(validate_note)


class ValidateNoteTests(unittest.TestCase):
    def run_gate(self, text: str, name: str = "note.md"):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory, name)
            path.write_text(text, encoding="utf-8")
            return validate_note.validate(path)

    def test_okf_v02_profile_passes(self):
        fails, _ = self.run_gate("""---
type: 도구
title: 예시
description: 한 줄 설명
tags: [okf, example]
status: stable
generated: { by: human:test, at: 2026-08-03T00:00:00Z }
verified: { by: human:test, at: 2026-08-03T01:00:00Z }
sources:
  - id: spec
    resource: https://example.com/spec
    title: Spec
---
주장이다.[^spec]

[^spec]: Spec
""")
        self.assertEqual([], fails)

    def test_profile_requires_tags(self):
        fails, _ = self.run_gate("""---
type: 개념
title: 예시
description: 설명
---
본문
""")
        self.assertTrue(any("tags" in failure for failure in fails))

    def test_source_requires_resource(self):
        fails, _ = self.run_gate("""---
type: 개념
title: 예시
description: 설명
tags: [test]
sources:
  - id: missing
---
본문[^missing]

[^missing]: Missing
""")
        self.assertTrue(any("resource" in failure for failure in fails))

    def test_footnote_must_join_source_id(self):
        fails, _ = self.run_gate("""---
type: 개념
title: 예시
description: 설명
tags: [test]
sources:
  - id: source-a
    resource: https://example.com/a
---
본문[^source-b]

[^source-b]: B
""")
        self.assertTrue(any("source-b" in failure for failure in fails))

    def test_attested_computation_requires_runtime(self):
        fails, _ = self.run_gate("""---
type: Attested Computation
title: 계산
description: 계산 설명
tags: [compute]
---
# Computation

```sql
SELECT 1
```
""")
        self.assertTrue(any("runtime" in failure for failure in fails))

    def test_verified_list_requires_at(self):
        fails, _ = self.run_gate("""---
type: 개념
title: 예시
description: 설명
tags: [test]
verified:
  - { by: human:test }
---
본문
""")
        self.assertTrue(any("at 누락" in failure for failure in fails))

    def test_reserved_filename_fails(self):
        fails, _ = self.run_gate("""---
type: 개념
title: 잘못된 이름
description: 설명
tags: [test]
---
본문
""", "index.md")
        self.assertTrue(any("예약" in failure for failure in fails))




FRONT = """---
type: 분석
title: 예시
description: 한 줄 설명
tags: [a, b]
---
"""


class CodeSpanAwareness(unittest.TestCase):
    """코드(펜스·인라인)는 산문이 아니다 — 마커·각주·강조 검사에서 제외한다."""

    def run_gate(self, body: str):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory, "note.md")
            path.write_text(FRONT + body, encoding="utf-8")
            return validate_note.validate(path)

    def test_regex_in_inline_code_is_not_a_footnote(self):
        fails, _ = self.run_gate("\n재현: `grep -oE '<link[^>]*rel'` 로 셌다.\n")
        self.assertEqual([f for f in fails if "각주" in f], [])

    def test_regex_in_fenced_block_is_not_a_footnote(self):
        fails, _ = self.run_gate("\n```bash\ngrep -oE 'cubic-bezier\\([^)]*\\)'\n```\n")
        self.assertEqual([f for f in fails if "각주" in f], [])

    def test_marker_inside_code_span_is_not_a_leftover(self):
        fails, _ = self.run_gate("\n초안은 `(검증 필요)` 마커로 유보했다.\n")
        self.assertEqual([f for f in fails if "검증 필요" in f], [])

    def test_real_marker_in_prose_still_fails(self):
        fails, _ = self.run_gate("\n이 수치는 (검증 필요) 이다.\n")
        self.assertTrue([f for f in fails if "검증 필요" in f])

    def test_real_footnote_still_checked(self):
        fails, _ = self.run_gate("\n주장이다.[^a]\n")
        self.assertTrue([f for f in fails if "각주 정의 누락" in f])

    def test_broken_emphasis_in_code_is_ignored(self):
        fails, _ = self.run_gate("\n`(주)**한글` 은 코드다.\n")
        self.assertEqual([f for f in fails if "깨진 강조" in f], [])


if __name__ == "__main__":
    unittest.main()
