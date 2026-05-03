# Conversor MD a PDF (UNLaR)

Script de automatización para convertir archivos Markdown (.md) a PDF con el formato institucional de la UNLaR (T.U.I.). Optimizado para generación de trabajos prácticos y documentación técnica.

## 🛠 Requisitos Técnicos

- **Git CLI** (Instalado y en el PATH)
- **Python 3.10+**
- **Dependencias:** `reportlab`, `Pillow`.

Instala las dependencias necesarias con:
```powershell
pip install -r requirements.txt
```

## 🚀 Instalación y Configuración en Windows

Para ejecutar el script desde cualquier ubicación de la terminal, añade estas funciones a tu perfil de PowerShell (`notepad $PROFILE`):
```powershell
# Sincronización automática cada 5 días y ejecución
$syncFile = "$HOME\.cvt_last_sync"
$currentDate = Get-Date

function Invoke-LazySync {
    param($repoPath)
    if (Test-Path $syncFile) {
        $rawContent = (Get-Content $syncFile -TotalCount 1).Trim()
        $lastSync = $null
        if ([DateTime]::TryParse($rawContent, [ref]$lastSync)) {
            if ($currentDate -gt $lastSync.AddDays(5)) {
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

## 📄 Uso

1. Navega hasta la carpeta de tu archivo `.md`.
2. Ejecuta:
   ```powershell
   cvtmdpdf "TuArchivo.md"
   ```

## ⚙️ Estructura del Proyecto

- `make_pdf.py`: Lógica principal de renderizado.
- `requirements.txt`: Dependencias del entorno.
- `logo.png`: Escudo institucional.
- `.gitignore`: Filtro de basura técnica y entornos virtuales.

## ⚖️ Licencia
MIT License.