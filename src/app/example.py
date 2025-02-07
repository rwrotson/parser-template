import tempfile

from fake_useragent import UserAgent
from base.bs4.interface import parse_html
from base.selenium.drivers import create_driver, ChromeDriver, ChromeOptions
from base.selenium.interface import BrowserInterface

options = ChromeOptions()
options.add_argument("--headless")
options.add_argument("--no-sandbox")
options.add_argument("--window-size=1920,1080")
options.add_argument("--disable-gpu")
options.add_argument("--disable-dev-shm-usage")
options.add_argument(f"--user-data-dir={tempfile.mkdtemp()}")

user_agent = UserAgent(browsers=["Chrome"], os=["Linux"], platforms=["desktop"])

driver = create_driver("undetected_chrome", options=options, user_agent=user_agent)
driver.set_window_size(1920, 1080)
interface = BrowserInterface(webdriver=driver)


def get_yandex_page() -> None:
    interface.get("https://yandex.ru/")
    interface.save_screenshot('/app/media/screenshots/test.png')

    element = interface.find_bs4_element_by("xpath", '//*[@id="card-news-morda"]/article/div[2]')

    for i, child in enumerate(list(list(element.children)[0].children)[0].children):
        print(f"Element {i}: {child.text}")



def main():
    with interface:
        get_yandex_page()


if __name__ == "__main__":
    main()
