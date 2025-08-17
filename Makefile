# Makefile для управления vLLM
# Использует docker-compose для запуска и остановки сервисов

.PHONY: up down restart status logs clean help

# Запуск vLLM (локальный профиль по умолчанию)
up:
	@echo "🚀 Запуск vLLM..."
	docker-compose --profile local up -d
	@echo "✅ vLLM запущен на порту $(shell grep VLLM_PORT dev-env | cut -d'=' -f2 || echo '3423')"

# Запуск vLLM с HuggingFace профилем
up-hf:
	@echo "🚀 Запуск vLLM с HuggingFace профилем..."
	docker-compose --profile hf up -d
	@echo "✅ vLLM с HF профилем запущен"

# Остановка vLLM
down:
	@echo "🛑 Остановка vLLM..."
	docker-compose down
	@echo "✅ vLLM остановлен"

# Перезапуск vLLM
restart: down up
	@echo "🔄 vLLM перезапущен"

# Перезапуск vLLM с HuggingFace профилем
restart-hf: down up-hf
	@echo "🔄 vLLM с HF профилем перезапущен"

# Статус сервисов
status:
	@echo "📊 Статус сервисов vLLM:"
	docker-compose ps

# Просмотр логов
logs:
	@echo "📋 Логи vLLM:"
	docker-compose logs -f

# Очистка (удаление контейнеров и образов)
clean:
	@echo "🧹 Очистка Docker ресурсов..."
	docker-compose down --rmi all --volumes --remove-orphans
	@echo "✅ Очистка завершена"

# Справка
help:
	@echo "📖 Доступные команды:"
	@echo "  make up        - Запуск vLLM (локальный профиль)"
	@echo "  make up-hf     - Запуск vLLM с HuggingFace профилем"
	@echo "  make down      - Остановка vLLM"
	@echo "  make restart   - Перезапуск vLLM"
	@echo "  make restart-hf- Перезапуск vLLM с HF профилем"
	@echo "  make status    - Показать статус сервисов"
	@echo "  make logs      - Показать логи"
	@echo "  make clean     - Очистка Docker ресурсов"
	@echo "  make help      - Показать эту справку" 