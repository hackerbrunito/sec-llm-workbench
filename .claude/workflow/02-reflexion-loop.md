# Reflexion Loop (PRA Pattern)

Para CADA tarea de desarrollo:

## 1. PERCEPTION
- Identificar qué hacer en especificación
- Identificar errores pasados en errors-to-rules.md

## 2. REASONING
- Query Context7 MCP para sintaxis de bibliotecas
- Diseñar approach basado en spec

## 3. ACTION
- Write/Edit código
- Usar sintaxis verificada por Context7

## 4. REFLECTION
Ejecutar 5 agentes:
1. best-practices-enforcer
2. security-auditor
3. hallucination-detector
4. code-reviewer
5. test-generator

## 5. VERIFY
- ✅ Todos pasan → COMMIT
- ❌ Alguno falla → Volver a REASONING

## 6. LEARN
Si hubo errores: documentar en errors-to-rules.md

## 7. COMMIT
Solo si verificación exitosa.
