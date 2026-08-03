#!/usr/bin/env python3
import importlib.util
import tempfile
import unittest
from pathlib import Path


MODULE_PATH = Path(__file__).with_name("validate-domain-brief.py")
SPEC = importlib.util.spec_from_file_location("validate_domain_brief", MODULE_PATH)
module = importlib.util.module_from_spec(SPEC)
assert SPEC and SPEC.loader
SPEC.loader.exec_module(module)


class DomainBriefTests(unittest.TestCase):
    def validate(self, text: str):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory, "00_domain_brief.md")
            path.write_text(text, encoding="utf-8")
            return module.validate(path)

    def test_complete_brief_passes(self):
        self.assertEqual([], self.validate("""# 도메인 브리프
- **도메인**: 분산 시스템
- **하위 분야**: 합의 알고리즘
- **대상 독자**: 백엔드 엔지니어

## 용어 기준 출처
- https://example.org/standard
- https://example.org/paper

## 핵심 용어
| 개념 | 채택 표기 | 첫 등장 표기 | 피할 표기 | 근거 |
|---|---|---|---|---|
| consensus | 합의 | 합의(consensus) | 컨센서스 | standard |
"""))

    def test_requires_two_sources(self):
        fails = self.validate("""# 도메인 브리프
- **도메인**: 분산 시스템
- **하위 분야**: 합의 알고리즘
- **대상 독자**: 백엔드 엔지니어
## 용어 기준 출처
- https://example.org/one
## 핵심 용어
| 개념 | 채택 표기 | 첫 등장 표기 | 피할 표기 | 근거 |
|---|---|---|---|---|
| consensus | 합의 | 합의(consensus) | 컨센서스 | standard |
""")
        self.assertTrue(any("2개 미만" in failure for failure in fails))


if __name__ == "__main__":
    unittest.main()
