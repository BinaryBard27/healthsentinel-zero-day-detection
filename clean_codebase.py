import os
import re
import tokenize
import io
import emoji
from pathlib import Path

TARGET_EXTS = {'.py', '.js', '.jsx', '.ts', '.tsx', '.html', '.css', '.md', '.json', '.bat', '.sh'}
EXCLUDE_DIRS = {'node_modules', 'venv', '.venv', '.git', '__pycache__'}

def remove_python_comments_and_docstrings(source):
    io_obj = io.StringIO(source)
    out = ""
    prev_toktype = tokenize.INDENT
    last_lineno = -1
    last_col = 0
    try:
        for tok in tokenize.generate_tokens(io_obj.readline):
            token_type = tok[0]
            token_string = tok[1]
            start_line, start_col = tok[2]
            end_line, end_col = tok[3]

            if start_line > last_lineno:
                last_col = 0
            if start_col > last_col:
                out += (" " * (start_col - last_col))

            if token_type == tokenize.COMMENT:
                pass
            elif token_type == tokenize.STRING:
                if prev_toktype == tokenize.INDENT or prev_toktype == tokenize.NEWLINE or prev_toktype == tokenize.NL:
                    pass
                else:
                    out += token_string
            else:
                out += token_string

            prev_toktype = token_type
            last_lineno = end_line
            last_col = end_col
    except tokenize.TokenError:
        return source # if syntax error, don't break the file completely
    return out

def remove_js_comments(text):
    # Matches strings OR comments
    pattern = r'(".*?"|\'.*?\'|`[\s\S]*?`)|(/\*[\s\S]*?\*/|//[^\r\n]*)'
    def replacer(match):
        if match.group(2) is not None:
            return ""
        return match.group(1)
    try:
        return re.sub(pattern, replacer, text)
    except Exception:
        return text

def remove_html_comments(text):
    pattern = r'(".*?"|\'.*?\')|(<!--[\s\S]*?-->)'
    def replacer(match):
        if match.group(2) is not None:
            return ""
        return match.group(1)
    try:
        return re.sub(pattern, replacer, text)
    except Exception:
        return text

def process_file(filepath):
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
    except UnicodeDecodeError:
        return # Skip binary or weird encoding

    original_content = content

    # 1. Strip emojis
    content = emoji.replace_emoji(content, replace='')

    # 2. Strip comments
    ext = filepath.suffix.lower()
    if ext == '.py':
        content = remove_python_comments_and_docstrings(content)
    elif ext in {'.js', '.jsx', '.ts', '.tsx', '.css'}:
        content = remove_js_comments(content)
    elif ext in {'.html', '.md'}:
        content = remove_html_comments(content)
    # json, bat, sh: we just stripped emojis.

    if content != original_content:
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)
        return True
    return False

def main():
    root_dir = Path("HealthSentinel")
    modified_count = 0
    scanned_count = 0

    for current_dir, dirs, files in os.walk(root_dir):
        # modify dirs in-place to prevent walking into excluded directories
        dirs[:] = [d for d in dirs if d not in EXCLUDE_DIRS]
        
        for file in files:
            filepath = Path(current_dir) / file
            if filepath.suffix.lower() in TARGET_EXTS:
                scanned_count += 1
                if process_file(filepath):
                    modified_count += 1

    print(f"Scanned {scanned_count} files.")
    print(f"Modified {modified_count} files (emojis or comments removed).")

if __name__ == "__main__":
    main()
