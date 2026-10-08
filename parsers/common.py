import json,re
from urllib.parse import quote_plus,urljoin
from bs4 import BeautifulSoup
from playwright.sync_api import sync_playwright,TimeoutError as PWTimeout

def price(v):
    if v is None:return None
    s=re.sub(r'[^0-9,.-]','',str(v).replace('\xa0',' ').replace('PLN','').replace('zł','')).replace(',','.')
    try:
        x=round(float(s),2);return x if 1<=x<=100000 else None
    except:return None

def extract(html,url):
    soup=BeautifulSoup(html,'lxml')
    for tag in soup.select('script[type="application/ld+json"]'):
        try:
            data=json.loads(tag.get_text(strip=True)); stack=data if isinstance(data,list) else [data]
            while stack:
                o=stack.pop(0)
                if isinstance(o,list):stack.extend(o);continue
                if not isinstance(o,dict):continue
                if isinstance(o.get('@graph'),list):stack.extend(o['@graph'])
                if isinstance(o.get('itemListElement'),list):stack.extend([x.get('item',x) for x in o['itemListElement'] if isinstance(x,dict)])
                if o.get('@type') in ('Product','IndividualProduct'):
                    offers=o.get('offers') or {}
                    if isinstance(offers,list):offers=offers[0] if offers else {}
                    p=price(offers.get('price') or offers.get('lowPrice'))
                    if p:return p,str(offers.get('availability','')).split('/')[-1] or 'nieznana',urljoin(url,o.get('url') or offers.get('url') or url),'JSON-LD'
        except:pass
    vals=[]
    for raw in re.findall(r'(\d{1,5}(?:[\s.]\d{3})*[,.]\d{2})\s*(?:zł|PLN)',soup.get_text(' ',strip=True),re.I):
        p=price(raw)
        if p:vals.append(p)
    return (min(vals),'nieznana',url,'widoczna cena') if vals else (None,'nieznana',url,'brak ceny')

def scan(products,selected,sources,progress):
    rows=[];done=0;total=max(1,len(products)*len(selected))
    with sync_playwright() as pw:
        browser=pw.chromium.launch(headless=True,args=['--no-sandbox','--disable-dev-shm-usage','--disable-gpu'])
        ctx=browser.new_context(locale='pl-PL',timezone_id='Europe/Warsaw',viewport={'width':1365,'height':900},user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/124 Safari/537.36')
        page=ctx.new_page();page.set_default_timeout(12000)
        for _,item in products.iterrows():
            for source in selected:
                kind,tpl=sources[source];last='';found=None;message=''
                for q in [str(item.EAN or '').strip(),str(item.PN or '').strip(),str(item.NAZWA or '').strip()]:
                    if not q:continue
                    last=tpl.format(q=quote_plus(q))
                    try:
                        response=page.goto(last,wait_until='domcontentloaded',timeout=30000);page.wait_for_timeout(1800)
                        if response and response.status in (403,429): message=f'HTTP {response.status}';continue
                        p,a,u,m=extract(page.content(),page.url)
                        if p:found=(p,a,u);message=f'{m}; po: {q}';break
                    except PWTimeout:message='timeout'
                    except Exception as exc:message=str(exc)[:160];break
                rows.append({'pn':item.PN,'ean':item.EAN,'nazwa':item.NAZWA,'zrodlo':source,'typ':kind,'cena':found[0] if found else None,'waluta':'PLN','dostepnosc':found[1] if found else 'nieznana','url':found[2] if found else last,'status':'ok' if found else 'brak','komunikat':message})
                done+=1;progress(done/total)
        ctx.close();browser.close()
    return rows
