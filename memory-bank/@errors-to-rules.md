# Errores → Reglas (Self-Correcting Log)

Registro de errores cometidos y las reglas creadas para no repetirlos.

---

## Cómo Usar Este Archivo

1. Cuando Claude cometa un error, documentarlo aquí
2. Crear una regla específica para prevenir el error
3. Si es un patrón recurrente, agregar a CLAUDE.md como REGLA ABSOLUTA

---

## Registro de Errores

### 2026-01-20: Usar pip en lugar de uv

**Error:**
```bash
pip install pydantic  # ❌
```

**Contexto:** Claude usó pip por defecto al instalar dependencias.

**Regla creada:**
```
SIEMPRE usar uv (uv sync, uv add, uv run)
NUNCA usar pip install, pip freeze, python -m venv
```

**Estado:** ✅ Agregado a REGLAS ABSOLUTAS

---

### 2026-01-20: Subagentes pasivos

**Error:**
Los subagentes solo documentaban qué verificar, no ejecutaban verificaciones.

**Contexto:** Los archivos .md de subagentes eran documentación pasiva.

**Regla creada:**
```
Subagentes DEBEN tener COMPORTAMIENTO MANDATORIO
Deben EJECUTAR automáticamente, no solo DOCUMENTAR
```

**Estado:** ✅ Subagentes reescritos con comportamiento activo

---

### 2026-01-20: Pedir confirmaciones innecesarias

**Error:**
```
"¿Quieres que implemente esta función?"
"¿Debería agregar tests?"
```

**Contexto:** Claude pedía confirmación para tareas estándar.

**Regla creada:**
```
HACER: Implementar, verificar, corregir
NO HACER: "¿Quieres que...?", "¿Debería...?"

Solo preguntar para:
- Decisiones arquitectónicas mayores
- Eliminación de archivos importantes
- Cambios irreversibles
```

**Estado:** ✅ Agregado a REGLAS ABSOLUTAS

---

### 2026-01-21: META-PROYECTO dentro de SIOPV

**Error:**
Poner `.claude/`, `memory-bank/`, hooks dentro del proyecto SIOPV, contaminando el TFM.

**Contexto:** El usuario necesita presentar SIOPV como proyecto limpio y profesional.

**Regla creada:**
```
El META-PROYECTO debe estar SEPARADO del proyecto generado
El proyecto generado debe ser EXPORTABLE sin configuración de Vibe Coding
NUNCA incluir .claude/, memory-bank/ en proyectos destino
```

**Estado:** ✅ Rediseño completado con separación

---

### 2026-01-23: Audit missed hardcoded GitHub URL in README

**Error:**
Ran an audit searching for hardcoded references but missed `https://github.com/hackerbrunito/VIBE_CODING_2026.git` in README.md line 33.

**Contexto:**
Used grep to search for `github.com/hackerbrunito` but the search returned "None found" despite the URL being present. Did not manually verify critical files like README.md after automated search.

**Regla creada:**
```
AFTER automated audits, ALWAYS manually verify critical files:
- README.md
- CLAUDE.md
- .env.example
- Any file that users will see first

Automated grep searches can fail silently. Trust but verify.
```

**Estado:** ✅ URL fixed, rule documented

---

## Template para Nuevos Errores

```markdown
### YYYY-MM-DD: [Título del error]

**Error:**
[Qué se hizo mal]

**Contexto:**
[Por qué ocurrió]

**Regla creada:**
```
[Nueva regla específica]
```

**Estado:** ⏳ Pendiente / ✅ Implementado
```

---

## Estadísticas

| Categoría | Errores | Reglas Creadas |
|-----------|---------|----------------|
| Package Management | 1 | 1 |
| Comportamiento | 2 | 2 |
| Arquitectura | 1 | 1 |
| Auditoría | 1 | 1 |
| **Total** | **5** | **5** |

---

## Patrones Identificados

1. **Asumir defaults legacy** - pip, typing.List, Pydantic v1
2. **Pasividad** - Documentar en lugar de ejecutar
3. **Exceso de confirmaciones** - Preguntar lo obvio
4. **Mezclar concerns** - META + PROYECTO juntos
5. **Confiar ciegamente en automatización** - No verificar resultados de grep/búsquedas

**Acción:** Estas categorías deben tener verificación automática en hooks.
