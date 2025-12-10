"""
Java Modernizator - Orquestrador de Modernização de Código Java
"""
import os
import json
from typing import Dict, Optional, List
from dataclasses import dataclass

try:
    from stackspot import Stackspot
except ImportError:
    print("⚠️ Aviso: stackspot não instalado. Execute: pip install stackspot-sdk")
    Stackspot = None

from fetch_repo import JavaFileProcessor, JavaFile


@dataclass
class ModernizationResult:
    """Resultado da modernização de um arquivo"""
    file_path: str
    success: bool
    execution_id: Optional[str] = None
    error_message: Optional[str] = None
    original_content: Optional[str] = None
    modernized_content: Optional[str] = None


class JavaModernizator:
    """Orquestrador principal da modernização de código Java"""

    def __init__(self, credentials_path: str = './credentials.json'):
        """
        Inicializa o modernizador

        Args:
            credentials_path: Caminho para o arquivo de credenciais
        """
        print(f"🔧 Inicializando JavaModernizator...")
        self.credentials = self._load_credentials(credentials_path)
        self.stackspot = self._create_stackspot_instance()
        self.qc_slug = 'modernize-legacy-java-code'
        self.results: List[ModernizationResult] = []

    def _load_credentials(self, credentials_path: str) -> dict:
        """Carrega credenciais do arquivo JSON"""
        try:
            with open(credentials_path, 'r', encoding='utf-8') as f:
                credentials = json.load(f)
            print(f"✅ Credenciais carregadas: {credentials_path}")
            return credentials
        except FileNotFoundError:
            raise Exception(f"❌ Arquivo de credenciais não encontrado: {credentials_path}")
        except json.JSONDecodeError:
            raise Exception(f"❌ Erro ao decodificar JSON: {credentials_path}")
        except Exception as e:
            raise Exception(f"❌ Erro ao carregar credenciais: {e}")

    def _create_stackspot_instance(self):
        """Cria instância do Stackspot"""
        if Stackspot is None:
            raise Exception("❌ Stackspot SDK não está instalado. Execute: pip install stackspot-sdk")

        try:
            stackspot_instance = Stackspot(self.credentials)
            print("✅ Instância Stackspot criada com sucesso")
            return stackspot_instance
        except Exception as e:
            raise Exception(f"❌ Erro ao criar instância Stackspot: {e}")

    def execute_qc(self, file_content: str, filename: str) -> Optional[str]:
        """
        Executa Quick Command na Stackspot

        Args:
            file_content: Conteúdo do arquivo Java
            filename: Nome do arquivo (para log)

        Returns:
            execution_id ou None em caso de erro
        """
        try:
            print(f"🔄 Executando QC para: {filename}")
            execution_id = self.stackspot.ai.quick_command.create_execution(
                self.qc_slug,
                file_content
            )
            print(f"✅ Execution ID: {execution_id}")
            return execution_id
        except Exception as e:
            print(f"❌ Erro ao executar QC para {filename}: {e}")
            return None

    def get_results(self, execution_id: str, filename: str) -> Optional[str]:
        """
        Obtém resultados da execução do Quick Command

        Args:
            execution_id: ID da execução
            filename: Nome do arquivo (para log)

        Returns:
            Código modernizado ou None em caso de erro
        """
        try:
            print(f"⏳ Aguardando resultado para: {filename}")

            def callback_function(e):
                status = e['progress']['status']
                print(f"   Status: {status}")

            config_execution = {
                'delay': 23,
                'on_callback_response': callback_function
            }

            execution = self.stackspot.ai.quick_command.poll_execution(
                execution_id,
                config_execution
            )

            final_status = execution['progress']['status']
            print(f"✅ Status final: {final_status}")

            if final_status == 'COMPLETED':
                result = execution.get('result')

                # Trata diferentes formatos de resposta
                if isinstance(result, dict):
                    modernized_code = (
                            result.get('codigo_java') or
                            result.get('code') or
                            result.get('content')
                    )
                elif isinstance(result, str):
                    modernized_code = result
                else:
                    print(f"⚠️ Formato de resultado inesperado: {type(result)}")
                    modernized_code = None

                if modernized_code:
                    print(f"✅ Código modernizado obtido ({len(modernized_code)} caracteres)")
                    return modernized_code
                else:
                    print(f"⚠️ Resultado vazio ou inválido")
                    return None
            else:
                print(f"❌ Execução não completada: {final_status}")
                return None

        except Exception as e:
            print(f"❌ Erro ao obter resultados para {filename}: {e}")
            return None

    def modernize_file(self, java_file: JavaFile, save_changes: bool = True) -> ModernizationResult:
        """
        Moderniza um arquivo Java individual

        Args:
            java_file: Objeto JavaFile com informações do arquivo
            save_changes: Se True, salva as mudanças no arquivo

        Returns:
            ModernizationResult com o resultado da operação
        """
        print(f"\n{'=' * 60}")
        print(f"📄 Processando: {java_file.relative_path}")
        print(f"   Tamanho: {java_file.size} bytes")
        print(f"{'=' * 60}")

        # Executa Quick Command
        execution_id = self.execute_qc(java_file.content, java_file.filename)

        if not execution_id:
            result = ModernizationResult(
                file_path=java_file.path,
                success=False,
                error_message="Falha ao criar execução"
            )
            self.results.append(result)
            return result

        # Obtém resultados
        modernized_content = self.get_results(execution_id, java_file.filename)

        if not modernized_content:
            result = ModernizationResult(
                file_path=java_file.path,
                success=False,
                execution_id=execution_id,
                error_message="Falha ao obter resultado ou resultado vazio"
            )
            self.results.append(result)
            return result

        # Salva mudanças se solicitado
        if save_changes:
            try:
                with open(java_file.path, 'w', encoding='utf-8') as f:
                    f.write(modernized_content)
                print(f"💾 Arquivo atualizado: {java_file.path}")

                result = ModernizationResult(
                    file_path=java_file.path,
                    success=True,
                    execution_id=execution_id,
                    original_content=java_file.content,
                    modernized_content=modernized_content
                )
            except Exception as e:
                print(f"❌ Erro ao salvar arquivo: {e}")
                result = ModernizationResult(
                    file_path=java_file.path,
                    success=False,
                    execution_id=execution_id,
                    error_message=f"Erro ao salvar: {e}",
                    modernized_content=modernized_content
                )
        else:
            result = ModernizationResult(
                file_path=java_file.path,
                success=True,
                execution_id=execution_id,
                original_content=java_file.content,
                modernized_content=modernized_content
            )

        self.results.append(result)
        return result

    def modernize_directory(self, root_directory: str, save_changes: bool = True) -> Dict:
        """
        Moderniza todos os arquivos Java em um diretório

        Args:
            root_directory: Diretório raiz para busca
            save_changes: Se True, salva as mudanças nos arquivos

        Returns:
            Dicionário com estatísticas da operação
        """
        print(f"\n{'#' * 60}")
        print(f"🚀 INICIANDO MODERNIZAÇÃO")
        print(f"📁 Diretório: {root_directory}")
        print(f"{'#' * 60}\n")

        # Inicializa processador de arquivos
        try:
            processor = JavaFileProcessor(root_directory)
        except Exception as e:
            print(f"❌ Erro ao inicializar processador: {e}")
            return {'error': str(e)}

        # Obtém resumo dos arquivos
        summary = processor.get_files_summary()
        print(f"📊 Total de arquivos .java encontrados: {summary['total_files']}")
        print(f"📊 Tamanho total: {summary['total_size_bytes']} bytes\n")

        if summary['total_files'] == 0:
            print("⚠️ Nenhum arquivo .java encontrado!")
            return {
                'total_files': 0,
                'processed': 0,
                'successful': 0,
                'failed': 0
            }

        # Processa cada arquivo
        processed = 0
        successful = 0
        failed = 0

        for java_file in processor.process_all_files():
            result = self.modernize_file(java_file, save_changes)
            processed += 1

            if result.success:
                successful += 1
            else:
                failed += 1

        # Estatísticas finais
        stats = {
            'total_files': summary['total_files'],
            'processed': processed,
            'successful': successful,
            'failed': failed,
            'success_rate': f"{(successful / processed * 100):.2f}%" if processed > 0 else "0%"
        }

        print(f"\n{'#' * 60}")
        print(f"✅ MODERNIZAÇÃO CONCLUÍDA")
        print(f"{'#' * 60}")
        print(f"📊 Total de arquivos: {stats['total_files']}")
        print(f"✅ Processados com sucesso: {stats['successful']}")
        print(f"❌ Falhas: {stats['failed']}")
        print(f"📈 Taxa de sucesso: {stats['success_rate']}")
        print(f"{'#' * 60}\n")

        return stats

    def get_detailed_results(self) -> List[ModernizationResult]:
        """Retorna lista detalhada de todos os resultados"""
        return self.results

    def save_report(self, output_path: str = './modernization_report.json'):
        """
        Salva relatório detalhado em JSON

        Args:
            output_path: Caminho do arquivo de saída
        """
        report = {
            'results': [
                {
                    'file_path': r.file_path,
                    'success': r.success,
                    'execution_id': r.execution_id,
                    'error_message': r.error_message,
                    'has_modernized_content': r.modernized_content is not None
                }
                for r in self.results
            ]
        }

        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2, ensure_ascii=False)

        print(f"📄 Relatório salvo em: {output_path}")


# ============================================
# TESTE DO MÓDULO
# ============================================
if __name__ == '__main__':
    print("🧪 Testando módulo modernizator...")
    print(f"✅ JavaModernizator disponível: {JavaModernizator is not None}")
    print(f"✅ ModernizationResult disponível: {ModernizationResult is not None}")