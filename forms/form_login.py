import tkinter as tk
from tkinter import ttk, messagebox
from tkinter.font import BOLD
import util.generic as utl
from forms.form_master import MasterPanel
#importamos la conexion a sap 
import conexion_sap
import pyodbc
import os
lio = conexion_sap.cnsap

class App:
    
    
    def verificar(self):
        usu = self.usuario.get()
        #usu = 'OSCAR RAMOS'
        password = self.password.get()
        #password = '0940126949'
        
        try:
            sp1 = lio.cursor()
            sp1.execute("""SELECT T0."Code", T0."workStreet", T0."StreetNoW"
                FROM "SBO_EC_TENA12_02"."OHEM" T0
                WHERE T0."workStreet" = ? and T0."StreetNoW" = ? """, (usu,password))
            
            cds = sp1.fetchall()
            print(usu, password, cds, len(cds))
            sp1.close()
            messagebox.showinfo(message="Conexión exitosa a SAP HANA", title="Éxito")
            
            if len(cds) > 0:
            
                nombre = usu[:3].upper()
                
                print("Traigo las dos primeras letras del usuario:", nombre)
                
                self.ventana.destroy()
                MasterPanel(nombre)
                
        except pyodbc.Error as e:
            messagebox.showerror(message=str(e), title="Error")

        if usu and password:
            print(sp1.rowcount == 0, sp1.rowcount)
            if len(cds) > 0:
                print("Login exitoso")
                self.ventana.destroy()
                MasterPanel()
            else:
                print("Usuario y/o contraseña incorrectos")
                messagebox.showerror(message="Usuario y/o contraseña incorrectos!", title="Mensaje")
        else:
            messagebox.showerror(message="Usuario y contraseña son obligatorios", title="Mensaje")
    
    
    # #verificacion sin conexion a sap 
    # def verificar(self):
    #     usu = self.usuario.get()
    #     password = self.password.get()        
    #     if(usu == "1" and password == "1") :
    #         self.ventana.destroy()
    #         MasterPanel()
    #     else:
    #         messagebox.showerror(message="La contraseña no es correcta",title="Mensaje")           
                      
    def __init__(self):
        self.ventana = tk.Tk()
        self.ventana.title('SISTEMA DE ETIQUETAS DE PRODUCTOS TERMINADOS CON SAP B1')
        self.ventana.geometry('800x500')
        self.ventana.config(bg='#fcfcfc')
        self.ventana.resizable(width=0, height=0)
        utl.centrar_ventana(self.ventana, 600, 500)  # -Dimension de login ojo

        #logo = utl.leer_imagen("./imagenes/logo.png", (100, 100))

        # frame_logo = tk.Frame(self.ventana, bd=0, width=300, relief=tk.SOLID, padx=10, pady=10, bg='#ffffff')
        # frame_logo.pack(side="top", expand=tk.YES, fill=tk.BOTH)
        # label = tk.Label(frame_logo, image=logo, bg='#ffffff')
        # label.place(x=0, y=0, relwidth=1, relheight=1)

        frame_form = tk.Frame(self.ventana, bd=0, relief=tk.SOLID, bg='#fcfcfc')
        frame_form.pack(side="right", expand=tk.YES, fill=tk.BOTH)

        frame_form_top = tk.Frame(frame_form, height=50, bd=0, relief=tk.SOLID, bg='black')
        frame_form_top.pack(side="top", fill=tk.X)
        title = tk.Label(frame_form_top, text="Inicio de sesión", font=('Times', 30), fg="#666a88", bg='#fcfcfc', pady=50)
        title.pack(expand=tk.YES, fill=tk.BOTH)

        frame_form_fill = tk.Frame(frame_form, height=50, bd=0, relief=tk.SOLID, bg='#fcfcfc')
        frame_form_fill.pack(side="bottom", expand=tk.YES, fill=tk.BOTH)

        etiqueta_usuario = tk.Label(frame_form_fill, text="Usuario", font=('Times', 14), fg="#666a88", bg='#fcfcfc',
                                    anchor="w")
        etiqueta_usuario.pack(fill=tk.X, padx=20, pady=5)
        self.usuario = ttk.Entry(frame_form_fill, font=('Times', 14))
        self.usuario.pack(fill=tk.X, padx=20, pady=10)

        etiqueta_password = tk.Label(frame_form_fill, text="Contraseña", font=('Times', 14), fg="#666a88",
                                     bg='#fcfcfc', anchor="w")
        etiqueta_password.pack(fill=tk.X, padx=20, pady=5)
        self.password = ttk.Entry(frame_form_fill, font=('Times', 14))
        self.password.pack(fill=tk.X, padx=20, pady=10)
        self.password.config(show="*")

        inicio = tk.Button(frame_form_fill, text="Iniciar sesión", font=('Times', 15, BOLD), bg='#3a7ff6', bd=0,
                           fg="#fff", command=self.verificar)
        inicio.pack(fill=tk.X, padx=20, pady=20)
        inicio.bind("<Return>", (lambda event: self.verificar()))
        self.ventana.mainloop()


if __name__ == "__main__":
    App()