# Git Workflow - META-PROYECTO

Workflow de Git para el framework Vibe Coding y proyectos generados.

---

## Dos Repositorios Separados

```
<meta-proyecto>/                 ~/<proyecto>/
├── .git/ ──► github/<meta-repo> ├── .git/ ──► github/<proyecto>
│   (privado)                    │   (público)
```

---

## Comportamiento Automático de Claude

### HACER Automáticamente (sin preguntar)
```bash
# Después de implementar feature completa
git add .
git commit -m "tipo(scope): descripción"
```

> **IMPORTANTE:** NUNCA incluir `Co-Authored-By` ni referencias a Claude/AI en commits de proyectos públicos generados. Solo en el meta-proyecto privado si el usuario lo solicita.

### NUNCA Hacer (sin confirmación explícita)
```bash
git push                    # Siempre pedir confirmación
git push --force            # PROHIBIDO
git reset --hard            # PROHIBIDO
git rebase -i               # PROHIBIDO
```

---

## Convención de Commits

```
tipo(scope): descripción corta (máx 72 chars)

[cuerpo opcional - explicar el por qué]
```

### Tipos

| Tipo | Uso |
|------|-----|
| `feat` | Nueva funcionalidad |
| `fix` | Corrección de bug |
| `refactor` | Refactorización (sin cambio funcional) |
| `test` | Agregar/modificar tests |
| `docs` | Documentación |
| `chore` | Mantenimiento, dependencias |
| `style` | Formato, espacios (sin cambio funcional) |
| `perf` | Mejora de rendimiento |

### Ejemplos
```
feat(classifier): add XGBoost model training
fix(rag): handle empty NVD responses
refactor(auth): simplify OpenFGA permission checks
test(ingestion): add Trivy parser tests
docs(readme): update installation instructions
chore(deps): update pydantic to 2.6
```

---

## Git Worktrees

Para trabajo paralelo en múltiples features sin cambiar de branch.

### Crear Worktree
```bash
# Desde el proyecto principal
cd ~/<proyecto>

# Crear worktree para feature
git worktree add ../<proyecto>-feature-auth -b feature/auth

# Crear worktree para hotfix
git worktree add ../<proyecto>-hotfix -b hotfix/critical-bug
```

### Estructura Resultante
```
~/
├── <proyecto>/                    # Branch: main o develop
├── <proyecto>-feature-auth/       # Branch: feature/auth
├── <proyecto>-feature-rag/        # Branch: feature/rag
└── <proyecto>-hotfix/             # Branch: hotfix/critical-bug
```

### Listar Worktrees
```bash
git worktree list
```

### Eliminar Worktree (después de merge)
```bash
# 1. Merge la branch
git checkout main
git merge feature/auth

# 2. Eliminar worktree
git worktree remove ../<proyecto>-feature-auth

# 3. Eliminar branch (opcional)
git branch -d feature/auth
```

### Reglas de Worktrees
- **NUNCA** tener el mismo branch en dos worktrees
- **SIEMPRE** eliminar worktree después de merge
- **PREFERIR** worktrees para features grandes o paralelas

---

## Flujo de Desarrollo

### Feature Branch
```
main
  │
  └── feature/nueva-feature
         │
         ├── commit 1
         ├── commit 2
         └── commit 3 (PR → main)
```

### Comandos
```bash
# Crear feature branch
git checkout -b feature/<your-feature>

# Trabajar y commitear
git add .
git commit -m "feat(scope): implementar X"

# Push (pedir confirmación)
git push -u origin feature/<your-feature>

# Crear PR
gh pr create --title "feat: <description>" --body "..."
```

---

## Para el META-PROYECTO

El META-PROYECTO tiene su propio .git:

```bash
cd ~/<meta-proyecto>  # Tu directorio del META-PROYECTO
git init
git remote add origin git@github.com:<your-username>/<meta-repo>.git

# Commits del META-PROYECTO
git add .
git commit -m "chore: update project config"
```

### .gitignore del META-PROYECTO
```gitignore
# Local settings
.claude/settings.local.json

# OS
.DS_Store

# Temporary
*.tmp
*.log
```

---

## Para Proyectos Generados

Cada proyecto tiene su propio .git independiente:

```bash
cd ~/<proyecto>
git init
git remote add origin git@github.com:<your-username>/<your-project>.git

# Verificar que está limpio (sin rastro de META-PROYECTO)
ls -la  # NO debe tener .claude/, memory-bank/
```

---

## Checklist Pre-Push

Antes de hacer push a cualquier proyecto:

```bash
# 1. Verificar estado
git status

# 2. Verificar que no hay archivos sensibles
git diff --staged | grep -i "password\|secret\|key"

# 3. Ejecutar verificaciones
/verify

# 4. Push (con confirmación)
git push origin [branch]
```
