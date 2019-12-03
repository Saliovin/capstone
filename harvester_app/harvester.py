from . import db_manager
import re
import os
import configparser
import requests
from . import logger
from bs4 import BeautifulSoup
from urllib.parse import urljoin
from getpass import getpass

logger = logger.ini_logger(__name__)


def get_parser(link):
    response = requests.get(link).text
    html_parser = BeautifulSoup(response, 'lxml')
    return html_parser


def get_program_info(html_parser, util_link):
    downloads = []
    string = html_parser.find(string=re.compile(r'v[0-9]*\.[0-9]*'))
    search = re.search(re.compile(r'v[0-9]*\.[0-9]*'), string)
    version = search.group(0)
    name = string[:search.start()]

    for tag in html_parser.select('a.downloadline'):
        if tag['href'].endswith(('.zip', '.exe')):
            downloads.append(urljoin(util_link, tag['href']))
    logger.info(f'Message: Found {len(downloads)} program files')
    return {'program_name': name.strip(),
            'program_version': version[1:].strip(),
            'downloads': downloads}


def get_translations(html_parser, util_link):
    translations = []
    table = html_parser.select('tr.utiltableheader')[-1].find_parent('table')
    table_rows = table.find_all('tr')[1:]

    for row in table_rows:
        table_data = row.find_all('td')
        translation = table_data[0].select_one('a')['href'].split('/')[-1]
        translation_version = table_data[-1].text.strip()
        link = urljoin(util_link, row.contents[0].next['href'])
        translations.append({'translation': translation,
                             'translation_version': translation_version,
                             'link': link})

    logger.info(f'Message: Found {len(translations)} translations')
    return translations


def download_file(link, version):
    logger.info(f'Downloading {link}')
    name = link.split("/")[-1]
    parent_path = os.path.abspath(os.path.dirname(__name__))
    path = f'{parent_path}{os.sep}downloads{os.sep}{version}-{name}'

    with open(path, "wb") as file:
        response = requests.get(link)
        file.write(response.content)

    return path


def nirsoft_scraper(link):
    logger.info('Message: Scraping nirsoft')
    program_info_list = []
    parser = get_parser(link)
    programs = parser.select("li > a:first-child")

    for program in programs:
        program_link = urljoin(link, program['href'])
        logger.info(f"Message: Parsing {program_link}")
        parser = get_parser(program_link)
        program_info = get_program_info(parser, program_link)
        program_info['translations'] = get_translations(parser, program_link)
        program_info_list.append(program_info)

    logger.info(f"Message: Found a total of {len(program_info_list)} programs")
    return program_info_list


def main():
    config = configparser.ConfigParser()
    path = os.path.abspath(os.path.dirname(__file__))
    config.read(f"{path}{os.sep}config.ini")
    config = config['default']
    password = getpass('Database password: ')
    data = nirsoft_scraper('http://54.174.36.110/')
    api = f'http://{config["api_container"]}:{config["api_port"]}/harvester/'
    download_list = db_manager.write_to_db(data,
                                           config['db_name'],
                                           config['username'],
                                           config['hostname'],
                                           password)

    for file in download_list:
        file_path = download_file(file['link'], file['version'])

        logger.info(f"Message: Posting {file['link'].split('/')[-1]} to API")
        files = {'file': open(file_path, 'rb')}

        r = requests.post(api, files=files)
        logger.info(f"{r.text} - {r.status_code}")


if __name__ == '__main__':
    main()
