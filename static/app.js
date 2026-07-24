// ===== Perfis: mapeia nome do Telegram -> avatar. (preenchido após confirmar nomes) =====
// chave = primeiro nome no Telegram (minúsculo) -> avatar + nome de exibição
const PERFIS = {
  "d":       {av:"marido", nome:"Diego"},
  "diego":   {av:"marido", nome:"Diego"},
  "j":       {av:"esposa", nome:"Juliana"},
  "juliana": {av:"esposa", nome:"Juliana"},
  "mateus":  {av:"esposa", nome:"Juliana"},
};
const dispName = n => { const k=(n||"").trim().toLowerCase(); return (PERFIS[k]&&PERFIS[k].nome) || n; };
const AV_CACHE = {};

const $ = (s, r=document) => r.querySelector(s);
const $$ = (s, r=document) => [...r.querySelectorAll(s)];
const fmt = v => "R$ " + (v||0).toLocaleString("pt-BR",{minimumFractionDigits:2,maximumFractionDigits:2});
const fmtDate = iso => { if(!iso) return "—"; const d=new Date(iso); return `${String(d.getDate()).padStart(2,"0")}/${String(d.getMonth()+1).padStart(2,"0")}`; };
const cap = s => (s||"").charAt(0).toUpperCase()+(s||"").slice(1);

function avatarFor(name){
  const key = (name||"").trim().toLowerCase();
  const disp = dispName(name);
  if(PERFIS[key]) return {img:`/static/avatars/${PERFIS[key].av}.jpg`, initial:cap(disp[0]||"?")};
  return {img:null, initial:cap((disp||"?")[0])};
}
function avatarEl(name, cls=""){
  const a = avatarFor(name);
  if(a.img) return `<div class="av ${cls}"><img src="${a.img}" style="width:100%;height:100%;object-fit:cover" onerror="this.parentNode.textContent='${a.initial}'"></div>`;
  return `<div class="av ${cls}">${a.initial}</div>`;
}

function toast(msg){ const t=$("#toast"); t.textContent=msg; t.classList.remove("hidden"); clearTimeout(t._t); t._t=setTimeout(()=>t.classList.add("hidden"),2200); }

// ===== Navegação =====
const TITLES = {
  inicio:["Início","Visão geral do mês"], lancamentos:["Lançamentos","Gerencie seus registros"],
  fixas:["Fixas","Contas e receitas fixas do mês"],
  historico:["Histórico","Todos os lançamentos"], graficos:["Gráficos","Análise visual do casal"],
  categorias:["Categorias","Classificação automática do bot"]
};
function go(view){
  $$(".view").forEach(v=>v.classList.add("hidden"));
  $("#view-"+view).classList.remove("hidden");
  $$(".nav-item").forEach(n=>n.classList.toggle("active", n.dataset.view===view));
  $("#page-title").textContent=TITLES[view][0];
  $("#page-sub").textContent=TITLES[view][1];
  if(view==="graficos") loadCharts();
  if(view==="categorias") loadCats();
  if(view==="fixas") loadFixas();
  if(view==="historico") loadTable("h");
  if(view==="lancamentos") loadTable("l");
}
document.addEventListener("click",e=>{ const b=e.target.closest("[data-view]"); if(b) go(b.dataset.view); });

// ===== Overview =====
async function loadOverview(){
  const d = await (await fetch("/api/overview")).json();
  $("#ref-mes").textContent = d.mes_ref;
  const saldoCls = d.saldo>=0?"pos":"neg";
  $("#stat-grid").innerHTML = `
    <div class="stat"><span class="lbl">Receitas do mês</span><div class="ic green">↑</div><div class="val">${fmt(d.receitas)}</div><div class="foot">Entradas em ${d.mes_ref}</div></div>
    <div class="stat"><span class="lbl">Despesas do mês</span><div class="ic red">↓</div><div class="val">${fmt(d.despesas)}</div><div class="foot">Saídas em ${d.mes_ref}</div></div>
    <div class="stat ${saldoCls}"><span class="lbl">Saldo do mês</span><div class="ic gold">≈</div><div class="val">${fmt(d.saldo)}</div><div class="foot">Receitas − despesas</div></div>
    <div class="stat ${d.patrimonio>=0?"pos":"neg"}"><span class="lbl">Patrimônio</span><div class="ic gold">✦</div><div class="val">${fmt(d.patrimonio)}</div><div class="foot">Acumulado total</div></div>`;

  // pessoas
  $("#people").innerHTML = d.membros.length ? d.membros.map(m=>`
    <div class="person">${avatarEl(m.nome,"lg")}
      <div class="pinfo"><div class="pname">${dispName(m.nome)}</div>
        <div class="pmeta">↑ ${fmt(m.receita)} · ↓ ${fmt(m.despesa)}</div></div>
      <div class="pval"><span class="s ${m.saldo>=0?"pos":"neg"}">${fmt(m.saldo)}</span><small>saldo</small></div>
    </div>`).join("") : emptyBlock("Sem movimentações neste mês");

  // side members
  $("#side-members").innerHTML = d.membros.map(m=>`<div style="display:flex;align-items:center;gap:10px">${avatarEl(m.nome)}<div style="font-size:13px"><div style="font-weight:600">${dispName(m.nome)}</div><div style="color:var(--muted);font-size:11.5px">${fmt(m.saldo)}</div></div></div>`).join("");

  // top avatars
  $("#top-avatars").innerHTML = d.membros.slice(0,2).map(m=>avatarEl(m.nome)).join("");

  // highlights
  const hl=[];
  if(d.mais_recebeu) hl.push(`<div class="hl"><div class="hic">🏆</div><div><div class="ht">Quem mais recebeu</div><div class="hv">${dispName(d.mais_recebeu.nome)}</div></div><div class="hs" style="color:var(--green)">${fmt(d.mais_recebeu.receita)}</div></div>`);
  if(d.mais_gastou) hl.push(`<div class="hl"><div class="hic">💳</div><div><div class="ht">Quem mais gastou</div><div class="hv">${dispName(d.mais_gastou.nome)}</div></div><div class="hs" style="color:var(--red)">${fmt(d.mais_gastou.despesa)}</div></div>`);
  $("#highlights").innerHTML = hl.length?hl.join(""):emptyBlock("Nada em destaque ainda");

  // mini list
  $("#mini-list").innerHTML = d.ultimos.length ? d.ultimos.map(l=>{
    const r=l.tipo==="Receita";
    return `<div class="mrow"><span class="dot ${r?"rec":"desp"}"></span>
      <div class="md"><div class="mdesc">${l.descricao}</div><div class="mcat">${l.categoria} · ${l.subcategoria}</div></div>
      <span class="muser">${dispName(l.usuario)}</span>
      <span class="mval ${r?"rec":"desp"}">${r?"+":"−"} ${fmt(l.valor)}</span></div>`;
  }).join("") : emptyBlock("Envie “Pizza 89” ao bot para começar");
}
function emptyBlock(sub){ return `<div class="empty"><div class="e-ic">✦</div><div class="e-t">Tudo pronto</div><div class="e-s">${sub}</div></div>`; }

// ===== Meta (selects) =====
let META={usuarios:[],categorias:[]};
async function loadMeta(){
  META = await (await fetch("/api/meta")).json();
  const uOpts = '<option value="">Pessoa · todas</option>'+META.usuarios.map(u=>`<option value="${u}">${dispName(u)}</option>`).join("");
  const cOpts = '<option value="">Categoria · todas</option>'+META.categorias.map(c=>`<option>${c}</option>`).join("");
  $("#l-usuario").innerHTML=uOpts; $("#h-usuario").innerHTML=uOpts;
  $("#l-categoria").innerHTML=cOpts; $("#h-categoria").innerHTML=cOpts;
  const uSel = (META.usuarios.length?META.usuarios:["—"]).map(u=>`<option value="${u}">${dispName(u)}</option>`).join("");
  $("#f-usuario").innerHTML = uSel;
  if($("#fx-usuario")) $("#fx-usuario").innerHTML = uSel;
}

// ===== Tabelas =====
const TS = { l:{sort:"data",order:"desc"}, h:{sort:"data",order:"desc"} };
function filters(p){
  const f={sort:TS[p].sort, order:TS[p].order};
  f.search=$(`#${p}-search`).value.trim();
  f.tipo=$(`#${p}-tipo`).value; f.usuario=$(`#${p}-usuario`).value; f.categoria=$(`#${p}-categoria`).value;
  if(p==="h"){ f.start=$("#h-start").value; f.end=$("#h-end").value; }
  return f;
}
async function loadTable(p){
  const qs=new URLSearchParams(filters(p)).toString();
  const {lancamentos}=await (await fetch("/api/lancamentos?"+qs)).json();
  const tbl=$(`#${p}-table`), empty=$(`#${p}-empty`);
  if(!lancamentos.length){ tbl.innerHTML=""; empty.classList.remove("hidden"); empty.innerHTML=`<div class="e-ic">✦</div><div class="e-t">Nenhum lançamento</div><div class="e-s">Ajuste os filtros ou adicione um novo.</div>`; return; }
  empty.classList.add("hidden");
  const arrow=c=> TS[p].sort===c ? `<span class="ar">${TS[p].order==="asc"?"▲":"▼"}</span>`:"";
  const head=`<thead><tr>
    <th data-s="data">Data ${arrow("data")}</th>
    <th data-s="tipo">Tipo ${arrow("tipo")}</th>
    <th data-s="descricao">Descrição ${arrow("descricao")}</th>
    <th data-s="categoria">Categoria ${arrow("categoria")}</th>
    <th data-s="usuario">Pessoa ${arrow("usuario")}</th>
    <th data-s="valor">Valor ${arrow("valor")}</th>
    <th></th></tr></thead>`;
  const body=lancamentos.map(l=>{const r=l.tipo==="Receita";return `<tr>
    <td style="color:var(--muted)">${fmtDate(l.data)}</td>
    <td><span class="pill ${r?"rec":"desp"}">${l.tipo}</span></td>
    <td style="font-weight:500">${l.descricao}</td>
    <td style="color:var(--muted)">${l.categoria}<br><span style="font-size:11.5px;color:var(--faint)">${l.subcategoria}</span></td>
    <td><div style="display:flex;align-items:center;gap:8px">${avatarEl(l.usuario,"udot")}<span style="font-size:13px">${dispName(l.usuario)}</span></div></td>
    <td class="tval ${r?"rec":"desp"}">${r?"+":"−"} ${fmt(l.valor)}</td>
    <td><div class="acts">
      <button class="ico" title="Editar" onclick='openEdit(${JSON.stringify(l)})'>✎</button>
      <button class="ico" title="Duplicar" onclick='openDup(${JSON.stringify(l)})'>⧉</button>
      <button class="ico del" title="Excluir" onclick='askDelete(${l.id},${JSON.stringify(l.descricao)})'>🗑</button>
    </div></td></tr>`;}).join("");
  tbl.innerHTML=head+"<tbody>"+body+"</tbody>";
  $$(`#${p}-table th[data-s]`).forEach(th=>th.onclick=()=>{
    const c=th.dataset.s;
    if(TS[p].sort===c) TS[p].order=TS[p].order==="asc"?"desc":"asc"; else {TS[p].sort=c;TS[p].order="desc";}
    loadTable(p);
  });
}
// debounce filtros
function bind(p){
  ["search","tipo","usuario","categoria"].forEach(k=>{ const el=$(`#${p}-${k}`); if(el) el.oninput=el.onchange=debounce(()=>loadTable(p)); });
  if(p==="h"){ ["start","end"].forEach(k=>$(`#h-${k}`).onchange=()=>loadTable("h")); }
}
function debounce(fn,ms=250){let t;return(...a)=>{clearTimeout(t);t=setTimeout(()=>fn(...a),ms);};}

// ===== Modal lançamento =====
let editId=null;
function openModal(title){ $("#modal-title").textContent=title; $("#modal").classList.remove("hidden"); }
function closeModal(){ $("#modal").classList.add("hidden"); }
function setTipo(v){ $$("#f-tipo button").forEach(b=>b.classList.toggle("active",b.dataset.v===v)); }
$("#btn-novo").onclick=()=>{
  editId=null; setTipo("Despesa");
  $("#f-descricao").value=""; $("#f-valor").value=""; $("#f-categoria").value=""; $("#f-subcategoria").value="";
  $("#f-data").value=new Date().toISOString().slice(0,10);
  openModal("Novo lançamento");
};
window.openEdit=(l)=>{
  editId=l.id; setTipo(l.tipo);
  $("#f-descricao").value=l.descricao; $("#f-valor").value=l.valor;
  $("#f-categoria").value=l.categoria; $("#f-subcategoria").value=l.subcategoria;
  $("#f-data").value=(l.data||"").slice(0,10);
  if([...$("#f-usuario").options].some(o=>o.value===l.usuario)) $("#f-usuario").value=l.usuario;
  openModal("Editar lançamento");
};
$$("#f-tipo button").forEach(b=>b.onclick=()=>setTipo(b.dataset.v));
$("#modal-x").onclick=$("#modal-cancel").onclick=closeModal;
$("#modal-save").onclick=async()=>{
  const body={
    tipo:$("#f-tipo .active").dataset.v, descricao:$("#f-descricao").value.trim()||"Lançamento",
    valor:parseFloat($("#f-valor").value||0), categoria:$("#f-categoria").value.trim()||"Outros",
    subcategoria:$("#f-subcategoria").value.trim()||"Outros", usuario:$("#f-usuario").value, data:$("#f-data").value
  };
  const url=editId?`/api/lancamentos/${editId}`:"/api/lancamentos";
  await fetch(url,{method:editId?"PUT":"POST",headers:{"Content-Type":"application/json"},body:JSON.stringify(body)});
  closeModal(); toast(editId?"Lançamento atualizado":"Lançamento adicionado"); refreshAll();
};

// ===== Duplicar =====
let dupId=null;
window.openDup=(l)=>{ dupId=l.id; $("#dup-info").textContent=`Cópia de “${l.descricao}”. Ajuste apenas o valor.`; $("#dup-valor").value=l.valor; $("#dup").classList.remove("hidden"); };
$("#dup-x").onclick=$("#dup-cancel").onclick=()=>$("#dup").classList.add("hidden");
$("#dup-save").onclick=async()=>{
  await fetch(`/api/lancamentos/${dupId}/duplicate`,{method:"POST",headers:{"Content-Type":"application/json"},body:JSON.stringify({valor:parseFloat($("#dup-valor").value||0)})});
  $("#dup").classList.add("hidden"); toast("Lançamento duplicado"); refreshAll();
};

// ===== Confirmar exclusão =====
let delId=null, delCb=null;
window.askDelete=(id,desc)=>{ delId=id; delCb=refreshAll; $("#confirm-txt").innerHTML=`Excluir <b>“${desc}”</b>? Esta ação não pode ser desfeita.`; $("#confirm").classList.remove("hidden"); };
$("#confirm-no").onclick=()=>$("#confirm").classList.add("hidden");
$("#confirm-yes").onclick=async()=>{
  if(delMode==="cat"){ await fetch(delUrl,{method:"DELETE"}); $("#confirm").classList.add("hidden"); toast("Removido"); loadCats(); delMode=null; return; }
  if(delMode==="fixa"){ await fetch(`/api/fixas/${delId}`,{method:"DELETE"}); $("#confirm").classList.add("hidden"); toast("Fixa removida"); loadFixas(); delMode=null; return; }
  await fetch(`/api/lancamentos/${delId}`,{method:"DELETE"});
  $("#confirm").classList.add("hidden"); toast("Lançamento excluído"); (delCb||refreshAll)();
};

// ===== Categorias =====
let delMode=null, delUrl=null;
async function loadCats(){
  const d=await (await fetch("/api/categorias")).json();
  $("#cat-desp").innerHTML = d.despesas.length? d.despesas.map(c=>`
    <div class="crow"><span class="kw">${c.kw}</span>
      <span class="cmeta">${c.categoria} · ${c.subcategoria}</span>
      <div class="cacts">
        <button class="ico" onclick='editCat("despesa",${JSON.stringify(c)})'>✎</button>
        <button class="ico del" onclick='delCat("despesa","${encodeURIComponent(c.kw)}")'>🗑</button></div></div>`).join("")
    : `<p class="hint">Nenhuma palavra-chave.</p>`;
  $("#cat-rec").innerHTML = d.receitas.length? d.receitas.map(c=>`
    <div class="crow"><span class="kw">${c.kw}</span>
      <span class="cmeta">${c.subcategoria}</span>
      <div class="cacts">
        <button class="ico" onclick='editCat("receita",${JSON.stringify(c)})'>✎</button>
        <button class="ico del" onclick='delCat("receita","${encodeURIComponent(c.kw)}")'>🗑</button></div></div>`).join("")
    : `<p class="hint">Nenhuma palavra-chave.</p>`;
}
let catKind="despesa", catOld=null;
function openCat(kind, c){
  catKind=kind; catOld=c?c.kw:null;
  $("#cmodal-title").textContent=(c?"Editar":"Nova")+" palavra-chave";
  $("#c-kw").value=c?c.kw:""; $("#c-sub").value=c?c.subcategoria:"";
  $("#c-cat").value=c?(c.categoria||""):"";
  $("#c-cat-wrap").style.display = kind==="despesa"?"block":"none";
  $("#cmodal").classList.remove("hidden");
}
window.editCat=(k,c)=>openCat(k,c);
$("#add-desp").onclick=()=>openCat("despesa",null);
$("#add-rec").onclick=()=>openCat("receita",null);
$("#cmodal-x").onclick=$("#cmodal-cancel").onclick=()=>$("#cmodal").classList.add("hidden");
$("#cmodal-save").onclick=async()=>{
  const body={kw:$("#c-kw").value, kw_old:catOld, subcategoria:$("#c-sub").value||"Outros"};
  if(catKind==="despesa") body.categoria=$("#c-cat").value||"Outros";
  const r=await fetch(`/api/categorias/${catKind}`,{method:"POST",headers:{"Content-Type":"application/json"},body:JSON.stringify(body)});
  if(r.ok){ $("#cmodal").classList.add("hidden"); toast("Categoria salva"); loadCats(); }
  else toast("Palavra-chave inválida");
};
window.delCat=(kind,kw)=>{ delMode="cat"; delUrl=`/api/categorias/${kind}/${kw}`; $("#confirm-txt").innerHTML=`Remover a palavra-chave <b>“${decodeURIComponent(kw)}”</b>?`; $("#confirm").classList.remove("hidden"); };

// ===== Fixas =====
function fxRow(i){
  const rec = i.tipo==="Receita";
  const cls = i.pago ? (rec?"rec":"ok") : "pend";
  const txt = i.pago ? (rec?"Recebida":"Paga") : (rec?"A receber":"Pendente");
  const action = i.pago
    ? `<button class="btn-soft sm" onclick="fxDesfazer(${i.id})">Desfazer</button>`
    : `<button class="btn-primary sm" onclick="fxPagar(${i.id})">${rec?"Recebi":"Paguei"}</button>`;
  const quem = (i.usuario && i.usuario!=="—") ? " · "+dispName(i.usuario) : "";
  return `<div class="fx-row ${i.pago?'done':''}">
    <div class="fx-day">dia ${i.dia}</div>
    <div class="fx-main"><div class="fx-desc">${i.descricao}</div>
      <div class="fx-meta">${i.categoria} · ${i.subcategoria}${quem}</div></div>
    <span class="fx-status ${cls}">${txt}</span>
    <span class="fx-val ${rec?'rec':'desp'}">${fmt(i.valor)}</span>
    <div class="acts">${action}
      <button class="ico" title="Editar" onclick='fxEdit(${JSON.stringify(i)})'>✎</button>
      <button class="ico del" title="Excluir" onclick='fxAskDel(${i.id},${JSON.stringify(i.descricao)})'>🗑</button>
    </div></div>`;
}
async function loadFixas(){
  const d = await (await fetch("/api/fixas")).json();
  const r=d.resumo;
  $("#fx-stats").innerHTML = `
    <div class="stat"><span class="lbl">Despesas fixas</span><div class="ic red">↓</div><div class="val">${fmt(r.desp_total)}</div><div class="foot">Pago ${fmt(r.desp_pago)} · falta ${fmt(r.desp_pendente)}</div></div>
    <div class="stat"><span class="lbl">Receitas fixas</span><div class="ic green">↑</div><div class="val">${fmt(r.rec_total)}</div><div class="foot">Recebido ${fmt(r.rec_recebido)} · falta ${fmt(r.rec_pendente)}</div></div>
    <div class="stat ${r.desp_pendente<=0?"pos":"neg"}"><span class="lbl">A pagar ainda</span><div class="ic gold">◷</div><div class="val">${fmt(r.desp_pendente)}</div><div class="foot">Despesas pendentes</div></div>
    <div class="stat ${r.rec_pendente<=0?"pos":"neg"}"><span class="lbl">A receber ainda</span><div class="ic gold">◷</div><div class="val">${fmt(r.rec_pendente)}</div><div class="foot">Receitas pendentes</div></div>`;
  const desp=d.itens.filter(i=>i.tipo==="Despesa"), rec=d.itens.filter(i=>i.tipo==="Receita");
  $("#fx-desp").innerHTML = desp.length? desp.map(fxRow).join("") : `<p class="hint">Nenhuma conta fixa. Clique em “+ Nova conta”.</p>`;
  $("#fx-rec").innerHTML  = rec.length?  rec.map(fxRow).join("") : `<p class="hint">Nenhuma receita fixa. Clique em “+ Nova receita”.</p>`;
}
window.fxPagar = async(id)=>{ await fetch(`/api/fixas/${id}/pagar`,{method:"POST",headers:{"Content-Type":"application/json"},body:"{}"}); toast("Lançado no mês"); loadFixas(); loadOverview(); };
window.fxDesfazer = async(id)=>{ await fetch(`/api/fixas/${id}/desfazer`,{method:"POST"}); toast("Desfeito"); loadFixas(); loadOverview(); };

let fxEditId=null;
function fxSetTipo(v){ $$("#fx-tipo button").forEach(b=>b.classList.toggle("active",b.dataset.v===v)); }
function fxOpen(title){ $("#fxmodal-title").textContent=title; $("#fxmodal").classList.remove("hidden"); }
function fxClose(){ $("#fxmodal").classList.add("hidden"); }
function fxNew(tipo){
  fxEditId=null; fxSetTipo(tipo);
  $("#fx-descricao").value=""; $("#fx-valor").value=""; $("#fx-dia").value="";
  $("#fx-categoria").value=""; $("#fx-subcategoria").value="";
  fxOpen(tipo==="Receita"?"Nova receita fixa":"Nova conta fixa");
}
window.fxEdit=(i)=>{
  fxEditId=i.id; fxSetTipo(i.tipo);
  $("#fx-descricao").value=i.descricao; $("#fx-valor").value=i.valor; $("#fx-dia").value=i.dia;
  $("#fx-categoria").value=i.categoria; $("#fx-subcategoria").value=i.subcategoria;
  if([...$("#fx-usuario").options].some(o=>o.value===i.usuario)) $("#fx-usuario").value=i.usuario;
  fxOpen("Editar fixa");
};
$$("#fx-tipo button").forEach(b=>b.onclick=()=>fxSetTipo(b.dataset.v));
$("#fx-add-desp").onclick=()=>fxNew("Despesa");
$("#fx-add-rec").onclick=()=>fxNew("Receita");
$("#fxmodal-x").onclick=$("#fxmodal-cancel").onclick=fxClose;
$("#fxmodal-save").onclick=async()=>{
  const body={
    tipo:$("#fx-tipo .active").dataset.v, descricao:$("#fx-descricao").value.trim()||"Fixa",
    valor:parseFloat($("#fx-valor").value||0), dia:parseInt($("#fx-dia").value||1),
    categoria:$("#fx-categoria").value.trim()||"Outros", subcategoria:$("#fx-subcategoria").value.trim()||"Outros",
    usuario:$("#fx-usuario").value
  };
  const url=fxEditId?`/api/fixas/${fxEditId}`:"/api/fixas";
  await fetch(url,{method:fxEditId?"PUT":"POST",headers:{"Content-Type":"application/json"},body:JSON.stringify(body)});
  fxClose(); toast(fxEditId?"Fixa atualizada":"Fixa criada"); loadFixas();
};
window.fxAskDel=(id,desc)=>{ delMode="fixa"; delId=id; $("#confirm-txt").innerHTML=`Remover a fixa <b>“${desc}”</b>? Lançamentos já feitos permanecem.`; $("#confirm").classList.remove("hidden"); };

// ===== Gráficos =====
let CH={};
const GOLD="#B7933F",GREEN="#3E8E63",RED="#B4553F";
const PALETTE=["#B7933F","#CDB06A","#8B857A","#3E8E63","#B4553F","#D8C79A","#6E6A63","#A8894B"];
let _chDefaults=false;
async function loadCharts(){
  if(typeof Chart==="undefined"){ toast("Não foi possível carregar os gráficos"); return; }
  if(!_chDefaults){ Chart.defaults.font.family="Inter"; Chart.defaults.color="#8B857A"; Chart.defaults.font.size=12; _chDefaults=true; }
  const d=await (await fetch("/api/charts")).json();
  mk("c-rxd",{type:"doughnut",data:{labels:["Receitas","Despesas"],datasets:[{data:[d.rec_x_desp.receitas,d.rec_x_desp.despesas],backgroundColor:[GREEN,RED],borderWidth:0}]},options:donut()});
  mk("c-cat",{type:"doughnut",data:{labels:d.categoria.labels,datasets:[{data:d.categoria.values,backgroundColor:PALETTE,borderWidth:0}]},options:donut()});
  mk("c-mensal",{type:"line",data:{labels:d.mensal.labels,datasets:[
    {label:"Receitas",data:d.mensal.receitas,borderColor:GREEN,backgroundColor:"rgba(62,142,99,.08)",fill:true,tension:.4,borderWidth:2.5,pointRadius:3,pointBackgroundColor:GREEN},
    {label:"Despesas",data:d.mensal.despesas,borderColor:RED,backgroundColor:"rgba(180,85,63,.08)",fill:true,tension:.4,borderWidth:2.5,pointRadius:3,pointBackgroundColor:RED}]},options:axes(true)});
  mk("c-users",{type:"bar",data:{labels:d.usuarios.labels,datasets:[
    {label:"Receitas",data:d.usuarios.receitas,backgroundColor:GREEN,borderRadius:6,barThickness:22},
    {label:"Despesas",data:d.usuarios.despesas,backgroundColor:RED,borderRadius:6,barThickness:22}]},options:axes(true)});
  const top={labels:d.categoria.labels.slice(0,6),values:d.categoria.values.slice(0,6)};
  mk("c-top",{type:"bar",data:{labels:top.labels,datasets:[{data:top.values,backgroundColor:GOLD,borderRadius:6}]},options:{...axes(false),indexAxis:"y"}});
}
function mk(id,cfg){ if(CH[id])CH[id].destroy(); CH[id]=new Chart($("#"+id),cfg); }
function donut(){return{responsive:true,maintainAspectRatio:false,cutout:"66%",plugins:{legend:{position:"bottom",labels:{usePointStyle:true,padding:16,boxWidth:8}},tooltip:tt()}};}
function axes(legend){return{responsive:true,maintainAspectRatio:false,plugins:{legend:{display:legend,position:"bottom",labels:{usePointStyle:true,padding:16,boxWidth:8}},tooltip:tt()},scales:{x:{grid:{display:false},border:{display:false}},y:{grid:{color:"#F3EFE8"},border:{display:false},ticks:{callback:v=>"R$ "+v.toLocaleString("pt-BR")}}}};}
function tt(){return{backgroundColor:"#1D1B17",padding:12,cornerRadius:10,titleFont:{family:"Playfair Display"},callbacks:{label:c=>` ${c.dataset.label?c.dataset.label+": ":""}${fmt(c.parsed.y!=null?c.parsed.y:c.parsed)}`}};}

// ===== Boot =====
function refreshAll(){ loadOverview(); loadMeta().then(()=>{ loadTable("l"); if(!$("#view-historico").classList.contains("hidden")) loadTable("h"); }); }
bind("l"); bind("h");
loadMeta().then(()=>{ loadOverview(); loadTable("l"); });
