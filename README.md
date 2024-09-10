
# Proyecto Revisor de Energía en el Proceso RCUT

El actual proyecto tiene como objetivo, automatizar diversos proceso dentro del departamento de transferencias de potencia y cargos de transmisión, específicamente en el proces de repartición de cargos únicos de transmisión. A continuación, se indicarán los códigos que se encuentran en el repositorio y su utilidad.

1- Revisor_Planillas.py: El código crea una base de datos mensual de los siguientes temas relacionados al envío de la recaudación por parte de los coordinados: 
- "Clientes_": Contiene el registro de los clientes informados por los coordinados.
- "Clientes Nuevos_": Contiene el registro de los nuevos clientes informados por los coordinados (clientes que noe están en el balance de energía).
- "Formularios Clientes Regulados_": Contiene la información de la energía de la hoja "Formulario de Clientes Regulados" de la planilla de recaudación CUT de las empresas que informan clientes regulados. 
- "Observaciones Clientes Libres_": Registra las observaciones que se han anotado por parte de los coordinados en la hoja "Formulario de Clientes Libres" de la planilla de recaudación CUT.
- "Observaciones Clientes Regulados_": Registra las observaciones que se han anotado por parte de los coordinados en la hoja "Formulario de Clientes Regulados" de la planilla de recaudación CUT.
- "Revisor Clientes Libres_": Registra diferencias de energía que se presentan en la hoja "Formulario de Clientes Libres" de la planilla de recaudación CUT.
- "Revisor Clientes Regulados_": en la hoja "Formulario de Clientes Regulados" de la planilla de recaudación CUT

2 - recaudaciones_historicas.py: El código concatena las bases de datos creadas en Revisor_Planillas.py y posteriormente actualiza elregistro histórico.

3 - creador_listado_clientes_energia.py: El código crea el registro de clientes que están registrados en el balance de energía, además de registrar cambios de empresas, nuevas incorporaciones y empresas eliminadas.

4 - retiros_historicos.py:  El código concatena las bases de datos creadas en creador_listado_clientes_energia.py y posteriormente actualiza elregistro histórico. 

5 - comparador_recaudacion_y_energia_clientes_libres.py: Compara la energía de clientes libres facturadas (informadas por los coordinados) y el balance de energía y crea una base de datos a partir de ella.

6 - comparador_recaudacion_y_energia_clientes_regulados.py: Compara la energía de clientes regulados facturadas (informadas por los coordinados) y el balance de energía y crea una base de datos a partir de ella.

7 - comparador_cliente_individualizado: Obtiene un registro, a partir de la planilla "Revisores RCUT" del departamento, para observar los contratos que están pronto a caducar.

8 - comparador_cliente_sistemas: Obtiene un registro, a partir de la planilla "Revisores RCUT" del departamento, para observar las diferencias de sistemas y nivel de tensión que se han producido entre lo informado y lo presente en el balance de energía.

9 - funciones.py: Contiene las funciones que se utilizan en los diferentes códigos.

10 - visualizador.py: Contiene los gráficos y tablas que se obtienen a partir de los códigos de comparación (los cuales se cargan desde un registro histórico). Se utiliza la librería dash de python para visualizar.

11 - style.css: Contiene el diseño de las clases utilizadas en el código visualizador.py

12 - entrada_datos_gui_clientes: Interfaz del proyecto con tkinter.

13 - main.py: Conecta los códigos entre sí y contiene una interfaz para seleccionar que tarea se requiere realizar.

14 - README.md: Explicación general del proyecto. 

## Configuración del entorno de desarrollo

Este proyecto utiliza Python 3.9.13 Asegúrate de tenerlo instalado en tu sistema.

1. Clona el repositorio:
    ```
    git clone https://github.com/usuario/mi-proyecto.git
    cd mi-proyecto
    ```

2. Crea un entorno virtual en la carpeta del proyecto (En caso de no existir):
    ```
    python3.9 -m venv venv
    ```

3. Activa el entorno virtual:
    - En Windows:
        ```
        venv\Scripts\activate
        ```
    - En Unix o MacOS:
        ```
        source venv/bin/activate
        ```

4. Instala las dependencias del proyecto:
    ```
    pip install -r requirements.txt

5. En caso de problemas con la instalación con alguna librería, usar el siguiente código (reemplazar pandas con la librería rerquerida con la versión específicada):
    ```
    pip install pandas==1.4.4 --trusted-host pypi.org --trusted-host files.pythonhosted.org mysql-connector-python

  Posteriormente se debe comentar la librería ya instalada con el código anterior con pip install -r requirements.txt

  En ocasiones, también hay problemas con las versiones de ciertas librerías por lo que se recomienda descargar pandas como: 
    ```
    pip install pandas --trusted-host pypi.org --trusted-host files.pythonhosted.org mysql-connector-python

  Posteriormente, se debe descarga la versión de numpy asociada, la cual puede ser la 1.24.3 como: 
    ```
    pip install numpy=1.24.3 --trusted-host pypi.org --trusted-host files.pythonhosted.org mysql-connector-python

      

  
