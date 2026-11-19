const KEY='waste-detective-browser-v1';
let memory=[];
export function getRows(){
  try{const rows=JSON.parse(localStorage.getItem(KEY)||'[]');if(!Array.isArray(rows))return memory;memory=rows.filter(r=>r&&typeof r.id==='string'&&typeof r.category==='string'&&Number.isFinite(r.confidence)).slice(0,500);}catch{}
  return memory;
}
export function saveRow(row){memory=[row,...getRows()].slice(0,500);try{localStorage.setItem(KEY,JSON.stringify(memory));return true;}catch{return false;}}
export function clearTests(){memory=getRows().filter(row=>!row.is_test);try{localStorage.setItem(KEY,JSON.stringify(memory));return true;}catch{return false;}}
export function csv(rows){
  const fields=['id','created_at','image_id','category','candidate','confidence','status','source','elapsed_ms','model','prompt_version','threshold','margin_threshold','is_test'];
  const cell=value=>{let s=String(value??'');if(/^[=+@-]/.test(s))s="'"+s;return '"'+s.replaceAll('"','""')+'"';};
  return '\ufeff'+[fields,...rows.map(row=>fields.map(field=>row[field]))].map(row=>row.map(cell).join(',')).join('\r\n')+'\r\n';
}
