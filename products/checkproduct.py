import requests
from time import sleep
from lxml import html
from bs4 import BeautifulSoup
import smtplib
from email.message import EmailMessage
import datetime
import logging
import logging.handlers as handlers


class CheckProduct:
    """
    Find product on site.
    If new product then Send message about new product to e-Mail or/and Discord (WebHook).
    """
    debug = False

    site = ""
    urls = list()  # list URLs for work
    xpath_count_products = ""

    access_email = False
    access_discord = False
    access_log_file = False

    log_file_max_size = 100*1024*1024  # 100 MB

    email_to = ""  # this email target
    email_from = ""  # from this email send message
    email_password_from = ""  # password for email send message

    discord_webhook_url = ""

    delay_between_parse_in_minutes = 0
    delay_between_send_in_seconds = 0
    delay_between_bad_request_in_seconds = 30
    delay_between_urls_parsing_in_seconds = 5

    log_file = "debug"
    logger = None

    count_request_error = 0

    def __init__(self):
        """
        Constructor.
        """
        pass

    # ### Debug
    def set_debug(self, debug: bool) -> None:
        """
        Set Debug state.
        :param debug: New state Debug variable.
        :return:
        """
        self.debug = debug

    # ### Site
    def set_site(self, site: str) -> None:
        """
        Set Site value.
        :param site: Site link.
        :return: None
        """
        self.site = site

    # ### Xpath for parsing
    def set_xpath_count_products(self, xpath: str) -> None:
        """
        Set XPath value for find Count products in page.
        :param xpath: XPath string.
        :return: None
        """
        self.xpath_count_products = xpath

    # ### ACCESS
    def set_access_email(self, access: bool) -> None:
        """
        Set Access for email send state.
        :param access:
        :return: None
        """
        self.access_email = access

    def set_access_discord(self, access: bool) -> None:
        """
        Set Access for discord send state.
        :param access:
        :return: None
        """
        self.access_discord = access

    def set_access_log_file(self, access: bool) -> None:
        """
        Set Access for log file state.
        :param access:
        :return: None
        """
        self.access_log_file = access

    # ### Size debug file
    def set_log_file_max_size(self, size: int) -> None:
        """
        Set Max size for Debug-File.
        :param size: New Max Size.
        :return: None
        """
        self.log_file_max_size = size

    # ### URLs
    def url_add(self, url: str) -> None:
        """
        Add "url" for work.
        :param url: This "url" add to "urls" list.
        :return: None
        """
        self.urls.append(url)

    def url_clear(self) -> None:
        """
        Clear list "urls".
        :return: None
        """
        self.urls.clear()

    def url_remove(self, url: str) -> bool:
        """
        This "url" remove from "urls" list.
        :param url: This "url" delete from work "urls" list.
        :return: If "url" find into "urls" then return True another False.
        """
        if url in self.urls:
            self.urls.remove(url)
            return True
        return False

    # ### E-mails
    def set_email_to(self, email: str) -> None:
        """
        Set address email To.
        :param email: Address email To.
        :return: None
        """
        self.email_to = email

    def set_email_from(self, email: str) -> None:
        """
        Set address email From.
        :param email: Email address.
        :return: None
        """
        self.email_from = email

    def set_email_password_from(self, password: str) -> None:
        """
        Set password for email From.
        :param password:
        :return: None
        """
        self.email_password_from = password

    def set_email_and_password_from(self, email: str, password: str) -> None:
        """
        Set email and password for email From.
        :param email: Address email From.
        :param password: Password for email From.
        :return: None
        """
        self.set_email_from(email=email)
        self.set_email_password_from(password=password)

    # ### Webhook
    def set_discord_webhook_url(self, webhook: str) -> None:
        """
        Set Webhook.
        :param webhook: Webhook link.
        :return: None
        """
        self.discord_webhook_url = webhook

    # ### Delays
    def set_delay_between_parse_in_minutes(self, minutes: int) -> None:
        """
        Set delay after ending parsing.
        :param minutes: Time in minutes for delay.
        :return: None
        """
        self.delay_between_parse_in_minutes = minutes

    def set_delay_between_send_in_seconds(self, seconds: int) -> None:
        """
        Set delay between send messages about new products.
        :param seconds: Time in seconds for delay.
        :return: None
        """
        self.delay_between_send_in_seconds = seconds

    def set_delay_between_bad_request_in_seconds(self, seconds: int) -> None:
        """
        Set delay between bad GET request.
        :param seconds: Time in seconds for delay.
        :return: None
        """
        self.delay_between_bad_request_in_seconds = seconds

    def set_delay_between_urls_parsing_in_seconds(self, seconds: int) -> None:
        """
        Set delay between URLs parsing.
        :param seconds: Time in seconds for delay.
        :return: None
        """
        self.delay_between_urls_parsing_in_seconds = seconds

    # ### DEBUG message
    def debug_msg(self, msg: str) -> None:
        """
        Message in console if Debug mode active.
        :param msg:  Message for output console.
        :return: None
        """
        if self.debug is True:
            print(f"debug_msg -> {msg}")

    def add_to_log_file(self, message: str) -> None:
        """
        Add message to log file.
        :param message:
        :return: None
        """
        if self.access_log_file is False:
            return
        self.logger.info(message)
        return

    # ### SEND
    def send_to_email(self, message: str) -> None:
        """
        Send E-mail.
        :param message: Message for send to E-Mail.
        :return: None
        """
        if self.access_email is False:
            return
        e_message = EmailMessage()
        e_message.set_content(message)
        e_message['Subject'] = f"Check {self.site} bot"
        e_message['From'] = self.email_from
        e_message['To'] = self.email_to
        try:
            server = smtplib.SMTP('smtp.gmail.com', 587)
            server.starttls()
            server.ehlo()
            server.login(self.email_from, self.email_password_from)
            server.sendmail(self.email_from, self.email_to, message)
            server.quit()
        except Exception as error:
            print(f'SMTP error | {error}')
        return

    def send_to_discord(self, message: str) -> None:
        """
        Send message to Discord.
        :param message: Message for send to Discord.
        :return: None
        """
        if self.access_discord is False:
            return
        data = {
            "content": message,
            "username": f"Check {self.site} bot."
        }

        result = requests.post(self.discord_webhook_url, json=data)

        try:
            result.raise_for_status()
        except requests.exceptions.HTTPError as error:
            error_message = f"(!!)ERROR: send_to_discord -> {error}"
            self.logger.info(error_message)
            print(error_message)
        return

    def send_messages(self, message: str) -> None:
        """
        Send Messages to services.
        :param message: Message for Send.
        :return: None
        """
        print(f"SEND--------->>>>>> {message}.")
        if self.debug is True:
            print(message)
        else:
            self.send_to_discord(message=message)
            self.send_to_email(message=message)
        sleep(self.delay_between_send_in_seconds)
        return

    # ### SERVICE FOR WORK
    def get_count_products(self, res_text) -> int:
        """
        This function return count product on page.
        :param res_text: Text page.
        :return: Count products on this page.
        """
        tree = html.fromstring(res_text)
        try:
            count = int(tree.xpath(self.xpath_count_products)[1].split(" ")[2])
        except (IndexError, ValueError, TypeError):
            count = -1
            print('products not found')
        return count

    def get_collect_products_on_page(self, url: str) -> dict:
        """
        Return dict() with products from 'url'.
        :param url: URL for parsing products.
        :return: Dict() products.
        """
        result = dict()
        res_text = requests.get(url).text
        soup = BeautifulSoup(res_text, "lxml")
        all_products = soup.find_all('div', class_='col-s-12 col-m-8 col-l-6')
        for idx, element in enumerate(all_products):
            link = self.site + element.find('a').get('href')
            brand = element.find(class_='product-card__brand').text.strip()
            model = element.find(class_='product-card__name dotdotdot js-truncate').text.strip()
            colors = element.find(class_='product-card__colour').text.strip()
            if element.find('div', class_='js-price') is not None:
                # no discount
                price = element.find('div', class_='js-price').text.strip()
            else:
                # discount
                price = element.find('span', class_='js-price product-card__price-now').text.strip()

            result[link] = dict()
            result[link]['brand'] = brand
            result[link]['model'] = model
            result[link]['colors'] = colors
            result[link]['price'] = price
        return result

    def init_logger(self) -> None:
        """
        Init state 'logger'.
        :return: None
        """
        self.logger = logging.getLogger('class_CheckProduct')
        self.logger.setLevel(logging.INFO)
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        errorLogHandler = handlers.RotatingFileHandler(self.log_file+'_info.log', maxBytes=self.log_file_max_size,
                                                       backupCount=1, encoding='UTF-8')
        errorLogHandler.setLevel(logging.INFO)
        errorLogHandler.setFormatter(formatter)
        self.logger.addHandler(errorLogHandler)
        return

    def get_first_page_for_parsing(self, url: str) -> requests:
        """
        Get request after GET page.
        :param url: URL for work.
        :return: Request after GET page.
        """
        result = None
        self.count_request_error = 0
        while self.count_request_error < 3:
            try:
                result = requests.get(url)
                if result.status_code == 200 and len(result.text) > 1000:
                    break
                else:
                    self.debug_msg(f"request error, will try again after 30 sec")
                    sleep(self.delay_between_bad_request_in_seconds)
                    self.count_request_error += 1
            except Exception as error:
                self.debug_msg(f"error: {error}\n trying again...")
                sleep(5)
                self.count_request_error = 10

        self.debug_msg(f"self.count_request_error = {self.count_request_error}")
        return result

    def analysis_old_and_new_products(self, count_products_old: int, count_products_new: int,
                                      products_old: dict, products_new: dict) -> None:
        """
        Analize products after new parsing.
        :param count_products_old: Count products Previous parsing.
        :param count_products_new: Count products Current parsing.
        :param products_old: Dictionary products Previous parsing.
        :param products_new: Dictionary products Current parsing.
        :return: None
        """
        new_items = 0
        for key, value in products_new.items():
            if key in products_old.keys():
                pass
            else:
                new_items += 1
                self.debug_msg(f"prod no [{key}] = {value}.")
                message_for_send = f"New product: Brand: {value['brand']}; Model: {value['model']}; " \
                                   f"Colors: {value['colors']}; Price: {value['price']}; Link: {key} ."
                self.send_messages(message_for_send)
                self.add_to_log_file(message_for_send)
        if new_items > 0:
            message_for_send = f"{new_items} new products"
            self.send_messages(message_for_send)
            self.add_to_log_file(message_for_send)
            print(f"new items:  {new_items}. Count products: "
                  f"['old']={count_products_old}, "
                  f"['new']={count_products_new}.")
        return

    # ### WORK
    def start(self) -> None:
        """
        Main Process.
        :return: None
        """
        # init Logging
        self.init_logger()

        # init variables
        count_products_old = dict()
        count_products_new = dict()
        products_old = dict()  # key=url, value={brand=str, model=str, colors=str, price=str}
        products_new = dict()  # key=url, value={brand=str, model=str, colors=str, price=str}
        for url in self.urls:
            count_products_old[url] = 0
            count_products_new[url] = 0
            products_old[url] = dict()
            products_new[url] = dict()

        # main cycle
        while True:
            # clear list for new products
            self.debug_msg("while True: --------------------------------------------------------->>")
            self.add_to_log_file(f"{datetime.datetime.now()}")
            for url in self.urls:
                self.debug_msg(f"products_new[{url}].clear()")
                products_new[url].clear()

            # start new parse data from site
            for url in self.urls:
                self.debug_msg(f"-->{url}")

                page_request = self.get_first_page_for_parsing(url=url)
                if self.count_request_error > 2:
                    self.send_messages(f"This URL: '{url}' in config-file BAD!!")
                    continue

                count_products_new[url] = self.get_count_products(res_text=page_request.text)
                self.debug_msg(f"count_products_new[{url}]  = {count_products_new[url]}")
                if count_products_new[url] == -1:
                    continue

                max_pages = int(count_products_new[url] / 60) + 2
                self.debug_msg(f"max_pages  = {max_pages - 1}")
                for page in range(1, max_pages):
                    self.debug_msg(f"page[{page}]")
                    url_next_page = url[:url.find('page=') + 5] + str(page)
                    products_new[url].update(self.get_collect_products_on_page(url=url_next_page))

                self.debug_msg(f"{url} - {products_new[url]}")
                self.analysis_old_and_new_products(count_products_old=count_products_old[url],
                                                   count_products_new=count_products_new[url],
                                                   products_old=products_old[url],
                                                   products_new=products_new[url])
                products_old[url] = products_new[url].copy()
                sleep(self.delay_between_urls_parsing_in_seconds)
            time_off = datetime.datetime.now() + datetime.timedelta(seconds=self.delay_between_parse_in_minutes)
            print(f"Next checking in {time_off}.")
            sleep(self.delay_between_parse_in_minutes)
