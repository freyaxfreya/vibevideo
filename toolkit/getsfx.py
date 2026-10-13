import sys, json, asyncio
from playwright.async_api import async_playwright
async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch(); pg = await b.new_page(viewport={"width":1920,"height":1080})
        await pg.goto("file://"+sys.argv[1]); await pg.wait_for_timeout(1500)
        data = await pg.evaluate("window.__sfx"); json.dump(data, open(sys.argv[2],"w")); print(len(data), "events")
        await b.close()
asyncio.run(main())
