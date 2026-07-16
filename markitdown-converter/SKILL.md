---
name: markitdown-converter
description: Convert local documents and media to Markdown using Microsoft MarkItDown on Windows. Use when the user wants Codex to directly convert files to Markdown, install or verify MarkItDown without a project virtual environment, troubleshoot DOCX/PDF/PPTX/XLSX/HTML conversion, handle Windows paths, Desktop permissions, Chinese or UTF-8 output, or ffmpeg warnings.
---

# MarkItDown Converter

## Overview

Use Microsoft MarkItDown to convert local files to Markdown reliably on Windows. Prefer direct conversion without a project `.venv`: use a user/system MarkItDown command or run `python -m markitdown` from a Python environment where MarkItDown is installed.

## Workflow

1. Identify the input file exactly.
   - Check whether the extension is `.docx` vs old `.doc`; MarkItDown handles `.docx` more reliably than legacy `.doc`.
   - Quote all Windows paths, especially paths containing spaces, non-ASCII characters, or punctuation.

2. Choose a writable output location.
   - In restricted Codex workspaces, write output into the writable workspace unless another location is explicitly permitted.
   - If writing to Desktop fails with `PermissionError: [Errno 13] Permission denied`, write to the current workspace and tell the user where the file was created.

3. Locate MarkItDown without relying on a project virtual environment.
   - First try `markitdown` from PATH.
   - Then try `python -m markitdown` using the current Python interpreter.
   - If Codex bundled Python is available, use it with user-site packages rather than creating `.venv`.
   - Only use `<workspace>/.venv/Scripts/markitdown.exe` as a legacy fallback if it already exists.

4. Install only when missing.
   - Prefer user-level install: `python -m pip install --user markitdown[all]`.
   - Network access may require user approval.
   - Do not recreate a project `.venv` unless the user explicitly asks for isolated installation.

5. Convert and verify.
   - Use the helper: `python C:\Users\Administrator\.codex\skills\markitdown-converter\scripts\convert_with_markitdown.py "input-file" --output "output.md" --workspace "C:\Users\Administrator\Desktop\markitdown"`.
   - Confirm the Markdown file exists and has nonzero length.
   - For Chinese text, read with UTF-8. If PowerShell displays mojibake, explain that console display encoding can be wrong even when the file is valid UTF-8.

## Common Windows fixes

- If `markitdown` is not recognized, try `python -m markitdown` before creating a virtual environment.
- If no normal `python` command exists, use Codex bundled Python when available.
- If output to Desktop is denied from Codex, output into the workspace, then ask the user to move or copy it if needed.
- If ffmpeg or avconv warning appears, it usually only affects audio/video conversion; document, spreadsheet, PDF, and HTML conversion can still work.
- If the file is legacy `.doc`, ask the user to save or export it as `.docx` first or use Word/LibreOffice conversion outside MarkItDown.

## Helper script

Use `scripts/convert_with_markitdown.py` to reduce quoting and path mistakes:

```powershell
python C:\Users\Administrator\.codex\skills\markitdown-converter\scripts\convert_with_markitdown.py "C:\path\input.docx" --output "C:\path\output.md" --workspace "C:\Users\Administrator\Desktop\markitdown"
```

The script tries PATH `markitdown`, then `python -m markitdown`, then an existing workspace `.venv` fallback. It prints the generated file path after verifying output.
