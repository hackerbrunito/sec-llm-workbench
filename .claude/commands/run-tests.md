# /run-tests

Ejecutar suite de tests con cobertura y reportes.

---

## Uso

```bash
/run-tests                    # Todos los tests
/run-tests unit               # Solo unit tests
/run-tests integration        # Solo integration tests
/run-tests --coverage         # Con reporte de cobertura
/run-tests --security         # Tests de seguridad
```

---

## Workflow

```
1. Verificar entorno (uv sync)
2. Ejecutar tests según tipo
3. Generar reporte de cobertura
4. Mostrar resumen
5. Fallar si cobertura < 80%
```

---

## Comandos Ejecutados

```bash
# Unit tests
uv run pytest tests/unit -v --tb=short

# Integration tests
uv run pytest tests/integration -v --tb=short

# Con cobertura
uv run pytest tests/ --cov=src --cov-report=html --cov-report=term-missing

# Tests de seguridad (bandit)
uv run bandit -r src/ -f json -o security-report.json
```

---

## Ejemplo de Output

```
🧪 TEST RESULTS

Unit Tests:      45 passed, 2 skipped
Integration:     12 passed, 1 failed
Security:        0 vulnerabilities found

Coverage Report:
├── src/domain/          92%
├── src/application/     87%
├── src/adapters/        78%
├── src/infrastructure/  85%
└── TOTAL:               84% ✅

Failed Tests:
1. tests/integration/test_nvd_client.py::test_rate_limiting
   - AssertionError: Expected 429, got 200
   - [Ver detalles en htmlcov/]

📁 Reports generated:
- htmlcov/index.html
- security-report.json
```

---

## Configuración pytest

```toml
# pyproject.toml
[tool.pytest.ini_options]
minversion = "8.0"
testpaths = ["tests"]
asyncio_mode = "auto"
markers = [
    "slow: marks tests as slow",
    "integration: marks tests as integration tests",
    "security: marks tests as security tests",
]
```

---

## Integración CI/CD

```yaml
# .github/workflows/test.yml
- name: Run tests
  run: |
    uv sync
    uv run pytest --cov=src --cov-fail-under=80
```
