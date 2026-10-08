"""Limpieza del CSV del INE (EOH, tabla 67190) -> CSV limpio + base SQLite."""
import pandas as pd, sqlite3, sys, re
src, out_csv, out_db = sys.argv[1:4]
d = pd.read_csv(src, sep=';', encoding='utf-8-sig', dtype=str)
d.columns = ['nacional','ccaa','provincia','variable','res1','res2','periodo','valor']
# Valores: "14.227.157" -> 14227157 (el punto es separador de miles); vacío = dato no publicado
d['valor'] = pd.to_numeric(d['valor'].str.replace('.', '', regex=False), errors='coerce')
strip = lambda s: s.str.replace(r'^\d+\s+', '', regex=True).str.strip()
d['ccaa'] = strip(d['ccaa'].fillna('')).replace('', None)
d['provincia'] = strip(d['provincia'].fillna('')).replace('', None)
d['residencia'] = d['res2'].map({'Residentes en España':'España','Residentes en el Extranjero':'Extranjero'}).fillna('Total')
d['ambito'] = 'Provincia'
d.loc[d.provincia.isna(), 'ambito'] = 'CCAA'
d.loc[d.ccaa.isna(), 'ambito'] = 'Nacional'
d['territorio'] = d.provincia.fillna(d.ccaa).fillna('Total Nacional')
d['anio'] = d.periodo.str[:4].astype(int); d['mes'] = d.periodo.str[5:].astype(int)
d['variable'] = d.variable.map({'Viajero':'viajeros','Pernoctaciones':'pernoctaciones'})
idx = ['ambito','territorio','ccaa','provincia','residencia','anio','mes']
d[['ccaa','provincia']] = d[['ccaa','provincia']].fillna('')
w = d.set_index(idx + ['variable'])['valor'].unstack('variable').reset_index()
w.columns.name = None
w[['ccaa','provincia']] = w[['ccaa','provincia']].replace('', None)
w['fecha'] = pd.to_datetime(dict(year=w.anio, month=w.mes, day=1)).dt.strftime('%Y-%m-%d')
w = w[['fecha','anio','mes','ambito','territorio','ccaa','provincia','residencia','viajeros','pernoctaciones']].sort_values(['ambito','territorio','residencia','fecha'])
# Controles de calidad
assert w.duplicated(['fecha','ambito','territorio','residencia']).sum() == 0
print('filas', len(w), '| nulos viajeros', w.viajeros.isna().sum(), '| periodo', w.fecha.min(), w.fecha.max())
w.to_csv(out_csv, index=False, encoding='utf-8-sig', float_format='%.0f')
con = sqlite3.connect(out_db); w.to_sql('eoh', con, if_exists='replace', index=False)
con.execute('CREATE INDEX ix_eoh ON eoh(territorio, residencia, fecha)'); con.commit(); con.close()
