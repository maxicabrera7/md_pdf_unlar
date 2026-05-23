import os
import glob
import re
import sys
import configparser
from PIL import Image, ImageDraw
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.units import cm
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_JUSTIFY, TA_RIGHT
from reportlab.platypus import (SimpleDocTemplate, Paragraph, Spacer, PageBreak,
                                 Table, TableStyle, HRFlowable,
                                 Image as RLImage, Preformatted, KeepTogether)
from reportlab.platypus.flowables import Flowable
from reportlab.pdfbase.pdfmetrics import stringWidth

# ==========================================
# 1. CONFIGURACIÓN DE ARCHIVOS
# ==========================================
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

if len(sys.argv) < 2:
    print("❌ Error: Debes especificar un archivo. Uso: cvtmdpdf 'nombre.md'")
    sys.exit(1)

ARCHIVO_MD = sys.argv[1]
INPUT_LOGO = os.path.join(BASE_DIR, 'logo.png')
TRANS_LOGO = os.path.join(BASE_DIR, 'trans_logo.png')
OUTPUT_PDF = ARCHIVO_MD.replace('.md', '.pdf')

# ==========================================
# 2. METADATOS DEL DOCUMENTO
# ==========================================
class DocMeta:
    titulo          = "Documento UNLaR"
    subtitulo       = "Trabajo Práctico"
    carrera         = "T.U.I."
    catedra         = ""
    docente         = "Docente"
    integrantes     = []
    portada_enabled = True

# ==========================================
# 3. CONFIGURACIÓN EXTERNA (.cfg)
# ==========================================
CONFIG_FILENAME = 'cvtmdpdf.cfg'

def _config_default_text():
    return (
        "# ============================================================\n"
        "# Configuración de cvtmdpdf\n"
        "# Edita este archivo para personalizar la portada de tus PDFs.\n"
        "# El título del documento se toma del primer '# Título' del .md\n"
        "# ============================================================\n"
        "\n"
        "[portada]\n"
        "\n"
        "# Cambiar a false para generar el PDF sin portada\n"
        "# Útil para borradores o documentos sin tapa formal\n"
        "enabled = true\n"
        "\n"
        "# Subtítulo que aparece debajo del título en la portada\n"
        "# Ejemplos: Trabajo Práctico, Trabajo Final, Resumen, Informe\n"
        "subtitulo = Trabajo Práctico\n"
        "\n"
        "# Nombre de la carrera\n"
        "carrera = T.U.I.\n"
        "\n"
        "# Nombre de la cátedra o materia\n"
        "catedra = Nombre de la Cátedra\n"
        "\n"
        "# Docente titular de la cátedra\n"
        "docente = Nombre del Docente\n"
        "\n"
        "# Integrantes del grupo\n"
        "# Escribir uno por línea con sangría (Tab o 4 espacios)\n"
        "# Formato sugerido: Apellido, Nombre - DNI 12345678\n"
        "integrantes =\n"
        "    Apellido, Nombre - DNI 12345678\n"
        "    Apellido, Nombre - DNI 87654321\n"
    )

def cargar_config():
    """
    Busca cvtmdpdf.cfg en el directorio del .md primero, luego en BASE_DIR.
    Si no existe en ninguno, lo crea en el directorio del .md con valores por defecto
    y termina el proceso para que el usuario lo edite antes de continuar.
    """
    md_dir   = os.path.dirname(os.path.abspath(ARCHIVO_MD))
    posibles = [
        os.path.join(md_dir,   CONFIG_FILENAME),
        os.path.join(BASE_DIR, CONFIG_FILENAME),
    ]
    ruta = next((p for p in posibles if os.path.exists(p)), None)

    if ruta is None:
        ruta = posibles[0]
        with open(ruta, 'w', encoding='utf-8') as f:
            f.write(_config_default_text())
        print(f"📄 Se creó el archivo de configuración en:\n   {ruta}")
        print("   Editalo con los datos de tu entrega y volvé a ejecutar el script.")
        sys.exit(0)

    cfg = configparser.ConfigParser()
    cfg.read(ruta, encoding='utf-8')
    p = cfg['portada'] if 'portada' in cfg else {}

    DocMeta.portada_enabled = p.getboolean('enabled',   True)
    DocMeta.subtitulo       = p.get('subtitulo', 'Trabajo Práctico').strip()
    DocMeta.carrera         = p.get('carrera',   'T.U.I.').strip()
    DocMeta.catedra         = p.get('catedra',   '').strip()
    DocMeta.docente         = p.get('docente',   'Docente').strip()
    DocMeta.integrantes     = [
        l.strip() for l in p.get('integrantes', '').splitlines() if l.strip()
    ]
    print(f"📋 Configuración cargada desde: {ruta}")

# ==========================================
# 4. PROCESAMIENTO DEL LOGO (Transparencia)
# ==========================================
def procesar_logo():
    if not os.path.exists(INPUT_LOGO):
        print(f"⚠️  No se encontró {INPUT_LOGO}. Se omitirá el escudo.")
        return False
    try:
        img = Image.open(INPUT_LOGO).convert("RGBA")
        ImageDraw.floodfill(img, xy=(0, 0),               value=(0, 0, 0, 0), thresh=40)
        ImageDraw.floodfill(img, xy=(img.width-1, 0),     value=(0, 0, 0, 0), thresh=40)
        ImageDraw.floodfill(img, xy=(0, img.height-1),    value=(0, 0, 0, 0), thresh=40)
        ImageDraw.floodfill(img, xy=(img.width-1, img.height-1), value=(0, 0, 0, 0), thresh=40)
        img.save(TRANS_LOGO, 'PNG')
        return True
    except Exception as e:
        print(f"Error procesando logo: {e}")
        return False

# ==========================================
# 5. COLORES Y ESTILOS INSTITUCIONALES UNLaR
# ==========================================
AZUL_UNLAR  = colors.HexColor('#003087')
DORADO      = colors.HexColor('#C5A028')
AZUL_CLARO  = colors.HexColor('#1A4FA0')
GRIS_CLARO  = colors.HexColor('#F4F6FA')
GRIS_LINEA  = colors.HexColor('#D0D8E8')
GRIS_CODIGO = colors.HexColor('#F0F2F5')
BLANCO      = colors.white
NEGRO_TEXTO = colors.HexColor('#1A1A2E')

W, H = A4
def S(name, **kw): return ParagraphStyle(name, **kw)

estilos = {
    'normal':       S('enormal',   fontName='Helvetica',         fontSize=10.5, leading=16,  textColor=NEGRO_TEXTO, alignment=TA_JUSTIFY, spaceAfter=8),
    'h2':           S('eh2',       fontName='Helvetica-Bold',    fontSize=12,   leading=16,  textColor=AZUL_UNLAR,  alignment=TA_LEFT,    spaceBefore=12, spaceAfter=6, keepWithNext=True),
    'cita':         S('ecita',     fontName='Helvetica-Oblique', fontSize=10,   leading=15,  textColor=AZUL_CLARO,  alignment=TA_LEFT,    leftIndent=20, rightIndent=20, spaceBefore=6, spaceAfter=6, keepWithNext=True),
    'bullet':       S('ebullet',   fontName='Helvetica',         fontSize=10.5, leading=15,  textColor=NEGRO_TEXTO, alignment=TA_LEFT,    leftIndent=18, bulletIndent=6, spaceAfter=4),
    'index_num':    S('index_num', fontName='Helvetica-Bold',    fontSize=10,   textColor=AZUL_UNLAR),
    'index_txt':    S('index_txt', fontName='Helvetica',         fontSize=10,   textColor=NEGRO_TEXTO),
    'tabla_header': S('tabla_h',   fontName='Helvetica-Bold',    fontSize=10,   leading=14,  textColor=BLANCO,      alignment=TA_CENTER),
'tabla_celda':  S('tabla_c', fontName='Helvetica', fontSize=9,  # Bajamos de 10 a 9[cite: 2]
                      leading=12, textColor=NEGRO_TEXTO, alignment=TA_LEFT),    'codigo':       S('ecodigo',   fontName='Courier',           fontSize=8.5,  leading=12,  textColor=NEGRO_TEXTO),
    'img_caption':  S('eimgcap',   fontName='Helvetica-Oblique', fontSize=9,    textColor=colors.HexColor('#666666'), alignment=TA_CENTER, spaceAfter=6),
    'img_error':    S('eimgerr',   fontName='Helvetica-Oblique', fontSize=9,    textColor=colors.red),
}
estilo_nota_pie = S('enotapie', fontName='Helvetica', fontSize=9, textColor=colors.HexColor('#555555'), alignment=TA_CENTER)

# ==========================================
# 6. FLOWABLES PERSONALIZADOS
# ==========================================
class BloqueSeccion(Flowable):
    def __init__(self, numero, texto, width=None):
        super().__init__()
        self.numero = numero
        self.texto = texto
        self.estilo_titulo = S('titulo_caja', fontName='Helvetica-Bold', fontSize=12, 
                               leading=14, textColor=BLANCO, alignment=TA_LEFT)
        self.p = Paragraph(texto, self.estilo_titulo)
        self.block_width = width
        self.padding = 10
        self.offset_x = 50 if self.numero else 15
        # ¡FUNDAMENTAL! Le dice a ReportLab que intente mantener este bloque con el siguiente
        self.keepWithNext = True 

    def wrap(self, avail_w, avail_h):
        self.bw = self.block_width or avail_w
        w_texto = self.bw - self.offset_x - self.padding
        _, self.h_texto = self.p.wrap(w_texto, avail_h)
        self.height = max(32, self.h_texto + 16)
        return self.bw, self.height

    def draw(self):
        c = self.canv
        c.setFillColor(AZUL_UNLAR)
        c.roundRect(0, 0, self.bw, self.height, 4, fill=1, stroke=0)
        
        if self.numero:
            c.setFillColor(DORADO)
            c.setFont('Helvetica-Bold', 14)
            c.drawString(10, (self.height / 2) - 5, self.numero)
        
        self.p.drawOn(c, self.offset_x, (self.height - self.h_texto) / 2)
# ==========================================
# 7. PLANTILLAS DE PÁGINA (header / footer / portada)
# ==========================================
MAX_TITULO_HEADER = 75  # caracteres máximos visibles en el encabezado de página

def titulo_para_header():
    """FIX titulo encabezado: trunca con elipsis si supera MAX_TITULO_HEADER."""
    t = DocMeta.titulo
    if len(t) > MAX_TITULO_HEADER:
        return t[:MAX_TITULO_HEADER - 1].rstrip() + '…'
    return t

def _dibujar_titulo_portada(c, titulo, y, max_w):
    """
    Dibuja el título en la portada usando Paragraph para permitir saltos de línea.
    Devuelve la altura calculada para posicionar elementos posteriores.
    """
    estilo_tapa = S('titulo_tapa', 
                    fontName='Helvetica-Bold', 
                    fontSize=24, 
                    leading=28, 
                    textColor=BLANCO, 
                    alignment=TA_CENTER)
    
    p = Paragraph(titulo, estilo_tapa)
    # Calcula el espacio que ocupará el texto según el ancho máximo
    w_p, h_p = p.wrap(max_w, H) 
    
    # Dibuja el párrafo centrado. Se resta h_p a 'y' porque Paragraph dibuja hacia abajo
    p.drawOn(c, (W - w_p) / 2, y - h_p)
    return h_p

def draw_portada(canvas, doc):
    c = canvas
    c.saveState()

    # Fondo azul completo[cite: 1]
    c.setFillColor(AZUL_UNLAR)
    c.rect(0, 0, W, H, fill=1, stroke=0)

    # Franjas doradas top y bottom[cite: 1]
    c.setFillColor(DORADO)
    c.rect(0, H - 0.6*cm, W, 0.6*cm, fill=1, stroke=0)
    c.rect(0, 0, W, 0.5*cm, fill=1, stroke=0)

    # Logo centrado[cite: 1]
    if os.path.exists(TRANS_LOGO):
        c.drawImage(TRANS_LOGO, (W - 4.5*cm) / 2, H - 7.5*cm,
                    width=4.5*cm, height=4.5*cm, preserveAspectRatio=True, mask='auto')

    # Nombre de la universidad[cite: 1]
    c.setFillColor(BLANCO)
    c.setFont('Helvetica-Bold', 16)
    c.drawCentredString(W/2, H - 8.6*cm, 'Universidad Nacional de La Rioja')
    c.setFillColor(DORADO)
    c.setFont('Helvetica-Bold', 12)
    c.drawCentredString(W/2, H - 9.3*cm, 'UNLaR')

    # Línea separadora superior[cite: 1]
    c.setStrokeColor(DORADO)
    c.setLineWidth(1.5)
    c.line(3*cm, H - 9.9*cm, W - 3*cm, H - 9.9*cm)

    # --- TÍTULO DINÁMICO ---
    # Dibujamos el título y recuperamos su altura real para mover el resto[cite: 1]
    y_inicio_titulo = H - 11.2*cm
    c.setFillColor(BLANCO)
    altura_total_titulo = _dibujar_titulo_portada(c, DocMeta.titulo, y_inicio_titulo, W - 6*cm)

    # --- SUBTÍTULO Y LÍNEA (Posición Relativa) ---
    # Calculamos la nueva posición 'y' basándonos en cuánto bajó el título[cite: 1]
    y_subtitulo = y_inicio_titulo - altura_total_titulo - 0.8*cm
    
    c.setFillColor(DORADO)
    c.setFont('Helvetica-Bold', 18)
    c.drawCentredString(W/2, y_subtitulo, DocMeta.subtitulo)

    # La línea inferior ahora se dibuja 1cm debajo del subtítulo[cite: 1]
    y_linea_inf = y_subtitulo - 1.0*cm
    c.setStrokeColor(DORADO)
    c.setLineWidth(0.8)
    c.line(3*cm, y_linea_inf, W - 3*cm, y_linea_inf)

    # Recuadro azul oscuro con metadata (se mantiene estático al fondo)[cite: 1]
    c.setFillColor(colors.HexColor('#0A1F5C'))
    c.roundRect(1.2*cm, 1.5*cm, W - 2.4*cm, 11.2*cm, 8, fill=1, stroke=0)

    meta_y = H - 18.2*cm
    meta_x = 2.0*cm
    line_h = 0.65*cm

    datos = [
        ('Carrera:',         f'{DocMeta.carrera} | {DocMeta.catedra}'),
        ('Docente Titular:', DocMeta.docente),
    ]
    for label, valor in datos:
        c.setFillColor(DORADO)
        c.setFont('Helvetica-Bold', 9.5)
        c.drawString(meta_x, meta_y, label)
        c.setFillColor(BLANCO)
        c.setFont('Helvetica', 9.5)
        c.drawString(meta_x + 3.2*cm, meta_y, valor)
        meta_y -= line_h

    meta_y -= 0.2*cm
    c.setFillColor(DORADO)
    c.setFont('Helvetica-Bold', 9.5)
    c.drawString(meta_x, meta_y, 'Integrantes:')
    meta_y -= line_h
    for nombre in DocMeta.integrantes:
        c.setFillColor(BLANCO)
        c.setFont('Helvetica', 9)
        c.drawString(meta_x + 0.5*cm, meta_y, f'• {nombre}')
        meta_y -= 0.6*cm

    c.restoreState()

def header_footer(canvas, doc):
    if doc.page == 1 and DocMeta.portada_enabled:
        draw_portada(canvas, doc)
        return

    canvas.saveState()

    # Barra azul superior[cite: 1]
    canvas.setFillColor(AZUL_UNLAR)
    canvas.rect(0, H - 1.5*cm, W, 1.5*cm, fill=1, stroke=0)

    if os.path.exists(TRANS_LOGO):
        canvas.drawImage(TRANS_LOGO, 0.6*cm, H - 1.35*cm,
                         width=1.0*cm, height=1.0*cm, preserveAspectRatio=True, mask='auto')

    canvas.setFillColor(BLANCO)
    canvas.setFont('Helvetica-Bold', 8)
    canvas.drawString(1.8*cm, H - 0.9*cm, f'UNLaR — {DocMeta.carrera} | {DocMeta.catedra}')

    canvas.setFillColor(DORADO)
    canvas.setFont('Helvetica-Bold', 8)
    canvas.drawRightString(W - 1.0*cm, H - 0.9*cm, titulo_para_header())

    canvas.setStrokeColor(DORADO)
    canvas.setLineWidth(1.2)
    canvas.line(0.6*cm, H - 1.5*cm, W - 0.6*cm, H - 1.5*cm)

    canvas.setStrokeColor(GRIS_LINEA)
    canvas.setLineWidth(0.8)
    canvas.line(0.6*cm, 1.4*cm, W - 0.6*cm, 1.4*cm)

    canvas.setFillColor(colors.HexColor('#555555'))
    canvas.setFont('Helvetica', 8)
    canvas.drawString(1.0*cm, 0.8*cm, f'{DocMeta.subtitulo} — {DocMeta.catedra}')
    page_num = doc.page - 1 if DocMeta.portada_enabled else doc.page
    canvas.drawRightString(W - 1.0*cm, 0.8*cm, f'Página {page_num}')

    canvas.restoreState()
    
# ==========================================
# 8. UTILIDADES DE PARSEO Y CONSTRUCCIÓN
# ==========================================
def formatear_texto(texto):
    texto = re.sub(r'\*\*(.*?)\*\*', r'<b>\1</b>', texto)
    texto = re.sub(r'\*(.*?)\*',     r'<i>\1</i>', texto)
    return texto

# --- Tablas: anchos proporcionales al contenido ---
TABLA_TOTAL_CM = 20.0
TABLA_MIN_CM   = 1.5
TABLA_MAX_CM   = 9.0

def calcular_anchos_tabla(textos_crudos):
    if not textos_crudos:
        return None
    n = len(textos_crudos[0])
    max_len_total = [0] * n
    max_palabra_len = [0] * n

    for fila in textos_crudos:
        for i, celda in enumerate(fila[:n]):
            limpio = re.sub(r'\*+|\[|\]', '', celda).strip()
            # Guardamos el largo total de la celda
            max_len_total[i] = max(max_len_total[i], len(limpio))
            # Buscamos la palabra más larga dentro de esa celda
            palabras = limpio.split()
            if palabras:
                largo_palabra = max(len(p) for p in palabras)
                max_palabra_len[i] = max(max_palabra_len[i], largo_palabra)

    total_len = sum(max_len_total) or n
    anchos_cm = []
    
    for i in range(n):
        # Calculamos el ancho proporcional
        proporcional = (max_len_total[i] / total_len) * TABLA_TOTAL_CM
        # Calculamos un mínimo basado en la palabra más larga (aprox 0.25cm por letra en 10pt)
        minimo_palabra = max_palabra_len[i] * 0.25
        # Elegimos el mayor entre el proporcional, el mínimo de palabra y el mínimo global
        ancho = max(TABLA_MIN_CM, proporcional, minimo_palabra)
        anchos_cm.append(min(TABLA_MAX_CM, ancho)) # Respetamos el máximo[cite: 1]

    # Normalizamos para que no se pase del ancho de página[cite: 1]
    factor = TABLA_TOTAL_CM / sum(anchos_cm)
    return [a * factor * cm for a in anchos_cm]

def construir_tabla(datos_tabla, textos_tabla):
    """FIX 10: manejo de errores para tablas con filas malformadas."""
    if not datos_tabla:
        return None
    try:
        anchos = calcular_anchos_tabla(textos_tabla)
        tabla  = Table(datos_tabla, colWidths=anchos, repeatRows=1)
        tabla.setStyle(TableStyle([
            ('BACKGROUND',     (0,  0), (-1,  0), AZUL_UNLAR),
            ('TEXTCOLOR',      (0,  0), (-1,  0), BLANCO),
            ('FONTNAME',       (0,  0), (-1,  0), 'Helvetica-Bold'),
            ('FONTSIZE',       (0,  0), (-1,  0), 10),
            ('ALIGN',          (0,  0), (-1,  0), 'CENTER'),
            ('ROWBACKGROUNDS', (0,  1), (-1, -1), [BLANCO, GRIS_CLARO]),
            ('FONTNAME',       (0,  1), (-1, -1), 'Helvetica'),
            ('FONTSIZE',       (0,  1), (-1, -1), 10),
            ('VALIGN',         (0,  0), (-1, -1), 'MIDDLE'),
            ('TOPPADDING',     (0,  0), (-1, -1), 5),
            ('BOTTOMPADDING',  (0,  0), (-1, -1), 5),
            ('LEFTPADDING',    (0, 0),  (-1, -1), 2), # Bajamos de 6 a 2
            ('RIGHTPADDING',   (0, 0),  (-1, -1), 2), # Bajamos de 6 a 2
            ('BOX',            (0,  0), (-1, -1), 0.5, GRIS_LINEA),
            ('INNERGRID',      (0,  0), (-1, -1), 0.3, GRIS_LINEA),
        ]))
        return tabla
    except Exception as e:
        print(f"⚠️  Error construyendo tabla (posible fila malformada): {e}")
        return None

def render_codigo(texto):
    """
    FIX 6: Renderiza un bloque de código con fondo gris y fuente Courier.
    Preserva indentación y saltos de línea originales del .md.
    """
    texto_escapado = (texto
                      .replace('&', '&amp;')
                      .replace('<', '&lt;')
                      .replace('>', '&gt;'))
    pre   = Preformatted(texto_escapado, estilos['codigo'])
    tabla = Table([[pre]], colWidths=[17 * cm])
    tabla.setStyle(TableStyle([
        ('BACKGROUND',    (0, 0), (-1, -1), GRIS_CODIGO),
        ('BOX',           (0, 0), (-1, -1), 0.5, GRIS_LINEA),
        ('LEFTPADDING',   (0, 0), (-1, -1), 10),
        ('RIGHTPADDING',  (0, 0), (-1, -1), 10),
        ('TOPPADDING',    (0, 0), (-1, -1), 8),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
    ]))
    return tabla

def insertar_imagen(ruta_imagen):
    """
    FIX 7: Inserta una imagen referenciada con sintaxis ![alt](ruta).
    La ruta puede ser relativa al .md o absoluta.
    Ajusta al ancho máximo de 14cm preservando la proporción original.
    """
    base      = os.path.dirname(os.path.abspath(ARCHIVO_MD))
    full_path = (os.path.join(base, ruta_imagen)
                 if not os.path.isabs(ruta_imagen)
                 else ruta_imagen)
    if not os.path.exists(full_path):
        print(f"⚠️  Imagen no encontrada: {full_path}")
        return Paragraph(f"[Imagen no encontrada: {ruta_imagen}]", estilos['img_error'])
    try:
        # kind='bound' ajusta dentro de width/height preservando proporción
        return RLImage(full_path, width=14 * cm, height=10 * cm, kind='bound')
    except Exception as e:
        print(f"⚠️  Error al incrustar imagen '{ruta_imagen}': {e}")
        return Paragraph(f"[Error en imagen: {ruta_imagen}]", estilos['img_error'])

# ==========================================
# 9. MOTOR DE PARSEO MARKDOWN -> REPORTLAB
# ==========================================
def compilar_markdown(ruta_md):
    # Si la portada está habilitada, el PageBreak hace que empiece en la página 2
    story = [PageBreak()] if DocMeta.portada_enabled else []

    if not os.path.exists(ruta_md):
        print(f"❌ No se encontró el archivo: {ruta_md}")
        return []

    with open(ruta_md, 'r', encoding='utf-8') as f:
        lineas = f.readlines()

    leyendo_tabla   = False
    datos_tabla     = []
    textos_tabla    = []
    leyendo_codigo  = False
    lineas_codigo   = []          # FIX 6: buffer de líneas del bloque de código actual
    tl_data         = []
    primera_seccion = False       # FIX 1: controla si ya apareció el primer ##

    def flush_tabla(story):
        """Vuelca la tabla acumulada al story y limpia buffers."""
        nonlocal leyendo_tabla, datos_tabla, textos_tabla
        if datos_tabla:
            t = construir_tabla(datos_tabla, textos_tabla)
            if t:
                # FIX: Obliga a la tabla a permanecer en una sola pieza
                story.append(KeepTogether([t])) 
                story.append(Spacer(1, 10))
        leyendo_tabla = False
        datos_tabla   = []
        textos_tabla  = []

    for linea_raw in lineas:
        linea_orig = linea_raw.rstrip('\n')   # Preserva indentación para código
        linea      = linea_raw.strip()        # Para todo lo demás

        # ── 1. CONTROL DE ESPACIO Y SALTOS (Prioridad Alta) ────────────────
        # Definimos m_subir siempre al inicio para evitar el UnboundLocalError
        m_subir = re.match(r'\\subir:\s*(\d+)', linea)
        
        if m_subir:
            puntos = int(m_subir.group(1))
            story.append(Spacer(1, -puntos))
            continue

        if linea == "\\salto de pagina":
            story.append(PageBreak())
            continue

        # ── 2. BLOQUE DE CÓDIGO ─────────────────────────────────────────────
        if linea.startswith('```'):
            if not leyendo_codigo:
                leyendo_codigo = True
                lineas_codigo  = []
            else:
                leyendo_codigo = False
                if lineas_codigo:
                    story.append(Spacer(1, 6))
                    story.append(render_codigo('\n'.join(lineas_codigo)))
                    story.append(Spacer(1, 6))
                lineas_codigo = []
            continue

        if leyendo_codigo:
            lineas_codigo.append(linea_orig)  # mantiene indentación original del .md
            continue

        # ── LÍNEA VACÍA ──────────────────────────────────────────────────────
        if not linea:
            if leyendo_tabla:
                flush_tabla(story)
            continue

        # ── ÍNDICE ───────────────────────────────────────────────────────────
        if re.match(r'^\d+\.\s+\[.*\]', linea):
            partes = linea.split('.')
            num = partes[0].strip() + "."
            txt = partes[1].replace('[', '').replace(']', '').strip()
            story.append(Table(
                [[Paragraph(num, estilos['index_num']), Paragraph(txt, estilos['index_txt'])]],
                colWidths=[1*cm, 14.5*cm],
                style=[('VALIGN', (0, 0), (-1, -1), 'TOP')]
            ))
            continue

# ── LÍNEA DE TIEMPO ──────────────────────────────────────────────────
        RE_TIMELINE = re.compile(r'^(.+?)\s*[─\-—]{2,}\s*(.+)$')
        m_tl = RE_TIMELINE.match(linea)
        
        if m_tl:
            year = m_tl.group(1).strip()
            desc = m_tl.group(2).strip()
            tl_data.append([
                Paragraph(f"<b>{year}</b>", S('tl_y', fontName='Helvetica-Bold', fontSize=10, textColor=DORADO, alignment=TA_CENTER)),
                Paragraph(desc, estilos['normal'])
            ])
            continue
        elif tl_data and not RE_TIMELINE.match(linea) and not linea.startswith('```'):
            t = Table(tl_data, colWidths=[2.2*cm, 13.3*cm])
            t.setStyle(TableStyle([
                ('LINEAFTER',      (0, 0), (0, -1), 1.5, DORADO),
                ('ROWBACKGROUNDS', (0, 0), (-1,-1), [colors.white, GRIS_CLARO]),
                ('VALIGN',         (0, 0), (-1,-1), 'MIDDLE'),
            ]))
            # Envolvemos la tabla completa para que no se separe entre páginas
            story.append(KeepTogether([t]))
            story.append(Spacer(1, 15))
            tl_data = []
            
        # ── METADATOS DESDE EL .md (soporte legado; el .cfg tiene prioridad) ─
        if linea.startswith('# ') and DocMeta.titulo == "Documento UNLaR":
            DocMeta.titulo = linea.replace('# ', '')
            continue
        if linea.startswith('**CARRERA:**'):
            partes = linea.split('|')
            DocMeta.carrera = partes[0].replace('**CARRERA:**', '').strip()
            DocMeta.catedra = partes[1].replace('**Cátedra:**', '').strip() if len(partes) > 1 else ""
            continue
        if linea.startswith('**Docente Titular:**'):
            DocMeta.docente = linea.replace('**Docente Titular:**', '').strip()
            continue
        # Detección de integrantes sin nombres hardcodeados (cualquier bullet con DNI)
        if linea.startswith('- ') and 'DNI' in linea:
            DocMeta.integrantes.append(linea.replace('- ', '').strip())
            continue

        # ── TABLAS ───────────────────────────────────────────────────────────
        if linea.startswith('|'):
            celdas_raw = [c.strip() for c in linea.split('|')[1:-1]]
            # Fila separadora de alineación (| :---- | --- |) → ignorar
            if all(re.match(r'^:?-+:?$', c) for c in celdas_raw if c):
                continue
            leyendo_tabla = True
            es_cabecera   = (len(datos_tabla) == 0)
            est = estilos['tabla_header'] if es_cabecera else estilos['tabla_celda']
            try:  # FIX 10: protege fila individual malformada
                datos_tabla.append([Paragraph(formatear_texto(c), est) for c in celdas_raw])
                textos_tabla.append(celdas_raw)
            except Exception as e:
                print(f"⚠️  Fila de tabla ignorada por error de parseo: {e}")
            continue
        else:
            if leyendo_tabla:
                flush_tabla(story)

        # ── SEPARADOR HORIZONTAL ---  ─────────────────────────────────────────
        if linea == '---':
            story.append(HRFlowable(width='100%', thickness=0.5, color=GRIS_LINEA, spaceBefore=15, spaceAfter=15))
            continue

# ── SALTO DE PÁGINA MANUAL ──────────────────────────────────────────
        if linea == "\\salto de pagina":
            story.append(PageBreak())
            continue
# ── CONTROL DE ESPACIO MANUAL ──────────────────────────────────────
        # Detecta si querés subir el texto (ej: \subir: 20)
            m_subir = re.match(r'\\subir:\s*(\d+)', linea)
        if m_subir:
            puntos = int(m_subir.group(1))
        # Un Spacer con altura negativa "tira" del siguiente elemento hacia arriba
            story.append(Spacer(1, -puntos))
            continue

        if linea == "\\salto de pagina":
            story.append(PageBreak())
            continue

        # ── SECCIONES ## ─────────────────────────────────────────────────────
        if linea.startswith('## '):
            titulo_crudo = linea.replace('## ', '')
            m = re.match(r'([\d\.]+)\s*(.*)', titulo_crudo)
            numero, texto = (m.group(1).strip(), m.group(2).strip()) if m else ('', titulo_crudo)
            
            # Agrupamos el título con su espacio para que no quede solo al final de la hoja
            bloque_titulo = [
                BloqueSeccion(numero, texto),
                Spacer(1, 8)
            ]
            story.append(KeepTogether(bloque_titulo))
            continue
        
        # ── SUB-SECCIONES ### ─────────────────────────────────────────────────
        if linea.startswith('### '):
            story.append(Paragraph(formatear_texto(linea.replace('### ', '')), estilos['h2']))
            continue
        # ── SUB-SECCIONES #### ───────────────────────────────────────────────
        if linea.startswith('#### '):
            story.append(Paragraph(
        formatear_texto(linea.replace('#### ', '')),
        S('eh4', fontName='Helvetica-Bold', fontSize=11, leading=14,
          textColor=AZUL_CLARO, alignment=TA_LEFT,
          spaceBefore=8, spaceAfter=4, keepWithNext=True)
    ))
            continue

# ── SUB-SECCIONES ##### ──────────────────────────────────────────────
        if linea.startswith('##### '):
            story.append(Paragraph(
            formatear_texto(linea.replace('##### ', '')),
            S('eh5', fontName='Helvetica-Bold', fontSize=10.5, leading=13,
            textColor=NEGRO_TEXTO, alignment=TA_LEFT,
            spaceBefore=6, spaceAfter=3, keepWithNext=True)
    ))
            continue  
        # ── CITAS > ──────────────────────────────────────────────────────────
        if linea.startswith('> '):
            cita_texto = linea.replace('> ', '').strip()
            if cita_texto.startswith('—'):
                # Estilo para el autor de la cita
                story.append(Paragraph(
                    formatear_texto(cita_texto),
                    S('eautor', fontName='Helvetica-Bold', fontSize=9, textColor=DORADO, alignment=TA_RIGHT, spaceAfter=12)
                ))
            else:
                # El "cuadrito sofisticado": una tabla de una celda con fondo tenue
                p_cita = Paragraph(formatear_texto(cita_texto), estilos['cita'])
                
                # Definimos la tabla. El ancho (16.5*cm) debe ser menor al total para que luzca centrada
                t_cita = Table([[p_cita]], colWidths=[17.5*cm])
                
                t_cita.setStyle(TableStyle([
                    # Fondo con transparencia (alpha=0.05 es casi invisible, muy elegante)
                    ('BACKGROUND', (0, 0), (-1, -1), colors.Color(0, 0, 0, alpha=0.04)),
                    # Línea lateral izquierda para reforzar el estilo "cita"
                    ('LINESTART', (0, 0), (0, -1), 2, AZUL_CLARO),
                    # Bordes muy finos arriba y abajo
                    ('LINEABOVE', (0, 0), (-1, 0), 0.3, GRIS_LINEA),
                    ('LINEBELOW', (0, 0), (-1, 0), 0.3, GRIS_LINEA),
                    # Espaciado interno (Padding) para que el texto no toque los bordes
                    ('LEFTPADDING', (0, 0), (-1, -1), 15),
                    ('RIGHTPADDING', (0, 0), (-1, -1), 15),
                    ('TOPPADDING', (0, 0), (-1, -1), 10),
                    ('BOTTOMPADDING', (0, 0), (-1, -1), 10),
                ]))
                
                story.append(Spacer(1, 5))
                # Envolvemos en KeepTogether para evitar que el cuadrito se parta entre hojas
                story.append(KeepTogether([t_cita]))
                story.append(Spacer(1, 5))
            continue

        # ── IMÁGENES ![alt](ruta) ─────────────────────────────────────────────
        # FIX 7: incrusta imágenes con ruta relativa al .md o absoluta
        m_img = re.match(r'^!\[([^\]]*)\]\(([^)]+)\)$', linea)
        if m_img:
            alt_text = m_img.group(1)
            img_path = m_img.group(2)
            story.append(Spacer(1, 6))
            story.append(insertar_imagen(img_path))
            if alt_text:
                story.append(Paragraph(alt_text, estilos['img_caption']))
            story.append(Spacer(1, 6))
            continue

        # ── BULLETS - y * ────────────────────────────────────────────────────
        if linea.startswith('- ') or linea.startswith('* '):
            if 'Integrantes:' not in linea:
                story.append(Paragraph(f"• {formatear_texto(linea[2:])}", estilos['bullet']))
            continue

        # ── LÍNEAS DE METADATA LEGADA A IGNORAR ──────────────────────────────
        ignorar = ['Universidad Nacional de La Rioja', 'CARRERA:', 'Docente Titular:', 'Integrantes:']
        if any(i in linea for i in ignorar):
            continue

        # ── PÁRRAFO NORMAL ────────────────────────────────────────────────────
        story.append(Paragraph(formatear_texto(linea), estilos['normal']))

    # ── VOLCADO FINAL ─────────────────────────────────────────────────────────
    # Si el archivo termina con una tabla o un bloque de código sin cerrar,
    # los vuelca igualmente para no perder contenido.
    if leyendo_tabla:
        flush_tabla(story)
    if leyendo_codigo and lineas_codigo:
        story.append(render_codigo('\n'.join(lineas_codigo)))

    return story

# ==========================================
# MAIN
# ==========================================
def reset_meta():
    """Limpia la metadata para evitar que se arrastren datos entre archivos."""
    DocMeta.titulo = "Documento UNLaR"
    DocMeta.subtitulo = "Trabajo Práctico"
    DocMeta.carrera = "T.U.I."
    DocMeta.catedra = ""
    DocMeta.docente = "Docente"
    DocMeta.integrantes = []
    
import traceback

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("❌ Error: Debes especificar archivos o un patrón (ej: *.md).")
        sys.exit(1)

    patrones = sys.argv[1:]
    archivos_encontrados = []
    for p in patrones:
        archivos_encontrados.extend(glob.glob(p))

    if not archivos_encontrados:
        print(f"⚠️ No se encontraron archivos para: {patrones}.")
        sys.exit(1)

    for ruta_archivo in archivos_encontrados:
        if os.path.isdir(ruta_archivo): continue
        if not ruta_archivo.lower().endswith('.md'): continue

        # REINICIO DE DATOS PARA CADA ARCHIVO
        reset_meta() 
        ARCHIVO_MD = ruta_archivo
        OUTPUT_PDF = ARCHIVO_MD.replace('.md', '.pdf')

        try:
            print(f"\n--- Procesando: {ARCHIVO_MD} ---")
            cargar_config() 
            procesar_logo()
            
            doc = SimpleDocTemplate(
    OUTPUT_PDF,
    pagesize=A4,
    rightMargin=0.5*cm,  # Reducido al mínimo físico
    leftMargin=0.5*cm,   # Reducido al mínimo físico
    topMargin=2.5*cm,
    bottomMargin=2.0*cm,
    allowWidows=0,
    allowOrphans=0,
)
            
            elementos = compilar_markdown(ARCHIVO_MD)
            if elementos:
                doc.build(elementos, onFirstPage=header_footer, onLaterPages=header_footer)
                print(f"✅ Generado: {OUTPUT_PDF})")

        except Exception as e:
            # REGISTRO DE ERRORES[cite: 1]
            msg_error = f"❌ Error procesando {ARCHIVO_MD}: {str(e)}\n"
            print(msg_error)
            with open("error_log.txt", "a", encoding="utf-8") as log:
                log.write(f"--- {ARCHIVO_MD} ---\n")
                log.write(traceback.format_exc())
                log.write("\n" + "="*40 + "\n")