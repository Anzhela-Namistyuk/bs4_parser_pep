import logging

from requests import RequestException

from exceptions import ParserFindTagException


def get_response(session, url):
    response = session.get(url)
    response.encoding = 'utf-8'
    return response


def get_response_not_fail(session, url):
    try:
        get_response(session, url)
    except RequestException as err:
        logging.exception(
            f'Возникла ошибка при загрузке страницы {err.response.url}',
            stack_info=True
        )


def find_tag(soup, tag, attrs=None):
    searched_tag = soup.find(tag, attrs=(attrs or {}))
    if searched_tag is None:
        error_msg = f'Не найден тег {tag} {attrs}'
        logging.error(error_msg, stack_info=True)
        raise ParserFindTagException(error_msg)
    return searched_tag
