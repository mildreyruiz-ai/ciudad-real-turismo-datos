"""Libro de Excel con fórmulas vivas (SUMIFS, INDEX/MATCH, validación de datos, formato condicional y gráficos)."""
import sqlite3, sys, pandas as pd
from openpyxl import Workbook
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
from openpyxl.chart import LineChart, BarChart, Reference
from openpyxl.worksheet.table import Table, TableStyleInfo
from openpyxl.worksheet.datavalidation import DataValidation
from openpyxl.formatting.rule import ColorScaleRule, CellIsRule
from openpyxl.utils import get_column_letter as L
db, out = sys.argv[1:3]
TERR = ['Ciudad Real','Albacete','Cuenca','Guadalajara','Toledo','Castilla - La Mancha','Total Nacional']
d = pd.read_sql("SELECT fecha,anio,mes,ambito,territorio,residencia,viajeros,pernoctaciones FROM eoh WHERE territorio IN (%s) AND NOT (ambito='Provincia' AND provincia IS NULL)" % ','.join('?'*len(TERR)), sqlite3.connect(db), params=TERR)
d = d[~((d.ambito=='CCAA')&(d.territorio=='Ciudad Real'))].sort_values(['territorio','residencia','fecha'])
wb = Workbook()
AZ='1F4E79'; hdr=Font(bold=True,color='FFFFFF'); fill=PatternFill('solid',fgColor=AZ); inp=PatternFill('solid',fgColor='FFF2CC')
def head(ws,row,vals,col=1):
    for i,v in enumerate(vals):
        c=ws.cell(row,col+i,v); c.font=hdr; c.fill=fill; c.alignment=Alignment(horizontal='center',wrap_text=True)
# --- Léeme
ws=wb.active; ws.title='Léeme'
for i,t in enumerate(['Turismo hotelero en Ciudad Real (INE · Encuesta de Ocupación Hotelera)','',
 'Fuente: INE, tabla 67190, "Viajeros y pernoctaciones por comunidades autónomas y provincias". Datos mensuales 1999-ene a 2026-ago.',
 'Hoja Datos: serie mensual de Ciudad Real, las otras 4 provincias de Castilla-La Mancha, el total de la comunidad y el total nacional.',
 'Hojas Anual, Estacionalidad, Recuperación y Ranking: todas son FÓRMULAS (SUMIFS / INDEX-MATCH) sobre la hoja Datos; cambian si se cambia el territorio (celda amarilla).',
 'Notas: viajeros = viajeros entrados; estancia media = pernoctaciones / viajeros; 2026 solo llega hasta agosto, por eso la comparación 2026 usa enero-agosto de todos los años.',
 'Autora: Mildrey Ruiz.'],1):
    ws.cell(i,1,t)
ws['A1'].font=Font(bold=True,size=14,color=AZ); ws.column_dimensions['A'].width=140
# --- Datos
wd=wb.create_sheet('Datos'); cols=list(d.columns); head(wd,1,cols)
for r,row in enumerate(d.itertuples(index=False),2):
    for c,v in enumerate(row,1): wd.cell(r,c,None if pd.isna(v) else v)
n=len(d)+1
t=Table(displayName='tblDatos',ref=f'A1:{L(len(cols))}{n}'); t.tableStyleInfo=TableStyleInfo(name='TableStyleMedium2',showRowStripes=True); wd.add_table(t)
for c,w in zip('ABCDEFGH',[12,7,6,11,22,12,12,14]): wd.column_dimensions[c].width=w
wd.freeze_panes='A2'
for r in range(2,n+1):
    for c in (7,8): wd.cell(r,c).number_format='#,##0'
D=lambda col: f"Datos!${col}$2:${col}${n}"   # A fecha B anio C mes D ambito E territorio F residencia G viajeros H pernoct
# --- Anual
wa=wb.create_sheet('Anual'); wa['A1']='Evolución anual'; wa['A1'].font=Font(bold=True,size=14,color=AZ)
wa['A2']='Territorio:'; wa['B2']='Ciudad Real'; wa['B2'].fill=inp; wa['B2'].font=Font(bold=True)
dv=DataValidation(type='list',formula1='"'+','.join(TERR)+'"',allow_blank=False); wa.add_data_validation(dv); dv.add('B2')
head(wa,4,['Año','Viajeros','Pernoctaciones','Estancia media','Var. interanual viajeros','Viajeros extranjeros','% extranjeros'])
for i,y in enumerate(range(1999,2026)):
    r=5+i; wa.cell(r,1,y)
    wa.cell(r,2,f'=SUMIFS({D("G")},{D("E")},$B$2,{D("F")},"Total",{D("B")},$A{r})')
    wa.cell(r,3,f'=SUMIFS({D("H")},{D("E")},$B$2,{D("F")},"Total",{D("B")},$A{r})')
    wa.cell(r,4,f'=IFERROR(C{r}/B{r},"")'); wa.cell(r,5,'' if i==0 else f'=IFERROR(B{r}/B{r-1}-1,"")')
    wa.cell(r,6,f'=SUMIFS({D("G")},{D("E")},$B$2,{D("F")},"Extranjero",{D("B")},$A{r})')
    wa.cell(r,7,f'=IFERROR(F{r}/B{r},"")')
    for c in (2,3,6): wa.cell(r,c).number_format='#,##0'
    wa.cell(r,4).number_format='0.00'; wa.cell(r,5).number_format='0.0%'; wa.cell(r,7).number_format='0.0%'
wa.conditional_formatting.add('E5:E31',CellIsRule(operator='lessThan',formula=['0'],font=Font(color='C00000')))
wa.conditional_formatting.add('B5:B31',ColorScaleRule(start_type='min',start_color='FFFFFF',end_type='max',end_color='9DC3E6'))
for c,w in zip('ABCDEFG',[12,14,16,14,18,18,14]): wa.column_dimensions[c].width=w
wa.freeze_panes='A5'
ch=LineChart(); ch.title='Viajeros por año'; ch.height=8; ch.width=18
ch.add_data(Reference(wa,min_col=2,min_row=4,max_row=31),titles_from_data=True); ch.set_categories(Reference(wa,min_col=1,min_row=5,max_row=31)); wa.add_chart(ch,'I4')
# --- Estacionalidad
we=wb.create_sheet('Estacionalidad'); we['A1']='Estacionalidad: peso de cada mes sobre el total del año'; we['A1'].font=Font(bold=True,size=14,color=AZ)
we['A2']='Territorio:'; we['B2']='=Anual!B2'
head(we,4,['Mes','Viajeros 2022','Viajeros 2023','Viajeros 2024','Viajeros 2025','% 2022','% 2023','% 2024','% 2025','Peso medio'])
for m in range(1,13):
    r=4+m; we.cell(r,1,m)
    for j,y in enumerate(range(2022,2026)):
        we.cell(r,2+j,f'=SUMIFS({D("G")},{D("E")},$B$2,{D("F")},"Total",{D("B")},{y},{D("C")},$A{r})').number_format='#,##0'
        we.cell(r,6+j,f'={L(2+j)}{r}/SUM({L(2+j)}$5:{L(2+j)}$16)').number_format='0.0%'
    we.cell(r,10,f'=AVERAGE(F{r}:I{r})').number_format='0.0%'
we.conditional_formatting.add('J5:J16',ColorScaleRule(start_type='min',start_color='FFFFFF',end_type='max',end_color='F4B183'))
bc=BarChart(); bc.title='Peso medio de cada mes (2022-2025)'; bc.height=8; bc.width=18
bc.add_data(Reference(we,min_col=10,min_row=4,max_row=16),titles_from_data=True); bc.set_categories(Reference(we,min_col=1,min_row=5,max_row=16)); we.add_chart(bc,'L4')
for c in 'ABCDEFGHIJ': we.column_dimensions[c].width=13
# --- Recuperación
wr=wb.create_sheet('Recuperación'); wr['A1']='Recuperación frente a 2019 (mismo periodo: enero-agosto)'; wr['A1'].font=Font(bold=True,size=14,color=AZ)
head(wr,3,['Año','Ciudad Real','Castilla-La Mancha','España','Índice Ciudad Real','Índice Castilla-La Mancha','Índice España'])
for i,y in enumerate(range(2018,2027)):
    r=4+i; wr.cell(r,1,y)
    for j,tt in enumerate(['Ciudad Real','Castilla - La Mancha','Total Nacional']):
        wr.cell(r,2+j,f'=SUMIFS({D("G")},{D("E")},"{tt}",{D("F")},"Total",{D("B")},$A{r},{D("C")},"<=8")').number_format='#,##0'
        wr.cell(r,5+j,f'={L(2+j)}{r}/INDEX({L(2+j)}$4:{L(2+j)}$12,MATCH(2019,$A$4:$A$12,0))*100').number_format='0.0'
for c in 'ABCDEFG': wr.column_dimensions[c].width=20
lc=LineChart(); lc.title='Índice (2019 = 100)'; lc.height=8; lc.width=18
lc.add_data(Reference(wr,min_col=5,max_col=7,min_row=3,max_row=12),titles_from_data=True); lc.set_categories(Reference(wr,min_col=1,min_row=4,max_row=12)); wr.add_chart(lc,'I3')
# --- Ranking CLM
wk=wb.create_sheet('Ranking CLM'); wk['A1']='Provincias de Castilla-La Mancha: 2025 y variación 2019-2025'; wk['A1'].font=Font(bold=True,size=14,color=AZ)
head(wk,3,['Provincia','Viajeros 2025','Pernoctaciones 2025','Estancia media','% de CLM','Viajeros 2019','Variación 2019-2025'])
for i,p in enumerate(['Toledo','Ciudad Real','Albacete','Guadalajara','Cuenca']):
    r=4+i; wk.cell(r,1,p)
    wk.cell(r,2,f'=SUMIFS({D("G")},{D("E")},$A{r},{D("F")},"Total",{D("B")},2025)').number_format='#,##0'
    wk.cell(r,3,f'=SUMIFS({D("H")},{D("E")},$A{r},{D("F")},"Total",{D("B")},2025)').number_format='#,##0'
    wk.cell(r,4,f'=C{r}/B{r}').number_format='0.00'
    wk.cell(r,5,f'=B{r}/SUM($B$4:$B$8)').number_format='0.0%'
    wk.cell(r,6,f'=SUMIFS({D("G")},{D("E")},$A{r},{D("F")},"Total",{D("B")},2019)').number_format='#,##0'
    wk.cell(r,7,f'=B{r}/F{r}-1').number_format='0.0%'
wk.conditional_formatting.add('G4:G8',CellIsRule(operator='lessThan',formula=['0'],font=Font(color='C00000')))
for c in 'ABCDEFG': wk.column_dimensions[c].width=20
bk=BarChart(); bk.type='bar'; bk.title='Viajeros 2025 por provincia'; bk.height=7; bk.width=16
bk.add_data(Reference(wk,min_col=2,min_row=3,max_row=8),titles_from_data=True); bk.set_categories(Reference(wk,min_col=1,min_row=4,max_row=8)); wk.add_chart(bk,'A11')
wb.save(out); print('guardado',out,len(d),'filas de datos')
