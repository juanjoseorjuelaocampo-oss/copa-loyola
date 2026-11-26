import tkinter
from tkinter import ttk
from tkinter import messagebox
import json
import csv
import os

#    COLORES
COLOR_FONDO = "#031018"       # fondo de las pestañas
COLOR_TITULO = "#FFFFFF"       # texto de los titulos de cada pestana
COLOR_TEXTO = "#C5A253"        # texto de las etiquetas
COLOR_BOTON = "#1F4E79"        # fondo de los botones
COLOR_BOTON_ACTIVO = "#2E6DA4" # fondo del boton cuando el mouse pasa por encima esto es el .map
COLOR_BOTON_TEXTO = "#FFFFFF"  # texto de los botones
COLOR_LISTA_FONDO = "#FFFFFF"  # fondo de las listas de la derecha
COLOR_LISTA_TEXTO = "#222222"  # texto de las listas
COLOR_SELECCION = "#CFE2F3"    # fila seleccionada en las listas
FUENTE = "Arial"
#    DATOS EN MEMORIA
universidades = []
deportistas = []
disciplinas = []
inscripciones = []
resultados = []

MEDALLAS = ["Oro", "Plata", "Bronce"]
PUNTOS = {"Oro": 3, "Plata": 2, "Bronce": 1}
ARCHIVO_DATOS = "copa_loyola_datos.json"
CAMPOS = {"universidades": ["nombre", "pais", "ciudad", "tipo"],
          "deportistas": ["nombre", "tipo_doc", "num_doc", "universidad"],
          "disciplinas": ["nombre", "modalidad"]}

#       FUNCIONES DE APOYO
def buscar(lista, clave, valor):

    for i in range(len(lista)):
        if lista[i][clave].lower() == valor.lower():
            return i
    return -1

def nombres(lista):

    resultado = []
    for registro in lista:
        resultado.append(registro["nombre"])
    return resultado

def campos_vacios(valores):

    for valor in valores:
        if valor.strip() == "":
            return True
    return False

def mostrar(listbox, lineas):

    listbox.delete(0, tkinter.END)
    for linea in lineas:
        listbox.insert(tkinter.END, linea)

def limpiar(campos):

    for campo_formulario in campos:
        if type(campo_formulario) == ttk.Combobox:
            campo_formulario.set("")
        else:
            campo_formulario.delete(0, tkinter.END)

def documento_invalido(tipo_doc, num_doc):

    if tipo_doc == "Pasaporte":
        return False
    return not num_doc.isdigit()

def refrescar_combo(combo, valores):

    combo["values"] = valores
    if combo.get() not in valores:
        combo.set("")

def actualizar_listas():

    lineas = []
    for i in range(len(universidades)):
        u = universidades[i]
        lineas.append(str(i + 1) + ". " + u["nombre"] + " | " + u["pais"] + " | " + u["ciudad"] + " | " + u["tipo"])
    mostrar(lista_universidades, lineas)

    lineas = []
    for i in range(len(deportistas)):
        d = deportistas[i]
        lineas.append(str(i + 1) + ". " + d["nombre"] + " | " + d["tipo_doc"] + " " + d["num_doc"] + " | " + d["universidad"])
    mostrar(lista_deportistas, lineas)

    lineas = []
    for i in range(len(disciplinas)):
        d = disciplinas[i]
        lineas.append(str(i + 1) + ". " + d["nombre"] + " | " + d["modalidad"])
    mostrar(lista_disciplinas, lineas)

    refrescar_combo(combo_universidad_dep, nombres(universidades))
    refrescar_combo(combo_universidad_res, nombres(universidades))
    refrescar_combo(combo_deportista_ins, nombres(deportistas))
    refrescar_combo(combo_disciplina_ins, nombres(disciplinas))
    refrescar_combo(combo_filtro_ins, ["Todas"] + nombres(disciplinas))
    refrescar_combo(combo_disciplina_res, nombres(disciplinas))
    mostrar_inscripciones()
    mostrar_resultados()

#    CALCULOS PARA LAS CONSULTAS

def calcular_medallero():

    medallero = {}
    for u in universidades:
        medallero[u["nombre"]] = [0, 0, 0]
    for fila in resultados:
        universidad = fila[1]
        posicion = fila[2]
        columna = MEDALLAS.index(posicion)   # Oro=0, Plata=1, Bronce=2
        medallero[universidad][columna] = medallero[universidad][columna] + 1
    return medallero

def clave_orden(fila):

    return [fila[1], fila[2], fila[3], fila[4]]

def calcular_clasificacion():

    medallero = calcular_medallero()
    clasificacion = []
    for universidad in medallero:
        oros = medallero[universidad][0]
        platas = medallero[universidad][1]
        bronces = medallero[universidad][2]
        puntos = oros * PUNTOS["Oro"] + platas * PUNTOS["Plata"] + bronces * PUNTOS["Bronce"]
        clasificacion.append([universidad, puntos, oros, platas, bronces])

    clasificacion.sort(key=clave_orden, reverse=True)
    return clasificacion

def universidades_ganadoras(clasificacion):

    ganadoras = []
    if len(clasificacion) > 0:
        mejor = clasificacion[0]
        for fila in clasificacion:

            if fila[1:] == mejor[1:]:
                ganadoras.append(fila[0])
    return ganadoras


def disciplinas_de(deportista):

    lista = []
    for fila in inscripciones:
        if fila[0] == deportista:
            lista.append(fila[1])
    if len(lista) == 0:
        return "Sin inscripciones"
    return ", ".join(lista)

#    PESTANA UNIVERSIDADES

def crear_universidad():

    nombre = entrada_nombre_uni.get().strip()
    pais = entrada_pais.get().strip()
    ciudad = entrada_ciudad.get().strip()
    tipo = combo_tipo.get().strip()

    if campos_vacios([nombre, pais, ciudad, tipo]):
        messagebox.showerror("Error", "Todos los campos son obligatorios.")
        return
    if buscar(universidades, "nombre", nombre) != -1:
        messagebox.showerror("Error", "La universidad ya está registrada.")
        return

    universidades.append({"nombre": nombre, "pais": pais, "ciudad": ciudad, "tipo": tipo})

    limpiar([entrada_nombre_uni, entrada_pais, entrada_ciudad, combo_tipo])
    actualizar_listas()

def seleccionar_universidad(evento):

    seleccion = lista_universidades.curselection()
    if len(seleccion) == 0:
        return
    u = universidades[seleccion[0]]
    limpiar([entrada_nombre_uni, entrada_pais, entrada_ciudad, combo_tipo])
    entrada_nombre_uni.insert(0, u["nombre"])
    entrada_pais.insert(0, u["pais"])
    entrada_ciudad.insert(0, u["ciudad"])
    combo_tipo.set(u["tipo"])

def actualizar_universidad():
    seleccion = lista_universidades.curselection()
    if len(seleccion) == 0:
        messagebox.showerror("Error", "Seleccione una universidad de la lista.")
        return
    i = seleccion[0]

    nombre = entrada_nombre_uni.get().strip()
    pais = entrada_pais.get().strip()
    ciudad = entrada_ciudad.get().strip()
    tipo = combo_tipo.get().strip()

    if campos_vacios([nombre, pais, ciudad, tipo]):
        messagebox.showerror("Error", "Todos los campos son obligatorios.")
        return
    existe = buscar(universidades, "nombre", nombre)
    if existe != -1 and existe != i:
        messagebox.showerror("Error", "Ya existe otra universidad con ese nombre.")
        return

    nombre_viejo = universidades[i]["nombre"]
    universidades[i] = {"nombre": nombre, "pais": pais, "ciudad": ciudad, "tipo": tipo}
    for d in deportistas:
        if d["universidad"] == nombre_viejo:
            d["universidad"] = nombre
    for fila in resultados:
        if fila[1] == nombre_viejo:
            fila[1] = nombre

    limpiar([entrada_nombre_uni, entrada_pais, entrada_ciudad, combo_tipo])
    actualizar_listas()


def eliminar_universidad():
    seleccion = lista_universidades.curselection()
    if len(seleccion) == 0:
        messagebox.showerror("Error", "Seleccione una universidad de la lista.")
        return
    nombre = universidades[seleccion[0]]["nombre"]

    asociada = False
    for d in deportistas:
        if d["universidad"] == nombre:
            asociada = True
    for fila in resultados:
        if fila[1] == nombre:
            asociada = True
    if asociada == True:
        messagebox.showerror("Error", "La universidad tiene deportistas o resultados asociados.")
        return
    universidades.pop(seleccion[0])
    limpiar([entrada_nombre_uni, entrada_pais, entrada_ciudad, combo_tipo])
    actualizar_listas()

#        PESTANA DEPORTISTAS
def crear_deportista():

    nombre = entrada_nombre_dep.get().strip()
    tipo_doc = combo_tipo_doc.get().strip()
    num_doc = entrada_num_doc.get().strip()
    universidad = combo_universidad_dep.get().strip()

    if campos_vacios([nombre, tipo_doc, num_doc, universidad]):
        messagebox.showerror("Error", "Todos los campos son obligatorios.")
        return
    if buscar(universidades, "nombre", universidad) == -1:
        messagebox.showerror("Error", "La universidad no existe.")
        return
    if documento_invalido(tipo_doc, num_doc):
        messagebox.showerror("Error", "El número de documento solo puede tener dígitos.")
        return
    if buscar(deportistas, "num_doc", num_doc) != -1 or buscar(deportistas, "nombre", nombre) != -1:
        messagebox.showerror("Error", "El deportista ya está registrado.")
        return
    deportistas.append({"nombre": nombre, "tipo_doc": tipo_doc, "num_doc": num_doc, "universidad": universidad})
    limpiar([entrada_nombre_dep, combo_tipo_doc, entrada_num_doc, combo_universidad_dep])
    actualizar_listas()

def seleccionar_deportista(evento):
    seleccion = lista_deportistas.curselection()
    if len(seleccion) == 0:
        return
    d = deportistas[seleccion[0]]
    limpiar([entrada_nombre_dep, combo_tipo_doc, entrada_num_doc, combo_universidad_dep])
    entrada_nombre_dep.insert(0, d["nombre"])
    combo_tipo_doc.set(d["tipo_doc"])
    entrada_num_doc.insert(0, d["num_doc"])
    combo_universidad_dep.set(d["universidad"])

def actualizar_deportista():
    seleccion = lista_deportistas.curselection()
    if len(seleccion) == 0:
        messagebox.showerror("Error", "Seleccione un deportista de la lista.")
        return
    i = seleccion[0]
    nombre = entrada_nombre_dep.get().strip()
    tipo_doc = combo_tipo_doc.get().strip()
    num_doc = entrada_num_doc.get().strip()
    universidad = combo_universidad_dep.get().strip()

    if campos_vacios([nombre, tipo_doc, num_doc, universidad]):
        messagebox.showerror("Error", "Todos los campos son obligatorios.")
        return
    if buscar(universidades, "nombre", universidad) == -1:
        messagebox.showerror("Error", "La universidad no existe.")
        return
    if documento_invalido(tipo_doc, num_doc):
        messagebox.showerror("Error", "El número de documento solo puede tener dígitos.")
        return
    existe_doc =buscar(deportistas, "num_doc", num_doc)
    existe_nombre = buscar(deportistas, "nombre", nombre)
    if (existe_doc != -1 and existe_doc != i) or (existe_nombre != -1 and existe_nombre != i):
        messagebox.showerror("Error", "Ya existe otro deportista con esos datos.")
        return

    nombre_viejo = deportistas[i]["nombre"]
    deportistas[i] = {"nombre": nombre, "tipo_doc": tipo_doc, "num_doc": num_doc, "universidad": universidad}
    for fila in inscripciones:
        if fila[0] == nombre_viejo:
            fila[0] = nombre

    limpiar([entrada_nombre_dep, combo_tipo_doc, entrada_num_doc, combo_universidad_dep])
    actualizar_listas()

def eliminar_deportista():
    seleccion = lista_deportistas.curselection()
    if len(seleccion) == 0:
        messagebox.showerror("Error", "Seleccione un deportista de la lista.")
        return
    nombre = deportistas[seleccion[0]]["nombre"]
    for fila in inscripciones:
        if fila[0] == nombre:
            messagebox.showerror("Error", "El deportista tiene inscripciones. Elimínelas primero.")
            return
    deportistas.pop(seleccion[0])
    limpiar([entrada_nombre_dep, combo_tipo_doc, entrada_num_doc, combo_universidad_dep])
    actualizar_listas()

#  PESTAÑA DE DISCIPLINAS
def crear_disciplina():
    nombre = entrada_nombre_dis.get().strip()
    modalidad = combo_modalidad.get().strip()
    if campos_vacios([nombre, modalidad]):
        messagebox.showerror("Error", "Todos los campos son obligatorios.")
        return
    if buscar(disciplinas, "nombre", nombre) != -1:
        messagebox.showerror("Error", "La disciplina ya está registrada.")
        return
    disciplinas.append({"nombre": nombre, "modalidad": modalidad})
    limpiar([entrada_nombre_dis, combo_modalidad])
    actualizar_listas()

def seleccionar_disciplina(evento):

    seleccion = lista_disciplinas.curselection()
    if len(seleccion) == 0:
        return
    d = disciplinas[seleccion[0]]
    limpiar([entrada_nombre_dis, combo_modalidad])
    entrada_nombre_dis.insert(0, d["nombre"])
    combo_modalidad.set(d["modalidad"])

def actualizar_disciplina():
    seleccion = lista_disciplinas.curselection()
    if len(seleccion) == 0:
        messagebox.showerror("Error", "Seleccione una disciplina de la lista.")
        return
    i = seleccion[0]

    nombre = entrada_nombre_dis.get().strip()
    modalidad = combo_modalidad.get().strip()
    if campos_vacios([nombre, modalidad]):
        messagebox.showerror("Error", "Todos los campos son obligatorios.")
        return
    existe = buscar(disciplinas, "nombre", nombre)
    if existe != -1 and existe != i:
        messagebox.showerror("Error", "Ya existe otra disciplina con ese nombre.")
        return
    nombre_viejo = disciplinas[i]["nombre"]
    disciplinas[i] = {"nombre": nombre, "modalidad": modalidad}
    for fila in inscripciones:
        if fila[1] == nombre_viejo:
            fila[1] = nombre
    for fila in resultados:
        if fila[0] == nombre_viejo:
            fila[0] = nombre
    limpiar([entrada_nombre_dis, combo_modalidad])
    actualizar_listas()

def eliminar_disciplina():
    seleccion = lista_disciplinas.curselection()
    if len(seleccion) == 0:
        messagebox.showerror("Error", "Seleccione una disciplina de la lista.")
        return
    nombre = disciplinas[seleccion[0]]["nombre"]
    for fila in inscripciones:
        if fila[1] == nombre:
            messagebox.showerror("Error", "La disciplina tiene inscripciones asociadas.")
            return
    for fila in resultados:
        if fila[0] == nombre:
            messagebox.showerror("Error", "La disciplina tiene resultados asociados.")
            return
    disciplinas.pop(seleccion[0])
    limpiar([entrada_nombre_dis, combo_modalidad])
    actualizar_listas()

#        PESTANA INSCRIPCIONES
filas_visibles = []

def mostrar_inscripciones():
    filtro = combo_filtro_ins.get().strip()
    lineas = []
    filas_visibles.clear()
    for d in disciplinas:

        if filtro != "" and filtro != "Todas" and filtro != d["nombre"]:
            continue
        lineas.append("--- " + d["nombre"] + " ---")
        filas_visibles.append(-1)
        contador = 1
        for i in range(len(inscripciones)):
            if inscripciones[i][1] == d["nombre"]:
                j = buscar(deportistas, "nombre", inscripciones[i][0])
                lineas.append(str(contador) + ". " + inscripciones[i][0] + " | " + deportistas[j]["universidad"])
                filas_visibles.append(i)
                contador = contador + 1
    mostrar(lista_inscripciones, lineas)

def filtrar_inscripciones(evento):

    mostrar_inscripciones()

def inscribir():
    deportista = combo_deportista_ins.get().strip()
    disciplina = combo_disciplina_ins.get().strip()
    if campos_vacios([deportista, disciplina]):
        messagebox.showerror("Error", "Seleccione deportista y disciplina.")
        return
    if buscar(deportistas, "nombre", deportista) == -1 or buscar(disciplinas, "nombre", disciplina) == -1:
        messagebox.showerror("Error", "El deportista o la disciplina no existen.")
        return
    for fila in inscripciones:
        if fila[0] == deportista and fila[1] == disciplina:
            messagebox.showerror("Error", "El deportista ya está inscrito en esa disciplina.")
            return
    inscripciones.append([deportista, disciplina])
    actualizar_listas()

def eliminar_inscripcion():
    seleccion = lista_inscripciones.curselection()
    if len(seleccion) == 0 or filas_visibles[seleccion[0]] == -1:
        messagebox.showerror("Error", "Seleccione una inscripción de la lista.")
        return
    inscripciones.pop(filas_visibles[seleccion[0]])
    actualizar_listas()

#        PESTANA RESULTADOS
filas_resultados = []

def mostrar_resultados():
    lineas = []
    filas_resultados.clear()
    for d in disciplinas:
        for posicion in MEDALLAS:
            for i in range(len(resultados)):
                fila = resultados[i]
                if fila[0] == d["nombre"] and fila[2] == posicion:
                    lineas.append(fila[0] + " | " + fila[1] + " | " + fila[2])
                    filas_resultados.append(i)
    mostrar(lista_resultados, lineas)


def registrar_resultado():

    disciplina = combo_disciplina_res.get().strip()
    universidad = combo_universidad_res.get().strip()
    posicion = combo_posicion.get().strip()

    if campos_vacios([disciplina, universidad, posicion]):
        messagebox.showerror("Error", "Todos los campos son obligatorios.")
        return
    if buscar(disciplinas, "nombre", disciplina) == -1:
        messagebox.showerror("Error", "La disciplina no existe.")
        return
    if buscar(universidades, "nombre", universidad) == -1:
        messagebox.showerror("Error", "La universidad no existe.")
        return
    if posicion not in MEDALLAS:
        messagebox.showerror("Error", "La posición debe ser Oro, Plata o Bronce.")
        return

    for fila in resultados:
        if fila[0] == disciplina and fila[2] == posicion:
            messagebox.showerror("Error", "Ya hay una universidad con " + posicion + " en " + disciplina + ".")
            return
        if fila[0] == disciplina and fila[1] == universidad:
            messagebox.showerror("Error", "La universidad ya tiene un resultado en " + disciplina + ".")
            return

    resultados.append([disciplina, universidad, posicion])
    actualizar_listas()

def eliminar_resultado():
    seleccion = lista_resultados.curselection()
    if len(seleccion) == 0:
        messagebox.showerror("Error", "Seleccione un resultado de la lista.")
        return
    resultados.pop(filas_resultados[seleccion[0]])
    actualizar_listas()

#       PESTANA CONSULTAS
def consultar():
    opcion = combo_consulta.get()
    lineas = []

    if opcion == "Deportistas participantes":
        for d in deportistas:
            i = buscar(universidades, "nombre", d["universidad"])
            lineas.append(d["nombre"] + " | " + d["universidad"] + " | " + universidades[i]["pais"] + " | " + disciplinas_de(d["nombre"]))

    elif opcion == "Medallero por universidad":
        medallero = calcular_medallero()
        for universidad in medallero:
            m = medallero[universidad]
            lineas.append(universidad + " | Oro: " + str(m[0]) + " | Plata: " + str(m[1]) + " | Bronce: " + str(m[2]))

    elif opcion == "Universidad ganadora":
        clasificacion = calcular_clasificacion()
        for i in range(len(clasificacion)):
            lineas.append(str(i + 1) + ". " + clasificacion[i][0] + " | " + str(clasificacion[i][1]) + " puntos")
        ganadoras = universidades_ganadoras(clasificacion)
        if len(ganadoras) == 0:
            lineas.append("No hay universidades registradas")
        elif len(resultados) == 0:
            # Sin medallas todas tendrian 0 puntos: no tiene sentido decir "empate"
            lineas.append("Aún no hay medallas registradas")
        elif len(ganadoras) == 1:
            lineas.append("Universidad ganadora: " + ganadoras[0])
        else:
            lineas.append("Empate entre: " + ", ".join(ganadoras))

    elif opcion == "Estadísticas generales":
        nacionales = 0
        for u in universidades:
            if u["tipo"] == "Nacional":
                nacionales = nacionales + 1
        lineas.append("Universidades: " + str(len(universidades)))
        lineas.append("Nacionales: " + str(nacionales) + " | Internacionales: " + str(len(universidades) - nacionales))
        lineas.append("Deportistas: " + str(len(deportistas)) + " | Disciplinas: " + str(len(disciplinas)))
        lineas.append("Inscripciones: " + str(len(inscripciones)) + " | Medallas: " + str(len(resultados)))

    else:
        messagebox.showerror("Error", "Seleccione una consulta.")
        return

    mostrar(lista_consultas, lineas)

#    MANEJO DE ARCHIVOS (JSON)
def estructura_valida(datos):

    if type(datos) != dict:
        return False
    for seccion in CAMPOS:
        if type(datos.get(seccion)) != list:
            return False
        for registro in datos[seccion]:
            if type(registro) != dict:
                return False
            for campo_registro in CAMPOS[seccion]:
                if type(registro.get(campo_registro)) != str:
                    return False
    for seccion, tamano in [["inscripciones", 2], ["resultados", 3]]:
        if type(datos.get(seccion)) != list:
            return False
        for fila in datos[seccion]:
            if type(fila) != list or len(fila) != tamano:
                return False

    # Las referencias deben existir, si no la interfaz falla al mostrar los datos
    nombres_uni = nombres(datos["universidades"])
    nombres_dep = nombres(datos["deportistas"])
    nombres_dis = nombres(datos["disciplinas"])
    for d in datos["deportistas"]:
        if d["universidad"] not in nombres_uni:
            return False
    for fila in datos["inscripciones"]:
        if fila[0] not in nombres_dep or fila[1] not in nombres_dis:
            return False
    for fila in datos["resultados"]:
        if fila[0] not in nombres_dis or fila[1] not in nombres_uni or fila[2] not in MEDALLAS:
            return False
    return True

def guardar_datos():

    datos = {"universidades": universidades, "deportistas": deportistas,
             "disciplinas": disciplinas, "inscripciones": inscripciones,
             "resultados": resultados}
    if not estructura_valida(datos):
        messagebox.showerror("Error", "Los datos no tienen una estructura válida.")
        return
    try:
        with open(ARCHIVO_DATOS, "w", encoding="utf-8") as archivo:
            json.dump(datos, archivo, ensure_ascii=False, indent=4)
    except (OSError, TypeError) as error:
        messagebox.showerror("Error", "No se pudo guardar el archivo: " + str(error))
        return
    if not exportar_medallero():
        return
    messagebox.showinfo("Guardar datos", "Datos guardados en " + ARCHIVO_DATOS + " y medallero.csv")

def cargar_datos():

    if not os.path.exists(ARCHIVO_DATOS):
        messagebox.showerror("Error", "No existe el archivo " + ARCHIVO_DATOS)
        return
    try:
        with open(ARCHIVO_DATOS, "r", encoding="utf-8") as archivo:
            datos = json.load(archivo)
    except json.JSONDecodeError:
        messagebox.showerror("Error", "El archivo JSON tiene un formato inválido.")
        return
    except (OSError, UnicodeDecodeError) as error:
        messagebox.showerror("Error", "No se pudo leer el archivo: " + str(error))
        return
    if not estructura_valida(datos):
        messagebox.showerror("Error", "El archivo no tiene la estructura esperada.")
        return

    # clear + extend (no "=") para que el resto del programa siga usando las mismas listas
    for lista, seccion in [[universidades, "universidades"], [deportistas, "deportistas"],
                           [disciplinas, "disciplinas"], [inscripciones, "inscripciones"],
                           [resultados, "resultados"]]:
        lista.clear()
        lista.extend(datos[seccion])
    actualizar_listas()
    messagebox.showinfo("Cargar datos", "Datos cargados correctamente.\n"
                        "Universidades: " + str(len(universidades)) + " | Deportistas: " + str(len(deportistas)) + "\n"
                        "Disciplinas: " + str(len(disciplinas)) + " | Inscripciones: " + str(len(inscripciones)) + "\n"
                        "Resultados: " + str(len(resultados)))

def exportar_medallero():

    medallero = calcular_medallero()
    try:
        with open("medallero.csv", "w", newline="", encoding="utf-8-sig") as archivo:
            escritor = csv.writer(archivo)
            escritor.writerow(["Universidad", "Oro", "Plata", "Bronce"])
            for universidad in medallero:
                escritor.writerow([universidad] + medallero[universidad])
    except OSError as error:
        messagebox.showerror("Error", "No se pudo crear medallero.csv: " + str(error))
        return False
    return True

def boton_medallero():

    if exportar_medallero():
        messagebox.showinfo("Medallero", "Archivo medallero.csv generado correctamente.")

#    CONSTRUCCION DE LA VENTANA

def crear_pestana(titulo):

    pestana = ttk.Frame(notebook, padding=10)
    notebook.add(pestana, text=titulo)
    formulario = ttk.Frame(pestana)
    formulario.pack(side="left", fill="y", padx=5)
    ttk.Label(formulario, text=titulo, style="Titulo.TLabel").pack(anchor="w", pady=5)
    listbox = tkinter.Listbox(pestana, width=60, height=18, font=(FUENTE, 10),
                              bg=COLOR_LISTA_FONDO, fg=COLOR_LISTA_TEXTO,
                              selectbackground=COLOR_SELECCION, selectforeground=COLOR_LISTA_TEXTO,
                              exportselection=False)

    listbox.pack(side="right", fill="both", expand=True, padx=5)
    return formulario, listbox


def campo(formulario, texto, valores=None):

    ttk.Label(formulario, text=texto).pack(anchor="w")
    if valores is None:
        widget = ttk.Entry(formulario, width=35)
    else:
        widget = ttk.Combobox(formulario, width=32, values=valores, state="readonly")
    widget.pack(anchor="w", pady=(0, 6))
    return widget


def botones(formulario, lista):

    fila = ttk.Frame(formulario)
    fila.pack(anchor="w", pady=10)
    for texto, funcion in lista:
        ttk.Button(fila, text=texto, command=funcion).pack(side="left", padx=3)



ventana = tkinter.Tk()
ventana.title("Copa Loyola - Sistema de Gestión Deportiva")
ventana.geometry("900x480")

estilo = ttk.Style()
estilo.theme_use("clam")
estilo.configure("TFrame", background=COLOR_FONDO)
estilo.configure("TNotebook", background=COLOR_FONDO)
estilo.configure("TLabel", background=COLOR_FONDO, foreground=COLOR_TEXTO, font=(FUENTE, 10))
estilo.configure("Titulo.TLabel", foreground=COLOR_TITULO, font=(FUENTE, 14, "bold"))
estilo.configure("TButton", background=COLOR_BOTON, foreground=COLOR_BOTON_TEXTO, font=(FUENTE, 10))
estilo.map("TButton", background=[("active", COLOR_BOTON_ACTIVO)])

notebook = ttk.Notebook(ventana)
notebook.pack(fill="both", expand=True)

#        Pestana Universidades
form, lista_universidades = crear_pestana("Universidades")
entrada_nombre_uni = campo(form, "Nombre de la universidad")
entrada_pais = campo(form, "País")
entrada_ciudad = campo(form, "Ciudad")
combo_tipo = campo(form, "Tipo de participación",
                    ["Nacional", "Internacional"]
)
botones(form, [["Crear", crear_universidad],
                ["Actualizar", actualizar_universidad],
                ["Eliminar", eliminar_universidad]]
)
lista_universidades.bind("<<ListboxSelect>>", seleccionar_universidad)
#     Pestana Deportistas
form, lista_deportistas = crear_pestana("Deportistas")
entrada_nombre_dep = campo(form, "Nombre completo")
combo_tipo_doc = campo(form, "Tipo de documento", ["CC", "TI", "CE", "Pasaporte"])
entrada_num_doc = campo(form, "Número de documento")
combo_universidad_dep = campo(form, "Universidad", [])
botones(form, [["Crear", crear_deportista],
                ["Actualizar", actualizar_deportista],
                ["Eliminar", eliminar_deportista]]
)
lista_deportistas.bind("<<ListboxSelect>>", seleccionar_deportista)
#       Pestana Disciplinas
form, lista_disciplinas = crear_pestana("Disciplinas")
entrada_nombre_dis = campo(form, "Nombre de la disciplina")
combo_modalidad = campo(form, "Modalidad", ["Individual", "Por equipos"])
botones(form, [["Crear", crear_disciplina],
                ["Actualizar", actualizar_disciplina],
                ["Eliminar", eliminar_disciplina]]
)
lista_disciplinas.bind("<<ListboxSelect>>", seleccionar_disciplina)
#        Pestana Inscripciones
form, lista_inscripciones = crear_pestana("Inscripciones")
combo_deportista_ins = campo(form, "Seleccionar deportista", [])
combo_disciplina_ins = campo(form, "Seleccionar disciplina", [])
combo_filtro_ins = campo(form, "Filtrar por disciplina", ["Todas"])
combo_filtro_ins.bind("<<ComboboxSelected>>", filtrar_inscripciones)
botones(form, [["Inscribir", inscribir],
                ["Eliminar", eliminar_inscripcion]]
)
#        Pestana Resultados
form, lista_resultados = crear_pestana("Resultados")
combo_disciplina_res = campo(form, "Seleccionar disciplina", [])
combo_universidad_res = campo(form, "Universidad", [])
combo_posicion = campo(form, "Posición obtenida", MEDALLAS)
botones(form, [["Registrar", registrar_resultado],
                ["Eliminar", eliminar_resultado]]
)
#           Pestana Consultas
form, lista_consultas = crear_pestana("Consultas")
combo_consulta = campo(form, "Consulta", ["Deportistas participantes",
                                           "Medallero por universidad",
                                             "Universidad ganadora",
                                               "Estadísticas generales"]
)
botones(form, [["Consultar", consultar]])
ttk.Label(form, text="Archivo: " + ARCHIVO_DATOS).pack(anchor="w")
botones(form, [["Guardar datos (JSON)", guardar_datos],
               ["Cargar datos (JSON)", cargar_datos]])
botones(form, [["Medallero (CSV)", boton_medallero]])

actualizar_listas()
ventana.mainloop()
