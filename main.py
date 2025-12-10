from modernizator import JavaModernizator

JAVA_PROJECT_PATH = r"C:\Users\marcelo.gomes\gomesmr\Hackathon\hackathon\src\main"
CREDENTIALS_PATH = './secrets.json'


def main():
    print("🚀 Java Modernizator - Iniciando...")

    try:
        modernizator = JavaModernizator(credentials_path=CREDENTIALS_PATH)

        stats = modernizator.modernize_directory(
            root_directory=JAVA_PROJECT_PATH,
            save_changes=True  # Altere para False para modo de teste
        )

        modernizator.save_report('./modernization_report.json')

        print("\n✅ Processo concluído com sucesso!")

    except Exception as e:
        print(f"\n❌ Erro fatal: {e}")
        raise


if __name__ == '__main__':
    main()