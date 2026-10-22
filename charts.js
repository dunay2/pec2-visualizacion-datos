'use strict';
const NS='http://www.w3.org/2000/svg';
const COLORS={ink:'#102A43',muted:'#536879',teal:'#007F86',coral:'#E76850',blue:'#4F6ACB'};
const fmt=(v,d=0)=>new Intl.NumberFormat('es-ES',{minimumFractionDigits:d,maximumFractionDigits:d,useGrouping:true}).format(v);
const esc=s=>String(s).replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
const svgEl=(tag,attrs={},text)=>{const e=document.createElementNS(NS,tag);for(const [k,v]of Object.entries(attrs))e.setAttribute(k,v);if(text!==undefined)e.textContent=text;return e;};
function add(root,tag,attrs,text){const e=svgEl(tag,attrs,text);root.append(e);return e;}
function rootSvg(height,label){const s=svgEl('svg',{viewBox:`0 0 1120 ${height}`,role:'group','aria-label':label});document.querySelector('#chart').replaceChildren(s);return s;}
const tooltip=document.querySelector('#tooltip');
const selected=document.querySelector('#selected');
function placeTooltip(e){if(!e||!('clientX'in e))return;tooltip.style.left=Math.min(e.clientX+15,window.innerWidth-tooltip.offsetWidth-12)+'px';tooltip.style.top=Math.max(12,Math.min(e.clientY+15,window.innerHeight-tooltip.offsetHeight-12))+'px';}
function bindMark(el,html,label,{keyboard=true}={}){
 el.classList.add('mark');if(keyboard){el.setAttribute('tabindex','0');el.setAttribute('role','button');el.setAttribute('aria-label',label);}
 add(el,'title',{},label);
 const show=e=>{selected.innerHTML=html;tooltip.innerHTML=html;tooltip.style.display=e.type==='focus'?'none':'block';placeTooltip(e);};
 el.addEventListener('pointerenter',show);el.addEventListener('pointermove',placeTooltip);el.addEventListener('pointerleave',()=>tooltip.style.display='none');el.addEventListener('focus',show);el.addEventListener('blur',()=>tooltip.style.display='none');el.addEventListener('click',e=>{show(e);tooltip.style.display='none';});el.addEventListener('keydown',e=>{if(e.key==='Enter'||e.key===' '){e.preventDefault();selected.innerHTML=html;}});
}
function table(headers,rows,caption){return `<table><caption>${esc(caption)}</caption><thead><tr>${headers.map(h=>`<th scope="col">${esc(h)}</th>`).join('')}</tr></thead><tbody>${rows.map(r=>'<tr>'+r.map((v,i)=>i===0?`<th scope="row">${esc(v)}</th>`:`<td>${esc(v)}</td>`).join('')+'</tr>').join('')}</tbody></table>`;}
function polar(cx,cy,r,a){return[cx+r*Math.cos(a),cy+r*Math.sin(a)];}
async function pie(){
 const d=await fetch('data/epa_canarias.json').then(r=>r.json());const colors=[COLORS.teal,COLORS.coral,COLORS.blue];
 const s=rootSvg(490,'Pie chart: ocupados 52,1 %, parados 6,8 % e inactivos 41,1 % de la población de 16 y más años en Canarias.');
 const cx=330,cy=240,r=203;let a=-Math.PI/2;
 d.rows.forEach((row,i)=>{const end=a+row.share*Math.PI*2;const p=polar(cx,cy,r,a),q=polar(cx,cy,r,end);const g=add(s,'g');add(g,'path',{d:`M ${cx} ${cy} L ${p[0]} ${p[1]} A ${r} ${r} 0 ${row.share>.5?1:0} 1 ${q[0]} ${q[1]} Z`,fill:colors[i],stroke:'#fff','stroke-width':3});
 const mid=(a+end)/2;const lp=polar(cx,cy,i===1?r+38:r*.61,mid);add(g,'text',{x:lp[0],y:lp[1]+7,'text-anchor':'middle',style:`fill:${i===1?COLORS.ink:'#fff'};font-weight:700;font-size:${i===1?22:28}px`},fmt(row.share*100,1)+' %');
 const y=110+i*125;add(s,'circle',{cx:650,cy:y-7,r:7,fill:colors[i]});add(s,'text',{x:674,y,'font-size':24,'font-weight':650},row.category);add(s,'text',{x:674,y:y+38,'font-size':28,'font-weight':700},fmt(row.share*100,1)+' %');add(s,'text',{x:674,y:y+65,'font-size':16,style:`fill:${COLORS.muted}`},fmt(row.thousands,1)+' miles de personas');
 const text=`<strong>${esc(row.category)} · ${fmt(row.share*100,1)} %</strong><br>${fmt(row.thousands,1)} miles de personas, sobre un total de ${fmt(d.total,1)} miles.`;bindMark(g,text,`${row.category}: ${fmt(row.share*100,1)} por ciento, ${fmt(row.thousands,1)} miles de personas.`);a=end;
 });
 selected.innerHTML='<strong>Tres partes de un mismo total</strong><br>Las categorías se excluyen entre sí; ocupados + parados + inactivos = 100 %.';
 document.querySelector('#data-table').innerHTML=table(['Relación con la actividad','Miles de personas','Porcentaje del total'],[...d.rows.map(r=>[r.category,fmt(r.thousands,1),fmt(r.share*100,1)+' %']),['Total',fmt(d.total,1),'100,0 %']],'INE · EPA · Canarias · Ambos sexos · Segundo trimestre de 2026. Valores absolutos en miles de personas.');
}
async function candles(){
 const rows=await fetch('data/taiex.json').then(r=>r.json());const s=rootSvg(530,'Candlestick chart de 11 sesiones del índice TAIEX entre el 1 y el 16 de octubre de 2026. Cada vela muestra apertura, máximo, mínimo y cierre.');
 const L=102,R=1080,T=40,B=450;const ymin=46500,ymax=50500;const y=v=>B-(v-ymin)/(ymax-ymin)*(B-T);const x=i=>L+44+i*(R-L-88)/(rows.length-1);
 for(let v=46500;v<=50500;v+=1000){add(s,'line',{x1:L,y1:y(v),x2:R,y2:y(v),class:'gridline'});add(s,'text',{x:L-16,y:y(v)+5,'text-anchor':'end',class:'axis'},fmt(v));}
 add(s,'text',{x:L,y:20,class:'axis'},'Puntos del índice');
 rows.forEach((row,i)=>{const px=x(i),up=row.close>=row.open,color=up?COLORS.teal:COLORS.coral;const g=add(s,'g');add(g,'rect',{x:px-29,y:T,width:58,height:B-T,fill:'transparent'});add(g,'line',{x1:px,y1:y(row.high),x2:px,y2:y(row.low),stroke:color,'stroke-width':2.4});add(g,'rect',{x:px-18,y:Math.min(y(row.open),y(row.close)),width:36,height:Math.max(2.6,Math.abs(y(row.open)-y(row.close))),fill:color,stroke:color,'stroke-width':1.1});
 const date=row.date.slice(8,10)+'/10';add(s,'text',{x:px,y:B+30,'text-anchor':'middle',class:'axis','font-weight':row.date==='2026-10-12'?750:400},date);
 const difference=row.close-row.open;const text=`<strong>${date}/2026 · ${up?'▲ Cierre por encima o igual a apertura':'▼ Cierre por debajo de apertura'}</strong><br>Apertura ${fmt(row.open,2)} · Máximo ${fmt(row.high,2)} · Mínimo ${fmt(row.low,2)} · Cierre ${fmt(row.close,2)}<br>Cambio ${difference>=0?'+':''}${fmt(difference,2)} puntos · Rango ${fmt(row.high-row.low,2)} puntos`;
 bindMark(g,text,`${date} de 2026: apertura ${row.open}, máximo ${row.high}, mínimo ${row.low}, cierre ${row.close} puntos.`);
 if(row.date==='2026-10-12')selected.innerHTML=text;
 });
 add(s,'text',{x:(L+R)/2,y:510,'text-anchor':'middle',class:'axis'},'Sesiones bursátiles de octubre de 2026');
 document.querySelector('#data-table').innerHTML=table(['Sesión','Apertura','Máximo','Mínimo','Cierre','Rango'],rows.map(r=>[r.date,fmt(r.open,2),fmt(r.high,2),fmt(r.low,2),fmt(r.close,2),fmt(r.high-r.low,2)]),'Fuente: Taiwan Stock Exchange. Todos los valores en puntos del índice TAIEX. Rango = máximo − mínimo.');
}
function swarmLayout(data,xScale,minDistance){
 const placed=[];const radiusSq=minDistance*minDistance;
 for(const datum of [...data].sort((a,b)=>a.body_mass_g-b.body_mass_g||a.source_csv_row-b.source_csv_row)){
  const x=xScale(datum.body_mass_g),near=placed.filter(p=>x-p.x<minDistance);let candidates=[0];
  for(const p of near){const dy=Math.sqrt(Math.max(0,radiusSq-(x-p.x)**2));candidates.push(p.offset+dy,p.offset-dy);}
  candidates.sort((a,b)=>Math.abs(a)-Math.abs(b)||a-b);
  const offset=candidates.find(y=>near.every(p=>(x-p.x)**2+(y-p.offset)**2>=radiusSq-1e-7));
  placed.push({datum,x,offset:offset??0});
 }
 return placed;
}
async function beeswarm(){
 const d=await fetch('data/penguins.json').then(r=>r.json());const s=rootSvg(565,'Beeswarm plot de 342 pingüinos: 151 Adélie, 68 Chinstrap y 123 Gentoo. Masa corporal en gramos. Gentoo presenta masas más altas. Use las flechas izquierda y derecha dentro del gráfico para consultar observaciones.');
 const L=170,R=1080,T=45,B=495;const x=v=>L+(v-2500)/4000*(R-L);const groups=['Adelie','Chinstrap','Gentoo'];const labels={Adelie:'Adélie',Chinstrap:'Chinstrap',Gentoo:'Gentoo'};const colors={Adelie:COLORS.teal,Chinstrap:COLORS.coral,Gentoo:COLORS.blue};const points=[];
 for(let v=2500;v<=6500;v+=500){add(s,'line',{x1:x(v),y1:T,x2:x(v),y2:B,class:'gridline'});add(s,'text',{x:x(v),y:B+29,'text-anchor':'middle',class:'axis'},fmt(v));}
 groups.forEach((species,j)=>{const base=125+j*153,stats=d.statistics_by_species.find(r=>r.species===species);const group=add(s,'g',{'data-group':species});
 add(s,'text',{x:L-28,y:base-6,'text-anchor':'end','font-size':21,'font-weight':650},labels[species]);add(s,'text',{x:L-28,y:base+20,'text-anchor':'end',class:'axis'},'n = '+stats.n_valid);
 const laid=swarmLayout(d.observations.filter(r=>r.species===species),x,10.4);
 for(const p of laid){const g=add(group,'g');const circle=add(g,'circle',{cx:p.x,cy:base+p.offset,r:4.5,fill:colors[species],stroke:'#fff','stroke-width':.6});
 const datum=p.datum;const html=`<strong>${labels[species]} · ${fmt(datum.body_mass_g)} g</strong><br>Isla ${esc(datum.island)} · Año ${datum.year} · Fila ${datum.source_csv_row} del CSV original`;
 bindMark(g,html,`${labels[species]}, masa ${datum.body_mass_g} gramos, isla ${datum.island}, año ${datum.year}`,{keyboard:false});points.push({el:circle,html,species});}
 const median=x(stats.median_body_mass_g);add(group,'line',{x1:median,y1:base-71,x2:median,y2:base+71,stroke:COLORS.ink,'stroke-width':2,'stroke-dasharray':'4 4','pointer-events':'none'});add(group,'text',{x:median+7,y:base-76,'font-size':13,'font-weight':650},'Mediana '+fmt(stats.median_body_mass_g)+' g');
 });
 add(s,'text',{x:(L+R)/2,y:552,'text-anchor':'middle',class:'axis'},'Masa corporal (g)');
 selected.innerHTML='<strong>342 observaciones individuales</strong><br>Cada punto conserva su masa horizontal. La separación vertical permite ver observaciones repetidas o muy próximas.';
 let active=-1;s.setAttribute('tabindex','0');s.setAttribute('role','img');
 s.addEventListener('keydown',e=>{if(!['ArrowLeft','ArrowRight','Home','End'].includes(e.key))return;e.preventDefault();if(active>=0){points[active].el.setAttribute('r','4.5');points[active].el.setAttribute('stroke','#fff');}active=e.key==='Home'?0:e.key==='End'?points.length-1:(active+(e.key==='ArrowLeft'?-1:1)+points.length)%points.length;const p=points[active];p.el.setAttribute('r','6');p.el.setAttribute('stroke',COLORS.ink);selected.innerHTML=p.html;});
 document.querySelectorAll('[data-species]').forEach(button=>button.addEventListener('click',()=>{const chosen=button.dataset.species;document.querySelectorAll('[data-species]').forEach(b=>b.setAttribute('aria-pressed',String(b===button)));document.querySelectorAll('[data-group]').forEach(g=>{g.style.opacity=chosen==='all'||g.dataset.group===chosen?'1':'.16';});if(chosen==='all'){selected.innerHTML='<strong>Las tres especies</strong><br>Adélie y Chinstrap se solapan ampliamente; Gentoo se concentra en masas mayores.';}else{const a=d.statistics_by_species.find(r=>r.species===chosen);selected.innerHTML=`<strong>${labels[chosen]} · ${a.n_valid} observaciones</strong><br>Mediana ${fmt(a.median_body_mass_g)} g · Rango observado ${fmt(a.min_body_mass_g)}–${fmt(a.max_body_mass_g)} g`;}}));
 document.querySelector('#data-table').innerHTML=table(['Especie','n','Mínimo (g)','Mediana (g)','Máximo (g)'],d.statistics_by_species.map(r=>[labels[r.species],r.n_valid,fmt(r.min_body_mass_g),fmt(r.median_body_mass_g),fmt(r.max_body_mass_g)]),'Resumen de las 342 filas con masa corporal disponible. Se excluyen dos valores ausentes de las 344 filas originales.')+table(['Fila CSV','Especie','Masa corporal (g)','Isla','Año'],d.observations.map(r=>[r.source_csv_row,labels[r.species],fmt(r.body_mass_g),r.island,r.year]),'Cada fila corresponde a un punto. El número de fila identifica su posición en el CSV original, no un identificador biológico.');
 window.__pec2Swarm={count:points.length,layout:groups.flatMap((species,j)=>swarmLayout(d.observations.filter(r=>r.species===species),x,10.4).map(p=>({species,x:p.x,y:125+j*153+p.offset,mass:p.datum.body_mass_g})))};
}
const renderers={pie,candlestick:candles,beeswarm};
renderers[document.body.dataset.chart]?.().catch(()=>{document.querySelector('#chart').innerHTML='<p>No se han podido cargar los datos. Recarga la página o consulta el archivo CSV descargable.</p>';selected.textContent='';});
