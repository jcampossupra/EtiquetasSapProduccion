import tkinter as tk
from tkinter import ttk
from tkinter.font import BOLD
import util.generic as utl
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
import webbrowser
from datetime import datetime, timedelta
import conexion_sap
from tkinter import messagebox
import pyodbc
import os
import serial 
import threading

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
        
        # Agrega la etiqueta y el campo para el peso de la balanza
        self.balanza_peso = tk.StringVar()
        etiqueta_peso = tk.Label(frame_form_fill, text="PESO BALANZA: ", font=('Times', 14), fg="#000000", bg='#fcfcfc', anchor="e")
        etiqueta_peso.grid(row=7, column=0, padx=20, pady=5, sticky="e")
        self.peso_balanza = ttk.Entry(frame_form_fill, font=('Times', 14), textvariable=self.balanza_peso, state=tk.DISABLED)
        self.peso_balanza.grid(row=7, column=1, padx=20, pady=10, sticky="w")

        threading.Thread(target=self.leer_balanza, daemon=True).start()
        self.ventana.mainloop()

    def toggle_codfin_state(self):
        if self.finca_var.get():
            self.codfin.config(state=tk.NORMAL)
        else:
            self.codfin.config(state=tk.DISABLED)

    def leer_balanza(self):
        try:
            ser = serial.Serial('COM4', 9600, timeout=1)

            while True:
                if ser.in_waiting > 0:
                    peso = ser.readline().decode('utf-8').strip()
                    self.balanza_peso.set(peso)

        except serial.SerialException as e:
            print(f"Error al conectar con la balanza: {e}")

    def verificar(self):
        orden_fabricacion = self.orden.get()
        poquillo = self.poquillo_var.get()
        operador = self.operador.get()
        kilos = self.balanza_peso.get()  # Ahora obtiene el peso de la balanza
        finca = self.finca_var.get()
        codfin = self.codfin.get() if finca else ""
        nombre = self.nombre

        try:
            sp1 = lio.cursor()
            sp1.execute(f"""SELECT T0."DocNum" FROM "SUPRALIVE_PRD"."OWOR" T0 WHERE "DocNum" = ? """, (orden_fabricacion,))
            cds = sp1.fetchall()
            sp1.close()

            if len(cds) > 0:
                print(f"La orden de fabricación {orden_fabricacion} existe.")
                sp1 = lio.cursor()
                sp1.execute(f"""SELECT T1."OriginNum", T1."DocNum", T0."ItemCode", T0."ItemName", T2."Name",T3."Name", T4."Name"
                ,T5."Name",T6."Name",T7."Name",T8."Name",T9."Name",T10."Name",T0."U_SUP_Uni_Bult"
                FROM "SUPRALIVE_PRD"."OITM" T0 
                INNER JOIN "SUPRALIVE_PRD"."OWOR" T1 ON T1."ItemCode" = T0."ItemCode"
                FULL JOIN "SUPRALIVE_PRD"."@EXX_TIPO_TRATAMIENT" T2 ON T2."Code" = T0."U_EXX_TIPO_TRATAMIENTO"
                FULL JOIN "SUPRALIVE_PRD"."@EXX_TIPO_PERFORACIO" T3 ON T3."Code" = T0."U_EXX_TIPO_PERFORACION"
                FULL JOIN "SUPRALIVE_PRD"."@EXX_ANCHO" T4 ON T4."Code" = T0."U_EXX_ANCHO" 
                FULL JOIN "SUPRALIVE_PRD"."@EXX_LARGO" T5 ON T5."Code" = T0."U_EXX_LARGO" 
                FULL JOIN "SUPRALIVE_PRD"."@EXX_ESPESOR_MM" T6 ON T6."Code" = T0."U_EXX_ESPESOR_MM" 
                FULL JOIN "SUPRALIVE_PRD"."@EXX_COLOR" T7 ON T7."Code" = T0."U_EXX_COLOR"
                FULL JOIN "SUPRALIVE_PRD"."@EXX_MATERIAL" T8 ON T8."Code" = T0."U_EXX_MATERIAL" 
                FULL JOIN "SUPRALIVE_PRD"."@EXX_ESTADO_MATERIAL" T9 ON T9."Code" = T0."U_EXX_ESTADO_MATERIAL" 
                FULL JOIN "SUPRALIVE_PRD"."@EXX_CALIBRE" T10 ON T10."Code" = T0."U_EXX_CALIBRE"
                WHERE T1."DocNum" = ? """, (orden_fabricacion,))
                datos = sp1.fetchall()

                itemcode = datos[0][2]
                descripcion = datos[0][3]
                tratamiento = datos[0][4]
                perforacion = datos[0][5]
                ancho = datos[0][6]
                largo = datos[0][7]
                espesor = datos[0][8]
                color = datos[0][9]
                material = datos[0][10]
                estado_material = datos[0][11]
                calibre = datos[0][12]
                unidadesxbulto = datos[0][13]

                filename = "etiqueta.pdf"
                c = canvas.Canvas(filename, pagesize=letter)

                c.drawString(100, 750, "Etiqueta de Producto Terminado")
                c.drawString(100, 735, f"Fecha: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
                c.drawString(100, 720, f"Orden de Fabricación: {orden_fabricacion}")
                c.drawString(100, 705, f"Operador: {operador}")
                c.drawString(100, 690, f"Poquillo: {'Sí' if poquillo else 'No'}")
                c.drawString(100, 675, f"Kilos: {kilos}")
                c.drawString(100, 660, f"Itemcode: {itemcode}")
                c.drawString(100, 645, f"Descripción: {descripcion}")
                c.drawString(100, 630, f"Tratamiento: {tratamiento}")
                c.drawString(100, 615, f"Perforación: {perforacion}")
                c.drawString(100, 600, f"Ancho: {ancho}")
                c.drawString(100, 585, f"Largo: {largo}")
                c.drawString(100, 570, f"Espesor: {espesor}")
                c.drawString(100, 555, f"Color: {color}")
                c.drawString(100, 540, f"Material: {material}")
                c.drawString(100, 525, f"Estado Material: {estado_material}")
                c.drawString(100, 510, f"Calibre: {calibre}")
                c.drawString(100, 495, f"Unidades por Bulto: {unidadesxbulto}")
                if finca:
                    c.drawString(100, 480, f"Finca: Sí")
                    c.drawString(100, 465, f"Codigo Finca: {codfin}")
                else:
                    c.drawString(100, 480, f"Finca: No")

                c.save()

                webbrowser.open_new(filename)

            else:
                messagebox.showerror("Error", f"La orden de fabricación {orden_fabricacion} no existe.")
        except Exception as e:
            print(f"Error al conectar con la base de datos: {e}")
