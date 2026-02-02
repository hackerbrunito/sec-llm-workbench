# Invocación de Agentes

## Agente de Implementación

| Agente | Cuándo | Qué hace | Reporte |
|--------|--------|----------|---------|
| code-implementer | Cuando hay código que escribir | Consulta fuentes (ver abajo), implementa con técnicas modernas | ~500+ líneas (flexible) |

### code-implementer DEBE consultar:

1. **`.claude/docs/python-standards.md`** → Estándares del proyecto (Pydantic v2, httpx, structlog, pathlib, type hints modernos)
2. **`.claude/rules/core-rules.md`** → Tech stack y reglas generales
3. **Context7 MCP** → Sintaxis moderna y patrones actualizados para CADA biblioteca usada

### Orden de consulta:
```
1. Leer python-standards.md (QUÉ usar)
2. Leer core-rules.md (reglas del proyecto)
3. Query Context7 (CÓMO usarlo correctamente)
4. Implementar código
5. Generar reporte técnico
```

## 5 Agentes de Verificación

| Agente | Cuándo | Qué verifica | Reporte |
|--------|--------|--------------|---------|
| best-practices-enforcer | Después de code-implementer | type hints, Pydantic v2, httpx, structlog | ~500+ líneas (flexible) |
| security-auditor | Después de best-practices | OWASP Top 10, secrets, injection | ~500+ líneas (flexible) |
| hallucination-detector | Siempre (TODO el código) | Sintaxis contra Context7 | ~500+ líneas (flexible) |
| code-reviewer | Antes de commit | Calidad, DRY, complejidad | ~500+ líneas (flexible) |
| test-generator | Al completar módulo | Tests unitarios | ~500+ líneas (flexible) |

## Cómo invocar

```
# Implementación
Task(subagent_type="code-implementer", prompt="Implementa [tarea] en [path]...")

# Verificación
Task(subagent_type="best-practices-enforcer", prompt="Verifica src/...")
Task(subagent_type="security-auditor", prompt="Audita src/...")
Task(subagent_type="hallucination-detector", prompt="Verifica sintaxis de TODO el código...")
Task(subagent_type="code-reviewer", prompt="Review src/...")
Task(subagent_type="test-generator", prompt="Genera tests...")
```

## Reportes Técnicos

Todos los agentes deben generar reportes técnicos detallados (~500+ líneas, flexible):
- Proporciona **trazabilidad completa** del proceso
- Permite al orquestador **responder cualquier pregunta**
- Total esperado: **~3000-4000 líneas** por ciclo completo

## Si falla
- Delegar corrección a code-implementer
- Documentar en errors-to-rules.md si es error nuevo
- Volver a verificar con los 5 agentes
