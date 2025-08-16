#!/usr/bin/env python3
"""
Performance test script for Bitcoin Legacy Wallet Scanner
Tests key generation performance without balance checking
"""

import time
import sys
from btc_legacy_scanner import KeyGenerator, BitcoinLegacyScanner

def test_key_generation():
    """Test key generation performance"""
    print("🔑 Тестирование производительности генерации ключей")
    print("=" * 60)
    
    # Test different batch sizes
    batch_sizes = [100, 500, 1000, 2000, 5000]
    
    for batch_size in batch_sizes:
        print(f"\n📦 Размер пакета: {batch_size}")
        
        generator = KeyGenerator(batch_size)
        
        # Warm up
        for _ in range(3):
            generator.generate_batch()
        
        # Performance test
        start_time = time.time()
        iterations = 10
        
        for i in range(iterations):
            wallets = generator.generate_batch()
            if i % 2 == 0:
                print(f"  Итерация {i+1}/{iterations}: {len(wallets)} адресов")
        
        end_time = time.time()
        total_time = end_time - start_time
        total_addresses = batch_size * iterations
        
        # Calculate rates
        addresses_per_second = total_addresses / total_time
        addresses_per_minute = addresses_per_second * 60
        
        print(f"  ⏱️  Время: {total_time:.2f} сек")
        print(f"  🚀 Адресов/сек: {addresses_per_second:,.0f}")
        print(f"  🚀 Адресов/мин: {addresses_per_minute:,.0f}")
        print(f"  📊 Всего адресов: {total_addresses:,}")

def test_scanner_initialization():
    """Test scanner initialization performance"""
    print("\n🔧 Тестирование инициализации сканера")
    print("=" * 60)
    
    start_time = time.time()
    
    try:
        scanner = BitcoinLegacyScanner("config.yaml")
        init_time = time.time() - start_time
        
        print(f"✅ Инициализация успешна за {init_time:.3f} сек")
        print(f"📊 Конфигурация загружена:")
        print(f"   - Размер пакета: {scanner.config.get('batch_size')}")
        print(f"   - Воркеры генерации: {scanner.config.get('gen_workers')}")
        print(f"   - RPC воркеры: {scanner.config.get('rpc_workers')}")
        print(f"   - Максимум очереди: {scanner.config.get('queue_max')}")
        
        # Test dry run mode
        print(f"\n🧪 Тест dry-run режима:")
        scanner.start()
        time.sleep(2)  # Let it run for 2 seconds
        scanner.stop()
        
        print(f"✅ Dry-run тест завершен")
        
    except Exception as e:
        print(f"❌ Ошибка инициализации: {e}")
        return False
    
    return True

def main():
    """Main test function"""
    print("🚀 Bitcoin Legacy Wallet Scanner - Тест производительности")
    print("=" * 70)
    
    # Test 1: Key generation
    test_key_generation()
    
    # Test 2: Scanner initialization
    if test_scanner_initialization():
        print("\n🎉 Все тесты пройдены успешно!")
    else:
        print("\n❌ Некоторые тесты не пройдены")
        sys.exit(1)
    
    print("\n📋 Рекомендации по оптимизации:")
    print("1. Увеличьте batch_size для лучшей производительности RPC")
    print("2. Настройте количество воркеров под вашу систему")
    print("3. Используйте coincurve вместо ecdsa для лучшей производительности")
    print("4. Мониторьте использование памяти и CPU")

if __name__ == "__main__":
    main()
