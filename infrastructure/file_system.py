"""
File system operations for Java files
"""
import os
from typing import List, Generator
from pathlib import Path

from domain.entities import JavaFile
from domain.exceptions import InvalidDirectoryError, FileProcessingError


class JavaFileRepository:
    """Repository for finding and reading Java files"""

    DEFAULT_IGNORED_DIRECTORIES = {
        '.git', '.idea', '__pycache__', 'target',
        'build', 'out', '.gradle', 'node_modules'
    }

    def __init__(
            self,
            root_directory: str,
            ignored_directories: set = None
    ):
        self.root_path = Path(root_directory).resolve()
        self.ignored_directories = ignored_directories or self.DEFAULT_IGNORED_DIRECTORIES

        self._validate_directory()

    def _validate_directory(self) -> None:
        """Validate that root directory exists and is accessible"""
        if not self.root_path.exists():
            raise InvalidDirectoryError(
                f"Directory does not exist: {self.root_path}"
            )

        if not self.root_path.is_dir():
            raise InvalidDirectoryError(
                f"Path is not a directory: {self.root_path}"
            )

    def find_all_java_files(self) -> List[Path]:
        """Find all .java files in directory tree"""
        java_files = []

        for root, dirs, files in os.walk(self.root_path):
            # Remove ignored directories from search
            dirs[:] = [
                d for d in dirs
                if d not in self.ignored_directories
            ]

            # Add .java files
            for file in files:
                if file.endswith('.java'):
                    java_files.append(Path(root) / file)

        return java_files

    def read_java_file(self, file_path: Path) -> JavaFile:
        """Read and parse a Java file"""
        try:
            content = self._read_file_content(file_path)

            return JavaFile(
                absolute_path=str(file_path),
                relative_path=str(file_path.relative_to(self.root_path)),
                filename=file_path.name,
                content=content,
                size_in_bytes=file_path.stat().st_size
            )
        except Exception as e:
            raise FileProcessingError(
                f"Failed to read file {file_path}: {e}"
            )

    def _read_file_content(self, file_path: Path) -> str:
        """Read file content with encoding fallback"""
        try:
            return file_path.read_text(encoding='utf-8')
        except UnicodeDecodeError:
            return file_path.read_text(encoding='latin-1')

    def get_all_java_files(self) -> Generator[JavaFile, None, None]:
        """Generator that yields all Java files"""
        for file_path in self.find_all_java_files():
            try:
                yield self.read_java_file(file_path)
            except FileProcessingError as e:
                print(f"⚠️ Warning: {e}")
                continue

    def save_file(self, file_path: str, content: str) -> None:
        """Save content to file"""
        try:
            Path(file_path).write_text(content, encoding='utf-8')
        except Exception as e:
            raise FileProcessingError(
                f"Failed to save file {file_path}: {e}"
            )

    def get_summary(self) -> dict:
        """Get summary statistics of Java files"""
        files = self.find_all_java_files()
        total_size = sum(f.stat().st_size for f in files)

        return {
            'root_directory': str(self.root_path),
            'total_files': len(files),
            'total_size_bytes': total_size,
            'file_paths': [str(f) for f in files]
        }