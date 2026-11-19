"""Regression check for an ASGI host that imports Streamlit before our app.

Run in a fresh process: python scripts/smoke_asgi.py
Only requests static HTML and health; it does not add database events.
"""
import os,asyncio,sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from streamlit import config
config.set_option('global.developmentMode',True)
os.environ['VERCEL']='1'
import asgi
async def request(path):
 messages=[]
 async def receive():return {'type':'http.request','body':b'','more_body':False}
 async def send(message):messages.append(message)
 scope={'type':'http','asgi':{'version':'3.0','spec_version':'2.4'},'http_version':'1.1','method':'GET','scheme':'http','path':path,'raw_path':path.encode(),'query_string':b'','root_path':'','headers':[(b'host',b'localhost')],'client':('127.0.0.1',1234),'server':('localhost',80)}
 await asgi.app(scope,receive,send)
 status=next(m['status'] for m in messages if m['type']=='http.response.start')
 body=b''.join(m.get('body',b'') for m in messages if m['type']=='http.response.body')
 return status,body
async def main():
 status,body=await request('/')
 assert status==200 and b'<title>Streamlit</title>' in body,(status,body[:200])
 assert (await request('/_stcore/health'))[0]==200
 print('Pre-import regression: root HTML 200 and health 200')
 from streamlit.runtime import Runtime
 Runtime.instance().stop()
 await asyncio.sleep(.1)
asyncio.run(main())
