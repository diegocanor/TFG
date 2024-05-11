#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from app import app
from flask import render_template, request, url_for, redirect, session, make_response
import json
import os
import sys
import hashlib
import os.path as path
import random
import time
from PIL import Image
import imagehash
import shutil

@app.route('/')
@app.route('/index',methods=['GET','POST'])
def index():
    return render_template('index.html', title = "Inicio")



@app.route('/login', methods=['GET', 'POST'])
def login():
    if 'correo' in request.form:

        dato =[]
        i = 0
        cadena1 = "conductores/" + request.form['correo']
        cadena1 = os.path.join(app.root_path,cadena1)
        cadena2 = "clientes/" + request.form['correo']
        cadena2 = os.path.join(app.root_path,cadena2)
        cadena3 = "admin/" + request.form['correo']
        cadena3 = os.path.join(app.root_path,cadena3)

        if path.exists(cadena1):
            cadena1 = cadena1 + "/datos.dat"
            with open(cadena1) as f:
                for linea in f:
                    dato.append((linea.split(": ")[1]).split('\n')[0])
                    i = i + 1
        elif path.exists(cadena2):
            cadena2 = cadena2 + "/datos.dat"
            with open(cadena2) as f:
                for linea in f:
                    dato.append ((linea.split(": ")[1]).split('\n')[0])
                    i = i + 1
        elif path.exists(cadena3):
            cadena3 = cadena3 + "/datos.dat"
            with open(cadena3) as f:
                for linea in f:
                    dato.append ((linea.split(": ")[1]).split('\n')[0])
                    i = i + 1
        else:
            return render_template('login.html', title = "Sign In", mensaje="No has realizado Login correctamente. Intentalo de nuevo")


        aux2 = hashlib.md5(request.form['contrasenna'].encode())
        aux2 = "" + aux2.hexdigest()
        if request.form['correo'] == dato[1] and aux2 == dato[2]:
            resp = make_response(redirect(url_for('index')))
            resp.set_cookie('usuario',dato[0])
            
            session['usuario'] = dato[0]
            session['correo'] = dato[1]
            session['roll'] = dato[3]
            session.modified=True
            return resp
        else:
            return render_template('login.html', title = "Sign In", mensaje="No has realizado Login correctamente. Intentalo de nuevo")
    else:
        nombre = request.cookies.get('usuario')
        
        session['url_origen']=request.referrer
        session.modified=True
        return render_template('login.html', title = "Login", nombre=nombre)

@app.route('/logout', methods=['GET', 'POST'])
def logout():
    session.modified = True
    session.pop('usuario', None)
    return redirect(url_for('index'))

    
@app.route('/registro-cliente', methods=['GET', 'POST'])
def registro_cliente():

    if 'email' in request.form:

        cadena = "clientes/" + request.form['email']
        cadena = os.path.join(app.root_path,cadena)
        if path.exists(cadena):
            return render_template('registro_cliente.html', title = "Registro", mensaje="Ese correo ya está registrado")
        else:
            os.mkdir(cadena)
            cadena_datos = cadena + "/datos.dat"
            f = open(cadena_datos, "w")
            aux_contrasenna = hashlib.md5(request.form['contrasenna'].encode())
            aux_contrasenna = "" + aux_contrasenna.hexdigest()

            f.write("usuario: " + request.form['nombre'] +" "+ request.form['apellidos'] + "\n" +
                    "correo: " + request.form['email'] + "\n" +
                    "contrasenna: " + aux_contrasenna + "\n" +
                    "roll: " + "cliente" + "\n" +
                    "DNI: " + request.form['dni'] + "\n" +
                    "telefono: " + request.form['telefono'] + "\n"
                    )
            f.close()

            f = open(cadena + "/tarjeta_registro.dat", "w")
            f.write("numeros: "+ request.form['tarjeta'])
            f.close
            
            return redirect(url_for('index'))
    else:
        return render_template('registro_cliente.html', title = "Registrarse")
    

@app.route('/registro-conductor', methods=['GET', 'POST'])
def registro_conductor():

    if 'email' in request.form:

        cadena = "conductores/" + request.form['email']
        cadena = os.path.join(app.root_path,cadena)
        if path.exists(cadena):
            return render_template('registro_conductor.html', title = "Registro", mensaje="Ese correo ya está registrado")
        else:
            carnet_conducir = request.files['carnet_conducir']
            foto_dni = request.files['foto_dni']
            selfie = request.files['selfie']

            if carnet_conducir.filename == '':
                return render_template('registro_conductor.html', title="Registro", mensaje="La foto del carne de conducir debe ser válida")
            if foto_dni.filename == '':
                return render_template('registro_conductor.html', title="Registro", mensaje="La foto del DNI debe ser válida")
            if selfie.filename == '':
                return render_template('registro_conductor.html', title="Registro", mensaje="La foto del selfie debe ser válida")

            try:
                img1 = Image.open(carnet_conducir)
                img2 = Image.open(foto_dni)
                img3 = Image.open(selfie)

                allowed_extensions = ['jpg', 'jpeg', 'png']
                if carnet_conducir.filename.split('.')[-1].lower() not in allowed_extensions:
                    return render_template('registro_conductor.html', title="Registro", mensaje="La foto del carne de conducir debe ser en un formato de tipo imagen")
                if foto_dni.filename.split('.')[-1].lower() not in allowed_extensions:
                    return render_template('registro_conductor.html', title="Registro", mensaje="La foto del DNI debe ser en un formato de tipo imagen")
                if selfie.filename.split('.')[-1].lower() not in allowed_extensions:
                    return render_template('registro_conductor.html', title="Registro", mensaje="La foto de selfie debe ser en un formato de tipo imagen")

                img_hash1 = imagehash.average_hash(img1)
                img_hash2 = imagehash.average_hash(img2)
                img_hash3 = imagehash.average_hash(img3)
                hashes_maliciosos = ['08f702fdcefea3cf', '1b340f2f23fd5f87', '3c0afcabf1a3f7b3']

                if str(img_hash1) in hashes_maliciosos or str(img_hash2) in hashes_maliciosos or str(img_hash3) in hashes_maliciosos:
                    return render_template('registro_conductor.html', title="Registro", mensaje="Error al procesar las fotos")

            except IOError:
                return render_template('registro_conductor.html', title="Registro", mensaje="Error al procesar las fotos")

            os.mkdir(cadena)
            cadena_datos = cadena + "/datos.dat"
            f = open(cadena_datos, "w")
            aux_contrasenna = hashlib.md5(request.form['contrasenna'].encode())
            aux_contrasenna = "" + aux_contrasenna.hexdigest()

            f.write("usuario: " + request.form['nombre'] + " "+ request.form['apellidos'] + "\n" +
                    "correo: " + request.form['email'] + "\n" +
                    "contrasenna: " + aux_contrasenna + "\n" +
                    "roll: " + "conductor" + "\n" +
                    "DNI: " + request.form['dni'] + "\n" +
                    "telefono: " + request.form['telefono'] + "\n" +
                    "IBAN: " + request.form['iban'] + "\n"
                    )
            f.close()

            foto_path1 = os.path.join(cadena, 'carnet_conducir.png')
            img1.save(foto_path1)
            foto_path2 = os.path.join(cadena, 'foto_dni.png')
            img2.save(foto_path2)
            foto_path3 = os.path.join(cadena, 'selfie.png')
            img3.save(foto_path3)

            cadena_historial = cadena + "/historial.json"

            f = open (cadena_historial, "w")

            historial = {}

            f.write(json.dumps(historial))
            return redirect(url_for('index'))
    else:
        return render_template('registro_conductor.html', title = "Registrarse")
    

@app.route('/datos', methods=['GET','POST'])
def informacion():
    datos ={}
    i = 0
    cadena = "clientes/" + session['correo'] + "/datos.dat"
    cadena = os.path.join(app.root_path,cadena)

    with open(cadena, "r") as f:
        for linea in f:
            clave, valor = linea.strip().split(":")
            datos[clave.strip()] = valor.strip()
    
    return render_template('datos_cliente.html', title = "Datos", datos=datos, flag=False)


@app.route('/datos/modificar', methods=['GET','POST'])
def modificar():
    if request.method == 'POST':
        nuevo_telefono = request.form['telefono']
        nuevo_correo = request.form['correo']

        cadena = "clientes/" + session['correo'] + "/datos.dat"
        cadena = os.path.join(app.root_path,cadena)

        datos = {}
        with open(cadena, "r") as archivo:
            for linea in archivo:
                clave, valor = linea.strip().split(":")
                datos[clave.strip()] = valor.strip()
        
        if datos["correo"] == nuevo_correo:
            datos["telefono"] = nuevo_telefono
            with open(cadena, "w") as archivo:
                for clave, valor in datos.items():
                    archivo.write(f"{clave}: {valor}\n")
        else:
            ruta_origen = "clientes/" + datos["correo"]
            ruta_origen = os.path.join(app.root_path,ruta_origen)
            
            ruta_destino = "clientes/" + nuevo_correo
            ruta_destino = os.path.join(app.root_path,ruta_destino)

            if path.exists(ruta_destino):
                return render_template('datos_cliente.html', title = "Datos", datos=datos, mensaje="Ese correo ya está registrado")

            session['correo'] = nuevo_correo
            shutil.copytree(ruta_origen, ruta_destino)
            shutil.rmtree(ruta_origen)
            datos["telefono"] = nuevo_telefono
            datos["correo"] = nuevo_correo
            cadena = "clientes/" + nuevo_correo + "/datos.dat"
            cadena = os.path.join(app.root_path,cadena)
            with open(cadena, "w") as archivo:
                for clave, valor in datos.items():
                    archivo.write(f"{clave}: {valor}\n")

        datos["correo"] = nuevo_correo

        


    return render_template('datos_cliente.html', title = "Datos", datos=datos, flag=False)


@app.route('/inicio-viaje', methods=['GET', 'POST'])
def inicio_viaje():

    if request.method == 'POST':
        cadena = os.path.join(app.root_path,"viajes/")
        cadena_datos = cadena + "datos.dat"
        
        usuario = session['correo']
        origen = request.form['origen']
        destino = request.form['destino']
        vehiculo = request.form['vehiculo']

        with open(cadena_datos, 'a') as f:
            f.write(f"Usuario: {usuario}\n")
            f.write(f"Conductor: \n")
            f.write(f"Origen: {origen}\n")
            f.write(f"Destino: {destino}\n")
            f.write(f"Vehículo: {vehiculo}\n")
            f.write(f"------------------------\n")

        return render_template('inicio_viaje.html', title='Viaje', mensaje="Viaje registrado correctamente")

    return render_template('inicio_viaje.html', title='Inicio de Viaje')


@app.route('/envio-paquete', methods=['GET', 'POST'])
def envio_paquete():

    if request.method == 'POST':
        cadena = os.path.join(app.root_path, "paquetes/")
        cadena_datos = cadena + "datos.dat"

        usuario = session['correo']
        peso = request.form['peso']
        tamano = request.form['tamano']
        forma = request.form['forma']
        origen = request.form['origen']
        destino = request.form['destino']
        fecha_hora = request.form['fecha_hora']
        descripcion = request.form['descripcion']

        with open(cadena_datos, 'a') as f:
            f.write(f"Usuario: {usuario}\n")
            f.write(f"Conductor: \n")
            f.write(f"Peso: {peso} kg\n")
            f.write(f"Tamaño: {tamano} m²\n")
            f.write(f"Forma: {forma}\n")
            f.write(f"Origen: {origen}\n")
            f.write(f"Destino: {destino}\n")
            f.write(f"Fecha y hora de recogida: {fecha_hora}\n")
            f.write(f"Descripción: {descripcion}\n")
            f.write("------------------------\n")

        return render_template('envio_paquete.html', title='Envío de Paquete', mensaje="Paquete enviado correctamente")

    return render_template('envio_paquete.html', title='Envío de Paquete')

@app.route('/admin/ver-usuarios')
def admin_ver_usuarios():

    if 'roll' in session and session['roll'] == 'admin':
        clientes = os.listdir(os.path.join(app.root_path, 'clientes'))
        conductores = os.listdir(os.path.join(app.root_path, 'conductores'))
        return render_template('admin_ver_usuarios.html', clientes=clientes, conductores=conductores)
    
    return redirect(url_for('login'))

@app.route('/admin/ver-viajes')
def admin_ver_viajes():
    if 'roll' in session and session['roll'] == 'admin':
        viajes_path = os.path.join(app.root_path, 'viajes', 'datos.dat')
        viajes = []
        if os.path.exists(viajes_path):
            with open(viajes_path, 'r') as file:
                content = file.read()
            viajes_data = content.strip().split("------------------------")
            for viaje_data in viajes_data:
                if viaje_data.strip():
                    viaje_info = {}
                    lines = viaje_data.strip().split("\n")
                    for line in lines:
                        if line.strip():
                            key, value = line.split(':', 1)
                            viaje_info[key.strip()] = value.strip()
                    viajes.append(viaje_info)
        return render_template('admin_ver_viajes.html', viajes=viajes)
    return redirect(url_for('login'))


@app.route('/admin/ver-paquetes')
def admin_ver_paquetes():
    if 'roll' in session and session['roll'] == 'admin':
        paquetes_path = os.path.join(app.root_path, 'paquetes', 'datos.dat')
        paquetes = []
        if os.path.exists(paquetes_path):
            with open(paquetes_path, 'r') as file:
                content = file.read()
            paquetes_data = content.strip().split("------------------------")
            for paquete_data in paquetes_data:
                if paquete_data.strip():
                    paquete_info = {}
                    lines = paquete_data.strip().split("\n")
                    for line in lines:
                        if line.strip():
                            key, value = line.split(':', 1)
                            paquete_info[key.strip()] = value.strip()
                    paquetes.append(paquete_info)
        return render_template('admin_ver_paquetes.html', paquetes=paquetes)
    return redirect(url_for('login'))



@app.route('/admin/editar-usuario/<tipo>/<correo>', methods=['GET', 'POST'])
def admin_edit_user(tipo, correo):

    if 'roll' in session and session['roll'] == 'admin':
        user_path = os.path.join(app.root_path, tipo, correo, 'datos.dat')
        if request.method == 'POST':
            with open(user_path, 'w') as f:
                f.write(f"usuario: {request.form['nombre']}\n")
                f.write(f"correo: {correo}\n")
                f.write(f"contrasenna: {hashlib.md5(request.form['contrasenna'].encode()).hexdigest()}\n")
                f.write(f"roll: {request.form['roll']}\n")
                f.write(f"DNI: {request.form['dni']}\n")
                f.write(f"telefono: {request.form['telefono']}\n")
            
            return redirect(url_for('admin_ver_usuarios'))
        
        else:
            with open(user_path, 'r') as f:
                datos = {line.split(': ')[0]: line.split(': ')[1].strip() for line in f}
            
            return render_template('admin_edit_user.html', datos=datos, tipo=tipo, correo=correo)
    
    return redirect(url_for('login'))


@app.route('/admin/eliminar-usuario/<tipo>/<correo>', methods=['GET', 'POST'])
def admin_delete_user(tipo, correo):
    
    if 'roll' in session and session['roll'] == 'admin':
        user_path = os.path.join(app.root_path, tipo, correo)
        shutil.rmtree(user_path)
        
        return redirect(url_for('admin_ver_usuarios'))
    
    return redirect(url_for('login'))