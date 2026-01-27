# Invocación de Agentes

## Los 5 Agentes

| Agente | Cuándo | Qué verifica |
|--------|--------|--------------|
| best-practices-enforcer | Después de Write/Edit | type hints, Pydantic v2, httpx, structlog |
| security-auditor | Después de best-practices | OWASP Top 10, secrets, injection |
| hallucination-detector | Si usa bibliotecas externas | Sintaxis contra Context7 |
| code-reviewer | Antes de commit | Calidad, DRY, complejidad |
| test-generator | Al completar módulo | Tests unitarios |

## Cómo invocar

```
Task(subagent_type="best-practices-enforcer", prompt="Verifica src/...")
Task(subagent_type="security-auditor", prompt="Audita src/...")
Task(subagent_type="hallucination-detector", prompt="Verifica sintaxis...")
Task(subagent_type="code-reviewer", prompt="Review src/...")
Task(subagent_type="test-generator", prompt="Genera tests...")
```

## Si falla
- Corregir automáticamente
- Documentar en errors-to-rules.md si es error nuevo
- Volver a verificar
