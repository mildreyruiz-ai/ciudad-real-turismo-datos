"""Ejecuta las consultas clave sobre SQLite y guarda resultados.json (alimenta el dashboard y el README)."""
import sqlite3, json, sys
db, out = sys.argv[1:3]
c = sqlite3.connect(db)
q = lambda s, *a: c.execute(s, a).fetchall()
CR = "provincia='Ciudad Real' AND residencia='Total'"
R = {}
R['anual'] = [dict(anio=a, viajeros=v, pernoct=p, extranjero=e, espana=s) for a, v, p, e, s in q(f"""
  SELECT anio, SUM(CASE WHEN residencia='Total' THEN viajeros END), SUM(CASE WHEN residencia='Total' THEN pernoctaciones END),
         SUM(CASE WHEN residencia='Extranjero' THEN viajeros END), SUM(CASE WHEN residencia='España' THEN viajeros END)
  FROM eoh WHERE provincia='Ciudad Real' AND anio<=2025 GROUP BY anio ORDER BY anio""")]
R['estacionalidad'] = [dict(mes=m, pct=p) for m, p in q(f"""
  WITH m AS (SELECT anio, mes, SUM(viajeros) v FROM eoh WHERE {CR} AND anio BETWEEN 2022 AND 2025 GROUP BY anio, mes),
  t AS (SELECT anio, SUM(v) tot FROM m GROUP BY anio)
  SELECT mes, ROUND(100.0*AVG(1.0*m.v/t.tot),2) FROM m JOIN t USING(anio) GROUP BY mes ORDER BY mes""")]
R['mensual'] = [dict(fecha=f, viajeros=v) for f, v in q(f"SELECT fecha, viajeros FROM eoh WHERE {CR} AND anio>=2015 ORDER BY fecha")]
# Índice 2019=100 con el mismo periodo (ene-ago) para que 2026 sea comparable
idx = {}
for terr, cond in [('Ciudad Real', "provincia='Ciudad Real'"), ('Castilla-La Mancha', "ambito='CCAA' AND territorio='Castilla - La Mancha'"), ('España', "ambito='Nacional'")]:
    rows = q(f"SELECT anio, SUM(viajeros) FROM eoh WHERE {cond} AND residencia='Total' AND mes<=8 AND anio>=2018 GROUP BY anio ORDER BY anio")
    base = dict(rows)[2019]
    idx[terr] = [dict(anio=a, valor=round(100*v/base, 1)) for a, v in rows]
R['indice'] = idx
R['ytd'] = {a: v for a, v in q(f"SELECT anio, SUM(viajeros) FROM eoh WHERE {CR} AND mes<=8 AND anio IN (2019,2025,2026) GROUP BY anio")}
R['ranking_clm'] = [dict(provincia=p, viajeros=v, pernoct=n, estancia=round(n/v, 2)) for p, v, n in q("""
  SELECT provincia, SUM(viajeros), SUM(pernoctaciones) FROM eoh WHERE ccaa='Castilla - La Mancha' AND ambito='Provincia' AND residencia='Total' AND anio=2025
  GROUP BY provincia ORDER BY 2 DESC""")]
R['crec_19_25'] = [dict(territorio=t, v2019=a, v2025=b, pct=round(100*(b-a)/a, 1)) for t, a, b in q("""
  SELECT a.territorio, a.v, b.v FROM (SELECT territorio, SUM(viajeros) v FROM eoh WHERE residencia='Total' AND anio=2019 AND ((ccaa='Castilla - La Mancha' AND ambito='Provincia') OR ambito='Nacional') GROUP BY territorio) a
  JOIN (SELECT territorio, SUM(viajeros) v FROM eoh WHERE residencia='Total' AND anio=2025 AND ((ccaa='Castilla - La Mancha' AND ambito='Provincia') OR ambito='Nacional') GROUP BY territorio) b USING(territorio) ORDER BY 1""")]
R['puesto_2025'] = q("""WITH r AS (SELECT provincia, SUM(viajeros) v, 1.0*SUM(pernoctaciones)/SUM(viajeros) em FROM eoh WHERE ambito='Provincia' AND residencia='Total' AND anio=2025 GROUP BY provincia),
  k AS (SELECT provincia, v, em, RANK() OVER (ORDER BY v DESC) pv, RANK() OVER (ORDER BY em DESC) pe FROM r) SELECT pv, pe FROM k WHERE provincia='Ciudad Real'""")[0]
R['records'] = [dict(fecha=f, viajeros=v) for f, v in q(f"SELECT fecha, viajeros FROM eoh WHERE {CR} ORDER BY viajeros DESC LIMIT 5")]
R['ultimo_mes'] = q(f"SELECT MAX(fecha) FROM eoh WHERE {CR}")[0][0]
json.dump(R, open(out, 'w'), ensure_ascii=False, indent=1)
print('ok', R['puesto_2025'], R['ytd'])
