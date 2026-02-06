# Human-in-the-Loop Checkpoints

<!-- COMPACT-SAFE: PAUSE only for: phase transitions, destructive actions, post-verification synthesis. CONTINUE for: agent delegation, Context7 queries, file reads, report generation. -->

## PAUSAR para aprobación humana en:

1. **Inicio de Fase Nueva**
   - Anunciar objetivos y deliverables
   - Esperar confirmación

2. **Acciones Destructivas/Irreversibles**
   - Eliminación de archivos
   - Cambios arquitectónicos mayores
   - Cambios multi-módulo (>3 módulos)
   - Esperar confirmación

3. **Después de TODOS los agentes de verificación reportan**
   - Presentar resumen consolidado de los 5 agentes
   - Si hay fallos: esperar confirmación para corregir
   - Si todo OK: esperar confirmación para commit

## CONTINUAR automáticamente para:

- ✅ Delegación a code-implementer (sin esperar)
- ✅ Delegación a agentes de verificación (sin esperar)
- ✅ Consultas a Context7 (dentro de agentes)
- ✅ Generación de reportes técnicos
- ✅ Lectura de archivos y exploración de código

## Flujo de Checkpoints

```
Orquestador delega a code-implementer
         ↓
code-implementer reporta (~500+ líneas)
         ↓
    [CHECKPOINT] → Humano aprueba
         ↓
Orquestador delega a 5 agentes verificación
         ↓
Agentes reportan (~2500+ líneas total)
         ↓
    [CHECKPOINT] → Humano aprueba
         ↓
Si fallos → code-implementer corrige → [CHECKPOINT]
         ↓
Si OK → COMMIT
```
