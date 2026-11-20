import config from './public/config.json';

const modelPath = `${config.browser_model}/resolve/${config.browser_revision}/`;
const files = new Map([
  ['config.json', 'application/json'],
  ['preprocessor_config.json', 'application/json'],
  ['onnx/vision_model_quantized.onnx', 'application/octet-stream'],
]);
const modelPrefix = '/model-assets/';

export default {
  async fetch(request, env) {
    const {pathname} = new URL(request.url);
    if (!pathname.startsWith(modelPrefix)) return env.ASSETS.fetch(request);

    const path = pathname.slice(modelPrefix.length);
    const file = path.startsWith(modelPath) ? path.slice(modelPath.length) : '';
    const contentType = files.get(file);
    if (!contentType) return new Response('Model asset not found', {status: 404});
    if (request.method !== 'GET' && request.method !== 'HEAD') {
      return new Response(null, {status: 405, headers: {Allow: 'GET, HEAD'}});
    }

    try {
      // Only the pinned public files are requested. No browser headers or image data are forwarded.
      const upstream = await fetch(`https://huggingface.co/${modelPath}${file}`, {
        method: request.method,
        redirect: 'follow',
      });
      if (!upstream.ok) {
        await upstream.body?.cancel();
        console.warn('Model asset download failed', file, upstream.status);
        return new Response('Model download unavailable', {status: 502});
      }

      const headers = new Headers({
        'Content-Type': contentType,
        'Cache-Control': 'public, max-age=31536000, immutable',
        'X-Content-Type-Options': 'nosniff',
      });
      // Workers derives Content-Length from the body stream when its size is known.
      return new Response(upstream.body, {headers});
    } catch (error) {
      console.warn('Model asset download failed', file, error.message);
      return new Response('Model download unavailable', {status: 502});
    }
  },
};
