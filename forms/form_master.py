import tkinter as tk
from tkinter import ttk
from tkinter.font import BOLD
import util.generic as utl
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
import webbrowser
from datetime import datetime
from datetime import datetime, timedelta
import conexion_sap
from tkinter import messagebox
from reportlab.graphics.barcode import code128
from reportlab.graphics.shapes import Drawing
import pyodbc
import os

lio = conexion_sap.cnsap

class MasterPanel:
    def __init__(self, nombre):
        self.nombre = nombre
        self.ventana = tk.Tk()
        self.ventana.title('ETIQUETAS DE PRODUCTO TERMINADO CON SAP B1')
        w, h = self.ventana.winfo_screenwidth(), self.ventana.winfo_screenheight()
        self.ventana.geometry("%dx%d+0+0" % (w, h))
        self.ventana.config(bg='#fcfcfc')
        self.ventana.resizable(width=0, height=0)
        utl.centrar_ventana(self.ventana, 515, 500)

        frame_form = tk.Frame(self.ventana, bd=0, relief=tk.SOLID, bg='#f2f2f2')  
        frame_form.pack(side="right", expand=tk.YES, fill=tk.BOTH)

        frame_form_top = tk.Frame(frame_form, height=50, bd=0, relief=tk.SOLID, bg='black')
        frame_form_top.pack(side="top", fill=tk.X)
        title = tk.Label(frame_form_top, text="ETIQUETAS GENERALES", font=('Times', 15, BOLD), fg="#000000", bg='#fcfcfc', pady=50)
        title.pack(expand=tk.YES, fill=tk.BOTH)

        frame_form_fill = tk.Frame(frame_form, height=50, bd=0, relief=tk.SOLID, bg='#fcfcfc')
        frame_form_fill.pack(side="bottom", expand=tk.YES, fill=tk.BOTH)

        self.poquillo_var = tk.BooleanVar()
        check_poquillo = tk.Checkbutton(frame_form_fill, text="Poquillo", variable=self.poquillo_var, font=('Times', 14), fg="#000000", bg='#fcfcfc', anchor="w")
        check_poquillo.grid(row=0, column=0, padx=20, pady=5, sticky="w")

        etiqueta_orden = tk.Label(frame_form_fill, text="ORDEN DE FABRICACIÓN #:", font=('Times', 14), fg="#000000", bg='#fcfcfc', anchor="e")
        etiqueta_orden.grid(row=1, column=0, padx=20, pady=5, sticky="e")
        self.orden = ttk.Entry(frame_form_fill, font=('Times', 14))
        self.orden.grid(row=1, column=1, padx=20, pady=10, sticky="w")

        etiqueta_operador = tk.Label(frame_form_fill, text="OPERADOR: ", font=('Times', 14), fg="#000000", bg='#fcfcfc', anchor="e")
        etiqueta_operador.grid(row=2, column=0, padx=20, pady=5, sticky="e")
        self.operador = ttk.Entry(frame_form_fill, font=('Times', 14))
        self.operador.grid(row=2, column=1, padx=20, pady=10, sticky="w")

        etiqueta_kilos = tk.Label(frame_form_fill, text="KILOS: ", font=('Times', 14), fg="#000000", bg='#fcfcfc', anchor="e")
        etiqueta_kilos.grid(row=3, column=0, padx=20, pady=5, sticky="e")
        self.kilos = ttk.Entry(frame_form_fill, font=('Times', 14))
        self.kilos.grid(row=3, column=1, padx=20, pady=10, sticky="w")

        self.finca_var = tk.BooleanVar()
        check_finca = tk.Checkbutton(frame_form_fill, text="FINCA", variable=self.finca_var, font=('Times', 14), fg="#000000", bg='#fcfcfc', anchor="w", command=self.toggle_codfin_state)
        check_finca.grid(row=4, column=0, padx=20, pady=5, sticky="w")

        etiqueta_codfin = tk.Label(frame_form_fill, text="CODIGO FINCA: ", font=('Times', 14), fg="#000000", bg='#fcfcfc', anchor="e")
        etiqueta_codfin.grid(row=5, column=0, padx=20, pady=5, sticky="e")
        self.codfin = ttk.Entry(frame_form_fill, font=('Times', 14), state=tk.DISABLED)
        self.codfin.grid(row=5, column=1, padx=20, pady=10, sticky="w")

        inicio = tk.Button(frame_form_fill, text="OBTENER ETIQUETA", font=('Times', 15, BOLD), bg='#3a7ff6', bd=0, fg="#000000", command=self.verificar)
        inicio.grid(row=6, column=0, columnspan=2, padx=10, pady=40, sticky="ew")
        inicio.bind("<Return>", (lambda event: self.verificar()))
        self.ventana.mainloop()

    def toggle_codfin_state(self):
        if self.finca_var.get():
            self.codfin.config(state=tk.NORMAL)
        else:
            self.codfin.config(state=tk.DISABLED)

    def verificar(self):
        # Obtén los datos que necesitas
        orden_fabricacion = self.orden.get()
        poquillo = self.poquillo_var.get()
        operador = self.operador.get()
        kilos = self.kilos.get()
        finca = self.finca_var.get()
        codfin = self.codfin.get() if finca else ""
        nombre= self.nombre
      

        try:
            # Valido si existe la orden de fabricación
            sp1 = lio.cursor()
            sp1.execute(f"""SELECT T0."DocNum" FROM "SBO_EC_TENA12_02"."OWOR" T0 WHERE "DocNum" = ? """, (orden_fabricacion,))
            cds = sp1.fetchall()
            sp1.close()

            if len(cds) > 0:
                print(f"La orden de fabricación {orden_fabricacion} existe.")
                # Consulta a SAP
                sp1 = lio.cursor()
                sp1.execute(f"""SELECT T1."OriginNum", T1."DocNum", T0."ItemCode", T0."ItemName", T2."Name",T3."Name", T4."Name"
                ,T5."Name",T6."Name",T7."Name",T8."Name",T9."Name",T10."Name",T0."U_SUP_Uni_Bult"
                FROM "SBO_EC_TENA12_02"."OITM" T0 
                INNER JOIN "SBO_EC_TENA12_02"."OWOR" T1 ON T1."ItemCode" = T0."ItemCode"
               LEFT JOIN "SBO_EC_TENA12_02"."@EXX_TIPO_TRATAMIENT" T2 ON T2."Code" = T0."U_EXX_TIPO_TRATAMIENTO"
                LEFT JOIN "SBO_EC_TENA12_02"."@EXX_TIPO_PERFORACIO" T3 ON T3."Code" = T0."U_EXX_TIPO_PERFORACION"
                LEFT JOIN "SBO_EC_TENA12_02"."@EXX_ANCHO" T4 ON T4."Code" = T0."U_EXX_ANCHO" 
                LEFT JOIN "SBO_EC_TENA12_02"."@EXX_LARGO" T5 ON T5."Code" = T0."U_EXX_LARGO" 
                LEFT JOIN "SBO_EC_TENA12_02"."@EXX_ESPESOR_MM" T6 ON T6."Code" = T0."U_EXX_ESPESOR_MM" 
                LEFT JOIN "SBO_EC_TENA12_02"."@EXX_COLOR" T7 ON T7."Code" = T0."U_EXX_COLOR"
               LEFT JOIN "SBO_EC_TENA12_02"."@EXX_LOGO_PRIMARIO" T8 ON T8."Code" = T0."U_EXX_LOGO_PRI"
               LEFT JOIN "SBO_EC_TENA12_02"."@EXX_DENSIDAD" T9 ON T9."Code" = T0."U_EXX_DENS"
              LEFT JOIN "SBO_EC_TENA12_02"."@EXX_PERFORACION" T10 ON T10."Code" = T0."U_EXX_PERFORACION"


                WHERE T1."DocNum" = ? """, (orden_fabricacion,))

                datos_sap = sp1.fetchone()
                sp1.close()

                # Asignar valores específicos a datos_sap
                datos_sap = {
                    "Pedido": datos_sap[0],  
                    "Orden": datos_sap[1],
                    #"Cliente": datos_sap[2],
                    "Codigo": datos_sap[2],
                    "Producto": datos_sap[3],
                    "Tratamiento": datos_sap[4],
                    "Tipo": datos_sap[5],
                    "Ancho": datos_sap[6],
                    "Largo": datos_sap[7],
                    "Espesor": datos_sap[8],
                    "Color": datos_sap[9],
                    "Sello": datos_sap[10],
                    "Densidad": datos_sap[11],
                    "Perforacion": datos_sap[12],
                    "Unidades": datos_sap[13],
                }

                # Resto de tu código para generar el PDF
                pdf_path = self.generar_pdf(orden_fabricacion, poquillo, operador, kilos, finca, codfin, datos_sap, nombre)

                # Abre el visor de PDF
                webbrowser.open_new(pdf_path)

                # Si el usuario seleccionó la opción de finca, genera la segunda etiqueta
                if finca:
                    # Genera el PDF de la segunda etiqueta
                    pdf_path_segunda_etiqueta = self.generar_segunda_etiqueta(orden_fabricacion, poquillo, operador, kilos, finca, codfin, datos_sap, nombre )

                    # Abre el visor de PDF para la segunda etiqueta
                    webbrowser.open_new(pdf_path_segunda_etiqueta)
            else:
                print(f"No se encontró la orden de fabricación {orden_fabricacion}.")
                messagebox.showerror(message=f"No existe la orden de fabricación: {orden_fabricacion}", title="Error")

        except pyodbc.Error as e:
            messagebox.showerror(message=str(e), title="Error")

    def generar_pdf(self, orden_fabricacion,poquillo, operador, kilos, finca, codfin, datos_sap, nombre):
        # Crea un documento PDF
        pdf_path = os.path.join(os.path.expanduser('~'), 'etiqueta.pdf')
        c = canvas.Canvas(pdf_path, pagesize=letter)
        
        #OJO Defino los colores de texto y fondo basados en la cantidad de kilos
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
        default_text = "VIA SAMBORONDÓN KM 1.5 S/N EDIF.XIMA-TORRE B"
        default_textb ="PISO 5 - OFIC 512 TELEFONO 3728600"
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
        #c.setFont("Helvetica", 15)
        #c.drawString(140, 690, f"CLIENTE: {datos_sap['Cliente']}")
        c.setFont("Helvetica-Bold", 25)  
        c.drawString(10, 675, f"CODIGO: {datos_sap['Codigo']}")
        producto = datos_sap['Producto']
        if len(producto) > 44:
            producto_parte1 = producto[:40]  # Primeras 40 caracteres
            producto_parte2 = producto[40:]  # Resto del texto
            c.setFont("Helvetica", 14) 
            c.drawString(10, 650, f"PRODUCTO: {producto_parte1}")
            c.drawString(10, 635, producto_parte2)  # Dibujar la segunda parte en la siguiente línea
        else:
            c.setFont("Helvetica", 14) 
            c.drawString(10, 650, f"PRODUCTO: {producto}")
        c.setFont("Helvetica", 15)
        #c.drawString(90, 640, f"TRATAMIENTO: {datos_sap['Tratamiento']}")
        c.drawString(10, 620, f"TIPO: {datos_sap['Tipo']}")
        c.setFont("Helvetica", 15)
        c.drawString(250, 620, f"DENSIDAD: {datos_sap['Densidad']}")
        c.setFont("Helvetica", 15)
        c.drawString(250, 605, f"PERF: {datos_sap['Perforacion']}")
        c.setFont("Helvetica", 15)
        c.drawString(10, 605, f"MEDIDAS: {datos_sap['Ancho']}X{datos_sap['Largo']}X{datos_sap['Espesor']}")
        c.setFont("Helvetica", 15)
        c.drawString(10, 590, f"COLOR: {datos_sap['Color']}")
        c.setFont("Helvetica", 15)
        c.drawString(10, 575, f"SELLO: {datos_sap['Sello']}")
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
        c.drawString(210, 705, f"LOTE: 1{nombre}{operador}{fecha_d}{fecha_m}{fecha_a}")
        c.setFont("Helvetica", 15)
        # Agrega fecha de vencimiento igual que xavier toma misma fecha y al año le suma +1
        fecha_vencimiento = (datetime.now() + timedelta(days=365)).strftime("%d/%m/%Y")
        c.drawString(230, 530, f"F.V: {fecha_vencimiento}")
        # Generar código de barras con la orden de fabricación
        barcode_value = str(orden_fabricacion)
        barcode = code128.Code128(barcode_value, barHeight=30, barWidth=1.8)
        barcode.drawOn(c, 140, 485)

        # Guarda y cierra el PDF
        c.save()

        return pdf_path

    def generar_segunda_etiqueta(self, orden_fabricacion, poquillo, operador, kilos, finca, codfin, datos_sap,nombre):
        # Crea un documento PDF para la segunda etiqueta
        pdf_path_segunda_etiqueta = os.path.join(os.path.expanduser('~'), 'segunda_etiqueta.pdf')
        c = canvas.Canvas(pdf_path_segunda_etiqueta, pagesize=letter)
        
         #OJO Defino los colores de texto y fondo basados en la cantidad de kilos
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
        default_text = "VIA SAMBORONDÓN KM 1.5 S/N EDIF.XIMA-TORRE B"
        default_textb ="PISO 5 - OFIC 512 TELEFONO 3728600"
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
        #c.setFont("Helvetica", 15)
        #c.drawString(140, 690, f"CLIENTE: {datos_sap['Cliente']}")
        c.setFont("Helvetica-Bold", 25)  
        c.drawString(10, 675, f"CODIGO: {codfin}")
        # producto = datos_sap['Producto']
        # if len(producto) > 44:
        #     producto_parte1 = producto[:40]  # Primeras 40 caracteres
        #     producto_parte2 = producto[40:]  # Resto del texto
        #     c.setFont("Helvetica", 14) 
        #     c.drawString(10, 650, f"PRODUCTO: {producto_parte1}")
        #     c.drawString(10, 635, producto_parte2)  # Dibujar la segunda parte en la siguiente línea
        # else:
        #     c.setFont("Helvetica", 14) 
        #     c.drawString(10, 650, f"PRODUCTO: {producto}")
        #c.setFont("Helvetica", 15)
        #c.drawString(90, 640, f"TRATAMIENTO: {datos_sap['Tratamiento']}")
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
        c.drawString(210, 705, f"LOTE: 1{nombre}{operador}{fecha_d}{fecha_m}{fecha_a}")
        c.setFont("Helvetica", 15)
        # Agrega fecha de vencimiento igual que xavier toma misma fecha y al año le suma +1
        fecha_vencimiento = (datetime.now() + timedelta(days=365)).strftime("%d/%m/%Y")
        c.drawString(230, 530, f"F.V: {fecha_vencimiento}")
        # Generar código de barras con la orden de fabricación
        barcode_value = str(orden_fabricacion)
        barcode = code128.Code128(barcode_value, barHeight=40, barWidth=1.2)

        # Posicionar el código de barras en el PDF
        barcode = code128.Code128(barcode_value, barHeight=40, barWidth=1.2)
        barcode.drawOn(c, 10, 590)  # Puedes ajustar la posición si hace falta

        # Guarda y cierra el PDF
        c.save()

        return pdf_path_segunda_etiqueta

    def abrir_pdf(self):
        webbrowser.open_new("etiqueta.pdf")

if __name__ == "__main__":
    MasterPanel()
