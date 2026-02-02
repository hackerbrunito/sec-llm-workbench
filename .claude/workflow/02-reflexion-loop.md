# Reflexion Loop (PRA Pattern)

Para CADA tarea de desarrollo:

## 1. PERCEPTION (Orquestador)
- Identificar qué hacer en especificación
- Identificar errores pasados en errors-to-rules.md

## 2. REASONING (Orquestador)
- Diseñar approach basado en spec
- Preparar prompt detallado para code-implementer

## 3. ACTION (Delegado a code-implementer)
- Orquestador delega a `code-implementer`
- code-implementer consulta Context7 para TODO el código (no solo bibliotecas)
- code-implementer genera código con técnicas/patrones modernos
- code-implementer reporta resultado (~500+ líneas, flexible)

## 4. CHECKPOINT HUMANO
- Orquestador presenta resumen del reporte de code-implementer
- Esperar aprobación humana para continuar a verificación

## 5. REFLECTION (Delegado a 5 agentes)
Ejecutar 5 agentes de verificación:
1. best-practices-enforcer → reporta ~500+ líneas
2. security-auditor → reporta ~500+ líneas
3. hallucination-detector → reporta ~500+ líneas
4. code-reviewer → reporta ~500+ líneas
5. test-generator → reporta ~500+ líneas

## 6. CHECKPOINT HUMANO
- Orquestador presenta resumen de reportes de verificación
- Esperar aprobación humana para continuar

## 7. VERIFY
- ✅ Todos pasan → continuar a COMMIT
- ❌ Alguno falla → Delegar corrección a code-implementer → volver a paso 4

## 8. LEARN
Si hubo errores: documentar en errors-to-rules.md

## 9. COMMIT
Solo si verificación exitosa y aprobación humana.

---

## Arquitectura de Contexto

| Componente | Contexto usado |
|------------|----------------|
| Orquestador | Mínimo (solo delega) |
| code-implementer | Su propio contexto |
| 5 agentes verificación | Su propio contexto |
| **Reportes totales** | ~3000-4000 líneas |
| **Contexto orquestador** | Libre para ingesta total |

**Beneficio:** Trazabilidad completa. Orquestador puede responder cualquier pregunta.
