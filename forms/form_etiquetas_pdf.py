from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from datetime import datetime, timedelta
from reportlab.graphics.barcode import code128
import os


def generar_pdf(orden_fabricacion, poquillo, operador, kilos, finca, codfin, datos_sap, nombre):
    # Crea un documento PDF
    pdf_path = os.path.join(os.path.expanduser('~'), 'etiqueta.pdf')
    c = canvas.Canvas(pdf_path, pagesize=letter)
    
    # OJO Defino los colores de texto y fondo basados en la cantidad de kilos
    if float(kilos) <= 300:
        texto_color = "white"
        fondo_color = "black"
    else:
        texto_color = "black"
        fondo_color = "white"
        
    if poquillo:
        texto_color = "white"
        fondo_color = "black"
    else:
        texto_color = "black"
        fondo_color = "white"

    # Configura los colores en el lienzo
    c.setFillColor(fondo_color)
    c.rect(0, 0, letter[0], letter[1], fill=True)
    c.setFillColor(texto_color)

    # CABEZA DE LA ETIQUETA
    default_text = "VIA SAMBORONDÓN KM 1.5 S/N EDIF.XIMA"
    default_textb = "PISO 5 - OFIC 512 TELEFONO 3728600"
    c.drawString(100, 770, default_text)
    c.setFont("Helvetica", 13)
    c.drawString(100, 755, default_textb)

    c.setFont("Helvetica-Bold", 18)
    c.drawString(135, 725, f"PEDIDO: {datos_sap['Pedido']}")

    c.setFont("Helvetica", 18)
    c.drawString(10, 705, f"ORDEN: {orden_fabricacion}")

    codigo = f"CODIGO: {datos_sap['Codigo']}"
    c.setFont("Helvetica-Bold", 25)
    c.drawString(10, 675, codigo)

    producto = datos_sap['Producto']
    c.setFont("Helvetica", 14)
    if len(producto) > 44:
        c.drawString(10, 650, f"PRODUCTO: {producto[:40]}")
        c.drawString(10, 635, producto[40:])
    else:
        c.drawString(10, 650, f"PRODUCTO: {producto}")

    c.setFont("Helvetica", 15)
    c.drawString(10, 620, f"TIPO: {datos_sap['Tipo']}")
    c.drawString(250, 620, f"DENSIDAD: {datos_sap['Densidad']}")
    c.drawString(250, 605, f"PERF: {datos_sap['Perforacion']}")
    c.drawString(10, 605, f"MEDIDAS: {datos_sap['Ancho']}X{datos_sap['Largo']}X{datos_sap['Espesor']}")
    c.drawString(10, 590, f"COLOR: {datos_sap['Color']}")
    c.drawString(10, 575, f"SELLO: {datos_sap['Sello']}")

    c.setFont("Helvetica-Bold", 20)
    c.drawString(130, 550, f"{kilos} UNIDADES")

    fecha_actual = datetime.now().strftime("%d/%m/%Y")

    # Por defecto un año (como funciona actualmente)
    dias_vencimiento = 365

    tiempo = datos_sap.get("TiempoDuracion")
    # Solo si la BD tiene un tiempo de duración lo reemplazo
    if tiempo:
        tiempo = tiempo.strip().lower()
        if tiempo == "6 meses":
            dias_vencimiento = 180
        elif tiempo == "12 meses":
            dias_vencimiento = 365
        elif tiempo == "24 meses":
            dias_vencimiento = 730
    fecha_vencimiento = (datetime.now() + timedelta(days=dias_vencimiento)).strftime("%d/%m/%Y")
        
    

    c.setFont("Helvetica", 15)
    c.drawString(80, 530, f"F.E: {fecha_actual}")
    c.drawString(230, 530, f"F.V: {fecha_vencimiento}")

    c.setFont("Helvetica", 18)
    fecha_d = datetime.now().strftime("%d")
    fecha_m = datetime.now().strftime("%m")
    fecha_a = datetime.now().strftime("%Y")
    # Lote original
    lote = f"1{nombre}{operador}{fecha_d}{fecha_m}{fecha_a}"
    # Si en la BD existe un lote, lo reemplazo
    if datos_sap.get("LoteMysql"):
        lote = datos_sap["LoteMysql"]
    c.drawString(210, 705, f"LOTE: {lote}")

    # === GENERAR CÓDIGO DE BARRAS ===
    barcode_value = str(orden_fabricacion)
    barcode = code128.Code128(barcode_value, barHeight=30, barWidth=1.8)

    # --- CAMBIO ÚNICO PARA POQUILLO ---
    if poquillo:
        # rectángulo blanco pequeño detrás de barras
        c.setFillColor("white")
        c.rect(145, 475, 150, 45, fill=True, stroke=False)
        c.setFillColor("black")

    # Dibujar código de barras
    barcode.drawOn(c, 140, 485)

    # Restaurar color del texto
    c.setFillColor(texto_color)

    c.save()
    return pdf_path


def generar_segunda_etiqueta(orden_fabricacion, poquillo, operador, kilos, finca, codfin, datos_sap, nombre):
    # Crea un documento PDF para la segunda etiqueta
    pdf_path_segunda_etiqueta = os.path.join(os.path.expanduser('~'), 'segunda_etiqueta.pdf')
    c = canvas.Canvas(pdf_path_segunda_etiqueta, pagesize=letter)
    
    # OJO Defino los colores de texto y fondo basados en la cantidad de kilos
    if float(kilos) <= 300:
        texto_color = "white"
        fondo_color = "black"
    else:
        texto_color = "black"
        fondo_color = "white"
        
    if poquillo:
        texto_color = "white"
        fondo_color = "black"
    else:
        texto_color = "black"
        fondo_color = "white"
        
    # Configura los colores en el lienzo
    c.setFillColor(fondo_color)
    c.rect(0, 0, letter[0], letter[1], fill=True)
    c.setFillColor(texto_color)

    # OJO ETIQUETA PARA FINCA J.CAMPOS
    # CABEZA DE LA ETIQUETA
    default_text = "VIA SAMBORONDÓN KM 1.5 S/N EDIF.XIMA"
    default_textb = "PISO 5 - OFIC 512 TELEFONO 3728600"
    width, height = letter
    text_width = c.stringWidth(default_text, "Helvetica", 14)
    text_width = c.stringWidth(default_textb, "Helvetica", 14)
    x_position = (width - text_width) / 2
    c.drawString(60, 770, default_text)
    c.setFont("Helvetica", 13)
    c.drawString(100, 755, default_textb)
    c.setFont("Helvetica-Bold", 18)

    # Agrega contenido al PDF con datos reales de SAP
    c.drawString(135, 725, f"PEDIDO: {datos_sap['Pedido']}")
    c.setFont("Helvetica", 18)
    c.drawString(10, 705, f"ORDEN: {orden_fabricacion}")

    c.setFont("Helvetica-Bold", 25)
    c.drawString(10, 675, f"CODIGO: {codfin}")

    c.setFont("Helvetica", 15)
    c.drawString(10, 650, f"TIPO: {datos_sap['Tipo']}")
    c.setFont("Helvetica-Bold", 25)
    c.drawString(250, 675, f"FINCA")
    c.setFont("Helvetica", 15)
    c.drawString(250, 650, f"DENSIDAD: {datos_sap['Densidad']}")
    c.setFont("Helvetica", 15)
    c.drawString(250, 635, f"PERF: {datos_sap['Perforacion']}")
    c.setFont("Helvetica", 15)
    c.drawString(10, 635, f"MEDIDAS: {datos_sap['Ancho']}X{datos_sap['Largo']}X{datos_sap['Espesor']}")
    c.setFont("Helvetica", 15)
    c.drawString(10, 620, f"COLOR: {datos_sap['Color']}")
    c.setFont("Helvetica", 15)
    c.drawString(10, 605, f"SELLO: {datos_sap['Sello']}")
    c.setFont("Helvetica-Bold", 20)
    c.drawString(130, 550, f"{kilos} UNIDADES")
    c.setFont("Helvetica", 15)
    
    # Agrega la fecha actual
    fecha_actual = datetime.now().strftime("%d/%m/%Y")
    c.drawString(80, 530, f"F.E: {fecha_actual}")
    c.setFont("Helvetica", 18)
    fecha_d = datetime.now().strftime("%d")
    fecha_m = datetime.now().strftime("%m")
    fecha_a = datetime.now().strftime("%Y")
    # Lote original
    lote = f"1{nombre}{operador}{fecha_d}{fecha_m}{fecha_a}"
    # Si en la BD existe un lote, lo reemplazo
    if datos_sap.get("LoteMysql"):
        lote = datos_sap["LoteMysql"]
    c.drawString(210, 705, f"LOTE: {lote}")
    c.setFont("Helvetica", 15)

    # Agrega fecha de vencimiento igual que xavier toma misma fecha y al año le suma +1
    dias_vencimiento = 365
    tiempo = datos_sap.get("TiempoDuracion")
    if tiempo:
        tiempo = tiempo.strip().lower()

        if tiempo == "6 meses":
            dias_vencimiento = 180
        elif tiempo == "12 meses":
            dias_vencimiento = 365
        elif tiempo == "24 meses":
            dias_vencimiento = 730
    fecha_vencimiento = ( datetime.now() + timedelta(days=dias_vencimiento)).strftime("%d/%m/%Y")
    c.drawString(230, 530, f"F.V: {fecha_vencimiento}")
    # Generar código de barras con la orden de fabricación
    barcode_value = str(orden_fabricacion)
    barcode = code128.Code128(barcode_value, barHeight=40, barWidth=0.7)

    barcode_x = 140
    barcode_y = 470
    barcode_w = 260
    barcode_h = 60

    c.setFillColor("white")
    c.rect(barcode_x, barcode_y, barcode_w, barcode_h, fill=True, stroke=False)

    c.setFillColor("black")
    barcode.drawOn(c, barcode_x + 15, barcode_y + 10)

    c.setFillColor(texto_color)

    # Guarda y cierra el PDF
    c.save()

    return pdf_path_segunda_etiqueta