import sys, asyncio
from playwright.async_api import async_playwright
async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch()
        pg = await b.new_page(viewport={"width":1920,"height":1080})
        errs=[]; pg.on("pageerror", lambda e: errs.append(str(e))); pg.on("console", lambda m: errs.append("console:"+m.text) if m.type=="error" else None)
        await pg.goto("file://"+sys.argv[1]); await pg.wait_for_timeout(1500)
        print("TOTAL", await pg.evaluate("window.__TOTAL")); [print(x) for x in await pg.evaluate("window.__beats")]
        print("ERRS", errs)
        await b.close()
asyncio.run(main())
