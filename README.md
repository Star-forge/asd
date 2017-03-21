# asd
Автоматизированная система диагностики рабочих мест  
Клиент-сервер с веб-интерфейсом  
  
## Проблематика  
Необходимость получения информации о состоянии РМ для информирования служб технической поддержки и администраторов  
  
## Решаемые задачи  
Получение информации о состоянии рабочих мест посредством WMI  

## Требования
Django==1.10.5  
djangorestframework==3.6.2  
pypiwin32==220  
WMI==1.4.9  

## Установка компонентов
1. Создание виртуального пространиства с именем asd_venv и вход в него(активация)  
1.1. python -m venv asd_venv  
1.2. asd_venv\Scripts\activate  
2. Обновление менеджера компонентов Питон и установка Джанго   
2.1. pip install --upgrade pip  
2.2. pip install django  
2.3. pip install pypiwin32  
2.4. pip install WMI==1.4.9  
или  
2.1. pip install -r requirements.txt  

## Дальнейшая установка
Производится настройка Django  
База данных заполняется начальными значениями при первом запросе к веб-серверу  
