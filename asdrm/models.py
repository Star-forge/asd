from django.db import models
from django.utils import timezone

'''
Для представления данных таблицы в виде объектов Python, 
Django использует интуитивно понятную систему: 
класс модели представляет таблицу, а экземпляр модели - запись в этой таблице.
Primary key - идентификатор записи может быть не указан. 
Django, в таком случае, подставляет (стандартный) целочисленный идентификатор
'''
# Модели таблиц БД
'''
Auth - класс данных, необходимых для авторизации на тестируемом ПК
Данные используются в процессе подключния по WMI
Подключение по WMI требует 4 параметра:
name - имя пользователя, от чьего имени будут получены данные
passw - пароль пользователя, от чьего имени будут получены данные
domain - домен(пользователя), необходим для авторизации пользователя
4-й параметр меняется  - адрес тестируемого ПК (запрашивается формой на странице)
'''
class Auth(models.Model):
    name = models.CharField(max_length=100)
    passw = models.CharField(max_length=100)
    domain = models.CharField(max_length=100)

'''
TestParameter - класс данных, параметры по которым проходит диагностика - строка в выдаче
name - имя параметра
title - заголовок, используется для объединения в группы - чтобы пользователь мог визуально проще искать параметр диагностики в выдаче
info - справочная информация - помогает пользователю ориентироваться что какой параметр означает
'''
class TestParameter(models.Model):
    name = models.CharField(max_length=100)
    title = models.CharField(max_length=100)
    info = models.CharField(max_length=500)

'''
TestStatus - класс данных - список статусов проверки
По сути, - список из вариантов концовок выполнения тестового(диагностического) случая
text - текст определенной концовки
Предполагается использовать:  'OK' - Успешное завершение; 'FAIL' - Ошибка в процессе выполнения
'''
class TestStatus(models.Model):
    text = models.CharField(max_length=100)

'''
TestCase - класс данных - тестовый случай (какого либо параметра)
Соответственно, первое это parameter - параметр, по которому проходит диагностика
testSuite - ссылка на набор тестовых случаев, к которому относится
status - статус проверки. 
Его отличие от результата в том, что результат отражает данные определенного параметра, 
в то время как Статус это отражение самого факта получения данных.
Например, в ответ от диагностируемого ПК получена пустая строка. 
Пользователь не может определить по ней где получено данное значение: на сайте или на тестируемом ПК...
Статус успешного завершения указывает на то, что эти данные успешно олучены от тестируемого ПК.
Статус ошибки в процессе выполнения означает, что пустая строка результат ошибки, 
а не пустого значения на тестируемом ПК.
result - данныве полученные на тестируемом ПК.
start_date - время начала диагностики параметра
end_date - время окончания диагностики параметра
'''
class TestCase(models.Model):
    testSuite = models.ForeignKey('TestSuite')  # TestCase *<--->1 TestSuite
                                                # набор тестов может содержать множество тестовых случаев,
                                                # но у тестовый случай может быть связан только с одной диагностикой
                                                # это как вытаскивать из горшка и выкидывать монеты -
                                                # нельзя дважды вытащить одну и ту же монету (она будет уже выброшена)
    parameter = models.ForeignKey('TestParameter') # TestCase *<--->1 TestParameter
    status = models.ForeignKey('TestStatus') # TestCase *<--->1 TestStatus
    result = models.TextField()
    start_date = models.DateTimeField(default=timezone.now)
    end_date = models.DateTimeField(default=timezone.now)

'''
TestSuite - класс данных - тестовый набор
Набор диагностик выполненных по просьбе пользователя
user - пользователь заказавший диагностику
ipv4 - ip адрес (в 4-й нотации) диагностируемого ПК
start_date - время начала диагностики параметра
end_date - время окончания диагностики параметра
'''
class TestSuite(models.Model):
    user = models.ForeignKey('auth.User')   # TestSuite *<--->1 user ---1
                                            # пользователь может заказать множество диагностик,
                                            # но у диагностики может быть всего один заказсчик
    ipv4 = models.CharField(max_length=20)
    start_date = models.DateTimeField(default=timezone.now)
    end_date = models.DateTimeField(default=timezone.now)

'''
TestAnalysis - класс данных, результаты анализа данных тестового случая
test_case - проанализированный тестовый случай 
recomendation - рекомендация (результат анализа данных)
'''
class TestAnalysis(models.Model):
    test_case = models.OneToOneField('TestCase')
    recomendation = models.TextField()