El actual Proyecto tiene como objetivo, automatizar diversos proceso dentro del departamento de transferencias de potencia y cargos de transmisión. A continuación, se indicarán los códigos que se pencuentran en el repositorio y su utilidad.

1- Revisor_Planillas.py: El código crea una base de datos mensual de los siguientes temas relacionados al envío de la recaudación por parte de los coordinados: 
- "Clientes_": Contiene el registro de los clientes informados por los coordinados.
- "Clientes Nuevos_": Contiene el registro de los nuevos clientes informados por los coordinados (clientes que noe están en el balance de energía).
- "Formularios Clientes Regulados_": Contiene la información de la energía de la hoja "Formulario de Clientes Regulados" de la planilla de recaudación CUT de las empresas que informan clientes regulados. 
- "Observaciones Clientes Libres_": Registra las observaciones que se han anotado por parte de los coordinados en la hoja "Formulario de Clientes Libres" de la planilla de recaudación CUT.
- "Observaciones Clientes Regulados_": Registra las observaciones que se han anotado por parte de los coordinados en la hoja "Formulario de Clientes Regulados" de la planilla de recaudación CUT.
- "Revisor Clientes Libres_": Registra diferencias de energía que se presentan en la hoja "Formulario de Clientes Libres" de la planilla de recaudación CUT.
- "Revisor Clientes Regulados_": en la hoja "Formulario de Clientes Regulados" de la planilla de recaudación CUT

2- recaudaciones_historicas.py: El código concatena las bases de datos creadas en Revisor_Planillas.py y posteriormente actualiza elregistro histórico.

3- creador_listado_clientes_energia.py: El código crea el registro de clientes que están registrados en el balance de energía, además de registrar cambios de empresas, nuevas incorporaciones y empresas eliminadas.

4- retiros_historicos.py:  El código concatena las bases de datos creadas en creador_listado_clientes_energia.py y posteriormente actualiza elregistro histórico. 

5- comparador_recaudacion_y_energia_clientes_libres.py: Compara la energía de clientes libres facturadas (informadas por los coordinados) y el balance de energía y crea una base de datos a partir de ella.

6- comparador_recaudacion_y_energia_clientes_regulados.py: Compara la energía de clientes regulados facturadas (informadas por los coordinados) y el balance de energía y crea una base de datos a partir de ella.

7- comparador_cliente_individualizado: Obtiene un registro, a partir de la planilla "Revisores RCUT" del departamento, para observar los contratos que están pronto a caducar.

8- comparador_cliente_sistemas: Obtiene un registro, a partir de la planilla "Revisores RCUT" del departamento, para observar las diferencias de sistemas y nivel de tensión que se han producido entre lo informa.

