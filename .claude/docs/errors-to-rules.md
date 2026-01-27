# Errores → Reglas (Self-Correcting Log)

Registro condensado de errores y reglas. Claude DEBE revisar antes de cada sesion.

---

## Reglas Activas (18 errores → 15 reglas unicas)

| # | Regla | Origen |
|---|-------|--------|
| 1 | SIEMPRE uv (nunca pip/venv) | 2026-01-20 |
| 2 | Agentes EJECUTAN, no solo documentan | 2026-01-20 |
| 3 | No pedir confirmacion en tareas estandar. Solo para: arquitectura mayor, eliminacion archivos, cambios irreversibles | 2026-01-20 |
| 4 | META-PROYECTO separado del PROYECTO. Nunca .claude/ ni memory-bank/ en proyectos destino | 2026-01-21 |
| 5 | Despues de audits automaticos, verificar manualmente README.md, CLAUDE.md, .env.example | 2026-01-23 |
| 6 | SIEMPRE consultar Context7 antes de escribir config o codigo con bibliotecas externas. Nunca asumir de memoria | 2026-01-26 |
| 7 | Cuando algo falla: ejecutar agentes primero, aplicar sus recomendaciones, nunca corregir solo | 2026-01-26 |
| 8 | Flujo COMPLETO del orchestrator antes de CADA commit, sin excepciones por simplicidad | 2026-01-26 |
| 9 | TODO modulo Python con logica necesita tests (validadores, config, CLI, exceptions) | 2026-01-26 |
| 10 | Documentar errores INMEDIATAMENTE, no esperar al final | 2026-01-26 |
| 11 | NUNCA afirmar "X recomienda Y" sin cita exacta. Honestidad > parecer experto | 2026-01-26 |
| 12 | Para afirmar "mas popular": necesitas 20+ fuentes. Con 3-5 decir "de las fuentes revisadas..." | 2026-01-26 |
| 13 | Verificar filesystem antes de afirmar sobre archivos. Filesystem = fuente de verdad | 2026-01-26 |
| 14 | Al hablar de configuracion, SIEMPRE aclarar scope: ~/.claude/ vs proyecto/.claude/ vs META/.claude/ | 2026-01-26 |
| 15 | Cuando falles en seguir docs existentes: admitirlo, no sugerir crear mas documentacion | 2026-01-26 |

---

## Patron Raiz: PILOTO AUTOMATICO

Actuar por memoria de entrenamiento ignorando orchestrator y especificaciones.

**Solucion implementada:** Sistema 2026
- Reflexion Loop (PRA): Perception → Reasoning → Action → Reflection
- 7 agentes de verificacion antes de commit
- Human-in-the-Loop solo en checkpoints mayores
- CLAUDE.md optimizado (<50 instrucciones)
- Hooks con additionalContext (middleware, no blocking)
- Anti-Autopilot ELIMINADO por contraproducente

---

## Patrones a Evitar

**Implementacion:**
1. Asumir defaults legacy (pip, typing.List, Pydantic v1)
2. Omitir pasos del workflow asumiendo "no aplican"
3. Corregir sin validar con agentes
4. Asumir excepciones por contexto ("es simple", "es setup")

**Comunicacion:**
5. Inventar autoridad sin evidencia
6. Presentar investigacion superficial como profunda
7. Evasion sugiriendo mas docs en lugar de admitir que no se consultan

---

## Template Nuevos Errores

```markdown
### YYYY-MM-DD: [Titulo]
**Error:** [Que se hizo mal]
**Regla:** [Como prevenirlo]
**Estado:** Pendiente / Implementado
```
