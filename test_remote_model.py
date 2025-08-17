#!/usr/bin/env python3
"""
Тестовый скрипт для проверки работы vLLM модели на удаленной машине
"""

import requests
import json
import time
import os
from typing import Dict, Any

# Конфигурация
REMOTE_HOST = "REMOTE_HOST"
API_KEY = "API_KEY"
REMOTE_PORT = 3423  # Порт из docker-compose.yml
BASE_URL = f"http://{REMOTE_HOST}:{REMOTE_PORT}"
MODEL_NAME = "MODEL_NAME"

# Получаем API ключ из переменной окружения или запрашиваем у пользователя
def get_api_key():
    api_key = os.getenv('VLLM_API_KEY')
    if not api_key:
        if API_KEY:
            api_key = API_KEY
        else:
            api_key = input("Введите API ключ для vLLM: ").strip()
    return api_key

def test_health_check():
    """Проверка здоровья сервиса"""
    try:
        response = requests.get(f"{BASE_URL}/health", timeout=10)
        print(f"✅ Health check: {response.status_code}")
        if response.status_code == 200:
            print(f"   Response: {response.text}")
        return response.status_code == 200
    except Exception as e:
        print(f"❌ Health check failed: {e}")
        return False

def test_completion():
    """Тест генерации текста"""
    # Получаем API ключ
    api_key = get_api_key()
    if not api_key:
        print("❌ API ключ не указан")
        return False
    
    payload = {
        "model": MODEL_NAME,  # Имя модели из конфигурации
        "messages": [
            {"role": "user", "content": "Привет! Как дела? Ответь кратко на русском языке."}
        ],
        "max_tokens": 100,
        "temperature": 0.7,
        "stream": False
    }
    
    try:
        print("🔄 Отправляю запрос на генерацию...")
        start_time = time.time()
        
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {api_key}"
        }
        
        response = requests.post(
            f"{BASE_URL}/v1/chat/completions",
            json=payload,
            timeout=30,
            headers=headers
        )
        
        end_time = time.time()
        print(f"✅ Completion: {response.status_code} (время: {end_time - start_time:.2f}с)")
        
        if response.status_code == 200:
            result = response.json()
            print(f"   Ответ модели:")
            print(f"   {result['choices'][0]['message']['content']}")
            return True
        else:
            print(f"   Error: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Completion failed: {e}")
        return False

def test_streaming():
    """Тест потоковой генерации"""
    # Получаем API ключ
    api_key = get_api_key()
    if not api_key:
        print("❌ API ключ не указан")
        return False
    
    payload = {
        "model": MODEL_NAME,
        "messages": [
            {"role": "user", "content": "Расскажи короткую историю про кота. Начни с 'Жил-был кот...'"}
        ],
        "max_tokens": 150,
        "temperature": 0.8,
        "stream": True
    }
    
    try:
        print("🔄 Тестирую потоковую генерацию...")
        start_time = time.time()
        
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {api_key}"
        }
        
        response = requests.post(
            f"{BASE_URL}/v1/chat/completions",
            json=payload,
            timeout=60,
            headers=headers,
            stream=True
        )
        
        if response.status_code == 200:
            print("✅ Streaming response:")
            full_response = ""
            for line in response.iter_lines():
                if line:
                    line_str = line.decode('utf-8')
                    if line_str.startswith('data: '):
                        data_str = line_str[6:]  # Убираем 'data: '
                        if data_str == '[DONE]':
                            break
                        try:
                            data = json.loads(data_str)
                            if 'choices' in data and len(data['choices']) > 0:
                                delta = data['choices'][0].get('delta', {})
                                if 'content' in delta:
                                    content = delta['content']
                                    print(content, end='', flush=True)
                                    full_response += content
                        except json.JSONDecodeError:
                            continue
            
            end_time = time.time()
            print(f"\n\n✅ Streaming completed (время: {end_time - start_time:.2f}с)")
            return True
        else:
            print(f"❌ Streaming failed: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Streaming failed: {e}")
        return False

def main():
    """Основная функция тестирования"""
    print("🚀 Тестирование vLLM модели на удаленной машине")
    print(f"📍 Адрес: {BASE_URL}")
    print("=" * 50)
    
    tests = [
        ("Health Check", test_health_check),
        ("Completion", test_completion),
        ("Streaming", test_streaming)
    ]
    
    results = []
    for test_name, test_func in tests:
        print(f"\n🧪 Тест: {test_name}")
        print("-" * 30)
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"❌ Тест {test_name} завершился с ошибкой: {e}")
            results.append((test_name, False))
    
    print("\n" + "=" * 50)
    print("📊 Результаты тестирования:")
    for test_name, result in results:
        status = "✅ ПРОЙДЕН" if result else "❌ ПРОВАЛЕН"
        print(f"   {test_name}: {status}")
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    print(f"\n🎯 Итого: {passed}/{total} тестов пройдено")
    
    if passed == total:
        print("🎉 Все тесты пройдены! Модель работает корректно.")
    else:
        print("⚠️  Некоторые тесты не пройдены. Проверьте конфигурацию и логи.")

if __name__ == "__main__":
    main() 