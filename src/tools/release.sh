#!/usr/bin/env bash
# ขึ้นเว็บจริงทางนี้ทางเดียว (ระหว่างยิงแอด): build → ทดสอบทางแอด (/go → LIFF → ฟอร์ม → รูป → จบ) + ทางเบราว์เซอร์ (ปุ่ม/QR/ไม่มีไลน์) → ผ่านครบถึง push
# ไม่ผ่านข้อไหน = ไม่ขึ้น เว็บจริงยังเป็นเวอร์ชันเดิม
set -euo pipefail
cd "$(dirname "$0")/../.."
python3 src/site-src/build.py
(curl -s -o /dev/null localhost:8090 || (python3 -m http.server 8090 >/dev/null 2>&1 &)); sleep 1
out=$(node src/tools/liff.js 2>&1); echo "$out" | tail -4
echo "$out" | grep -q "doneView shown: true" || { echo "FAIL: ทางแอด (LIFF) ไม่จบ"; exit 1; }
echo "$out" | grep -q "closeWindow called: true" || { echo "FAIL: ไม่กลับแชท"; exit 1; }
echo "$out" | grep -q "sent to chat: \[{" || { echo "FAIL: ไม่ส่งข้อความเข้าแชท (ห้องแชทไม่เกิด)"; exit 1; }
echo "$out" | grep -q "posts: lead photo photo photo photo photo done" || { echo "FAIL: ส่งลีด/รูปไม่ครบ"; exit 1; }
echo "$out" | grep -q "ads conversion: true" || { echo "FAIL: Google Ads conversion ไม่ยิง"; exit 1; }
echo "$out" | grep -q "meta pixel: true" || { echo "FAIL: Meta Pixel ส่งรูปครบไม่ยิง"; exit 1; }
echo "$out" | grep -q "errors: \[\]" || { echo "FAIL: มี JavaScript error"; exit 1; }
h=$(node src/tools/handoff.js 2>&1); echo "$h" | tail -3
echo "$h" | grep -q "desktop qr svg: 1" || { echo "FAIL: QR คอม"; exit 1; }
echo "$h" | grep -q "done shown: true" || { echo "FAIL: ทางไม่มีไลน์"; exit 1; }
grep -q "fbq\|trackCustom" assets/site.js || { echo "FAIL: tracking หาย"; exit 1; }
git add -A
git diff --cached --quiet && { echo "ไม่มีอะไรเปลี่ยน"; exit 0; }
git commit -q -m "${1:-release}

Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>
Claude-Session: https://claude.ai/code/session_016ApbNuWGkd5qjRpkoGMv7a"
git push -q origin main && echo "PASS + pushed: $(git log --oneline -1)"
