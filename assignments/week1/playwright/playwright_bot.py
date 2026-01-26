import asyncio
from playwright.async_api import async_playwright


async def step(msg, delay=2):
    print(f"👉 {msg}")
    await asyncio.sleep(delay)


async def main():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False, slow_mo=100)
        page = await browser.new_page()

        await step("Opening Netflix")
        await page.goto("https://www.netflix.com")

        await step("Clicking Sign In")
        await page.locator('a[data-uia="header-login-link"]').click()

        await step("Waiting for phone/email input")
        phone = page.locator('xpath=//input[@name="userLoginId"]')
        await phone.wait_for()
        await phone.fill("12345678")

        await step("Clicking Continue button")
        await page.locator('xpath=//button[@type="submit"]').click()

        await step("Waiting for next page to load", 3)
        await page.wait_for_load_state("domcontentloaded")

        await step("Collecting metadata")

        title = await page.title()
        url = page.url
        user_agent = await page.evaluate("navigator.userAgent")
        viewport = page.viewport_size
        locale = await page.evaluate("navigator.language")

        meta_tags = await page.evaluate("""
            Array.from(document.querySelectorAll('meta'))
            .map(m => `${m.name || m.property || m.charset || m.httpEquiv} = ${m.content}`)
        """)

        await step("Writing metadata to text file")

        with open("netflix_metadata.txt", "w", encoding="utf-8") as f:
            f.write(f"Title: {title}\nURL: {url}\n")
            f.write(f"UserAgent: {user_agent}\n")
            f.write(f"Viewport: {viewport}\n")
            f.write(f"Locale: {locale}\n\nMETA TAGS:\n")
            f.write("\n".join(meta_tags))

        await step("Done. Closing browser", 2)
        await browser.close()


asyncio.run(main())
