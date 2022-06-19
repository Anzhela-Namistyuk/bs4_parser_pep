import logging
import re
import requests_cache
from collections import Counter
from urllib.parse import urljoin

from bs4 import BeautifulSoup
from requests import RequestException
from tqdm import tqdm

from configs import configure_argument_parser, configure_logging
from constants import (BASE_DIR, EXPECTED_STATUS, MAIN_DOC_URL,
                       MAIN_DOC_URL_PYTHON)
from outputs import control_output
from utils import find_tag, get_response, get_response_not_fail


def whats_new(session):
    whats_new_url = urljoin(MAIN_DOC_URL_PYTHON, 'whatsnew/')
    response = get_response(session, whats_new_url)
    soup = BeautifulSoup(response.text, 'lxml')
    main_div = find_tag(soup, 'section', attrs={'id': 'what-s-new-in-python'})
    div_with_ul = find_tag(main_div, 'div', attrs={'class': 'toctree-wrapper'})
    sections_by_python = div_with_ul.find_all(
        'li', attrs={'class': 'toctree-l1'})
    results = [('Ссылка на статью', 'Заголовок', 'Редактор, Автор')]
    for section in tqdm(sections_by_python):
        version_a_tag = section.find('a')
        href = version_a_tag['href']
        version_link = urljoin(whats_new_url, href)
        response = get_response_not_fail(session, version_link)
        if response is None:
            continue
        soup = BeautifulSoup(response.text, 'lxml')
        h1 = find_tag(soup, 'h1')
        dl = find_tag(soup, 'dl')
        dl_text = dl.text.replace('\n', ' ')
        results.append(
            (version_link, h1.text, dl_text)
        )
    return results


def latest_versions(session):
    response = get_response(session, MAIN_DOC_URL_PYTHON)
    soup = BeautifulSoup(response.text, 'lxml')
    sidebar = find_tag(soup, 'div', attrs={'class': 'sphinxsidebarwrapper'})
    ul_tags = sidebar.find_all('ul')

    for ul in ul_tags:
        if 'All versions' in ul.text:
            a_tags = ul.find_all('a')
            break
        else:
            raise Exception('Ничего не нашлось')
    results = [('Ссылка на документацию', 'Версия', 'Статус')]
    pattern = r'Python (?P<version>\d\.\d+) \((?P<status>.*)\)'

    for a_tag in a_tags:
        link = a_tag['href']
        text_match = re.search(pattern, a_tag.text)
        if text_match:
            version, status = text_match.groups()
        else:
            version = a_tag.text
            status = ''
        results.append((link, version, status))

    return results


def download(session):
    downloads_url = urljoin(MAIN_DOC_URL_PYTHON, 'download.html')
    response = get_response(session, downloads_url)
    soup = BeautifulSoup(response.text, 'lxml')
    tag_table = find_tag(soup, 'table', {'class': 'docutils'})
    pdf_a4_tag = find_tag(tag_table, 'a',
                          {'href': re.compile(r'.+pdf-a4\.zip$')})

    pdf_a4_link = pdf_a4_tag['href']
    arcive_url = urljoin(downloads_url, pdf_a4_link)
    filename = arcive_url.split('/')[-1]
    downloads_dir = BASE_DIR / 'downloads'
    downloads_dir.mkdir(exist_ok=True)
    archive_path = downloads_dir / filename
    response = session.get(arcive_url)
    with open(archive_path, 'wb') as file:
        file.write(response.content)
    logging.info(f'Архив был загружен и сохранён: {archive_path}')


def find_status(link, session):
    version_link = urljoin(MAIN_DOC_URL, link)
    response = get_response_not_fail(session, version_link)
    soup = BeautifulSoup(response.text, 'lxml')

    table = find_tag(soup, 'dl', {'class': 'rfc2822 field-list simple'})
    status = (table.find(string='Status').parent
              .find_next_sibling('dd').string)
    return status


def pep(session):
    count_status = Counter()
    unexpected_statuses = []
    total = 0

    result = [('Статус', 'Количество')]
    peps_url = MAIN_DOC_URL
    response = get_response(session, peps_url)
    soup = BeautifulSoup(response.text, 'lxml')
    main_table = find_tag(soup, 'section',
                          attrs={'id': 'numerical-index'})  # нахожу все таблицы на странице
    body_table = find_tag(main_table, 'tbody')
    row = body_table.find_all('tr')  # В таблице нахожу все строки
    for column in row:  # в каждой строке просматриваю колонки
        status = find_tag(column, 'td')  # в первом теге td находится статус
        a_tag = find_tag(column, 'a')  # в первом теге <а> находится ссылка
        link = a_tag['href']  # находим ссылку
        status = status.text[1:]  # находим ожидаемый статус
        expected_statuses = EXPECTED_STATUS[status]
        new_status = find_status(link, session)
        if new_status is None:
            continue
        count_status[new_status] += 1
        total += 1
        if new_status not in expected_statuses:
            unexpected_statuses.append(
                f'{urljoin(MAIN_DOC_URL, link)}'
                f'\nСтатус в карточке: {new_status}\n'
                f'Ожидаемые статусы: {expected_statuses}'
            )
    logging.info(*unexpected_statuses)
    for key, value in count_status.items():
        result.append((key, str(value)))
    result.append(('Total', str(total)))
    return result


MODE_TO_FUNCTION = {
    'pep': pep,
    'whats-new': whats_new,
    'latest-versions': latest_versions,
    'download': download,
}


def main():
    configure_logging()
    logging.info('Парсер запущен!')
    arg_parser = configure_argument_parser(MODE_TO_FUNCTION.keys())
    args = arg_parser.parse_args()
    logging.info(f'Аргументы командной строки: {args}')

    session = requests_cache.CachedSession()
    if args.clear_cache:
        session.cache.clear()
    parser_mode = args.mode
    try:
        results = MODE_TO_FUNCTION[parser_mode](session)
    except RequestException as err:
        logging.exception(
            f'Возникла ошибка при загрузке страницы {err.response.url}',
            stack_info=True
        )

    if results is not None:
        control_output(results, args)
    logging.info('Парсер завершил работу.')


if __name__ == '__main__':
    main()
