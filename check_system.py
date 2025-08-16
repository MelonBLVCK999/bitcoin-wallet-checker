#!/usr/bin/env python3
"""
System Check Script for Bitcoin Legacy Wallet Scanner
Checks all dependencies and system requirements
"""

import sys
import subprocess
import platform
import os
from pathlib import Path

def check_python_version():
    """Check Python version"""
    print("🐍 Проверка версии Python...")
    version = sys.version_info
    if version.major < 3 or (version.major == 3 and version.minor < 10):
        print(f"❌ Требуется Python 3.10+, установлена {version.major}.{version.minor}.{version.micro}")
        return False
    else:
        print(f"✅ Python {version.major}.{version.minor}.{version.micro} - OK")
        return True

def check_system():
    """Check operating system"""
    print("\n💻 Проверка операционной системы...")
    system = platform.system()
    if system == "Linux":
        distro = "Unknown"
        try:
            with open("/etc/os-release", "r") as f:
                for line in f:
                    if line.startswith("PRETTY_NAME"):
                        distro = line.split("=")[1].strip().strip('"')
                        break
        except:
            pass
        print(f"✅ {system} - {distro}")
        return True
    else:
        print(f"⚠️  {system} - Рекомендуется Linux (Ubuntu/Debian)")
        return False

def check_dependencies():
    """Check Python dependencies"""
    print("\n📦 Проверка Python зависимостей...")
    
    required_packages = {
        'coincurve': 'coincurve (рекомендуется для производительности)',
        'ecdsa': 'ecdsa (альтернатива coincurve)',
        'yaml': 'PyYAML',
        'blessed': 'blessed (TUI библиотека)'
    }
    
    missing_packages = []
    crypto_available = False
    
    for package, description in required_packages.items():
        try:
            if package == 'yaml':
                import yaml
            else:
                __import__(package)
            
            if package in ['coincurve', 'ecdsa']:
                crypto_available = True
                print(f"✅ {description}")
            else:
                print(f"✅ {description}")
                
        except ImportError:
            if package in ['coincurve', 'ecdsa']:
                print(f"⚠️  {description} - НЕ УСТАНОВЛЕН")
            else:
                print(f"❌ {description} - НЕ УСТАНОВЛЕН")
                missing_packages.append(package)
    
    if not crypto_available:
        print("❌ КРИТИЧЕСКАЯ ОШИБКА: Ни одна криптографическая библиотека не доступна!")
        print("   Установите: pip install coincurve или pip install ecdsa")
        return False
    
    if missing_packages:
        print(f"\n⚠️  Отсутствуют пакеты: {', '.join(missing_packages)}")
        print("   Установите: pip install -r requirements.txt")
        return False
    
    return True

def check_bitcoin_core():
    """Check Bitcoin Core installation"""
    print("\n₿ Проверка Bitcoin Core...")
    
    # Check if bitcoin-cli is available
    try:
        result = subprocess.run(['which', 'bitcoin-cli'], 
                              capture_output=True, text=True, timeout=10)
        if result.returncode == 0:
            bitcoin_cli_path = result.stdout.strip()
            print(f"✅ bitcoin-cli найден: {bitcoin_cli_path}")
        else:
            print("❌ bitcoin-cli не найден в PATH")
            return False
    except subprocess.TimeoutExpired:
        print("❌ Таймаут при поиске bitcoin-cli")
        return False
    
    # Check if bitcoind is running
    try:
        result = subprocess.run(['bitcoin-cli', 'getblockchaininfo'], 
                              capture_output=True, text=True, timeout=30)
        if result.returncode == 0:
            print("✅ Bitcoin Core запущен и отвечает")
            
            # Parse blockchain info
            import json
            try:
                info = json.loads(result.stdout)
                blocks = info.get('blocks', 0)
                headers = info.get('headers', 0)
                verification_progress = info.get('verificationprogress', 0)
                
                print(f"   Блоки: {blocks:,}")
                print(f"   Заголовки: {headers:,}")
                print(f"   Прогресс синхронизации: {verification_progress:.2%}")
                
                if verification_progress < 0.99:
                    print("   ⚠️  Блокчейн не полностью синхронизирован")
                    print("      Рекомендуется дождаться полной синхронизации")
                
            except json.JSONDecodeError:
                print("   ⚠️  Не удалось разобрать ответ Bitcoin Core")
                
        else:
            print(f"❌ Bitcoin Core не отвечает: {result.stderr}")
            return False
            
    except subprocess.TimeoutExpired:
        print("❌ Таймаут при обращении к Bitcoin Core")
        return False
    except FileNotFoundError:
        print("❌ bitcoin-cli не найден")
        return False
    
    return True

def check_disk_space():
    """Check available disk space"""
    print("\n💾 Проверка свободного места на диске...")
    
    try:
        result = subprocess.run(['df', '-h', '.'], 
                              capture_output=True, text=True, timeout=10)
        if result.returncode == 0:
            lines = result.stdout.strip().split('\n')
            if len(lines) > 1:
                parts = lines[1].split()
                if len(parts) >= 4:
                    available = parts[3]
                    print(f"✅ Свободно: {available}")
                    
                    # Check if it's GB or TB
                    if 'G' in available:
                        gb = float(available.replace('G', ''))
                        if gb < 10:
                            print("   ⚠️  Рекомендуется минимум 10GB свободного места")
                    elif 'T' in available:
                        print("   ✅ Достаточно места")
                    else:
                        print("   ⚠️  Проверьте размер вручную")
                        
        else:
            print("⚠️  Не удалось проверить свободное место")
            
    except Exception as e:
        print(f"⚠️  Ошибка проверки диска: {e}")
    
    return True

def check_memory():
    """Check available memory"""
    print("\n🧠 Проверка оперативной памяти...")
    
    try:
        with open('/proc/meminfo', 'r') as f:
            meminfo = f.read()
            
        total_mem = 0
        for line in meminfo.split('\n'):
            if line.startswith('MemTotal:'):
                total_mem = int(line.split()[1]) // 1024  # Convert to MB
                break
        
        if total_mem > 0:
            print(f"✅ Общая память: {total_mem:,} MB")
            
            if total_mem < 4096:
                print("   ⚠️  Рекомендуется минимум 4GB RAM")
            elif total_mem < 8192:
                print("   ✅ Минимальные требования выполнены")
            else:
                print("   ✅ Рекомендуемые требования выполнены")
                
        else:
            print("⚠️  Не удалось определить размер памяти")
            
    except Exception as e:
        print(f"⚠️  Ошибка проверки памяти: {e}")
    
    return True

def check_output_directory():
    """Check output directory"""
    print("\n📁 Проверка выходной директории...")
    
    output_dir = Path("./out")
    
    if not output_dir.exists():
        try:
            output_dir.mkdir(exist_ok=True)
            print("✅ Выходная директория создана")
        except Exception as e:
            print(f"❌ Не удалось создать выходную директорию: {e}")
            return False
    else:
        print("✅ Выходная директория существует")
    
    # Check permissions
    try:
        if os.access(output_dir, os.W_OK):
            print("✅ Права на запись в выходную директорию")
        else:
            print("❌ Нет прав на запись в выходную директорию")
            return False
    except Exception as e:
        print(f"⚠️  Не удалось проверить права: {e}")
    
    return True

def main():
    """Main check function"""
    print("🔍 Проверка системы для Bitcoin Legacy Wallet Scanner")
    print("=" * 60)
    
    checks = [
        check_python_version,
        check_system,
        check_dependencies,
        check_bitcoin_core,
        check_disk_space,
        check_memory,
        check_output_directory
    ]
    
    results = []
    for check in checks:
        try:
            result = check()
            results.append(result)
        except Exception as e:
            print(f"❌ Ошибка при выполнении проверки: {e}")
            results.append(False)
    
    print("\n" + "=" * 60)
    print("📊 РЕЗУЛЬТАТЫ ПРОВЕРКИ")
    print("=" * 60)
    
    passed = sum(results)
    total = len(results)
    
    if passed == total:
        print("🎉 ВСЕ ПРОВЕРКИ ПРОЙДЕНЫ УСПЕШНО!")
        print("✅ Система готова к работе")
        print("\n🚀 Запустите сканер:")
        print("   python3 btc_legacy_scanner.py")
        print("   или")
        print("   ./run_scanner.sh")
        
    else:
        print(f"⚠️  ПРОЙДЕНО {passed}/{total} ПРОВЕРОК")
        print("❌ Некоторые проверки не пройдены")
        print("\n🔧 Исправьте ошибки и запустите проверку снова")
        print("   python3 check_system.py")
        
        if not results[2]:  # dependencies
            print("\n📦 Установите зависимости:")
            print("   pip install -r requirements.txt")
            
        if not results[3]:  # bitcoin core
            print("\n₿ Настройте Bitcoin Core:")
            print("   ./install.sh")
    
    return passed == total

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
