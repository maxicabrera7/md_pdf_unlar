# Conversor MD a PDF (UNLaR)

Script de automatización para convertir archivos Markdown (.md) a PDF con el formato institucional de la UNLaR (T.U.I.). Optimizado para generación de trabajos prácticos y documentación técnica.

## 🛠 Requisitos Técnicos

- **Python 3.10+**
- **Dependencias:**
  - `reportlab` (Motor de renderizado PDF)
  - `Pillow` (Procesamiento de logos y transparencia)

Instala las dependencias necesarias con:
```powershell
pip install -r requirements.txt
```

## 🚀 Instalación y Configuración en Windows

Para ejecutar el script desde cualquier ubicación de la terminal, añade las siguientes funciones a tu perfil de PowerShell (`notepad $PROFILE`):
```powershell
# Sincronización automática cada 5 días y ejecución
$syncFile = "$HOME\.cvt_last_sync"
$currentDate = Get-Date

function Invoke-LazySync {
    param($repoPath)
    if (Test-Path $syncFile) {
        $lastSync = Get-Date (Get-Content $syncFile)
        if ($currentDate -gt $lastSync.AddDays(5)) {
            Write-Host "[!] Sincronizando repositorio..." -ForegroundColor Yellow
            Push-Location $repoPath
            git pull origin main
            Pop-Location
            $currentDate | Out-File $syncFile
        }
    } else { $currentDate | Out-File $syncFile }
}

function cvtmdpdf {
    Invoke-LazySync "C:\md_pdf_unlar"
    & "C:\md_pdf_unlar\Scripts\python.exe" "C:\md_pdf_unlar\make_pdf.py" $args[0]
}
```

## 📄 Uso

1. Navega hasta la carpeta donde tienes tu archivo `.md`.
2. Ejecuta:
   ```powershell
   cvtmdpdf "TuArchivo.md"
   ```
3. Si es la primera vez que lo usas, el script generará un archivo `cvtmdpdf.cfg`. Edítalo con tus datos (Nombre, DNI, Cátedra) y vuelve a ejecutar el comando.

## ⚙️ Estructura del Proyecto

- `make_pdf.py`: Lógica principal y manejo de estilos ReportLab.
- `requirements.txt`: Dependencias mínimas del entorno.
- `logo.png`: Escudo institucional (requerido para la portada).
- `.gitignore`: Filtro de basura técnica (PDFs generados, entornos virtuales y logs).

## ⚖️ Licencia
Distribuido bajo la **MIT License**. Úsalo bajo tu propio riesgo; si tu docente te desaprueba por el formato, no es problema del código.