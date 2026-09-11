# NEXUS-KORNET Core v0.1 Bootstrap
.PHONY: all setup test lint clean docs

all: setup test lint

setup:
	@echo "[+] Инициализация окружения Earth OS..."
	pip install -r requirements.txt || echo "Python зависимости отсутствуют"
	cd core-engine && cargo update 2>/dev/null || echo "Rust зависимости отсутствуют"

test:
	@echo "[+] Запуск глобальных тестов консенсуса..."
	python3 -m py_compile core-engine/genesis_protocol.py
	python3 -m py_compile core-engine/reputation_decay.py
	python3 -m py_compile core-engine/graceful_degradation.py
	python3 -m py_compile core-engine/entropy_filter.py
	python3 -m py_compile validators/social_awakening.py
	python3 -m py_compile validators/eco_bio_vision.py
	python3 -m py_compile validators/infrastructure_scan.py
	python3 -m py_compile validators/science_peer_review.py
	python3 -m py_compile validators/dispute_arbiter.py
	python3 -m py_compile identity-zkp/web_of_trust.py
	python3 -m py_compile scripts/deploy_purge.py
	python3 -m unittest discover -s tests -v
	@echo "[+] Все Python-модули прошли проверку синтаксиса."

lint:
	@echo "[+] Проверка чистоты кода..."
	flake8 core-engine/ validators/ identity-zkp/ scripts/
	@echo "[+] Линтинг завершен."

clean:
	@echo "[+] Очистка артефактов сборки..."
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete 2>/dev/null || true
	cd core-engine && cargo clean 2>/dev/null || true

docs:
	@echo "[+] Генерация документации..."
	mkdir -p docs/build
	cp docs/*.md docs/build/ 2>/dev/null || true
	@echo "[+] Документация готова в docs/build/"

help:
	@echo "NEXUS-KORNET Core v0.1"
	@echo ""
	@echo "Доступные команды:"
	@echo "  make setup    - Установка зависимостей"
	@echo "  make test     - Проверка синтаксиса всех модулей"
	@echo "  make lint     - Линтинг кода"
	@echo "  make clean    - Очистка артефактов"
	@echo "  make docs     - Копирование документации"
	@echo "  make all      - Полный цикл: setup + test + lint"
