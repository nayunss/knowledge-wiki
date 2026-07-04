#!/usr/bin/env node
// 한글(CJK)과 마크다운 기호가 붙을 때 CommonMark 렌더링이 깨지는 걸 빌드 전에 자동 교정한다.
// 누가 어떤 도구로 작성하든 published 사이트에서는 안 깨지게 하는 안전망.
//
//   1) 닫는 `**` 바로 앞이 문장부호( ) ] 」 . , 등)이고 바로 뒤가 한글/영숫자면
//      그 볼드는 안 닫히고 별표가 노출된다(right-flanking 조건 실패).
//      예: `**총소유비용(TCO)**이다` → 해당 span을 <strong>…</strong>로 감싸 강제 렌더.
//   2) 숫자~숫자 / 영문~영문 범위 물결은 subscript로 먹혀 글자가 사라진다(`6~12` → `612`).
//      → en대시(–)로 치환.
//
// 코드펜스(``` / ~~~)와 인라인 코드(`...`)는 건드리지 않는다.
// 사용:  node scripts/fix-korean-markdown.mjs [contentDir]   (기본 content)
//        node scripts/fix-korean-markdown.mjs --selftest      (자체 테스트)

import { readdirSync, statSync, readFileSync, writeFileSync } from "node:fs"
import { join } from "node:path"

// 닫는 ** 앞에 오면 볼드가 안 닫히는 문장부호들
const CLOSE_PUNCT = ")\\]）］」』》”’.,%:;!?"
const brokenBold = new RegExp(`\\*\\*([^*\\n]*[${CLOSE_PUNCT}])\\*\\*(?=[0-9A-Za-z가-힣])`, "g")

// 인라인 코드(`...`) 밖에서만 치환 — 백틱 기준 분할 후 짝수 인덱스(코드 아님)만 손봄
function fixInline(s) {
  const parts = s.split("`")
  for (let i = 0; i < parts.length; i += 2) {
    parts[i] = parts[i]
      .replace(brokenBold, "<strong>$1</strong>")
      .replace(/([0-9])~([0-9])/g, "$1–$2")
      .replace(/([A-Za-z])~([A-Za-z])/g, "$1–$2")
  }
  return parts.join("`")
}

// 코드펜스 안은 통째로 건너뜀
export function fixText(text) {
  const lines = text.split("\n")
  let inFence = false
  for (let i = 0; i < lines.length; i++) {
    if (/^\s*(```|~~~)/.test(lines[i])) {
      inFence = !inFence
      continue
    }
    if (!inFence) lines[i] = fixInline(lines[i])
  }
  return lines.join("\n")
}

function walk(dir, acc = []) {
  for (const name of readdirSync(dir)) {
    const p = join(dir, name)
    if (statSync(p).isDirectory()) walk(p, acc)
    else if (name.endsWith(".md")) acc.push(p)
  }
  return acc
}

function selftest() {
  const cases = [
    ["**총소유비용(TCO)**이다", "<strong>총소유비용(TCO)</strong>이다"], // 깨짐 → 교정
    ["**구현자(a) → 오케스트레이터(b)**로", "<strong>구현자(a) → 오케스트레이터(b)</strong>로"], // 다중 괄호도
    ["**중요**한 것", "**중요**한 것"], // 앞이 한글 → 정상, 그대로
    ["**끝(gloss)**", "**끝(gloss)**"], // 뒤가 줄끝 → 정상, 그대로
    ["**끝(gloss)**,", "**끝(gloss)**,"], // 뒤가 문장부호 → 정상, 그대로
    ["6~12개월 → 6~12주", "6–12개월 → 6–12주"], // 범위 물결
    ["assistance~semi", "assistance–semi"],
    ["`a~1`은 코드", "`a~1`은 코드"], // 인라인 코드 보존
    ["```\n6~12\n```", "```\n6~12\n```"], // 코드펜스 보존
  ]
  let ok = true
  for (const [inp, exp] of cases) {
    const got = fixText(inp)
    if (got !== exp) {
      ok = false
      console.error(`FAIL: ${JSON.stringify(inp)}\n  exp ${JSON.stringify(exp)}\n  got ${JSON.stringify(got)}`)
    }
  }
  console.log(ok ? "selftest OK" : "selftest FAILED")
  process.exit(ok ? 0 : 1)
}

const arg = process.argv[2]
if (arg === "--selftest") selftest()

const root = arg || "content"
let changed = 0
for (const f of walk(root)) {
  const orig = readFileSync(f, "utf8")
  const fixed = fixText(orig)
  if (fixed !== orig) {
    writeFileSync(f, fixed)
    changed++
    console.log("fixed:", f)
  }
}
console.log(`[fix-korean-markdown] ${changed} file(s) fixed`)
