import unittest
import sys
import os

def run_all_tests():
    """Запуск всех тестов"""
    project_root = os.path.dirname(__file__)
    sys.path.insert(0, project_root)  # Исправлено: добавлен 0
    
    print("=" * 60)
    print("🎮 ЗАПУСК АВТОТЕСТОВ ДЛЯ ИГРЫ")
    print("=" * 60)
    
    # Добавляем tests в Python path
    sys.path.insert(0, os.path.join(project_root, 'tests'))  # Исправлено: добавлен 0
    
    test_files = [
        'test_imports',
        'test_units', 
        'test_integration',
        'test_enemy_respawn'
    ]
    
    loader = unittest.TestLoader()
    suites = []
    
    for test_name in test_files:
        print(f"🔍 Загрузка: {test_name}")
        try:
            suite = loader.loadTestsFromName(test_name)
            suites.append(suite)
        except Exception as e:
            print(f"❌ Ошибка загрузки {test_name}: {e}")
    
    if not suites:
        print("❌ Не найдено тестов для запуска")
        return 1
    
    
    combined_suite = unittest.TestSuite(suites)
    
    print("\n" + "=" * 60)
    print("РЕЗУЛЬТАТЫ ТЕСТИРОВАНИЯ")
    print("=" * 60)
    
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(combined_suite)
    
    # Вывод подробных ошибок
    if result.errors:
        print("\n" + "🚨 ОШИБКИ:" + "=" * 50)
        for test, error in result.errors:
            print(f"❌ {test}: {error}")
    
    if result.failures:
        print("\n" + "💥 ПРОВАЛЕННЫЕ ТЕСТЫ:" + "=" * 40)
        for test, failure in result.failures:
            print(f"❌ {test}: {failure}")
    
    print("\n" + "=" * 60)
    print("ИТОГИ:")
    print(f"✅ Успешных: {result.testsRun - len(result.failures) - len(result.errors)}")
    print(f"❌ Провалено: {len(result.failures)}")
    print(f"⚠️  Ошибок: {len(result.errors)}")
    print("=" * 60)
    
    if result.wasSuccessful():
        print("🎉 Все тесты прошли успешно!")
        return 0  # Исправлено: добавлен 0
    else:
        print("💥 Обнаружены проблемы в тестах")
        return 1  # Исправлено: добавлен 1

if __name__ == '__main__':
    exit_code = run_all_tests()
    sys.exit(exit_code)