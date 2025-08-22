from flask import render_template, redirect, request, jsonify, send_file
from flask import current_app
from .services.commissions import report_act as ra
from .services.commissions import report_rec as rr
from .services.commissions import clean_folders as clean
import polars as pl
import pandas as pd
import os

def init_app(app):

    @app.route("/")
    def home():
        return redirect("/inicio")

    @app.route("/inicio")
    def inicio():
        return render_template('inicio.html')

    @app.route("/pruebas")
    def pruebas():
        return render_template('pruebas.html')

    @app.route("/comisiones/")
    def comisiones():
        return render_template('commisions/comisiones.html')
    
    @app.errorhandler(404)
    def page_not_found(e):
        return render_template('error_404.html'), 404

    @app.route('/commissions', methods = ['POST'])
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
                    csv_limpio=csv_limpio.height
                )
                
                


            
        
    @app.route('/descargar/<archivo>')
    def descargar(archivo):
        if os.environ.get("RAILWAY_ENVIRONMENT"):
            ruta_archivo = os.path.join("/tmp", archivo)
        else:
            ruta_archivo = os.path.join("static", "downloads", archivo)

        print(f"[DEBUG] Intentando descargar: {ruta_archivo}")

        return send_file(ruta_archivo, as_attachment=True)