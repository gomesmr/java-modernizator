"""
Setup script to validate and configure the project
"""
from pathlib import Path
import json
import sys


def check_secrets_file():
    """Check if secrets.json exists and is valid"""
    project_root = Path(__file__).parent
    secrets_path = project_root / 'secrets.json'
    example_path = project_root / 'secrets-example.json'

    print("🔍 Checking secrets configuration...")

    if not secrets_path.exists():
        print(f"❌ secrets.json not found at: {secrets_path}")

        if example_path.exists():
            print(f"\n💡 Creating secrets.json from example...")
            secrets_path.write_text(example_path.read_text())
            print(f"✅ Created: {secrets_path}")
            print("\n⚠️  Please edit secrets.json and add your credentials:")
            print("   - client_id")
            print("   - client_secret")
            print("   - realm")
            return False
        else:
            print(f"❌ Example file not found: {example_path}")
            return False

    # Validate JSON
    try:
        with open(secrets_path, 'r') as f:
            credentials = json.load(f)

        required_keys = ['client_id', 'client_secret', 'realm']
        missing_keys = [key for key in required_keys if not credentials.get(key) or credentials.get(key) == '...']

        if missing_keys:
            print(f"⚠️  secrets.json exists but missing values for: {', '.join(missing_keys)}")
            print(f"   Please edit: {secrets_path}")
            return False

        print(f"✅ secrets.json is valid")
        return True

    except json.JSONDecodeError as e:
        print(f"❌ Invalid JSON in secrets.json: {e}")
        return False


def check_project_structure():
    """Check if project structure is correct"""
    project_root = Path(__file__).parent

    required_dirs = [
        'application',
        'config',
        'domain',
        'infrastructure'
    ]

    print("\n🔍 Checking project structure...")

    all_exist = True
    for dir_name in required_dirs:
        dir_path = project_root / dir_name
        if dir_path.exists():
            print(f"✅ {dir_name}/")
        else:
            print(f"❌ {dir_name}/ not found")
            all_exist = False

    return all_exist


def check_dependencies():
    """Check if required dependencies are installed"""
    print("\n🔍 Checking dependencies...")

    try:
        import stackspot
        print("✅ stackspot SDK installed")
        return True
    except ImportError:
        print("❌ stackspot SDK not installed")
        print("   Run: pip install stackspot")
        return False


def main():
    """Run all checks"""
    print("🚀 Java Modernizator - Setup Check\n")
    print("=" * 60)

    checks = [
        ("Project Structure", check_project_structure),
        ("Dependencies", check_dependencies),
        ("Secrets Configuration", check_secrets_file),
    ]

    results = []
    for name, check_func in checks:
        result = check_func()
        results.append((name, result))
        print()

    print("=" * 60)
    print("\n📊 Setup Summary:")

    all_passed = True
    for name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"   {status} - {name}")
        if not result:
            all_passed = False

    print("\n" + "=" * 60)

    if all_passed:
        print("\n🎉 All checks passed! You're ready to run the modernizator.")
        print("\n▶️  Run: python main.py")
        return 0
    else:
        print("\n⚠️  Some checks failed. Please fix the issues above.")
        return 1


if __name__ == '__main__':
    sys.exit(main())