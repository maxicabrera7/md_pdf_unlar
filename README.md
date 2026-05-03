# Conversor MD a PDF (UNLaR)

Script de automatización para convertir archivos Markdown (.md) a PDF con el formato institucional de la UNLaR (T.U.I.). Optimizado para generación de trabajos prácticos y documentación técnica con estricto cumplimiento de estilo.

## 🛠 Requisitos Técnicos e Infraestructura

Para evitar fallos de ejecución por un entorno mal configurado, asegúrese de cumplir con los siguientes requisitos:

* **Git CLI**: Instalado y configurado en el PATH del sistema para permitir la sincronización automática. [Git Cli](https://git-scm.com/download/win)
* **Python 3.10+**: Con la opción "Add Python to PATH" activa durante la instalación. [Python](https://www.python.org/downloads/)
* **Terminal**: Windows PowerShell o PowerShell 7+. No se garantiza compatibilidad con CMD o Git Bash.
* **Dependencias**: Se requiere la instalación de `reportlab` y `Pillow`.

## 🚀 Instalación y Despliegue

Siga esta secuencia de comandos para inicializar el entorno de trabajo:

1. **Clonación del Repositorio**:
```
   1. git clone https://github.com/maxicabrera7/md_pdf_unlar.git C:\dev\md_pdf_unlar
   2. cd C:\dev\md_pdf_unlar
```

2. **Instalación de Librerías**:
   ```python
   pip install -r requirements.txt

3. **Configuración de Automatización ($PROFILE)**:
   Abra su perfil de PowerShell (`notepad $PROFILE`) y añada el siguiente bloque técnico para habilitar la sincronización de 5 días y el comando global:
```powershell
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
                       Write-Host "[!] Sincronizando repositorio UNLaR..." -ForegroundColor Yellow
                       Push-Location $repoPath; git pull origin main; Pop-Location
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

* `make_pdf.py`: Motor principal de renderizado PDF.
* `requirements.txt`: Definición de dependencias del proyecto.
* `logo.png`: Recurso gráfico para el encabezado institucional.
* `.gitignore`: Configuración de exclusión para entornos virtuales y archivos temporales.

## ⚖️ Licencia
MIT License.
