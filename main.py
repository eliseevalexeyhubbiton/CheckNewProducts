import sys
from pathlib import Path
import configparser
from products.checkproduct import CheckProduct


# ### INI-FILE
def check_data_from_ini_file(data: dict) -> bool:
    """
    Check Value data from ini-file - empty or not empty.
    :param data: Dictionary for check empty keys.
    :return:
    """
    result = True
    for key, value in data.items():
        if value == "":
            print(f"\t(!!) WARNING: Key '{key}' or Key and Value not found into ini-file.")
            exit(-1)  # result = False
    return result


def read_ini_file(file_ini: str) -> dict:
    """
    Read data from Ini-File.
    :param file_ini:
    :return:
    """
    result = dict()
    config = configparser.ConfigParser()
    config.read(file_ini)

    block = "SETTINGS"
    keys = ['site', 'debug',
            'email_to', 'email_from', 'email_password_from',
            'discord_webhook_url',
            'delay_between_parse_in_minutes', 'delay_between_send_in_seconds',
            'file_with_links',
            'send_to_email', 'send_to_discord', 'send_to_log_file',
            'xpath_count_products']
    try:
        for key in keys:
            result[key] = config[block][key]
            if result[key] == "False" or result[key] == "True":
                result[key] = config[block].getboolean(key)
    except KeyError:
        print(f"(!!)ERROR: Ini file must contain the following:\n"
              f"\t - block [SETTINGS]\n"
              f"\t - keys {keys}.")
        exit(-1)
    return result


# ### URLs-FILE
def check_urls(urls: list) -> list:
    """
    Check list URLs and correct links.
    :param urls: List URLs for check and correct.
    :return: List URLs for work.
    """
    result = list()
    for url in urls:
        if url == '':
            continue
        if url.find("page=") != -1:
            # find ok
            url_res = url[:url.find('page=')] + 'page=1'
            print(f'OK - {url_res}')
            result.append(url_res)
        else:
            # find no
            url_res = url + '&page=1'
            print(f'NO - {url_res}')
            result.append(url_res)
    return result


def read_urls(file_with_urls: str) -> list:
    """
    Read file with URLs for parsing.
    :param file_with_urls: Filename with URLs.
    :return: List URLs from file.
    """
    if Path(file_with_urls).exists() is not True:
        print("File with URLs Not Exist().")
        exit(-1)

    with open(file_with_urls, encoding='utf-8') as f:
        urls = f.read().split('\n')
    urls = check_urls(urls=urls)
    return urls


# ### PROCESS
def process(args: list) -> None:
    """
    Main Proccess.
    :param args: List launch params.
    :return: None
    """
    # ### ARGS
    settings_ini = "settings.ini"
    if len(args) > 1:
        if args[1] == "-h" or args[1] == "--help":
            print(f"HELP:\n"
                  f"\tmain.py [-h] [--help] [file_settings_ini]\n"
                  f"\t\t[-h] or [--help] - This Help-message;\n"
                  f"\t\t[file_settings_ini] - short filename in current dir or subdir with settings for app.")
            return
        if Path(args[1]).exists() is True:
            settings_ini = args[1]
    print(f"File settings '{settings_ini}'.")

    # ### INI
    if Path(settings_ini).exists() is not True:
        print("INI-file Not Exist().")
        return

    # ### URLs
    data_from_ini_file = read_ini_file(file_ini=settings_ini)
    if check_data_from_ini_file(data_from_ini_file) is False:
        return

    # ### DATA from INI-file
    check = CheckProduct()
    try:
        check.set_debug(debug=data_from_ini_file['debug'])
        check.set_site(site=data_from_ini_file['site'])
        check.set_access_email(access=data_from_ini_file['send_to_email'])
        check.set_access_discord(access=data_from_ini_file['send_to_discord'])
        check.set_access_log_file(access=data_from_ini_file['send_to_log_file'])
        check.set_email_to(email=data_from_ini_file['email_to'])
        check.set_email_and_password_from(email=data_from_ini_file['email_from'],
                                          password=data_from_ini_file['email_password_from'])
        check.set_discord_webhook_url(webhook=data_from_ini_file['discord_webhook_url'])
        check.set_delay_between_parse_in_minutes(minutes=int(data_from_ini_file['delay_between_parse_in_minutes'])*6)
        check.set_delay_between_send_in_seconds(seconds=int(data_from_ini_file['delay_between_send_in_seconds']))
        check.set_xpath_count_products(xpath=data_from_ini_file['xpath_count_products'])
    except ValueError:
        print(f'\tCheck correct data into {settings_ini}.')
        print(f'\t\tExample: may be you write Str-value for Int-variable.')
        return
    except Exception as error:
        print(f'Class Init error | {error}')
        return

    # ### Correct URLs
    urls = read_urls(file_with_urls=data_from_ini_file['file_with_links'])
    for url in urls:
        check.url_add(url=url)

    # ### Main Process
    check.start()
    return


if __name__ == "__main__":
    process(args=sys.argv)
