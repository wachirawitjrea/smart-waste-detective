export function classify(features, config) {
  const norm=Math.hypot(...features);
  if (!Number.isFinite(norm)||norm===0) throw new Error('Invalid image features');
  const logits=config.text_features.map(vector=>{
    if(vector.length!==features.length)throw new Error('Feature dimensions differ');
    return vector.reduce((sum,value,i)=>sum+value*features[i]/norm,0)*config.logit_scale;
  });
  const maximum=Math.max(...logits), exp=logits.map(x=>Math.exp(x-maximum));
  const denominator=exp.reduce((sum,x)=>sum+x,0);
  const ranked=exp.map((x,i)=>[config.labels[i],x/denominator]).sort((a,b)=>b[1]-a[1]);
  const [candidate,confidence]=ranked[0], margin=confidence-ranked[1][1];
  const accepted=candidate!=='Unknown'&&confidence>=config.settings.threshold&&margin>=config.settings.margin;
  return {category:accepted?candidate:'Unknown',candidate,confidence,margin,
    status:accepted?'classified':'uncertain',scores:Object.fromEntries(ranked),
    threshold:config.settings.threshold,margin_threshold:config.settings.margin,
    model:`${config.browser_model}@${config.browser_revision}:q8`,prompt_version:config.settings.prompt_version};
}
