from flask import render_template, redirect, request, jsonify, send_file, flash, url_for
from flask import current_app
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from datetime import datetime, timedelta
from .services.commissions import report_act as ra
from .services.commissions import report_rec as rr
from .services.commissions import clean_folders as clean
from .services.portOuts import portouts as bp
from .models.ModelsContracargos import ModelContracargo
from .models.entities.contracargos import Contracargo
from .models.ModelsUsers import ModelUser
from . import db
import polars as pl
import pandas as pd
import os

def init_app(app):

    @app.route("/")
    def home():
        return render_template('landing.html')

    @app.route("/inicio")
    @login_required
    def inicio():
        return render_template('inicio.html')

    @app.route("/pruebas")
    @login_required
    def pruebas():
        return render_template('pruebas.html', active_page="pruebas")

    @app.route("/comisiones/")
    @login_required
    def comisiones():
        return render_template('commisions/comisiones.html', active_page="comisiones")

    @app.route("/portouts/")
    @login_required
    def portouts():
        mvnos = bp.lista_mvnos()
        #acomodar nombre de carpeta
        return render_template('portOuts/portouts.html', active_page="portouts", mvnos=mvnos)
    
    
    @app.errorhandler(404)
    def page_not_found(e):
        return render_template('error_404.html'), 404
    
    @app.errorhandler(401)
    def unauthorized(e):
        return render_template('auth/login.html'), 401
    
    @app.route("/contracargos/")
    @login_required
    def list_contracargos():
        page = request.args.get("page", 1, type=int)  # número de página
        #search = request.args.get("search", None)     # búsqueda por nombre
        #fecha_desde = request.args.get("fecha_desde")
        #fecha_hasta = request.args.get("fecha_hasta")

        per_page = 5  # cuántos por página

        try:
            """if search: 
                
                pagination = ModelContracargo.search_contracargos_by_name(search, fecha_desde, fecha_hasta, page, per_page)
                

                print(f"Busqueda: {search}, Fecha desde: {fecha_desde}, Fecha hasta: {fecha_hasta}")

            elif fecha_desde and fecha_hasta:
                # ✅ Convertir fechas si existen
                fecha_desde_dt = datetime.strptime(fecha_desde, "%Y-%m-%d") if fecha_desde else None
                fecha_hasta_dt = datetime.strptime(fecha_hasta, "%Y-%m-%d") if fecha_hasta else None
                
                pagination = ModelContracargo.search_contracargos_by_date(fecha_desde_dt, fecha_hasta_dt, page, per_page)
                print(f"Búsqueda por fecha: Desde {fecha_desde} hasta {fecha_hasta}")
                        
            else:"""
            pagination = ModelContracargo.get_all_contracargos(page, per_page)

            contracargos = pagination.items  
            total_pages = pagination.pages  

            return render_template(
                "contracargos/contracargos.html",
                active_page="contracargos",
                contracargos=contracargos,
                page=page,
                total_pages=total_pages,
                #search=search
            )

        except Exception as e:
            print("Error en list_contracargos:", str(e))
            return render_template(
                "contracargos/contracargos.html",
                active_page="contracargos",
                contracargos=[],
                page=1,
                total_pages=1,
                search=None
            )
        
    @app.route("/contracargos/add", methods=["GET", "POST"])
    @login_required
    def add_contracargo():
        if request.method == "POST":
            print("POST request to /contracargos/add")
            print("Form data received:", request.form.get("name"), request.form.get("email"), request.form.get("msisdn"), request.form.get("monto"), request.form.get("marca"), request.form.get("ord_pay"), request.form.get("paid"), request.form.get("descripcion"))

            name = request.form.get("name")
            email = request.form.get("email")
            msisdn = request.form.get("msisdn")
            monto = request.form.get("monto")
            marca = request.form.get("marca")
            ord_pay = request.form.get("ord_pay")
            paid_str = request.form.get("paid")
            descripcion = request.form.get("descripcion")

            #obtener la fecha actual
            date = datetime.now().strftime('%Y-%m-%d') 

            if paid_str == "yes":
                paid = True
            else:
                paid = False

            nuevo = Contracargo(
                name=name,
                msisdn=msisdn,
                ord_pay=ord_pay,
                email=email,
                monto=monto,
                marca=marca,
                paid= paid,
                date_inserted=date,
                descripcion=descripcion
            )

            try:
                ModelContracargo.add_contracargo(nuevo)
                print("Contracargo agregado exitosamente")
                flash("Contracargo agregado con éxito", "success")
                return redirect(url_for("list_contracargos"))
            except Exception as e:
                print("Error al agregar contracargo:", str(e))
                flash(f"Error: {str(e)}", "danger")
        else:
            print("GET request to /contracargos/add")

        return render_template("contracargos/add_contracargo.html", active_page="contracargos",)
    
    @app.route("/contracargos/edit/<int:contracargo_id>", methods=["GET", "POST"])
    @login_required
    def edit_contracargo(contracargo_id):
        contracargo = Contracargo.query.get_or_404(contracargo_id)
        if request.method == "POST":
            ord_pay = request.form.get("ord_pay")
            paid = request.form.get("paid")
            descripcion = request.form.get("comentario")

            if paid == "yes":
                paid = True
            else:
                paid = False

            try:
                ModelContracargo.edit_contracargo(contracargo_id, ord_pay, paid, descripcion)
                flash("Contracargo editado con éxito", "success")
                return redirect(url_for("list_contracargos"))
            except Exception as e:
                flash(f"Error: {str(e)}", "danger")

        return render_template("contracargos/edit_contracargo.html", contracargo=contracargo, active_page="contracargos",)
    
    @app.route('/delete_contracargo/<int:contracargo_id>', methods = ['GET', 'POST'])
    def delete_contracargo(contracargo_id):
        # Obtén la clave ingresada por el usuario
        entered_password = request.form.get('password')

        if entered_password == os.getenv("SECRET_DELETE_KEY"):
            # Elimina el contracargo si la clave es correcta
            ModelContracargo.delete_contracargo(contracargo_id)
            flash("El registro se eliminó correctamente.", "success")
        else:
            flash("Clave incorrecta. No se pudo eliminar el registro.", "danger")

        return redirect(url_for('list_contracargos'))
    
    @app.route('/search', methods=["GET", "POST"])
    @login_required
    def search_contracargo():
        print("POST request to /search")
        
        busqueda = request.args.get('search', '').strip()
        fecha_desde = request.args.get('fecha_desde')
        fecha_hasta = request.args.get('fecha_hasta')

        print(f"Busqueda: {busqueda}, Fecha desde: {fecha_desde}, Fecha hasta: {fecha_hasta}")

        page = int(request.args.get('page', 1))
        per_page = 5

        # ✅ Convertir fechas si existen
        fecha_desde_dt = datetime.strptime(fecha_desde, "%Y-%m-%d") if fecha_desde else None
        fecha_hasta_dt = datetime.strptime(fecha_hasta, "%Y-%m-%d") if fecha_hasta else None

        # 🔹 Llamamos siempre a la función unificada
        pagination = ModelContracargo.search_contracargos(busqueda, fecha_desde_dt, fecha_hasta_dt, page, per_page)

        contracargos = pagination.items
        total_pages = pagination.pages

        return render_template(
            "contracargos/contracargos.html",
            active_page="contracargos",
            contracargos=contracargos,
            page=page,
            total_pages=total_pages,
            search=busqueda
        )




    @app.route('/commissions', methods = ['POST'])
    @login_required
    def form_comisiones():
        if request.method == 'POST':

            UPLOAD_FOLDER = current_app.config['UPLOAD_FOLDER']

            # Obtener archivos
            csv_finanzas = request.files['file_csv']
            xlsx_general = request.files['file_xlsx']

            # Obtener datos del formulario
            comision_sales = request.form.get('comision-sales')
            proceso = request.form.get('proceso')
            porcentaje = request.form.get('comision')
            fecha = request.form['fecha']

            print(f"Comision Sales: {comision_sales}, Proceso: {proceso}, Porcentaje: {porcentaje}, Fecha: {fecha}")

            print(f"carpeta:  {UPLOAD_FOLDER}")

            path_1 = os.path.join(UPLOAD_FOLDER, csv_finanzas.filename)
            path_2 = os.path.join(UPLOAD_FOLDER, xlsx_general.filename)

            csv_finanzas.save(path_1)
            xlsx_general.save(path_2)

            
            # Leer archivos con polars
            csv = pl.read_csv(path_1)
            xlsx = pl.read_excel(path_2)

            # verificar la marca del archivo de finanzas
            valor = csv.select(pl.col("mvno_name").unique()).to_series().to_list()
            print(f"Marca del archivo de finanzas: {valor[0]}.")

            marca = valor[0]

            clean.limpiar_storage()
            clean.limpiar_downloads()

            if proceso == "activacion":

                
                if marca == "Sigma Móvil ":
                    marca = "Sigma MÃ³vil "
                    print(f"Entro marca sigma")
                elif marca == "Gou! Móvil":
                    marca = "Gou! MÃ³vil"
                elif marca == "Hey Móvil":
                    marca = "Hey MÃ³vil"
                

                # Procesar los archivos
                duplicados, csv_limpio = ra.limpiar_duplicados(csv)

                #obtener los números duplicados
                duplicados_list = duplicados.select("msisdn").to_series().to_list()

                # Mostrar activaciones de la marca elegida
                act_general = (
                            xlsx.filter(pl.col("mvno_name") == marca)
                            .select(pl.count())
                            .item()
                        )

                csv_procesado, precios_iguales = ra.procesar_comisiones(csv_limpio, comision_sales, porcentaje, fecha)
                print(csv_procesado)
                df_pandas = csv_procesado.to_pandas()

                # Separar totales
                df_sin_total = df_pandas[df_pandas['mvno_package_name'] != 'TOTAL'].sort_values(by='date')
                fila_total = df_pandas[df_pandas['mvno_package_name'] == 'TOTAL']

                # Concatenar ordenados
                df_pandas = pd.concat([df_sin_total, fila_total], ignore_index=True)


                nombre_archivo = ra.estilos_excel(df_pandas, marca, precios_iguales, fecha)

                print(f"Archivo generado: {nombre_archivo}")

                return jsonify(
                csv_finanzas=csv_finanzas.filename,
                xlsx_general=xlsx_general.filename,
                marca=marca,
                comision_sales=comision_sales,
                proceso=proceso,
                porcentaje=porcentaje,
                fecha=fecha,
                num_duplicados=duplicados.height,
                csv_limpio=csv_limpio.height,
                total_general=act_general,
                lista_duplicados=duplicados_list,
                archivo_generado=nombre_archivo,
                )

            elif proceso == "recarga":

                print("Entrando al proceso de recarga")
                print(f"Marca del archivo de finanzas: {marca}!")

                if marca == "Sigma Móvil ":
                    marca = "Sigma MÃ³vil "
                    print(f"Entro marca sigma")
                elif marca == "Gou! Móvil":
                    marca = "Gou! MÃ³vil"
                elif marca == "Hey Móvil":
                    marca = "Hey MÃ³vil"

                # Mostrar recargas de la marca elegida
                rec_general = (
                            xlsx.filter(pl.col("name") == marca)
                            .select(pl.count())
                            .item()
                        )
                print(f"Marca del archivo de finanzas: {rec_general}+")

                # Procesar los archivos
                resultados = rr.limpiar_archivo_polars(csv, xlsx)
                csv_limpio = resultados['df1_limpio']
                total_df1 = resultados['total_df1']
                total_df2 = rec_general
                solo_en_df1 = resultados['solo_en_df1']
                solo_en_df2 = resultados['solo_en_df2']
                msisdn_eliminados = resultados['msisdn_eliminados']
                print(f"Total después de limpieza: {total_df1}")
                print(f"Números eliminados de DataFrame 1 (por empezar con '1'): {msisdn_eliminados}")
                print(f"Números únicos en DataFrame 1: {len(solo_en_df1)}")
                print(f"Números únicos en DataFrame 2: {len(solo_en_df2)}")

                csv_procesado, precios_iguales = rr.procesar_comisiones(csv_limpio, comision_sales, porcentaje, fecha)
                df_pandas = csv_procesado.to_pandas()

                # Separar totales
                df_sin_total = df_pandas[df_pandas['mvno_package_name'] != 'TOTAL'].sort_values(by='date')
                fila_total = df_pandas[df_pandas['mvno_package_name'] == 'TOTAL']

                # Concatenar ordenados
                df_pandas = pd.concat([df_sin_total, fila_total], ignore_index=True)

                nombre_archivo = rr.estilos_excel(df_pandas, marca, precios_iguales, fecha)

                return jsonify(
                    csv_finanzas=csv_finanzas.filename,
                    xlsx_general=xlsx_general.filename,
                    marca=marca,
                    comision_sales=comision_sales,
                    proceso=proceso,
                    porcentaje=porcentaje,
                    fecha=fecha,
                    total_df1=total_df1,
                    total_df2=total_df2,
                    solo_en_df1=list(solo_en_df1),
                    solo_en_df2=list(solo_en_df2),
                    msisdn_eliminados=msisdn_eliminados,
                    csv_limpio=csv_limpio.height,
                    archivo_generado=nombre_archivo
                )
                
    @app.route('/descargar/<archivo>')
    @login_required
    def descargar(archivo):
        if os.environ.get("RAILWAY_ENVIRONMENT"):
            ruta_archivo = os.path.join("/tmp", archivo)
        else:
            ruta_archivo = os.path.join("static", "downloads", archivo)

        print(f"[DEBUG] Intentando descargar: {ruta_archivo}")

        return send_file(ruta_archivo, as_attachment=True)

    
    
    @app.route('/form_portouts', methods=['POST'])
    @login_required
    def form_portouts():

        if request.method == 'POST':
            mvno = request.form.get('mvno')
            fecha_desde = request.form.get('fecha_desde')
            fecha_hasta = request.form.get('fecha_hasta')
            
            # Obtener lista de MVNOs para el dropdown
            mvnos = bp.lista_mvnos()

            print(f"Búsqueda: MVNO={mvno}, Desde={fecha_desde}, Hasta={fecha_hasta}")
            
            # Obtener resultados filtrados
            resultados = bp.buscar_portouts(mvno, fecha_desde, fecha_hasta)

            return render_template('portOuts/portouts.html', 
                                   active_page="portouts", 
                                   mvnos=mvnos, 
                                   resultados=resultados,
                                   selected_mvno=mvno,
                                   selected_fecha_desde=fecha_desde,
                                   selected_fecha_hasta=fecha_hasta)

    @app.route('/download_portouts', methods=['POST'])
    @login_required
    def download_portouts():
        mvno = request.form.get('mvno')
        fecha_desde = request.form.get('fecha_desde')
        fecha_hasta = request.form.get('fecha_hasta')

        # 1. Limpiar carpeta de descargas
        try:
           clean.limpiar_downloads()
        except Exception as e:
           print(f"Error limpiando downloads: {e}")

        # 2. Obtener datos
        resultados = bp.buscar_portouts(mvno, fecha_desde, fecha_hasta)
        
        if not resultados:
            flash("No hay datos para descargar con los filtros seleccionados.", "warning")
            return redirect(url_for('portouts'))

        # 3. Generar Excel
        DOWNLOAD_FOLDER = current_app.config['DOWNLOAD_FOLDER']
        filename = bp.generar_excel(resultados, DOWNLOAD_FOLDER)

        if filename:
             return redirect(url_for('descargar', archivo=filename))
        else:
             flash("Error al generar el archivo Excel.", "danger")
             return redirect(url_for('portouts'))

    @app.route("/configuracion")
    @login_required
    def configuracion():
        return render_template('configuracion.html', active_page="configuracion")

    @app.route("/configuracion/update", methods=["POST"])
    @login_required
    def update_profile():
        fullname = request.form.get("fullname")
        password = request.form.get("password")
        
        try:
            # Si el password está vacío, enviamos None para que no se actualice
            if not password or password.strip() == "":
                password = None
            
            success = ModelUser.update_user(current_user.id, fullname, password)
            
            if success:
                flash("Perfil actualizado correctamente.", "success")
            else:
                flash("No se pudo actualizar el perfil.", "danger")
                
        except Exception as e:
            flash(f"Error al actualizar: {str(e)}", "danger")
            
        return redirect(url_for('configuracion'))