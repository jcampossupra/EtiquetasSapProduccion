import tkinter as tk
from tkinter import ttk
from tkinter.font import BOLD
import util.generic as utl
import webbrowser
import conexion_sap
from tkinter import messagebox
from conexion_mysql import conectar_mysql
import pyodbc

from forms.form_etiquetas_pdf import generar_pdf, generar_segunda_etiqueta

lio = conexion_sap.cnsap


class MasterPanel:
    def __init__(self, nombre):
        self.nombre = nombre

        # CONTROL DE EDICION MANUAL DE KILOS
        self.kilos_original = ""
        self.edicion_manual_usada = False
        self.cantidad_fue_editada = False

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

        self.orden.bind("<Return>", self.cargar_kilos_orden_evento)
        self.orden.bind("<FocusOut>", self.cargar_kilos_orden_evento)

        etiqueta_operador = tk.Label(frame_form_fill, text="OPERADOR: ", font=('Times', 14), fg="#000000", bg='#fcfcfc', anchor="e")
        etiqueta_operador.grid(row=2, column=0, padx=20, pady=5, sticky="e")
        self.operador = ttk.Entry(frame_form_fill, font=('Times', 14))
        self.operador.grid(row=2, column=1, padx=20, pady=10, sticky="w")

        self.editar_kilos_var = tk.BooleanVar()
        check_editar_kilos = tk.Checkbutton(
            frame_form_fill,
            text="Editar Cantidad",
            variable=self.editar_kilos_var,
            font=('Times', 14),
            fg="#000000",
            bg='#fcfcfc',
            anchor="w",
            command=self.toggle_kilos_state
        )
        check_editar_kilos.grid(row=3, column=0, padx=20, pady=5, sticky="w")

        etiqueta_kilos = tk.Label(frame_form_fill, text="KILOS: ", font=('Times', 14), fg="#000000", bg='#fcfcfc', anchor="e")
        etiqueta_kilos.grid(row=3, column=0, padx=20, pady=5, sticky="e")
        self.kilos = ttk.Entry(frame_form_fill, font=('Times', 14), state="readonly")
        self.kilos.grid(row=3, column=1, padx=20, pady=10, sticky="w")
        self.kilos.bind("<KeyRelease>", self.marcar_edicion_manual_kilos)

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
        self.boton_obtener = inicio

        self.ventana.mainloop()

    def toggle_codfin_state(self):
        if self.finca_var.get():
            self.codfin.config(state=tk.NORMAL)
        else:
            self.codfin.config(state=tk.DISABLED)

    def toggle_kilos_state(self):
        if self.edicion_manual_usada:
            self.editar_kilos_var.set(False)
            self.kilos.config(state="readonly")
            messagebox.showwarning(
                title="Aviso",
                message="La cantidad ya fue editada una vez. Debe cerrar y volver a abrir el programa para generar más etiquetas."
            )
            return

        if self.editar_kilos_var.get():
            self.kilos.config(state="normal")
            self.kilos.focus_set()
            self.kilos.icursor(tk.END)
        else:
            self.kilos.config(state="readonly")

    def marcar_edicion_manual_kilos(self, event=None):
        if self.editar_kilos_var.get():
            valor_actual = self.kilos.get().strip()
            self.cantidad_fue_editada = (valor_actual != self.kilos_original)

    def cargar_kilos_orden_evento(self, event=None):
        self.cargar_kilos_orden()

    def cargar_kilos_orden(self):
        orden_fabricacion = self.orden.get().strip()

        if orden_fabricacion == "":
            self.kilos.config(state="normal")
            self.kilos.delete(0, tk.END)
            self.kilos.config(state="readonly")
            self.kilos_original = ""
            self.cantidad_fue_editada = False
            return

        try:
            sp1 = lio.cursor()
            sp1.execute("""
                SELECT T1."U_SUP_Uni_Bult"
                FROM "SBO_EC_TENA12_02"."OWOR" T0
                INNER JOIN "SBO_EC_TENA12_02"."OITM" T1 ON T1."ItemCode" = T0."ItemCode"
                WHERE T0."DocNum" = ?
            """, (orden_fabricacion,))
            resultado = sp1.fetchone()
            sp1.close()

            self.kilos.config(state="normal")
            self.kilos.delete(0, tk.END)

            if resultado and resultado[0] is not None:
                valor_kilos = str(resultado[0])
                self.kilos.insert(0, valor_kilos)
                self.kilos_original = valor_kilos
                self.cantidad_fue_editada = False

                if self.editar_kilos_var.get() and not self.edicion_manual_usada:
                    self.kilos.config(state="normal")
                else:
                    self.kilos.config(state="readonly")
            else:
                self.kilos.config(state="readonly")
                messagebox.showwarning(
                    title="Aviso",
                    message=f"La orden {orden_fabricacion} no tiene valor en U_SUP_Uni_Bult."
                )

        except pyodbc.Error as e:
            self.kilos.config(state="readonly")
            messagebox.showerror(message=str(e), title="Error")

    def verificar(self):
        if self.edicion_manual_usada:
            messagebox.showwarning(
                title="Aviso",
                message="Ya se utilizó una edición manual de cantidad. Debe cerrar y volver a abrir el programa para generar más etiquetas."
            )
            return

        if not self.editar_kilos_var.get():
            self.cargar_kilos_orden()

        # Obtén los datos que necesitas
        orden_fabricacion = self.orden.get()
        poquillo = self.poquillo_var.get()
        operador = self.operador.get()
        kilos = self.kilos.get()
        finca = self.finca_var.get()
        codfin = self.codfin.get() if finca else ""
        nombre = self.nombre

        try:
            # Valido si existe la orden de fabricación
            sp1 = lio.cursor()
            sp1.execute("""SELECT T0."DocNum" FROM "SBO_EC_TENA12_02"."OWOR" T0 WHERE "DocNum" = ? """, (orden_fabricacion,))
            cds = sp1.fetchall()
            sp1.close()

            if len(cds) > 0:
                print(f"La orden de fabricación {orden_fabricacion} existe.")

                # Consulta a SAP
                sp1 = lio.cursor()
                sp1.execute("""SELECT T1."OriginNum", T1."DocNum", T0."ItemCode",T11."ItmsGrpNam", T0."ItemName", T2."Name",T3."Name", T4."Name"
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
                INNER JOIN "SBO_EC_TENA12_02"."OITB" T11 ON T0."ItmsGrpCod" = T11."ItmsGrpCod"    
                WHERE T1."DocNum" = ? """, (orden_fabricacion,))

                fila_sap = sp1.fetchone()
                sp1.close()

                if not fila_sap:
                    messagebox.showerror(message="No se encontraron datos de SAP para la orden indicada.", title="Error")
                    return

                datos_sap = {
                        "Pedido": fila_sap[0],
                        "Orden": fila_sap[1],
                        "Codigo": fila_sap[2],
                        "GrupoArticulo": fila_sap[3],
                        "Producto": fila_sap[4],
                        "Tratamiento": fila_sap[5],
                        "Tipo": fila_sap[6],
                        "Ancho": fila_sap[7],
                        "Largo": fila_sap[8],
                        "Espesor": fila_sap[9],
                        "Color": fila_sap[10],
                        "Sello": fila_sap[11],
                        "Densidad": fila_sap[12],
                        "Perforacion": fila_sap[13],
                        "Unidades": fila_sap[14],
                }

                if not kilos:
                    kilos = str(datos_sap["Unidades"])
                    self.kilos.config(state="normal")
                    self.kilos.delete(0, tk.END)
                    self.kilos.insert(0, kilos)
                    self.kilos_original = kilos

                    if self.editar_kilos_var.get() and not self.edicion_manual_usada:
                        self.kilos.config(state="normal")
                    else:
                        self.kilos.config(state="readonly")

                # Detecta si se editó manualmente la cantidad
                if self.editar_kilos_var.get():
                    self.cantidad_fue_editada = (self.kilos.get().strip() != self.kilos_original)
                grupo = datos_sap["GrupoArticulo"]

                lote_mysql = None
                tiempo_mysql = None

                try:
                    conexion = conectar_mysql()
                    cursor = conexion.cursor()

                    cursor.execute("""
                        SELECT Tiempo_Duracion, Lote
                        FROM AUDITORIA_ETIQUETAS_TBL
                        WHERE Grupo_Articulo = %s
                        LIMIT 1
                    """, (grupo,))

                    fila_mysql = cursor.fetchone()

                    if fila_mysql:
                        tiempo_mysql = fila_mysql[0]
                        lote_mysql = fila_mysql[1]

                    cursor.close()
                    conexion.close()

                except Exception as e:
                    print("Error MySQL:", e)
                datos_sap["TiempoDuracion"] = tiempo_mysql
                datos_sap["LoteMysql"] = lote_mysql

                pdf_path = generar_pdf(orden_fabricacion, poquillo, operador, kilos, finca, codfin, datos_sap, nombre)
                webbrowser.open_new(pdf_path)

                if finca:
                    pdf_path_segunda_etiqueta = generar_segunda_etiqueta(orden_fabricacion, poquillo, operador, kilos, finca, codfin, datos_sap, nombre)
                    webbrowser.open_new(pdf_path_segunda_etiqueta)

                if self.cantidad_fue_editada:
                    self.edicion_manual_usada = True
                    self.kilos.config(state="readonly")
                    self.boton_obtener.config(state=tk.DISABLED)
                    messagebox.showinfo(
                        title="Aviso",
                        message="Se generó la etiqueta con cantidad editada manualmente. Para generar más etiquetas debe cerrar y volver a abrir el programa."
                    )

            else:
                print(f"No se encontró la orden de fabricación {orden_fabricacion}.")
                messagebox.showerror(message=f"No existe la orden de fabricación: {orden_fabricacion}", title="Error")

        except pyodbc.Error as e:
            messagebox.showerror(message=str(e), title="Error")

    def abrir_pdf(self):
        webbrowser.open_new("etiqueta.pdf")


if __name__ == "__main__":
    MasterPanel("JC")