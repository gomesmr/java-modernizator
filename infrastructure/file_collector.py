"""
File collector service for generating payload files
"""
import os
from pathlib import Path
from typing import List
import chardet

from domain.exceptions import FileProcessingError


class FileCollectorService:
    """Service for collecting files and generating consolidated payloads"""

    def generate_payload_file(
            self,
            cloned_repo_path: str,
            paths_file_path: str,
            output_file_path: str
    ) -> str:
        """
        Gera um arquivo consolidado com o conteúdo dos arquivos listados

        Args:
            cloned_repo_path: Caminho do repositório clonado
            paths_file_path: Arquivo com lista de caminhos
            output_file_path: Arquivo de saída consolidado

        Returns:
            Caminho do arquivo gerado
        """
        try:
            print(f"\n{'=' * 60}")
            print(f"📄 Generating Payload File")
            print(f"{'=' * 60}")
            print(f"📁 Source repo: {cloned_repo_path}")
            print(f"📋 Paths file: {paths_file_path}")
            print(f"📄 Output file: {output_file_path}")

            # 1. Lê a lista de arquivos
            file_paths = self._read_paths_file(paths_file_path)
            print(f"📊 Found {len(file_paths)} files to collect")

            # 2. Coleta cada arquivo
            payload_content = ["# Código do Repositório para Modernização\n\n"]

            collected_count = 0
            missing_count = 0

            for relative_path in file_paths:
                full_path = os.path.join(cloned_repo_path, relative_path)

                if os.path.exists(full_path):
                    content = self._read_file_as_utf8_safe(full_path)
                    extension = Path(full_path).suffix.lower()
                    language = self._get_language_from_extension(extension)

                    payload_content.extend([
                        f"## 📄 {relative_path}\n\n",
                        f"```{language}\n",
                        content,
                        "\n```\n\n"
                    ])
                    collected_count += 1
                    print(f"✅ Collected: {relative_path}")
                else:
                    payload_content.extend([
                        f"## ❌ {relative_path} (arquivo não encontrado)\n\n"
                    ])
                    missing_count += 1
                    print(f"⚠️  Missing: {relative_path}")

            # 3. Salva o arquivo consolidado
            os.makedirs(os.path.dirname(output_file_path), exist_ok=True)

            with open(output_file_path, 'w', encoding='utf-8') as f:
                f.writelines(payload_content)

            print(f"\n📊 Collection Summary:")
            print(f"   ✅ Collected: {collected_count}")
            print(f"   ⚠️  Missing: {missing_count}")
            print(f"   📄 Output: {output_file_path}")

            return output_file_path

        except Exception as e:
            raise FileProcessingError(f"Erro ao gerar arquivo payload: {str(e)}")

    def _read_paths_file(self, paths_file_path: str) -> List[str]:
        """Lê arquivo com lista de caminhos"""
        try:
            with open(paths_file_path, 'r', encoding='utf-8') as f:
                paths = [line.strip() for line in f.readlines() if line.strip()]
            return paths
        except Exception as e:
            raise FileProcessingError(f"Erro ao ler arquivo de caminhos: {str(e)}")

    def _read_file_as_utf8_safe(self, file_path: str) -> str:
        """Lê arquivo garantindo UTF-8 seguro"""
        try:
            # Detecta a codificação do arquivo
            with open(file_path, 'rb') as f:
                raw_data = f.read()

            result = chardet.detect(raw_data)
            encoding = result['encoding'] or 'utf-8'

            # Lê com a codificação detectada
            with open(file_path, 'r', encoding=encoding) as f:
                return f.read()
        except Exception:
            # Fallback para latin-1 se tudo falhar
            try:
                with open(file_path, 'r', encoding='latin-1') as f:
                    return f.read()
            except Exception as e:
                return f"# Erro ao ler arquivo: {str(e)}\n"

    def _get_language_from_extension(self, extension: str) -> str:
        """Mapeia extensão para linguagem do markdown"""
        language_map = {
            '.py': 'python',
            '.java': 'java',
            '.js': 'javascript',
            '.ts': 'typescript',
            '.cs': 'csharp',
            '.sql': 'sql',
            '.xml': 'xml',
            '.json': 'json',
            '.yml': 'yaml',
            '.yaml': 'yaml',
            '.md': 'markdown',
            '.html': 'html',
            '.css': 'css',
            '.sh': 'bash',
            '.dockerfile': 'dockerfile',
            '.txt': 'text'
        }
        return language_map.get(extension, 'text')