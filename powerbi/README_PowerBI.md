# Power BI — cómo montar el informe

Archivo de datos: `data/eoh_limpio.csv` (UTF-8, separador coma; ya limpio con `python/01_limpieza.py`).

## 1. Importar
Inicio → Obtener datos → Texto/CSV → `eoh_limpio.csv` → Transformar datos. Comprueba tipos: `fecha` = Fecha, `viajeros` y `pernoctaciones` = Número entero. Filtra la tabla a lo que necesites (por ejemplo `ambito = "Provincia"` o `"Nacional"`).

## 2. Tabla de calendario (DAX)
```dax
Calendario = ADDCOLUMNS(
    CALENDARAUTO(),
    "Año", YEAR([Date]),
    "MesNum", MONTH([Date]),
    "Mes", FORMAT([Date], "mmm")
)
```
Relación: `Calendario[Date]` → `eoh[fecha]` (uno a varios).

## 3. Medidas
```dax
Viajeros = CALCULATE(SUM(eoh[viajeros]), eoh[residencia] = "Total")
Pernoctaciones = CALCULATE(SUM(eoh[pernoctaciones]), eoh[residencia] = "Total")
Estancia media = DIVIDE([Pernoctaciones], [Viajeros])
Viajeros extranjeros = CALCULATE(SUM(eoh[viajeros]), eoh[residencia] = "Extranjero")
% extranjeros = DIVIDE([Viajeros extranjeros], [Viajeros])
Viajeros año anterior = CALCULATE([Viajeros], SAMEPERIODLASTYEAR(Calendario[Date]))
Var. interanual = DIVIDE([Viajeros] - [Viajeros año anterior], [Viajeros año anterior])
Viajeros 2019 = CALCULATE([Viajeros], Calendario[Año] = 2019)
Índice 2019=100 = DIVIDE([Viajeros], [Viajeros 2019]) * 100
Peso del mes = DIVIDE([Viajeros], CALCULATE([Viajeros], ALLEXCEPT(Calendario, Calendario[Año])))
Cuota en CLM = DIVIDE([Viajeros], CALCULATE([Viajeros], ALL(eoh[provincia]), eoh[ambito] = "Provincia", eoh[ccaa] = "Castilla - La Mancha"))
```
Para comparar el mismo periodo (ene-ago) usa un filtro de página `MesNum <= 8`.

**Importante:** la tabla mezcla filas de provincia, comunidad y total nacional. Nunca pongas una tarjeta de `Viajeros` sin filtrar `territorio` (o `ambito`), porque sumaría los tres niveles a la vez.

## 4. Páginas sugeridas
1. **Resumen**: tarjetas (Viajeros, Var. interanual, % extranjeros, Estancia media), línea mensual 2015-hoy, segmentador de Año y de Provincia (por defecto Ciudad Real).
2. **Estacionalidad**: columnas por `Mes` con `Peso del mes`, matriz Año × Mes con formato condicional (mapa de calor).
3. **Recuperación**: líneas de `Índice 2019=100` para Ciudad Real, Castilla-La Mancha y España.
4. **Comparativa**: barras de viajeros 2025 por provincia de Castilla-La Mancha y dispersión viajeros vs estancia media.
