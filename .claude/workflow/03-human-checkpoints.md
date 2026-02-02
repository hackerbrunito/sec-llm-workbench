# Human-in-the-Loop Checkpoints

## PAUSAR para aprobación humana en:

1. **Inicio de Fase Nueva**
   - Anunciar objetivos y deliverables
   - Esperar confirmación

2. **Cambio Arquitectónico Mayor**
   - Explicar propuesta e impacto
   - Esperar confirmación

3. **Eliminación de Archivos**
   - Listar archivos a eliminar
   - Esperar confirmación

4. **Cambio Multi-Módulo (>3 módulos)**
   - Listar módulos afectados
   - Esperar confirmación

5. **Después de code-implementer reporta**
   - Presentar resumen del reporte técnico
   - Esperar confirmación para lanzar verificación

6. **Después de agentes de verificación reportan**
   - Presentar resumen de todos los reportes
   - Si hay fallos: esperar confirmación para corregir
   - Si todo OK: esperar confirmación para commit

## CONTINUAR automáticamente para:

- ✅ Delegación a code-implementer (sin esperar)
- ✅ Delegación a agentes de verificación (sin esperar)
- ✅ Consultas a Context7 (dentro de agentes)
- ✅ Generación de reportes técnicos

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
