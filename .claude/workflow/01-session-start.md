<!-- version: 2026-02 -->
# Session Start

<!-- COMPACT-SAFE: Session triggers (continua/crea/default), state detection (NO_EXISTE/NECESITA_SETUP/EN_PROGRESO/COMPLETADO) -->

## Triggers de Inicio

### "Continúa con [PROYECTO]"
1. Leer projects/[proyecto].json
2. Leer especificación del proyecto
3. Detectar estado actual
4. Continuar desde donde se quedó

### "Crea nuevo proyecto [NOMBRE]"
1. Ejecutar /new-project [nombre] [path]
2. Crear projects/[nombre].json
3. Iniciar Fase 0: Setup

### Sesión sin instrucción específica
1. Listar proyectos en projects/*.json
2. Si solo hay uno → usarlo
3. Si hay múltiples → preguntar cuál
4. Identificar siguiente tarea pendiente
5. HACER la tarea (no preguntar)

## Detección de Estado

| Estado | Acción |
|--------|--------|
| NO_EXISTE | /new-project |
| NECESITA_SETUP | Crear pyproject.toml |
| EN_PROGRESO | Continuar siguiente fase |
| COMPLETADO | Reportar, siguiente proyecto |
