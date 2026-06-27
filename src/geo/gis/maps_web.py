"""Interactive Leaflet map from the canonical GeoJSON layers.

Produces a single self-contained HTML (vectors embedded inline) with toggleable
layers — sales choropleth (villages & talukas), territories, delivery routes,
customer-density, coverage rings, and expansion-opportunity markers — replacing
the static bubble charts. Uses Leaflet from a CDN with an OpenStreetMap basemap.
"""
from __future__ import annotations

import json

import yaml

from src.geo.gis import layers as gis_layers
from src.utils import CONFIG_DIR, PROJECT_ROOT

OUT = PROJECT_ROOT / "dashboards" / "geo" / "geo_intelligence_map.html"

_TEMPLATE = """<!doctype html><html><head><meta charset="utf-8">
<title>Geographic Intelligence — {firm}</title>
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<link rel="stylesheet" href="https://unpkg.com/leaflet@1.9.4/dist/leaflet.css"/>
<script src="https://unpkg.com/leaflet@1.9.4/dist/leaflet.js"></script>
<style>
 html,body{{margin:0;height:100%}} #map{{height:100%}}
 .legend{{background:#fff;padding:8px 10px;border-radius:6px;font:12px Arial;line-height:18px;box-shadow:0 1px 4px rgba(0,0,0,.3)}}
 .legend i{{width:16px;height:16px;float:left;margin-right:6px;opacity:.8}}
 .title{{background:#1f3a5f;color:#fff;padding:8px 12px;border-radius:6px;font:600 13px Arial}}
</style></head><body><div id="map"></div><script>
const DATA = {data};
const BASE = {base};
const BREAKS = {breaks};
const map = L.map('map').setView([BASE.lat, BASE.lon], 9);
L.tileLayer('https://{{s}}.tile.openstreetmap.org/{{z}}/{{x}}/{{y}}.png',
  {{maxZoom:18, attribution:'© OpenStreetMap'}}).addTo(map);

function inr(v){{return '₹'+Math.round(v).toLocaleString('en-IN');}}
function color(v){{
  return v> BREAKS[4] ? '#08519c' : v> BREAKS[3] ? '#3182bd' :
         v> BREAKS[2] ? '#6baed6' : v> BREAKS[1] ? '#bdd7e7' :
         v> BREAKS[0] ? '#eff3ff' : '#f7f7f7';
}}
function choro(metric){{return f=>({{fillColor:color(f.properties[metric]||0),
  weight:1,color:'#666',fillOpacity:.7}});}}
function popup(layer,f){{
  const p=f.properties; let h='<b>'+(p.name||p.town||p.delivery_day||'')+'</b><br>';
  if(p.sales_inr!=null)h+='Sales: '+inr(p.sales_inr)+'<br>';
  if(p.customers!=null)h+='Customers: '+p.customers+'<br>';
  if(p.bills!=null)h+='Bills: '+p.bills+'<br>';
  if(p.distance_km!=null)h+='Distance: '+p.distance_km+' km<br>';
  if(p.delivery_day&&p.name==null)h+='Towns: '+(p.towns||'')+'<br>';
  layer.bindPopup(h);
}}

// choropleth layers
const villages=L.geoJSON(DATA.villages,{{style:choro('sales_inr'),
  onEachFeature:(f,l)=>popup(l,f)}}).addTo(map);
const talukas=L.geoJSON(DATA.talukas,{{style:choro('sales_inr'),
  onEachFeature:(f,l)=>popup(l,f)}});
const territories=L.geoJSON(DATA.territories,{{style:f=>({{
  fillColor:'#'+(Math.abs(hash(f.properties.name))%0xffffff).toString(16).padStart(6,'0'),
  weight:1,color:'#444',fillOpacity:.45}}),onEachFeature:(f,l)=>popup(l,f)}});
const districts=L.geoJSON(DATA.districts,{{style:{{fill:false,weight:2.5,color:'#b11b1b'}},
  onEachFeature:(f,l)=>popup(l,f)}}).addTo(map);

// delivery routes
const dayColors={{Monday:'#e41a1c',Tuesday:'#377eb8',Wednesday:'#4daf4a',
  Thursday:'#984ea3',Friday:'#ff7f00',Saturday:'#a65628'}};
const routes=L.geoJSON(DATA.routes,{{style:f=>({{color:dayColors[f.properties.delivery_day]||'#333',
  weight:3,opacity:.8,dashArray:'4 4'}}),onEachFeature:(f,l)=>popup(l,f)}});

// customer density (sized circles)
const cust=L.geoJSON(DATA.customers,{{pointToLayer:(f,ll)=>L.circleMarker(ll,{{
  radius:Math.max(4,Math.sqrt(f.properties.customers||1)*1.6),
  fillColor:'#2a7ab0',color:'#fff',weight:1,fillOpacity:.7}}),
  onEachFeature:(f,l)=>popup(l,f)}});

// coverage rings (15/30/50/80 km)
const rings=L.layerGroup([15,30,50,80].map(km=>L.circle([BASE.lat,BASE.lon],
  {{radius:km*1000,fill:false,color:'#777',weight:1,dashArray:'2 6'}})
  .bindTooltip(km+' km')));

// expansion opportunities: near (<=50km) towns with below-median sales
const med=median(DATA.customers.features.map(f=>f.properties.sales_inr||0));
const expansion=L.geoJSON(DATA.customers,{{filter:f=>f.properties.distance_km<=50 &&
  (f.properties.sales_inr||0)<med, pointToLayer:(f,ll)=>L.marker(ll).bindPopup(
  '<b>Expansion target</b><br>'+f.properties.town+'<br>Sales '+inr(f.properties.sales_inr)+
  '<br>'+f.properties.customers+' customers @ '+f.properties.distance_km+' km')}});

// warehouse
const wh=L.geoJSON(DATA.warehouses,{{pointToLayer:(f,ll)=>L.marker(ll).bindPopup(
  '<b>★ '+f.properties.name+'</b><br>Distribution base')}}).addTo(map);

function hash(s){{s=String(s);let h=0;for(let i=0;i<s.length;i++)h=(h*31+s.charCodeAt(i))|0;return h;}}
function median(a){{a=a.slice().sort((x,y)=>x-y);return a[Math.floor(a.length/2)]||0;}}

L.control.layers(
  {{}},
  {{'Villages (sales choropleth)':villages,'Talukas (choropleth)':talukas,
   'Sales territories (by route-day)':territories,'District boundaries':districts,
   'Delivery routes':routes,'Customer density':cust,'Coverage rings':rings,
   'Expansion opportunities':expansion,'Warehouse':wh}},
  {{collapsed:false}}).addTo(map);

const title=L.control({{position:'topleft'}});
title.onAdd=()=>{{const d=L.DomUtil.create('div','title');
  d.innerHTML='Geographic Intelligence — {firm}<br><span style="font-weight:400">FY {fy} · GeoJSON canonical layers</span>';return d;}};
title.addTo(map);

const legend=L.control({{position:'bottomright'}});
legend.onAdd=()=>{{const d=L.DomUtil.create('div','legend');
  d.innerHTML='<b>Sales (₹)</b><br>'+BREAKS.map((b,i)=>
   '<i style="background:'+color(b+1)+'"></i> '+inr(b)+(i<BREAKS.length-1?'+':'')).reverse().join('<br>');
  return d;}};
legend.addTo(map);
</script></body></html>"""


def _firm_name() -> str:
    return "Sukhakarta Distributors"


def generate() -> str:
    cols = gis_layers.build_all()
    base = yaml.safe_load((CONFIG_DIR / "geo.yaml").read_text(encoding="utf-8"))["base"]
    data = {name: fc.to_dict() for name, fc in cols.items()}
    sales = sorted(f.properties.get("sales_inr", 0)
                   for f in cols["villages"].features)
    # 5 quantile breaks for the choropleth
    n = len(sales)
    breaks = [round(sales[int(q * (n - 1))]) for q in (0.0, 0.25, 0.5, 0.75, 0.9)] \
        if n else [0, 1, 2, 3, 4]
    fy = cols["villages"].features[0].properties.get("fy") if cols["villages"].features else "—"

    html = _TEMPLATE.format(
        firm=_firm_name(), fy=fy,
        data=json.dumps(data, ensure_ascii=False),
        base=json.dumps({"lat": base["lat"], "lon": base["lon"]}),
        breaks=json.dumps(breaks))
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(html, encoding="utf-8")
    return str(OUT)


if __name__ == "__main__":
    print("Interactive map:", generate())
