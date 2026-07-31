from pathlib import Path
import sys

if len(sys.argv) != 2:
    print("Usage: python Tools/atlas_apply.py <target-file>")
    raise SystemExit(1)

target = Path(sys.argv[1])

print("Paste new content. Finish with Ctrl+D.")

content = sys.stdin.read()

target.parent.mkdir(parents=True, exist_ok=True)
target.write_text(content, encoding="utf-8")

print(f"Updated: {target}")
