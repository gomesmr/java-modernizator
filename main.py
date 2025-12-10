"""
Script principal simplificado - usa o modernizator.py
"""
from modernizator import JavaModernizator

# Configurações
JAVA_PROJECT_PATH = r"C:\Users\marcelo.gomes\gomesmr\Hackathon\hackathon\src\main"
CREDENTIALS_PATH = './credentials.json'


def main():
    """Função principal"""
    print("🚀 Java Modernizator - Iniciando...")

    try:
        # Cria instância do modernizador
        modernizator = JavaModernizator(credentials_path=CREDENTIALS_PATH)

        # Executa modernização
        stats = modernizator.modernize_directory(
            root_directory=JAVA_PROJECT_PATH,
            save_changes=True  # Altere para False para modo de teste
        )

        # Salva relatório
        modernizator.save_report('./modernization_report.json')

        print("\n✅ Processo concluído com sucesso!")

    except Exception as e:
        print(f"\n❌ Erro fatal: {e}")
        raise


if __name__ == '__main__':
    main()