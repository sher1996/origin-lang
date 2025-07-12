# Origin Language Makefile

.PHONY: help dev build preview test

help:
	@echo "Available commands:"
	@echo "  dev     - Start the visual editor development server"
	@echo "  build   - Build the visual editor for production"
	@echo "  preview - Preview the built visual editor"
	@echo "  test    - Run tests"

dev:
	@echo "Starting visual editor development server..."
	cd visual && npm run dev

build:
	@echo "Building visual editor..."
	cd visual && npm run build

preview:
	@echo "Starting preview server..."
	cd visual && npm run preview

test:
	@echo "Running tests..."
	python -m pytest tests/ 