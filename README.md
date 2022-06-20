# Проект парсинга pep

## Краткое описание проекта.

В проекте описан парсинг данных со страниц документации и PEP Python.  
На странице документации Python парсер скачивает архив с документацией Python,
собирает: ссылки на все статьи о нововведениях в Python, информацию о версиях Python.  
На странице документации с PEP парсер находит статус в общем списке и статус на отдельной странице 
каждого PEP. Статусы сравниваются и если есть отличие, то такой ответ логируется. 
Происходит подсчет количества PEP в каждом статусе и общее количество PEP.
В проекте настроено логирование.


### Технологии.
```
Python 3, Beautifulsoup4, PrettyTable
```
### Как запустить проект.

- Cоздать и активировать виртуальное окружение:

```
python3 -m venv venv
```

```
source venv/bin/activate
```

- Установить зависимости из файла requirements.txt:

```
python3 -m pip install --upgrade pip
```

```
pip install -r requirements.txt
```

- Вывод информации в терминал
```
python main.py pep 
```
- Вывод информации в csv файл
```
python main.py pep  --output file
```
- Cкачивание файла
```
python main.py downloads
```
- Очистка кеша
```
python main.py peps --clear-cache
```
- Вывод таблицы в терминал
```
python main.py latest-versions --output pretty
```

### Автор.
Анжела Намистюк
