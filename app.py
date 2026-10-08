import io,sqlite3
from datetime import datetime
import pandas as pd
import streamlit as st
from parsers.sources import SOURCES
from parsers.common import scan
st.set_page_config(page_title='Monitor Cen PL',page_icon='💰',layout='wide')
st.title('Monitor Cen PL');st.caption('MVP v0.2 • Playwright + Chromium • retail osobno od marketplace')
def load(f):
    d=pd.read_excel(f,dtype=str).fillna('');d.columns=[str(c).strip().upper() for c in d.columns]
    if 'PN' not in d:raise ValueError('Plik musi zawierać kolumnę PN.')
    for c in ['EAN','NAZWA']:
        if c not in d:d[c]=''
    return d[['PN','EAN','NAZWA']][d.PN.str.strip()!=''].drop_duplicates('PN')
def report(d):
    b=io.BytesIO();ok=d[d.cena.notna()].sort_values(['pn','cena']);low=ok.groupby('pn',as_index=False).first() if not ok.empty else ok
    with pd.ExcelWriter(b,engine='openpyxl') as w:
        d.to_excel(w,index=False,sheet_name='Wszystkie');d[d.typ=='retail'].to_excel(w,index=False,sheet_name='Retail');d[d.typ=='marketplace'].to_excel(w,index=False,sheet_name='Marketplace');low.to_excel(w,index=False,sheet_name='Najniższe ceny')
    return b.getvalue()
upload=st.file_uploader('Wgraj listę produktów XLSX',type=['xlsx']);demo=st.checkbox('Użyj dołączonego products.xlsx',value=upload is None)
try:d=load(upload if upload else 'products.xlsx') if (upload or demo) else pd.DataFrame()
except Exception as e:st.error(str(e));st.stop()
if not d.empty:
    st.success(f'Wczytano produktów: {len(d)}');st.dataframe(d,use_container_width=True,height=240)
    selected=st.multiselect('Źródła',list(SOURCES),default=list(SOURCES));limit=st.number_input('Limit produktów',1,len(d),min(2,len(d)))
    st.info('Na pierwszy test wybierz 2 produkty i 2 źródła. Skan działa sekwencyjnie.')
    if st.button('Uruchom skan',type='primary',disabled=not selected):
        bar=st.progress(0)
        with st.spinner('Uruchamianie Chromium i skanowanie...'):rows=scan(d.head(int(limit)),selected,SOURCES,bar.progress)
        st.session_state.result=pd.DataFrame(rows)
if 'result' in st.session_state:
    r=st.session_state.result;c1,c2,c3=st.columns(3);c1.metric('Rekordy',len(r));c2.metric('Z ceną',int(r.cena.notna().sum()));c3.metric('Źródła',r.zrodlo.nunique())
    a,b,c=st.tabs(['Wszystkie','Retail','Marketplace']);a.dataframe(r,use_container_width=True);b.dataframe(r[r.typ=='retail'],use_container_width=True);c.dataframe(r[r.typ=='marketplace'],use_container_width=True)
    st.download_button('Pobierz raport Excel',report(r),'raport_cen.xlsx','application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
