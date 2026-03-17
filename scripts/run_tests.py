#!/usr/bin/env python
"""
Script para executar testes da aplicação.
Usage: python run_tests.py [opcao]

Opções:
  all              - Rodar todos os testes
  unit             - Apenas testes unitários
  integration      - Apenas testes de integração
  security         - Apenas testes de segurança
  performance      - Apenas testes de performance
  coverage         - Gerar relatório de cobertura
  watch            - Modo watch (pytest-watch)
  parallel         - Executar em paralelo
  fast             - Execução rápida (skip performance)
"""

import subprocess
import sys
from pathlib import Path


class TestRunner:
    """Executor de testes."""
    
    def __init__(self):
        self.root_dir = Path(__file__).parent
        self.tests_dir = self.root_dir / "tests"
    
    def run_all(self, verbose=2):
        """Rodar todos os testes."""
        cmd = ["pytest", str(self.tests_dir), "-v" * verbose]
        return subprocess.run(cmd)
    
    def run_unit_tests(self):
        """Rodar apenas testes unitários."""
        cmd = [
            "pytest",
            str(self.tests_dir / "test_app.py"),
            "-v",
            "-k", "not performance"
        ]
        return subprocess.run(cmd)
    
    def run_integration_tests(self):
        """Rodar apenas testes de integração."""
        cmd = [
            "pytest",
            str(self.tests_dir / "test_app.py"),
            "-v",
            "-k", "TestIntegration"
        ]
        return subprocess.run(cmd)
    
    def run_security_tests(self):
        """Rodar apenas testes de segurança."""
        cmd = [
            "pytest",
            str(self.tests_dir / "test_security.py"),
            "-v"
        ]
        return subprocess.run(cmd)
    
    def run_performance_tests(self):
        """Rodar apenas testes de performance."""
        cmd = [
            "pytest",
            str(self.tests_dir / "test_performance.py"),
            "-v",
            "--tb=short"
        ]
        return subprocess.run(cmd)
    
    def run_with_coverage(self):
        """Rodar testes com cobertura."""
        cmd = [
            "pytest",
            str(self.tests_dir),
            "--cov=app",
            "--cov-report=html",
            "--cov-report=term-missing",
            "-v"
        ]
        result = subprocess.run(cmd)
        
        print("\n" + "="*60)
        print("📊 Relatório de cobertura gerado em: htmlcov/index.html")
        print("="*60)
        
        return result
    
    def run_parallel(self):
        """Rodar testes em paralelo."""
        cmd = [
            "pytest",
            str(self.tests_dir),
            "-n", "auto",
            "-v"
        ]
        return subprocess.run(cmd)
    
    def run_fast(self):
        """Execução rápida (skip performance tests)."""
        cmd = [
            "pytest",
            str(self.tests_dir),
            "-v",
            "-k", "not performance"
        ]
        return subprocess.run(cmd)
    
    def run_watch_mode(self):
        """Modo watch - reexecuta ao salvar arquivo."""
        try:
            import pytest_watch
        except ImportError:
            print("❌ pytest-watch não instalado. Install com:")
            print("  pip install pytest-watch")
            return
        
        cmd = ["ptw", str(self.tests_dir), "--clear"]
        return subprocess.run(cmd)
    
    def print_menu(self):
        """Exibir menu de opções."""
        print("""
╔══════════════════════════════════════════════════════╗
║      🧪 ASSISTENTE LANGCHAIN - EXECUTOR DE TESTES    ║
╠══════════════════════════════════════════════════════╣
║                                                      ║
║  Opções disponíveis:                                 ║
║                                                      ║
║  1. all        - Todos os testes                     ║
║  2. unit       - Apenas unitários                    ║
║  3. integration- Apenas integração                   ║
║  4. security   - Apenas segurança                    ║
║  5. performance- Apenas performance                  ║
║  6. coverage   - Com relatório de cobertura          ║
║  7. parallel   - Execução em paralelo                ║
║  8. fast       - Rápido (sem performance)            ║
║  9. watch      - Modo watch (auto-rerun)             ║
║  0. sair       - Sair                                ║
║                                                      ║
╚══════════════════════════════════════════════════════╝
        """)
    
    def run_interactive(self):
        """Menu interativo."""
        while True:
            self.print_menu()
            choice = input("Escolha uma opção (0-9): ").strip()
            
            if choice == "1":
                print("\n🏃 Executando todos os testes...\n")
                result = self.run_all()
            elif choice == "2":
                print("\n🏃 Executando testes unitários...\n")
                result = self.run_unit_tests()
            elif choice == "3":
                print("\n🏃 Executando testes de integração...\n")
                result = self.run_integration_tests()
            elif choice == "4":
                print("\n🏃 Executando testes de segurança...\n")
                result = self.run_security_tests()
            elif choice == "5":
                print("\n🏃 Executando testes de performance...\n")
                result = self.run_performance_tests()
            elif choice == "6":
                print("\n🏃 Executando com cobertura...\n")
                result = self.run_with_coverage()
            elif choice == "7":
                print("\n🏃 Executando em paralelo...\n")
                result = self.run_parallel()
            elif choice == "8":
                print("\n🏃 Execução rápida...\n")
                result = self.run_fast()
            elif choice == "9":
                print("\n🏃 Modo watch (pressione Ctrl+C para sair)...\n")
                result = self.run_watch_mode()
            elif choice == "0":
                print("\n👋 Saindo...\n")
                break
            else:
                print("❌ Opção inválida. Tente novamente.")
                continue
            
            if result and result.returncode != 0:
                print("\n⚠️ Testes falharam!")
            else:
                print("\n✅ Testes concluídos!")
            
            input("\nPressione Enter para continuar...")


def main():
    """Ponto de entrada."""
    runner = TestRunner()
    
    if len(sys.argv) > 1:
        option = sys.argv[1].lower()
        
        print(f"\n{'='*60}")
        print(f"🧪 Executor de Testes - Opção: {option}")
        print(f"{'='*60}\n")
        
        if option == "all":
            result = runner.run_all()
        elif option == "unit":
            result = runner.run_unit_tests()
        elif option == "integration":
            result = runner.run_integration_tests()
        elif option == "security":
            result = runner.run_security_tests()
        elif option == "performance":
            result = runner.run_performance_tests()
        elif option == "coverage":
            result = runner.run_with_coverage()
        elif option == "parallel":
            result = runner.run_parallel()
        elif option == "fast":
            result = runner.run_fast()
        elif option == "watch":
            result = runner.run_watch_mode()
        else:
            print(__doc__)
            sys.exit(1)
        
        sys.exit(result.returncode if result else 1)
    else:
        # Menu interativo
        runner.run_interactive()


if __name__ == "__main__":
    main()
