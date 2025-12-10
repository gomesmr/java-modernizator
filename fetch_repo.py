import os
from typing import List, Dict, Generator
from dataclasses import dataclass


@dataclass
class JavaFile:
    """Representa um arquivo Java encontrado"""
    path: str
    relative_path: str
    filename: str
    content: str
    size: int


class JavaFileProcessor:
    """Processador de arquivos Java para integração em API"""

    def __init__(self, root_directory: str, ignore_dirs: List[str] = None):
        self.root_directory = os.path.normpath(root_directory)
        self.ignore_dirs = ignore_dirs or [
            '.git', '.idea', '__pycache__', 'target',
            'build', 'out', '.gradle', 'node_modules'
        ]

        if not os.path.isdir(self.root_directory):
            raise ValueError(f"Diretório inválido: {self.root_directory}")

    def find_java_files(self) -> List[str]:
        java_files = []

        for root, dirs, files in os.walk(self.root_directory):
            # Remove diretórios ignorados da busca
            dirs[:] = [
                d for d in dirs
                if d not in self.ignore_dirs
            ]

            # Adiciona arquivos .java
            for file in files:
                if file.endswith('.java'):
                    file_path = os.path.join(root, file)
                    java_files.append(file_path)

        return java_files

    def process_java_file(self, file_path: str) -> JavaFile:
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
        except UnicodeDecodeError:
            # Fallback para latin-1
            with open(file_path, 'r', encoding='latin-1') as f:
                content = f.read()

        relative_path = os.path.relpath(file_path, self.root_directory)
        filename = os.path.basename(file_path)
        size = os.path.getsize(file_path)

        return JavaFile(
            path=file_path,
            relative_path=relative_path,
            filename=filename,
            content=content,
            size=size
        )

    def process_all_files(self) -> Generator[JavaFile, None, None]:
        java_files = self.find_java_files()

        for file_path in java_files:
            try:
                yield self.process_java_file(file_path)
            except Exception as e:
                print(f"Erro ao processar {file_path}: {e}")
                continue

    def get_all_files_list(self) -> List[Dict]:
        result = []

        for java_file in self.process_all_files():
            result.append({
                'path': java_file.path,
                'relative_path': java_file.relative_path,
                'filename': java_file.filename,
                'content': java_file.content,
                'size': java_file.size
            })

        return result

    def get_files_summary(self) -> Dict:
        java_files = self.find_java_files()

        total_size = 0
        for file_path in java_files:
            try:
                total_size += os.path.getsize(file_path)
            except:
                continue

        return {
            'root_directory': self.root_directory,
            'total_files': len(java_files),
            'total_size_bytes': total_size,
            'files': java_files
        }