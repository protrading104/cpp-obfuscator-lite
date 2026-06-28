import argparse
import os
import logging

from obfuscator import code_transformer
from utils.encrypt_dll import AES128

from stringguard import (
    vcxproj_parser, solution_manager,
    string_parser, string_encoder,
    decryptor_generator, injector,
    backup_restore, validator
)

logger = logging.getLogger("CLI")

def setup_logging(debug=False):
    level = logging.DEBUG if debug else logging.INFO
    logging.basicConfig(level=level, format="%(levelname)s:%(name)s: %(message)s")

def obfuscate_cpp(input_file, output_file, project_type="dll"):
    logger.info("Obfuscating C++ code...")
    with open(input_file, "r", encoding="utf-8", errors="replace") as f:
        code = f.read()
    obfuscated = code_transformer.obfuscate(code, project_type)
    with open(output_file, "w", encoding="utf-8") as f:
        f.write(obfuscated)
    logger.info("Obfuscation complete.")

def encrypt_dll(input_dll, output_bin, key):
    logger.info("Encrypting DLL (AES128)...")
    with open(input_dll, "rb") as f:
        data = f.read()
    encrypted = AES128(key).encrypt(data)
    with open(output_bin, "wb") as f:
        f.write(encrypted)
    logger.info("DLL encrypted.")

def run_stringguard_project(project_path, debug=False):
    if project_path.endswith(".sln"):
        projects = solution_manager.SolutionManager(project_path).extract_vcxproj_paths()
    elif project_path.endswith(".vcxproj"):
        projects = [project_path]
    else:
        raise ValueError("Specify a .sln or .vcxproj file")

    for proj in projects:
        base_dir = os.path.dirname(os.path.abspath(proj))
        source_files = vcxproj_parser.VcxprojParser(proj).extract_source_files()

        for rel_path in source_files:
            abs_path = os.path.normpath(os.path.join(base_dir, rel_path))
            if not os.path.exists(abs_path):
                print(f"[!] Skipping missing file: {abs_path}")
                continue

            backup_mgr = backup_restore.BackupManager()
            backup_mgr.backup_file(abs_path)

            parser = string_parser.StringParser()
            strings = parser.parse_file(abs_path)

            if not strings:
                validator.log_results(abs_path, [], {})
                continue

            encoder = string_encoder.StringEncoder()

            base_name = os.path.splitext(os.path.basename(abs_path))[0]
            name_normal = f"decrypt_{base_name}"
            name_wide = f"decrypt_wide_{base_name}"

            encoded = encoder.encode_strings(
                strings,
                name_normal=name_normal,
                name_wide=name_wide
            )

            decryptor_gen = decryptor_generator.DecryptorGenerator(encoder.xor_key, name_normal, name_wide)
            decryptor_code = decryptor_gen.get_decryptor() + "\n" + decryptor_gen.get_decryptor_wide()

            injection = injector.Injector(inline=True)
            updated_code = injection.inject(abs_path, encoded, decryptor_code)

            with open(abs_path, "w", encoding="utf-8") as f:
                f.write(updated_code)

            validator.log_results(abs_path, strings, encoded)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="C++ Obfuscator with string encryption")

    parser.add_argument("--obfuscate", action="store_true", help="Apply obfuscation to a C++ file")
    parser.add_argument("--encrypt-dll", action="store_true", help="Encrypt a DLL file with AES128")
    parser.add_argument("--debug", action="store_true", help="Enable verbose logging")

    parser.add_argument("--type", choices=["dll", "exe"], default="dll")
    parser.add_argument("--input", help="Input C++ file", default="sample/test_dll.cpp")
    parser.add_argument("--output", help="Obfuscated C++ output", default="output/test_dll_obf.cpp")
    parser.add_argument("--dll", help="Path to DLL", default="output/test_dll.dll")
    parser.add_argument("--bin", help="Path to encrypted binary output", default="output/test_dll_encrypted.bin")
    parser.add_argument("--key", help="AES key (16 bytes)", default="0123456789abcdef")
    parser.add_argument("--project", help="Path to .vcxproj or .sln file")

    args = parser.parse_args()
    setup_logging(args.debug)

    if args.project:
        run_stringguard_project(args.project, debug=args.debug)
    if args.obfuscate:
        obfuscate_cpp(args.input, args.output, args.type)
    if args.encrypt_dll:
        encrypt_dll(args.dll, args.bin, args.key.encode())
