import asyncio,sys,json
from playwright.async_api import async_playwright
async def m():
  async with async_playwright() as p:
    import shutil;ch=shutil.which('google-chrome');b=await p.chromium.launch(**({'executable_path':ch} if ch else {}),args=['--no-sandbox','--allow-file-access-from-files'])
    pg=await b.new_page(viewport={'width':1000,'height':400})
    for cap in sys.argv[1:]:
      await pg.goto((__import__('pathlib').Path(__file__).resolve().parent/'lock.html').as_uri()+f'?cap={cap}');await pg.wait_for_selector('body[data-ready]',state='attached')
      L=await pg.evaluate('L');await pg.locator('canvas').screenshot(path=f'lock-{cap}.png',omit_background=True);print(cap,round(L['inkW']),round(L['tfs'],1),L['pad'])
    await b.close()
asyncio.run(m())
