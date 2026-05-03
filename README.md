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

### 4. Registrar comando global en el `notepad $PROFILE`
Sincronización automática cada 1 día y ejecución
```
$syncFile = "$HOME\.cvt_last_sync"
$currentDate = Get-Date

function Invoke-LazySync {
    param($repoPath)
    if (Test-Path $syncFile) {
        $rawContent = (Get-Content $syncFile -TotalCount 1).Trim()
        $lastSync = $null
        if ([DateTime]::TryParse($rawContent, [ref]$lastSync)) {
            if ($currentDate -gt $lastSync.AddDays(1)) {
                if (Test-Path "$repoPath\.git") {
                    Push-Location $repoPath
                    git pull origin main
                    Pop-Location
                    $currentDate.ToString() | Out-File $syncFile
                }
            }
        } else { $currentDate.ToString() | Out-File $syncFile }
    } else { $currentDate.ToString() | Out-File $syncFile }
}

function cvtmdpdf {
    Invoke-LazySync "C:\dev\md_pdf_unlar"
    & "C:\dev\md_pdf_unlar\Scripts\python.exe" "C:\dev\md_pdf_unlar\make_pdf.py" $args[0]
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
