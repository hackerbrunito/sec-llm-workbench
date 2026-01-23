# Técnicas de Vibe Coding 2026

Referencia rápida de todas las técnicas implementadas en este framework.

---

## 1. uv (Package Manager)

**Reemplaza:** pip, venv, pip-tools

```bash
uv sync              # Instalar dependencias
uv run pytest        # Ejecutar con venv
uv add pydantic      # Agregar dependencia
uv add --dev pytest  # Agregar dev dependency
```

**Por qué:** 10-100x más rápido que pip, lockfile determinístico.

---

## 2. Subagentes con Comportamiento Activo

**Reemplaza:** Documentación pasiva

Los subagentes **EJECUTAN** automáticamente, no solo documentan:
- `best-practices-enforcer` - Verifica y corrige
- `security-auditor` - Escanea vulnerabilidades
- `code-reviewer` - Review automático
- `test-generator` - Genera tests

---

## 3. Hooks de Enforcement

**Reemplaza:** Verificación manual

```
post-code.sh        → Ejecuta después de generar código
pre-commit.sh       → Ejecuta antes de commit
verify-best-practices.sh → Verifica estándares
```

---

## 4. MCP Context7

**Reemplaza:** Asumir sintaxis de bibliotecas

```bash
claude mcp add context7 -- npx -y @upstash/context7-mcp@latest
```

**Uso:** SIEMPRE consultar antes de usar bibliotecas externas.

---

## 5. Self-Correcting Pattern

**Reemplaza:** Repetir errores

```
Error detectado → Documentar en @errors-to-rules.md → No repetir
```

---

## 6. Git Worktrees

**Reemplaza:** git stash, cambiar branches constantemente

```bash
git worktree add ../project-feature -b feature/X
```

Permite trabajar en múltiples branches simultáneamente.

---

## 7. Sin Confirmaciones

**Reemplaza:** "¿Quieres que...?", "¿Debería...?"

Claude HACE, no PREGUNTA (excepto decisiones arquitectónicas).

---

## 8. Separación META vs PROYECTO

**Reemplaza:** Configuración dentro del proyecto

```
META-PROYECTO (framework)     →    PROYECTO (código limpio)
<meta-proyecto>/              →    ~/<proyecto>/
```

El proyecto generado es exportable sin el META-PROYECTO.

---

## 9. Docker Multi-stage

**Reemplaza:** Dockerfile monolítico

```dockerfile
FROM python:3.11-slim AS base
FROM base AS builder
FROM base AS production
FROM base AS development
```

---

## 10. DevContainers

**Reemplaza:** "En mi máquina funciona"

Entorno de desarrollo reproducible con VS Code.

---

## 11. Modern Python Type Hints

**Reemplaza:** typing.List, typing.Dict, typing.Optional

```python
# Moderno (Python 3.11+)
list[str]
dict[str, int]
X | None
```

---

## 12. Pydantic v2

**Reemplaza:** Pydantic v1 patterns

```python
# v2
model_config = ConfigDict(strict=True)

@field_validator("field")
@classmethod
def validate(cls, v): ...
```

---

## 13. Async HTTP (httpx)

**Reemplaza:** requests (sync)

```python
async with httpx.AsyncClient() as client:
    response = await client.get(url)
```

---

## Resumen Visual

```
┌─────────────────────────────────────────────────────────────┐
│                    VIBE CODING 2026                          │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  Package Manager:     uv (no pip)                            │
│  Subagentes:          Activos (no pasivos)                   │
│  Enforcement:         Hooks automáticos                      │
│  Documentación:       Context7 MCP                           │
│  Errores:             Self-correcting                        │
│  Git:                 Worktrees                              │
│  Confirmaciones:      Sin (excepto arquitectura)             │
│  Estructura:          META separado de PROYECTO              │
│  Containers:          Docker multi-stage                     │
│  Dev Environment:     DevContainers                          │
│  Python:              Type hints modernos                    │
│  Validación:          Pydantic v2                            │
│  HTTP:                httpx async                            │
│                                                              │
└─────────────────────────────────────────────────────────────┘
```
