# Conversor MD a PDF (UNLaR)

Script de automatización para convertir archivos Markdown (.md) a PDF con el formato institucional de la UNLaR (T.U.I.). Optimizado para generación de trabajos prácticos con cumplimiento estricto de estilo y márgenes.

## 🛠 Requisitos Técnicos

El sistema requiere un entorno configurado correctamente para evitar errores de ejecución:

*   [**Git CLI**](https://git-scm.com/install/windows): Necesario para la sincronización de actualizaciones.
*   [**Python 3.10+**](https://www.python.org/downloads/): Motor de ejecución principal.
*   **PowerShell 7+**: Terminal recomendada para la ejecución de scripts.

## 🚀 Instalación y Configuración Automática

Ejecute este bloque de comandos en su terminal para inicializar el entorno. No requiere configuración manual de rutas.
```powershell
# 1. Habilitar ejecución de scripts en el sistema
Set-ExecutionPolicy RemoteSigned -Scope CurrentUser -Force

# 2. Clonar el repositorio e ingresar al directorio
git clone [https://github.com/maxicabrera7/md_pdf_unlar.git](https://github.com/maxicabrera7/md_pdf_unlar.git)
cd md_pdf_unlar

# 3. Crear entorno virtual e instalar dependencias (reportlab, Pillow)
python -m venv venv
.\venv\Scripts\pip install -q -r requirements.txt

# 4. Registrar comando global en el $PROFILE
```powershell
$currentPath = Get-Location
$profileDir = Split-Path $PROFILE -Parent
if (!(Test-Path $profileDir)) { New-Item -Path $profileDir -ItemType Directory }

$functionBlock = @"

function cvtmdpdf {
    # Sincronización automática con el repositorio
    Write-Host "[!] Validando actualizaciones..." -ForegroundColor Cyan
    Push-Location "$currentPath"
    git pull --quiet
    Pop-Location

    # Ejecución mediante el entorno virtual aislado
    & "$currentPath\venv\Scripts\python.exe" "$currentPath\make_pdf.py" `$args[0]
}
"@
```
Add-Content -Path $PROFILE -Value `n$functionBlock
Write-Host "[!] Instalación completada. Reinicie su terminal para usar 'cvtmdpdf'." -ForegroundColor Green

## 📄 Modo de Uso

Una vez reiniciada la terminal, el comando `cvtmdpdf` estará disponible globalmente:

1. Navegue hasta la ubicación del archivo fuente.
2. Ejecute:
   cvtmdpdf "Nombre_Del_Archivo.md"

El sistema generará el PDF aplicando automáticamente el logo institucional y los márgenes configurados en `make_pdf.py`.

## ⚙️ Estructura del Proyecto
'make_pdf.py:' Motor principal de renderizado.

'logo.png:' Recurso gráfico institucional.

'venv/:' Entorno virtual aislado para evitar conflictos de librerías.

'requirements.txt:' Lista de dependencias técnicas.

## ⚖️ Licencia
MIT License.