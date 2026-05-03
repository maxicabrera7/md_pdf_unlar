# cvtmdpdf 📄

Convierte archivos `.md` a PDF con portada institucional UNLaR, estilos, tablas, imágenes y bloques de código. Se configura por proyecto mediante un archivo `.cfg`.

---

## Requisitos

- Python 3.8 o superior
- pip

---

## Instalación

### 1. Clonar o descargar el repositorio

Copiá los archivos en una carpeta fija, por ejemplo:

```
C:\Users\TuUsuario\scripts\cvtmdpdf\
```

Asegurate de que estén presentes:

```
cvtmdpdf/
├── make_pdf.py
├── requirements.txt
└── logo.png          ← opcional, para la portada
```

### 2. Instalar dependencias

Abrí una terminal en esa carpeta y ejecutá:

```powershell
pip install -r requirements.txt
```

---

### 3. Registrar el comando `cvtmdpdf` en PowerShell

Para poder escribir `cvtmdpdf archivo.md` desde cualquier carpeta, hay que agregar una función al perfil de PowerShell.

#### Paso 1 — Verificar si ya existe el archivo de perfil

```powershell
Test-Path $PROFILE
```

- Si devuelve `True` → ya existe, pasá al paso 2.
- Si devuelve `False` → crealo con:

```powershell
New-Item -ItemType File -Path $PROFILE -Force
```

#### Paso 2 — Abrir el perfil en el Bloc de notas

```powershell
notepad $PROFILE
```

#### Paso 3 — Agregar la función al final del archivo

Pegá esto al final, reemplazando la ruta por donde guardaste el script:

```powershell
function cvtmdpdf {
    python "C:\Users\TuUsuario\scripts\cvtmdpdf\make_pdf.py" @args
}
```

Guardá y cerrá el Bloc de notas.

#### Paso 4 — Recargar el perfil sin cerrar la terminal

```powershell
. $PROFILE
```

> ⚠️ **Si aparece un error de ejecución de scripts**, ejecutá esto una sola vez con PowerShell como administrador:
> ```powershell
> Set-ExecutionPolicy -Scope CurrentUser -ExecutionPolicy RemoteSigned
> ```

#### Paso 5 — Verificar que funciona

```powershell
cvtmdpdf --help
```

Debería mostrar el mensaje de uso del script.

---

## Uso

### Convertir un archivo

```powershell
cvtmdpdf "mi_documento.md"
```

El PDF se genera en la misma carpeta que el `.md`.

### Convertir múltiples archivos a la vez

```powershell
cvtmdpdf "tp1.md" "tp2.md"
```

### Convertir todos los `.md` de una carpeta

```powershell
cvtmdpdf *.md
```

---

## Configuración por proyecto (`cvtmdpdf.cfg`)

La primera vez que ejecutás el script en una carpeta nueva, se genera automáticamente un archivo `cvtmdpdf.cfg` con los datos de la portada:

```ini
[portada]
enabled     = true
subtitulo   = Trabajo Práctico
carrera     = T.U.I.
catedra     = Nombre de la Cátedra
docente     = Nombre del Docente
integrantes =
    Apellido, Nombre - DNI 12345678
    Apellido, Nombre - DNI 87654321
```

Editá ese archivo con los datos de tu entrega y volvé a ejecutar el comando. El script lo busca primero en la carpeta del `.md` y, si no lo encuentra ahí, en la carpeta del propio script.

> Para generar el PDF **sin portada**, cambiá `enabled = false`.

---

## Logo institucional

Colocá un archivo `logo.png` en la misma carpeta que `make_pdf.py`. El script procesa automáticamente la transparencia del fondo. Si no existe, se omite el escudo sin generar errores.

---

## Elementos de Markdown soportados

| Elemento | Sintaxis |
|---|---|
| Título del documento | `# Título` (primer H1 del archivo) |
| Sección numerada | `## 1. Nombre` |
| Subsección | `### Nombre` |
| Párrafo normal | Texto plano |
| **Negrita** / *Itálica* | `**texto**` / `*texto*` |
| Cita | `> texto` |
| Bullet | `- item` o `* item` |
| Código en línea | `` `código` `` |
| Bloque de código | ` ```lenguaje ... ``` ` |
| Tabla | Sintaxis Markdown estándar |
| Imagen | `![caption](ruta/imagen.png)` |
| Separador | `---` |
| Salto de página | `\salto de pagina` |

---

## Solución de problemas

| Problema | Solución |
|---|---|
| `cvtmdpdf` no se reconoce como comando | Verificá que ejecutaste `. $PROFILE` o reiniciaste PowerShell |
| Error de política de ejecución | Ejecutá `Set-ExecutionPolicy -Scope CurrentUser RemoteSigned` como administrador |
| PDF generado sin portada | Revisá que `enabled = true` en el `.cfg` |
| Sin escudo en la portada | Verificá que `logo.png` esté en la carpeta del script |
| Errores en el procesamiento | Revisá el archivo `error_log.txt` que se genera en la carpeta de trabajo |
