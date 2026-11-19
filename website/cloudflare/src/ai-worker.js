import {AutoProcessor,CLIPVisionModelWithProjection,RawImage,env} from '@huggingface/transformers';
import {classify} from './classify.js';
env.allowLocalModels=false;
env.useBrowserCache=true;
env.backends.onnx.wasm.numThreads=1;
env.backends.onnx.wasm.proxy=false;
let session;
function load(config){
  if(!session)session=Promise.all([
    AutoProcessor.from_pretrained(config.browser_model,{revision:config.browser_revision}),
    CLIPVisionModelWithProjection.from_pretrained(config.browser_model,{
      revision:config.browser_revision,device:'wasm',dtype:'q8',
      progress_callback:p=>{if(p.status==='progress')self.postMessage({type:'progress',value:p.progress,file:p.file});},
    }),
  ]).catch(error=>{session=null;throw error;});
  return session;
}
self.onmessage=async({data})=>{
  try{
    const [processor,model]=await load(data.config);
    self.postMessage({type:'ready'});
    const started=performance.now();
    const image=new RawImage(new Uint8ClampedArray(data.pixels),data.width,data.height,3);
    const inputs=await processor(image);
    const output=await model(inputs);
    const result=classify(Array.from(output.image_embeds.data),data.config);
    result.elapsed_ms=Math.round((performance.now()-started)*10)/10;
    self.postMessage({type:'result',result});
  }catch(error){self.postMessage({type:'error',message:String(error.message||error)});}
};
