# Project Rules

- Python 版本: 构建与校验脚本需要 Python ≥ 3.9(manual_manuscript.py 使用 str.removeprefix)。系统自带的 /usr/bin/python3 是 3.7 不可用,统一用 uv 管理的 3.12:$HOME/.local/share/uv/python/cpython-3.12-linux-x86_64-gnu/bin/python3.12。

- Any change to this project, even a one-line or one-character change, must be verified before it is considered done.
- Verification must include the relevant reviewer/check gate for the changed area. For book content this means the reviewer audit path; for layout this means browser/MCP inspection against the actual rendered page.
- Do not rely only on code inspection, build success, prior reviewer approval, or intention. Open the page yourself and inspect the current rendered result after rebuilding.
- If a change affects layout, navigation, scrolling, SVG, mobile display, or reading experience, verify with MCP on the live local preview before claiming it is fixed.
- If a change affects prose, facts, chapter structure, word count, or diagrams, rerun the appropriate static checks and update the reviewer audit evidence.
