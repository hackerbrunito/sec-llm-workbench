---
auto-load: true
priority: critical
---

# Confirmación Humana Obligatoria

**Estado:** ACTIVO (parte del Sistema Anti-Autopilot)

## Regla Fundamental

Antes de CADA operación Write/Edit, Claude DEBE:

1. **ANUNCIAR** qué va a hacer
2. **ESPECIFICAR** qué consultó (orchestrator, spec, Context7, agentes)
3. **ESPERAR** confirmación explícita del usuario
4. **EJECUTAR** solo después de confirmación

## Excepciones

Ninguna. Esta regla aplica a TODO Write/Edit sin excepción.

## Formato de Anuncio

```
🔧 VOY A: [acción específica]

📚 CONSULTÉ:
- [ ] orchestrator.md (sección X)
- [ ] Especificación (línea Y)
- [ ] errors-to-rules.md (error Z)
- [ ] Context7: [biblioteca] (resultado: ...)
- [ ] Agente: [nombre] (resultado: ...)

❓ ¿Confirmas que proceda? (sí/no)
```

## Ejemplo

```
🔧 VOY A: Crear src/domain/models/vulnerability.py con modelo Pydantic v2

📚 CONSULTÉ:
- [x] orchestrator.md (sección 3.1: Fase 0 - Domain Layer)
- [x] Especificación (línea 245-289: Modelo de Vulnerabilidad)
- [x] errors-to-rules.md (error "No consultar Context7 antes de escribir")
- [x] Context7: pydantic (confirma sintaxis model_config, field_validator)
- [x] Agente: hallucination-detector (verificó sintaxis Pydantic v2)

❓ ¿Confirmas que proceda? (sí/no)
```

## Propósito

Prevenir "piloto automático" donde Claude actúa basado en entrenamiento obsoleto en lugar de consultar documentación actual.

## Historia

Creado 2026-01-26 después de errores repetidos (ver errors-to-rules.md, error "Piloto automático").

Usuario invirtió 10 días creando orchestrator + especificaciones. En 2 intentos de implementación, Claude los ignoró completamente.

Este sistema fuerza verificación humana para cada acción.
