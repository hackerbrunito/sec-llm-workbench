# /verify Command

Ejecuta todas las verificaciones en el proyecto activo.

---

## Uso

```
/verify
/verify --fix
/verify --project <nombre-proyecto>
```

---

## Comportamiento

Cuando se ejecute este comando, Claude DEBE:

### 1. Identificar Proyecto Activo
```python
# Leer de settings.json
active_project = settings["active_project"]["path"]
```

### 2. Ejecutar Verificaciones

```bash
cd $PROJECT_PATH

# 1. Format check
echo "📝 Verificando formato..."
uv run ruff format src tests --check

# 2. Linting
echo "🔎 Verificando linting..."
uv run ruff check src tests

# 3. Type checking
echo "🔤 Verificando tipos..."
uv run mypy src

# 4. Best practices
echo "🎯 Verificando best practices..."
"$CLAUDE_PROJECT_DIR/.claude/hooks/verify-best-practices.sh"

# 5. Security audit
echo "🔒 Ejecutando security audit..."
# Invocar security-auditor agent

# 6. Tests
echo "🧪 Ejecutando tests..."
uv run pytest tests/ -v --cov=src
```

### 3. Con --fix
```bash
# Aplicar correcciones automáticas
uv run ruff format src tests
uv run ruff check src tests --fix
```

---

## Output

```
🔍 VERIFICATION REPORT - {{proyecto}}

FORMAT:     ✅ OK
LINTING:    ✅ OK (0 errors, 2 warnings)
TYPES:      ✅ OK
PRACTICES:  ✅ OK
SECURITY:   ✅ OK (0 critical, 0 high)
TESTS:      ✅ OK (45 passed, 0 failed)
COVERAGE:   78%

═══════════════════════════════════
✅ ALL CHECKS PASSED
═══════════════════════════════════

# O si hay errores:

═══════════════════════════════════
❌ VERIFICATION FAILED

Issues to fix:
1. LINTING: 3 errors in src/api.py
2. TYPES: 2 errors in src/models.py
3. TESTS: 1 test failed

Run `/verify --fix` to auto-fix where possible
═══════════════════════════════════
```
