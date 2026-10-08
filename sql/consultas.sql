-- Turismo hotelero en Ciudad Real (INE, EOH). Base: tabla eoh(fecha, anio, mes, ambito, territorio, ccaa, provincia, residencia, viajeros, pernoctaciones)

-- Q1. Evolución anual en Ciudad Real (años completos) y estancia media
SELECT anio, SUM(viajeros) AS viajeros, SUM(pernoctaciones) AS pernoctaciones,
       ROUND(1.0*SUM(pernoctaciones)/SUM(viajeros),2) AS estancia_media
FROM eoh WHERE provincia='Ciudad Real' AND residencia='Total' AND anio<=2025
GROUP BY anio ORDER BY anio;

-- Q2. Variación interanual con función de ventana
WITH a AS (SELECT anio, SUM(viajeros) v FROM eoh WHERE provincia='Ciudad Real' AND residencia='Total' AND anio<=2025 GROUP BY anio)
SELECT anio, v, ROUND(100.0*(v-LAG(v) OVER (ORDER BY anio))/LAG(v) OVER (ORDER BY anio),1) AS var_pct FROM a ORDER BY anio;

-- Q3. Estacionalidad: peso de cada mes sobre el año (media 2022-2025)
WITH m AS (SELECT anio, mes, SUM(viajeros) v FROM eoh WHERE provincia='Ciudad Real' AND residencia='Total' AND anio BETWEEN 2022 AND 2025 GROUP BY anio, mes),
t AS (SELECT anio, SUM(v) tot FROM m GROUP BY anio)
SELECT mes, ROUND(100.0*AVG(1.0*m.v/t.tot),2) AS pct_del_anio
FROM m JOIN t USING(anio) GROUP BY mes ORDER BY mes;

-- Q4. Residentes en España vs extranjero (cuota de viajeros extranjeros por año)
SELECT anio,
  SUM(CASE WHEN residencia='España' THEN viajeros END) AS espana,
  SUM(CASE WHEN residencia='Extranjero' THEN viajeros END) AS extranjero,
  ROUND(100.0*SUM(CASE WHEN residencia='Extranjero' THEN viajeros END)/SUM(CASE WHEN residencia='Total' THEN viajeros END),1) AS pct_extranjero
FROM eoh WHERE provincia='Ciudad Real' AND anio<=2025 GROUP BY anio ORDER BY anio;

-- Q5. Impacto y recuperación del COVID: mismo periodo (ene-ago) de cada año frente a 2019
WITH y AS (SELECT anio, SUM(viajeros) v FROM eoh WHERE provincia='Ciudad Real' AND residencia='Total' AND mes<=8 AND anio>=2018 GROUP BY anio)
SELECT anio, v, ROUND(100.0*v/(SELECT v FROM y WHERE anio=2019),1) AS indice_2019_100 FROM y ORDER BY anio;

-- Q6. Ranking de provincias de Castilla-La Mancha en 2025
SELECT provincia, SUM(viajeros) AS viajeros, SUM(pernoctaciones) AS pernoctaciones,
       ROUND(1.0*SUM(pernoctaciones)/SUM(viajeros),2) AS estancia_media,
       ROUND(100.0*SUM(viajeros)/(SELECT SUM(viajeros) FROM eoh WHERE ambito='CCAA' AND territorio='Castilla - La Mancha' AND residencia='Total' AND anio=2025),1) AS pct_clm
FROM eoh WHERE ccaa='Castilla - La Mancha' AND ambito='Provincia' AND residencia='Total' AND anio=2025
GROUP BY provincia ORDER BY viajeros DESC;

-- Q7. Posición de Ciudad Real entre las 50 provincias (2025): viajeros y estancia media
WITH r AS (SELECT provincia, SUM(viajeros) v, 1.0*SUM(pernoctaciones)/SUM(viajeros) em FROM eoh WHERE ambito='Provincia' AND residencia='Total' AND anio=2025 GROUP BY provincia),
k AS (SELECT provincia, v, ROUND(em,2) AS estancia_media, RANK() OVER (ORDER BY v DESC) AS puesto_viajeros, RANK() OVER (ORDER BY em DESC) AS puesto_estancia FROM r)
SELECT * FROM k WHERE provincia='Ciudad Real';

-- Q8. Crecimiento 2019 -> 2025 por provincia de CLM y total nacional
WITH p AS (SELECT territorio, anio, SUM(viajeros) v FROM eoh WHERE residencia='Total' AND anio IN (2019,2025) AND (ccaa='Castilla - La Mancha' AND ambito='Provincia' OR ambito='Nacional') GROUP BY territorio, anio)
SELECT a.territorio, a.v AS v2019, b.v AS v2025, ROUND(100.0*(b.v-a.v)/a.v,1) AS crec_pct
FROM p a JOIN p b ON a.territorio=b.territorio AND a.anio=2019 AND b.anio=2025 ORDER BY crec_pct DESC;

-- Q9. Mejores meses de la serie (récords) en Ciudad Real
SELECT fecha, viajeros, pernoctaciones FROM eoh WHERE provincia='Ciudad Real' AND residencia='Total' ORDER BY viajeros DESC LIMIT 5;
