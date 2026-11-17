# EYRA avatar badge: python3 render.py '{"avatar-800":""}'  -> avatar-800.png (800x800). Params: see badge.html
import asyncio,sys,json,shutil
from pathlib import Path
from playwright.async_api import async_playwright
HERE=Path(__file__).resolve().parent
V=json.loads(sys.argv[1]) if len(sys.argv)>1 else {'avatar-800':''}
async def main():
  async with async_playwright() as p:
    ch=shutil.which('google-chrome') or shutil.which('google-chrome-stable')
    kw=dict(executable_path=ch) if ch else {}
    b=await p.chromium.launch(args=['--no-sandbox','--allow-file-access-from-files'],**kw);pg=await b.new_page(viewport={'width':800,'height':800});pg.on('pageerror',lambda e:print('ERR',e))
    for name,q in V.items():
      await pg.goto((HERE/'badge.html').as_uri()+'?'+q);await pg.wait_for_selector('body[data-ready]',state='attached')
      await pg.screenshot(path=f'{name}.png');print(name,await pg.evaluate('document.body.dataset.ink'))
    await b.close()
asyncio.run(main())
