// 빌드가 낸 JS를 실제로 파싱해본다.
//
// 왜 있는가: 2026-09-06, componentResources.ts가 템플릿 리터럴 안에 정규식을
// 담아 내보내다 백슬래시를 잃었다. 남은 `//`가 나머지 줄을 주석으로 만들어
// 번들 하나가 통째로 죽었는데, `npx quartz build`는 성공했고 배포도 초록이었다.
// 빌드는 생성한 문자열을 파싱해보지 않기 때문이다.
//
// ponytail: 파싱만 본다. 런타임 동작은 여기서 검증하지 않는다.

import { readdir, readFile, writeFile, mkdtemp, rm } from "node:fs/promises"
import { execFile } from "node:child_process"
import { join, extname, basename } from "node:path"
import { tmpdir } from "node:os"
import { promisify } from "node:util"

const run = promisify(execFile)
const root = process.argv[2] ?? "public"

async function* walk(dir) {
  for (const e of await readdir(dir, { withFileTypes: true })) {
    const p = join(dir, e.name)
    if (e.isDirectory()) yield* walk(p)
    else if (extname(p) === ".js") yield p
  }
}

// node --check는 .js를 CommonJS로, .mjs를 ES 모듈로 읽는다.
// 어느 쪽으로든 파싱되면 통과 — 우리가 잡으려는 건 구문 오류뿐이다.
async function parses(file) {
  const tmp = await mkdtemp(join(tmpdir(), "emitjs-"))
  try {
    const src = await readFile(file)
    for (const ext of [".js", ".mjs"]) {
      const probe = join(tmp, basename(file, ".js") + ext)
      await writeFile(probe, src)
      try {
        await run(process.execPath, ["--check", probe])
        return null
      } catch (err) {
        var last = err.stderr?.toString().trim() ?? String(err)
      }
    }
    return last
  } finally {
    await rm(tmp, { recursive: true, force: true })
  }
}

const bad = []
let n = 0
for await (const file of walk(root)) {
  n++
  const err = await parses(file)
  if (err) bad.push([file, err])
}

if (bad.length) {
  for (const [file, err] of bad) console.error(`\n✗ ${file}\n${err}`)
  console.error(`\n${bad.length}/${n}개 파일이 파싱되지 않는다.`)
  process.exit(1)
}
console.log(`emitted JS ${n}개 전부 파싱됨`)
