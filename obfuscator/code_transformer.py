import os
from crypto.string_encryptor import StringEncryptor
from obfuscator.control_flow import ControlFlowFlattener
from obfuscator.opaque_predicates import OpaquePredicateInjector
from obfuscator.api_resolver import ApiCallRewriter
from obfuscator.polymorph_engine import Polymorpher


def obfuscate(code: str, project_type: str = "dll") -> str:
    transformer = CodeTransformer()
    return transformer.apply_transformations(code)


class CodeTransformer:
    def __init__(self, config: dict = None):
        self.config = config or {}
        self.flattener = ControlFlowFlattener()
        self.opaque_injector = OpaquePredicateInjector()
        self.api_rewriter = ApiCallRewriter()
        self.encryptor = StringEncryptor()
        self.morpher = Polymorpher()


    def load_file(self, path: str) -> str:
        with open(path, "r", encoding="utf-8-sig") as f:  # ✅ удаляет BOM
            code = f.read()
        # 🧹 Удаляем «проблемные» символы
        bad_chars = ["\u2014", "\u200b", "\ufeff", "\u202a", "\u202c"]
        for ch in bad_chars:
            code = code.replace(ch, "")

        return code

    def save_file(self, path: str, content: str):
        with open(path, "w", encoding="utf-8") as f:
            f.write(content)

    def apply_transformations(self, code: str) -> str:
        """
        Применяет обфускации к исходному коду: 
        AST-трансформации (если не C++), API-скрытие, шифрование строк, морфинг.
        """
        language = self.config.get("language", "cpp")  # По умолчанию считаем, что это C++

        if language != "cpp":
            self.log("🔁 Применение Control Flow Flattening...")
            code = self.flattener.transform(code)

            self.log("🌀 Внедрение Opaque Predicates...")
            code = self.opaque_injector.inject(code)

        self.log("🔍 Переписываем API вызовы...")
        code = self.api_rewriter.rewrite_calls(code)

        self.log("🔐 Шифруем строки и переменные...")
        code = self.encryptor.encrypt_strings(code)

        self.log("Applying morphing...")
        code = self.morpher.morph(code)

        return code



    def run(self, input_path: str, output_path: str):
        self.log(f"📥 Загрузка исходного файла: {input_path}")
        code = self.load_file(input_path)

        code = self.apply_transformations(code)

        self.log(f"📤 Сохраняем обфусцированный файл: {output_path}")
        self.save_file(output_path, code)

    def log(self, message: str):
        print(f"[CodeTransformer] {message}")
