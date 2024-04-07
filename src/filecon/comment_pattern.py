__hash_like = r"/^\s*#/d; s/#.*//"
__slash_like = r"s://.*::; /\/\*/,/\*\//d"
__semicolon_hash_like = r"/^[;#].*$/d"
__dash_like = r"--.*"

code_comment_patterns = {
    "sh": __hash_like,  # Shell scripts
    "py": __hash_like,  # Python
    "c": __slash_like,  # C
    "cpp": __slash_like,  # C++
    "cs": __slash_like,  # C#
    "h": __slash_like,  # C/C++ Header
    "js": __slash_like,  # JavaScript
    "java": __slash_like,  # Java
    "rs": __slash_like,  # Rust
    "rb": __hash_like,  # Ruby
    "ts": __slash_like,  # TypeScript
    "html": r"s:<!--.*-->::g",  # HTML
    "css": r"s:/\*.*\*/::g",  # CSS
    "php": __slash_like,  # PHP
    "go": __slash_like,  # Go
    "swift": __slash_like,  # Swift
    "pl": __hash_like,  # Perl
    "lua": __dash_like,  # Lua
    "groovy": __slash_like,  # Groovy
    "scala": __slash_like,  # Scala
    "kt": __slash_like,  # Kotlin
    "m": r"%.*",  # MATLAB/Octave
    "sql": __dash_like,  # SQL
    "pas": r"^\{.*\}$; /^\(*\).*\)$",  # Pascal
    "asm": r";.*",  # Assembly
    "bat": r"/^::.*$/d; s/REM.*//",  # Batch files
}

document_comment_patterns = {
    "md": r"/<!--.*-->/d",  # Markdown
    "tex": r"/%.*/d",  # LaTeX
    "yaml": __hash_like,  # YAML
    "yml": __hash_like,  # YML
    "json": "",  # JSON does not support comments
    "toml": __hash_like,  # TOML
    "ini": __semicolon_hash_like,  # INI
    "xml": r"/<!--.*-->/d",  # XML
    "cfg": __semicolon_hash_like,  # Generic config files, often similar to INI
    "properties": r"/^#.*$/d",  # Java properties files
    "conf": __semicolon_hash_like,  # General configuration files
}
