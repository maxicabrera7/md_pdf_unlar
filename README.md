# Conversor MD a PDF (UNLaR)

Script de automatización para convertir archivos Markdown (.md) a PDF con el formato institucional de la UNLaR (T.U.I.). Optimizado para generación de trabajos prácticos con cumplimiento estricto de estilo y márgenes.

## 🛠 Requisitos Técnicos

El sistema requiere un entorno configurado correctamente para evitar errores de ejecución:

*   [**Git CLI**](https://git-scm.com/install/windows): Necesario para la sincronización de actualizaciones.
*   [**Python 3.10+**](https://www.python.org/downloads/): Motor de ejecución principal.
*   **PowerShell 7+**: Terminal recomendada para la ejecución de scripts.

## 🚀 Instalación y Configuración Automática

### 1. Habilitar ejecución de scripts en el sistema
`Set-ExecutionPolicy RemoteSigned -Scope CurrentUser -Force`

### 2. Clonar el repositorio e ingresar al directorio
`git clone https://github.com/maxicabrera7/md_pdf_unlar.git`
`cd md_pdf_unlar`

### 3. Crear entorno virtual e instalar dependencias (reportlab, Pillow)
1. `python -m venv venv`
2. `.\venv\Scripts\Activate.ps1`
3. `pip install -q -r requirements.txt`

### **Configuración Dinámica ($PROFILE)**:
   Añade este bloque a tu perfil de PowerShell (`notepad $PROFILE`). Solo debes editar la primera línea (`$basePath`) con la ruta real donde clonaste el proyecto:
```
   # --- COPIAR ESTO EN EL $PROFILE DE POWERSHELL ---

# 1. Definir la ruta donde se clonó el proyecto
$PATH_UNLAR = "C:\ruta\donde\esta\el\repo"

# 2. Función de sincronización inteligente (Si no existe, crearla)
if (-not (Get-Command Invoke-LazySync -ErrorAction SilentlyContinue)) {
    function Invoke-LazySync {
        param($repoPath, $repoName, $days = 5)
        $sFile = Join-Path $HOME ".cvt_sync_$repoName"
        $now = Get-Date
        if (Test-Path $sFile) {
            try {
                $last = [DateTime](Get-Content $sFile -Raw)
                if ($now -lt $last.AddDays($days)) { return }
            } catch { }
        }
        if (Test-Path (Join-Path $repoPath ".git")) {
            Write-Host "[!] Sincronizando $repoName..." -ForegroundColor Yellow
            Push-Location $repoPath; git pull origin main; Pop-Location
            $now.ToString("yyyy-MM-dd HH:mm:ss") | Out-File $sFile
        }
    }
}

# 3. Comando de ejecución
function cvtmdpdf {
    Invoke-LazySync $PATH_UNLAR "unlar"
    $py = Join-Path $PATH_UNLAR "Scripts\python.exe"
    $sc = Join-Path $PATH_UNLAR "make_pdf.py"
    if (Test-Path $py) { & $py $sc $args[0] } else { Write-Error "Entorno virtual no encontrado." }
}
```

## 📄 Modo de Uso

Una vez reiniciada la terminal, el comando `cvtmdpdf` estará disponible globalmente:

1. Navegue hasta la ubicación del archivo fuente.
2. Ejecute:
   cvtmdpdf "Nombre_Del_Archivo.md"

El sistema generará el PDF aplicando automáticamente el logo institucional y los márgenes configurados en `make_pdf.py`.

## ⚙️ Estructura del Proyecto
- `make_pdf.py:` Motor principal de renderizado.
- `logo.png:` Recurso gráfico institucional.
- `venv/:` Entorno virtual aislado para evitar conflictos de librerías.
- `requirements.txt:` Lista de dependencias técnicas.
- `.gitignore`: Configuración de exclusión para entornos virtuales y archivos temporales.

## ⚖️ Licencia
MIT License.
