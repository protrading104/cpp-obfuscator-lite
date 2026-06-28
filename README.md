# CppObfuscator

A Python-based static obfuscation toolkit for C++ source code and Visual Studio projects.

## Features

### StringGuard — string literal encryption for VS projects
- Parses `.sln` / `.vcxproj` to enumerate all source files
- Extracts narrow (`char*`) and wide (`wchar_t*`) string literals
- XOR-encrypts strings and replaces them with inline decrypt calls
- Injects generated `decrypt()` / `decrypt_wide()` functions into source
- Backs up original files before modification
- YAML-based filter rules to skip format strings, technical noise, etc.

### C++ Code Obfuscation
- **API resolver** — replaces static WinAPI calls with dynamic `GetProcAddress` resolution
- **Opaque predicates** — inserts always-true/always-false conditions before branches
- **Polymorphic engine** — variable renaming + junk code insertion
- **String encryption** — XOR-based compile-time string hiding

### Crypto primitives
- AES-128 ECB (`pycryptodome`)
- RC4
- Rolling XOR

## Usage

### Encrypt strings in a Visual Studio project
```bash
python main.py --project path/to/Project.vcxproj
python main.py --project path/to/Solution.sln
```

### Obfuscate a single C++ file
```bash
python main.py --obfuscate --input src/main.cpp --output out/main_obf.cpp
```

### Encrypt a DLL with AES128
```bash
python main.py --encrypt-dll --dll output/my.dll --bin output/my.bin --key 0123456789abcdef
```

## Requirements

```
pycryptodome
pyyaml
astor
pefile
```

Install:
```bash
pip install pycryptodome pyyaml astor pefile
```

## Project Structure

```
CppObfuscator/
├── main.py                    # CLI entry point
├── stringguard/               # VS project string encryption pipeline
│   ├── string_parser.py       # extract string literals from C++ source
│   ├── string_encoder.py      # XOR-encode strings
│   ├── decryptor_generator.py # generate C decrypt functions
│   ├── injector.py            # inject encrypted code back into source
│   ├── filter_engine.py       # YAML-based string filter
│   ├── vcxproj_parser.py      # parse .vcxproj file lists
│   ├── solution_manager.py    # parse .sln project lists
│   ├── backup_restore.py      # backup/restore source files
│   └── validator.py           # verify encryption results
├── obfuscator/                # C++ code transformations
│   ├── code_transformer.py    # transformation orchestrator
│   ├── api_resolver.py        # dynamic WinAPI resolution
│   ├── opaque_predicates.py   # opaque predicate injection
│   ├── polymorph_engine.py    # variable renaming + junk code
│   ├── control_flow.py        # control flow flattening (Python AST)
│   └── string_encryptor.py    # (see crypto/)
├── crypto/                    # crypto primitives
│   ├── aes.py
│   ├── rc4.py
│   ├── xor_mask.py
│   └── string_encryptor.py
├── rules/
│   └── filter_rules.yaml      # string filter configuration
└── tests/
```

## License

MIT
