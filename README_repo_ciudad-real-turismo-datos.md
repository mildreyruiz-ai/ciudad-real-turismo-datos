# Turismo hotelero en Ciudad Real — proyecto de análisis de datos

Análisis de 27 años de datos oficiales del INE sobre viajeros y pernoctaciones en hoteles de la provincia de **Ciudad Real**, comparados con Castilla-La Mancha y España.

> *Proyecto de análisis de datos con datos públicos abiertos: limpieza con Python, consultas SQL, libro de Excel con fórmulas, modelo y medidas DAX para Power BI, y una página web con las conclusiones.*

**Página con el análisis:** https://mildreyruiz-ai.github.io/ciudad-real-turismo-datos/web/

## Preguntas que responde
1. ¿Cómo ha evolucionado el turismo hotelero de la provincia desde 1999?
2. ¿Cuánto tardó en recuperarse del COVID, y cómo se compara con España y Castilla-La Mancha?
3. ¿En qué meses viene la gente? ¿Qué peso tiene el turismo extranjero?
4. ¿Qué posición ocupa Ciudad Real entre las provincias de la región y de España?

## Hallazgos principales
- **2025: 451.302 viajeros**, el mejor año desde 2007 y un 4,5 % por encima de 2019. Agosto de 2025 es el récord mensual de la serie (46.419).
- **Se recuperó antes que España** (98 % del nivel de 2019 en 2022, frente a 93 %), pero **creció menos después**: +4,5 % en 2019-2025 frente a +8,8 % de España.
- **Temporada larga**: de abril a octubre cada mes pesa entre el 9 % y el 10 % del año; enero es el más flojo (5,3 %).
- **Puesto 42 de 50 provincias** en viajeros y 41 en estancia media (2025). Segunda de Castilla-La Mancha en viajeros; Albacete la supera en noches por viajero (2,06 frente a 1,71).
- **Señal de alerta**: de enero a agosto de 2026 los viajeros bajan un 3,5 % frente al mismo periodo de 2025.

## Datos
Fuente: INE, [Viajeros y pernoctaciones por comunidades autónomas y provincias, EOH (tabla 67190)](https://datos.gob.es/es/catalogo/ea0042823-viajeros-y-pernoctaciones-por-comunidades-autonomas-y-provincias-eoh-identificador-api-67190). Mensual, enero de 1999 a agosto de 2026, 50 provincias, 19 comunidades/ciudades autónomas y total nacional; con desglose residentes en España / en el extranjero. El INE es la fuente; este repositorio contiene una versión limpia (`data/eoh_limpio.csv`).

Alcance: solo **establecimientos hoteleros** (no apartamentos, alojamientos rurales ni vivienda turística). 2026 llega hasta agosto, así que las comparaciones con 2026 usan enero-agosto de todos los años.

## Estructura
```
python/01_limpieza.py   limpieza del CSV bruto y carga en SQLite
python/02_analisis.py   ejecuta las consultas y genera resultados.json
python/03_excel.py      genera el libro de Excel con fórmulas
sql/consultas.sql       9 consultas documentadas (CTE, funciones de ventana, JOIN, CASE)
data/eoh_limpio.csv     datos limpios (69.720 filas)
data/resultados.json    resultados que alimentan la página web
turismo_ciudad_real.xlsx  Excel: SUMIFS, INDEX/MATCH, lista desplegable, formato condicional, gráficos
powerbi/                informe .pbix, PDF y guía con medidas DAX
web/index.html          página con el análisis (un solo archivo)
```

## Cómo reproducirlo
```
pip install pandas openpyxl
python python/01_limpieza.py datos_ine_bruto.csv data/eoh_limpio.csv data/eoh.db
python python/02_analisis.py data/eoh.db data/resultados.json
python python/03_excel.py data/eoh.db turismo_ciudad_real.xlsx
```
(`datos_ine_bruto.csv` es la descarga original de la tabla 67190 del INE, CSV separado por «;».)

## Limpieza y control de calidad
- Los valores vienen con punto de miles (`14.227.157`) y se convierten a número.
- Los códigos numéricos de provincias y comunidades (`13 Ciudad Real`) se eliminan.
- Se separan ámbito (nacional, comunidad, provincia) y residencia (total, España, extranjero).
- 43 valores no publicados (Ceuta, Melilla y Castilla y León en mayo-junio de 2020) se dejan vacíos, no se inventan. Ciudad Real tiene la serie completa (332 meses).
- Los resultados de SQL y los de las fórmulas de Excel se compararon y coinciden.

## Power BI
El informe está en `powerbi/turismo_ciudad_real.pbix` (4 páginas: Summary, Seasonality, Recovery y Comparison), con una exportación a PDF. Las medidas DAX están en `powerbi/README_PowerBI.md`.

## Notas de desarrollo
Proyecto realizado con un flujo de trabajo asistido por IA (Claude) para la programación y la revisión. La elección del tema, las preguntas, la interpretación y las conclusiones son mías.

## Licencia
Código © Mildrey Ruiz. Datos: INE, reutilización según su aviso legal.
