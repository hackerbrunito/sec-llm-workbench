---
name: run-tests
disable-model-invocation: true
description: "Ejecutar suite de tests con cobertura y reportes"
argument-hint: "[scope]"
context: fork
allowed-tools: ["Read", "Bash", "Glob", "Grep"]
---

# /run-tests

Ejecutar suite de tests con cobertura.

## Uso

```
/run-tests                    # Todos los tests
/run-tests unit               # Solo unit tests
/run-tests integration        # Solo integration tests
/run-tests --coverage         # Con reporte de cobertura
/run-tests --security         # Tests de seguridad
```

## Comandos

```bash
# Unit tests
uv run pytest tests/unit -v --tb=short

# Integration tests
uv run pytest tests/integration -v --tb=short

# Con cobertura
uv run pytest tests/ --cov=src --cov-report=html --cov-report=term-missing

# Tests de seguridad
uv run bandit -r src/ -f json -o security-report.json
```

## Cobertura minima: 80%
