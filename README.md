# marketplace_scraper

## О проекте
Всегда считал, что для хорошего Python разработчика написать какой-либо парсер не является проблемой. <br>
Но вот у меня с этой технологией как-то не складывалось, поэтому я решил изменить эту ситуацию и углубиться в данную тему 🤓

Существует простенький веб-ресурс, который представляет собой простейшую модель маркетплейса.<br>
Именно на нем я буду тренироваться в данном проекте.

## Цели проекта

Изначально, перед парсером стояла задача просто посчитать общую стоимость товаров, размещенных в магазине.
Конечно, это все можно сделать через пару циклов, можно даже написать функции или их асинхронные аналоги.
Но я решил, что если начинать что-то изучать, то подходить к процессу серьезно 👨‍💻

Задачи, которые я поставил перед проектом:
* __Скорость работы__ <br>
Так как парсер обычно обрабатывает множество ресурсов, то я решил, что мой должен работать быстро
* __Запись данных в файлы различных форматов__ <br>
JSON, CSV

## Стек технологий:
- python
- requests
- bs4
- lxml
- httpx
- pre-commit
- black

## Текущий функционал

В данный момент реализованы следующий возможности:

- Получение URL адресов всех категорий товаров
```python
start_time = time.perf_counter()

url_parser = URLParser()
await url_parser.get_category_urls()

print(f'Elapsed time: {time.perf_counter() - start_time}')
# Elapsed time: 0.13041989994235337
```

- Получение URL адресов всех страниц со всех категорий товаров
```python
start_time = time.perf_counter()

url_parser = URLParser()
await url_parser.get_url_for_each_category_page()

print(f'Elapsed time: {time.perf_counter() - start_time}')
# Elapsed time: 0.41123030008748174
```

- Получение URL адресов всех товаров на площадке
```python
start_time = time.perf_counter()

url_parser = URLParser()
await url_parser.get_url_for_each_product_card()

print(f'Elapsed time: {time.perf_counter() - start_time}')
# Elapsed time: 0.7981272999895737
```

- Получение общей стоимости всех товаров, размещенных на площадке
```python
start_time = time.perf_counter()
url_parser = URLParser()
data_parser = DataParser()

product_url_list = await url_parser.get_url_for_each_product_card()
await data_parser.get_total_product_price(product_url_list)

print(f'Elapsed time: {time.perf_counter() - start_time}')
# Elapsed time: 2.8478403000626713
```

# ToDo List

Необходимо реализовать следующий функционал:
- запись данных в файлы
- подключить SQLAlchemy
- подключить Postgresql через asyncpg


## Лицензия
marketplace scraper распространяется по [MIT License](https://opensource.org/licenses/MIT).
