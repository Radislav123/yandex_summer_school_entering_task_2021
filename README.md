1) если не сказано иное, команды выполняются из корня проекта.
2) везде, где используется `python` в командах, в Unix необходимо использовать `python3` (и `pip` => `pip3`)


# Оглавление
- [Запуск сервера](#запуск-сервера)
- [Реализованные обработчики](#реализованные-обработчики)
  - [POST /couriers](#post-couriers)
  - [PATCH /couriers/$courier_id](#patch-courierscourier_id)
- [Из задания](#из-задания)
  - [На что обратить внимание](#на-что-обратить-внимание)
  - [Также оценивается](#также-оценивается)
- [Project_env](#project_env)
  - [Активация интерпретатора](#активация-интерпретатора)
- [Требуемые модули](#требуемые-модули)
- [Описание модулей проекта](#описание-модулей-проекта)
  - [Не модули, но тоже присутствуют](#не-модули,-но-тоже-присутствуют)
- [База данных](#база-данных)
  - [Первоначальная настройка БД](#первоначальная-настройка-БД)
  - [Модели](#модели)
- [Скрипты](#скрипты)


# Запуск сервера
`python manage.py runserver 0.0.0.0:8080`


# Реализованные обработчики

## POST /couriers
Обработчик принимает на вход в формате json список с данными о курьерах и графиком их работы.
Курьеры работают только в заранее определенных районах,
а так же различаются по типу: пеший (foot), велокурьер (bike) и курьер на автомобиле (car). От типа курьера
зависит его грузоподъемность — 10 кг, 15 кг и 50 кг соответственно.
Районы задаются целыми положительными числами. График работы задается списком строк формата HH:MM-HH:MM .

### Пример запроса
`POST /couriers`
```json
{
  "data":[
    {
      "courier_id": 1,
      "courier_type": "foot",
      "regions": [1, 12, 22],
      "working_hours": ["11:35-14:05", "09:00-11:00"]
    },
    {
      "courier_id": 2,
      "courier_type": "bike",
      "regions": [22],
      "working_hours": ["09:00-18:00"]
    },
    {
      "courier_id": 3,
      "courier_type": "car",
      "regions": [12, 22, 23, 33],
      "working_hours":[]
    }
  ]
}
```

### Описание полей
Все поля обязательны.
- `courier_id` - целое положительное число (Уникальный идентификатор курьера, положительное число.
                                          Идентификаторы уникальны в пределах всего сервиса.)
- `courier_type` - строка (Тип курьера. Возможные значения:
                         foot — пеший курьер
                         bike — велокурьер
                         car — курьер на автомобиле.)
- `regions` - массив целых положительных чисел (Список идентификаторов районов, в которых работает курьер.)
- `working_hours` - массив строк (График работы курьера. Формат строки HH:MM-HH:MM. Есть гарантия на
                                то, что промежутки, переданные тестирующей системой, не будут
                                пересекаться.)

### Ответы
В случае, если в наборе есть неописанные поля или какие-либо из полей отсутствуют — следует вернуть ошибку `HTTP
400 Bad Request` и список id, которые не удалось провалидировать.  
Пример:  
`HTTP 400 Bad Request`
```json
{
  "validation_error": {
    "couriers": [{"id": 2}, {"id": 3}]
  },
  "validation_error_details": [
    {
      "courier_id": 2,
      "message": "CourierType with such name does not exist"
    },
    {
      "courier_id": 3,
      "message": "list of regions can not be empty"
    }
  ],
  "request_data": [
    {
      "courier_id": "one",
      "courier_type": "foot",
      "regions": [1, 12, 22],
      "working_hours": ["11:35-14:05", "09:00-11:00"]
    },
    {
      "courier_id": 2,
      "courier_type": "bike and car",
      "regions": [22],
      "working_hours": ["09:00-18:00"]
    },
    {
      "courier_id": 3,
      "courier_type": "car",
      "regions": ["eleven", 22, 23, 33],
      "working_hours": ["11:00-22:00"]
    },
    {
      "courier_id": 4,
      "courier_type": "car",
      "regions": [22, 23, 33],
      "working_hours": [11, 22]
    }
  ]
}
```

В случае успеха — вернуть ответ `HTTP 201 Created` и списком импортированных id.  
Пример:  
`HTTP 201 Created`
```json
{
  "couriers": [{"id": 1}, {"id": 2}, {"id": 3}]
}
```

## PATCH /couriers/$courier_id
Позволяет изменить информацию о курьере. Принимает json и любые поля из списка:
courier_type, regions, working_hours.
При редактировании следует учесть случаи, когда меняется график и уменьшается грузоподъемность и появляются заказы,
которые курьер уже не сможет развести — такие заказы должны сниматься и быть доступными для выдачи другим курьерам.

### Пример запроса
`PATCH /couriers/2`
```json
{
  "regions": [11, 33, 2]
}
```

### Ответы
В случае, если передано неописанное поле — вернуть `HTTP 400 Bad Request`.  
Пример:  
`HTTP 400 Bad Request`
```json
{
  "validation_error_details": [
    {
      "courier_id": 2,
      "message": "CourierType with such ('car and bike') name does not exist"
    }
  ],
  "request_data": {
    "regions": [11, 33, "string"],
    "courier_type": "car and bike",
    "courier_id": "2"
  }
}
```

В случае успеха — `HTTP 200 OK` и актуальную информацию о редактируемом курьере.  
Пример:  
`HTTP 200 OK`
```json
{
  "courier_id": 2,
  "courier_type": "foot",
  "regions": [11, 33, 2],
  "working_hours": ["09:00-18:00"]
}
```


# Из задания

## На что обратить внимание
- [x] валидация входных данных ([*models.py*](candy_shop/shop_api/models.py))
- [x] все даты должны быть в формате, удовлетворяющем ISO 8601 и RFC 3339
- [x] статусы HTTP ответов
- [x] структура json на входе и выходе
- [x] типы данных (строки, числа)
- [x] URL без trailing slash

## Также оценивается
- [ ] наличие реализованного обработчика 6: GET /couriers/$courier_id
- [x] наличие структуры с подробным описанием ошибок каждого (только первого некорректного поля в структуре)
некорректного поля, пришедшего в запросе
- [x] явно описанные внешние python-библиотеки (зависимости) ([*requirements.txt*](requirements.txt))
- [x] наличие тестов ([*candy_shop/shop_api/tests*](candy_shop/shop_api/tests))
- [x] наличие файла README в корне репозитория с инструкциями:
    - [ ] по [*установке/развертыванию*](https://coderanch.com/t/132937/engineering/difference-deployment-installation)
    - [x] по запуску сервиса
    - [x] по запуску тестов
- [ ] автоматическое возобновление работы REST API после перезагрузки виртуальной машины
- [ ] возможность обработки нескольких запросов сервисом одновременно

### Инструкции
1) как установить/развернуть:
    0) (описывается процесс на чистой машине, которую дают для выполнения этого задания)
    1) установить git
    `sudo apt install git`
    2) склонить проект (но проект приватный так что тут нужен к нему доступ)
    `git clone https://github.com/Radislav123/yandex_summer_school_entering_task.git`
    3) перейти в корень проекта
    `cd yandex_summer_school_entering_task`
    3) обновить apt
    `sudo apt update`
    4) установить pip
    `sudo apt install python3-pip`
    5) установить необходимые зависимости
    `pip3 install -r requirements.txt`
    6) инициализировать БД
    `python3 manage.py runscript initialize_db`
    7) запустить сервер
    `python3 manage.py runserver 0.0.0.0:8080`
2) как запустить сервис
    1) необходимо выполнить следующую команду:  
    `python manage.py runserver 0.0.0.0:8080`
3) как запустить тесты
    1) для запуска всех тестов, что есть в проекте, необходимо выполнить следующую команду:  
    `python manage.py test`
    2) для более подробного лога необходимо добавить `-v 2`:  
    `python manage.py test -v 2`
    3) для запуска конкретных тестов смотреть
    [*сюда*](https://docs.djangoproject.com/en/3.1/topics/testing/overview/#running-tests)


# Project_env
[*Как*](https://www.jetbrains.com/help/idea/creating-virtual-environment.html)
создать виртуальное окружение.  
Папка для интерпретатора - [*venv/*](venv)

## Активация интерпретатора
```
project_env/Scripts/activate        # Unix
project_env/Scripts/activate.bat    # Windows
```

# Требуемые модули
`pip install -r requirements.txt`
  
[*requirements.txt*](https://pip.pypa.io/en/stable/user_guide/#requirements-files)


# Описание модулей проекта
1) [*candy_shop*](candy_shop) - django-проект
2) [*candy_shop/shop_api*](candy_shop/shop_api) - django-приложение, собственно, api
3) [*candy_shop/shop_api/tests*](candy_shop/shop_api/tests) - тесты api

## Не модули, но тоже присутствуют
1) [*attachments/*](attachments) - разное, но полезное
2) [*venv/*](venv) - интерпретатор


# База данных
Используется встроенная sqlite БД.

## Первоначальная настройка БД
1) для создания и инициализации БД необходимым, для корректной работы api, минимумом данных,
требуется выполнить следующую команду:  
`python3 manage.py runscript initialize_db`

## Модели
Структура таблиц описана в файле [*candy_shop/shop_api/models.py*](candy_shop/shop_api/models.py).  
После внесения в [*файл моделей*](candy_shop/shop_api/models.py) любых изменений,
касающихся структуры таблиц или базы, нужно выполнить следующие команды для внесения изменений в саму БД.  
```
python manage.py makemigrations
python manage.py migrate
```
После добавления/изменения каких-то функций в модель эти команды выполнять не нужно.


# Скрипты  
Скрипты необходимо размещать в [*candy_shop/shop_api/scripts/*](candy_shop/shop_api/scripts).  
Для запуска скрипта нужно выполнить команду  
`python manage.py runscript <название скрипта (без .py)>`

```
add_courier_types_to_db     - добавляет в БД типы курьеров (car/bike/foot)
add_couriers_to_db          - добавляет 3 курьеров в БД (для тестов)
database_for_test           - содержит действия, которые необходимо выполнить до и после тестов (View)
```
