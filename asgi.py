"""ASGI entrypoint for Vercel and uvicorn; the UI remains a Streamlit script."""
import os
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent

if os.environ.get('VERCEL') == '1':
    # Vercel vendors packages outside site-packages. Streamlit otherwise infers
    # developmentMode=True from its package path and omits its frontend routes.
    os.environ['STREAMLIT_GLOBAL_DEVELOPMENT_MODE'] = 'false'
    # A serverless instance can only write temporary files. This is demo storage,
    # not a persistent or shared database across instances/deployments.
    os.environ.setdefault('WASTE_DB', str(Path(tempfile.gettempdir()) / 'waste-detective/waste.db'))
    os.environ.setdefault('STREAMLIT_SERVER_FILE_WATCHER_TYPE', 'none')

import streamlit as st
from streamlit import config

if os.environ.get('VERCEL') == '1':
    # The Python host can import Streamlit before this module, caching its
    # inferred config before the environment override. Set the parsed value too.
    config.set_option('global.developmentMode', False)

app = st.App(ROOT / 'app.py')

if os.environ.get('VERCEL') == '1':
    from streamlit import config, file_util
    print('Streamlit ASGI production:',
          'developmentMode=' + str(config.get_option('global.developmentMode')),
          'static_assets=' + str(Path(file_util.get_static_dir()).is_dir()))
