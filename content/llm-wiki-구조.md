---
title: LLM 위키 구조
type: 개념
description: 이 저장소를 위키·RAG·편집 세 렌즈로 쓰는 단일 원본 구조 개요
tags:
  - meta
---

이 저장소는 세 가지 렌즈로 동시에 쓰입니다.

- **원본**: `content/` 폴더의 `.md` 파일들 (단일 진실 원본)
- **위키 뷰**: Quartz가 `[[링크]]`·백링크·그래프로 렌더링
- **RAG**: 같은 폴더를 Claude Project 등에 연결

작성은 대부분 [[index|홈]]을 기점으로 AI가 md를 쓰고 커밋합니다.
