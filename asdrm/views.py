import sys
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, get_object_or_404
# Импорт моделей
from .models import Auth
from .models import TestCase
from .models import TestParameter
from .models import TestStatus
from .models import TestSuite
from .models import TestAnalysis

# Импорт поддержки времени
from django.utils import timezone

# Импорт библиотеки для работы с wmi
from .wmiutil import *

# Импорт библиотеки доп. утилит
from .util import *

from django.views.generic.edit import FormView
from django.contrib.auth.forms import UserCreationForm

# Опять же, спасибо django за готовую форму аутентификации.
from django.contrib.auth.forms import AuthenticationForm

# Функция для установки сессионного ключа.
# По нему django будет определять, выполнил ли вход пользователь.
from django.contrib.auth import login

from django.http import HttpResponseRedirect
from django.views.generic.base import View
from django.contrib.auth import logout
from django.shortcuts import redirect

class LogoutView(View):
    def get(self, request):
        # Выполняем выход для пользователя, запросившего данное представление.
        logout(request)
        # После чего, перенаправляем пользователя на главную страницу.
        return HttpResponseRedirect("/")
'''
def user_login_view(request):
    isIE8 = False
    agent = request.META['HTTP_USER_AGENT']
    if ('MSIE 8.0'.lower() in agent.lower()) or ('compatible'.lower() in agent.lower()):
        isIE8 = True
        print("IE = " + request.META['HTTP_USER_AGENT'])
    else:
        print(request.META['HTTP_USER_AGENT'])

    form = LoginFormView

    return render(request, 'test.html', {'form': form, 'isIE8': isIE8})

class LoginFormView(FormView):
    form_class = AuthenticationForm

    # Аналогично регистрации, только используем шаблон аутентификации.
    template_name = "test.html"

    # В случае успеха перенаправим на главную.
    success_url = "/"

    def form_valid(self, form):
        # Получаем объект пользователя на основе введённых в форму данных.
        self.user = form.get_user()

        # Выполняем аутентификацию пользователя.
        login(self.request, self.user)
        return super(LoginFormView, self).form_valid(form)
'''
class RegisterFormView(FormView):
    form_class = UserCreationForm

    # Ссылка, на которую будет перенаправляться пользователь в случае успешной регистрации.
    # В данном случае указана ссылка на страницу входа для зарегистрированных пользователей.
    success_url = "/login/"

    # Шаблон, который будет использоваться при отображении представления.
    template_name = "register.html"

    def form_valid(self, form):
        # Создаём пользователя, если данные в форму были введены корректно.
        form.save()

        # Вызываем метод базового класса
        return super(RegisterFormView, self).form_valid(form)

# Представление списка ранее выполненных диагностик
@login_required
def asdrm_testsuite_list(request) :
    # isIE8 = False
    # agent = request.META['HTTP_USER_AGENT']
    # if ('MSIE 8.0'.lower() in agent.lower()) or ('compatible'.lower() in agent.lower()):
    #     isIE8 = True
    #     print("IE = "+request.META['HTTP_USER_AGENT'])
    # else:
    #     print(request.META['HTTP_USER_AGENT'])

    # Выполнение запроса QuerySet к базе данных
    tests = TestSuite.objects.filter(start_date__lte=timezone.now()).order_by('start_date')
    # tests = TestCase.objects.filter(start_date__lte=testsuites).order_by('pk')
    # Возвращение отрисованной (готовой) страницы вместе с полученными из бд данными (шаблон+данные=готовая страница)
    return render(request, 'test_list.html', {'tests': tests})

# Представление ранее выполненной диагностики
@login_required
def asdrm_testsuite_complete(request, pk) :
    # isIE8 = False
    # agent = request.META['HTTP_USER_AGENT']
    # if ('MSIE 8.0'.lower() in agent.lower()) or ('compatible'.lower() in agent.lower()):
    #     isIE8 = True
    #     print("IE = " + request.META['HTTP_USER_AGENT'])
    # else:
    #     print(request.META['HTTP_USER_AGENT'])

    # Выполнение запроса QuerySet к базе данных - сли есть, то возврат, иначе 404
    # for ts in TestSuite.objects.all() :
    #     print(ts.pk)
    testSuite = get_object_or_404(TestSuite, pk=pk)
    # Получение списка параметров и их заголовков для заполнения таблицы
    testParams = TestParameter.objects.all().order_by('pk')
    testParamTitles = list(set(testParam.title for testParam in testParams))
    # поиск ранее созданного списка проверок и запись в него результатов проверки
    testSuiteCases = TestCase.objects.filter(testSuite=testSuite)
    return render(request, 'test.html', {'testsuite': testSuite,
                                         'user': request.user,
                                         'testParams': testParams,
                                         'testParamTitles': testParamTitles,
                                         'testSuiteCases': testSuiteCases})


# Представление основной страницы
@login_required
def asdrm_main(request) :
    # isIE8 = False
    # agent = request.META['HTTP_USER_AGENT']
    # if ('MSIE 8.0'.lower() in agent.lower()) or ('compatible'.lower() in agent.lower()):
    #     isIE8 = True
    #     print("IE = " + request.META['HTTP_USER_AGENT'])
    # else:
    #     print(request.META['HTTP_USER_AGENT'])

    username = request.user
    # Если запрос GET (значит это запрос на диагностику) - параметры анализируются
    if request.method == 'GET':
        # в ip записывается значение параметра ip - если есть, иначе записывается 0
        ip = request.GET.get('ip', request.GET.get('IP', '0'))
        # Если ip не равен 0
        if ip != '0' :
            # Если БД не содержит записей Статусов, то она вероятно пустая, а это первый запуск
            if(TestStatus.objects.count() == 0):
                # в таком случае запись в БД стандартных данных
                TestStatus(text = 'OK').save()
                TestStatus(text = 'FAIL').save()
                # TestParameter(name = '', title = '', info = '').save()
                TestParameter(name='Доступность ПК по сети передачи данных', title='СПД', info='Выполняется команда ping').save()
                TestParameter(name='135/TCP порт', title='СПД', info='Удаленный вызов процедур (RPC)').save()
                TestParameter(name='137/UDP порт', title='СПД', info='Определение NetBIOS-имени машины').save()
                TestParameter(name='139/TCP порт', title='СПД', info='Для обеспечения сетевых операций ввода-вывода и управления низлежащим транспортным протоколом - TCP/IP').save()
                TestParameter(name='445/TCP порт', title='СПД', info='Удаленный доступ к файловой системе, принтерам, службам и реестру').save()
                TestParameter(name='Конфигурация', title='ПК', info='Выводятся технические характеристики ПК: частота и разрядность процессора, размер оперативной памяти, общий объем жестких дисков.').save()
                TestParameter(name='ОС', title='ПК', info='Выводится название и версия операционной системы, установленный пакет обновления, разрядность ОС, дата установки.').save()
                TestParameter(name='Диски', title='ПК', info='Определяется текущее состояние заполнения дисковой системы. Выводится информация при свободном объеме каждого из дисков. ').save()
                TestParameter(name='Последняя загрузка ОС', title='ПК', info='Определяется время последней перезагрузки ПК').save()

                Auth(name = r'Starforge', passw = r'Password', domain = r'127.0.0.1').save()

            # регистрируется время начала
            _start_date = timezone.now()

            # Получение списка параметров и их заголовков для заполнения таблицы
            testParams = TestParameter.objects.all().order_by('pk')
            testParamTitles = list(set(testParam.title for testParam in testParams))

            # Инициализация объекта через который выполняется работа с wmi
            wmi_util = WmiUtil()
            if ip != "127.0.0.1" :
                # Данные для подключения к другому ПК
                wmi_util._computer = ip
                wmi_util._user = Auth.objects.last().domain + "\\" + Auth.objects.last().name
                wmi_util._password = Auth.objects.last().passw
            wmi_util.start() # запуск потока - подключение по WMI и получение данных
            wmi_util.join() # синхронизация (этот поток ожидает проверки данных в другом потоке, который был запущен ранее)

            # регистрируется время окончания
            _end_date = timezone.now()

            # Как только закончены затратные по времени процессы получения данных с удалённого ПК
            # Создание объекта тестового набора, с которым позже будут связаны результаты проверки
            testSuite = TestSuite(
                user=request.user,
                ipv4 = ip,
                start_date = _start_date,
                end_date = _end_date
            )
            testSuite.save() # Запись набора в БД

            # Инициализация переменных
            _result = "2"       # Результат проверки параметра. Первая цифра - цвет текста результата в представлении:
                                # 0-зеленый, 1-красный, 2-желтый, 3-красный
            _status = 'FAIL'    # статус проверки параметра
            ping_ret = ping_service(ip) # получение результата проверки на поступность
            for testParam in testParams : # Перебор и анализ всех параметров
                if(testParam.name == 'Доступность ПК по сети передачи данных') :
                    try :
                        if ping_ret == 0 : # Если ПК доступен
                            _result = '0ПК доступен по сети'
                        else :
                            _result = '1ПК не доступен по сети'
                        _status = 'OK'
                    except : # Если произошла ошибка-текст ошибки выводится в представлении
                        _result = '1' + str(sys.exc_info()[0])
                        _status = 'FAIL'
                elif(testParam.name == '135/TCP порт') :
                    try :
                        if ping_ret == 0 : # Если ПК доступен
                            ret_code = checkTcpPort(135, server=ip) # Проверка порта
                            if ret_code == 0 : # Если проверка порта удачна запись результата и удачного статуса
                                _result = '0TCP порт 135 открыт'
                            else :
                                _result = '1TCP порт 135 закрыт или иная ошибка в процессе'
                            _status = 'OK'
                        else : # Если ПК не доступен
                            _status = 'FAIL' # Изменение только статуса т.к. в таком случае результат уже есть
                    except : # Если произошла ошибка-текст ошибки выводится в представлении
                        _result = '1' + str(sys.exc_info()[0])
                        _status = 'FAIL'
                elif (testParam.name == '137/UDP порт') :
                    try :
                        if ping_ret == 0: # Если ПК доступен
                            ret_code = checkUdpPort(137, server=ip) # Проверка порта
                            if ret_code == 0 : # Если проверка порта удачна запись результата и удачного статуса
                                _result = '0UDP порт 137 открыт'
                            else :
                                _result = '1UDP порт 137 закрыт или иная ошибка в процессе'
                            _status = 'OK'
                        else : # Если ПК не доступен
                            _status = 'FAIL' # Изменение только статуса т.к. в таком случае результат уже есть
                    except : # Если произошла ошибка-текст ошибки выводится в представлении
                        _result = '1' + str(sys.exc_info()[0])
                        _status = 'FAIL'
                elif (testParam.name == '139/TCP порт') :
                    try :
                        if ping_ret == 0: # Если ПК доступен
                            ret_code = checkTcpPort(139, server=ip) # Проверка порта
                            if ret_code == 0 : # Если проверка порта удачна запись результата и удачного статуса
                                _result = '0TCP порт 139 открыт'
                            else :
                                _result = '1TCP порт 139 закрыт или иная ошибка в процессе'
                            _status = 'OK'
                        else : # Если ПК не доступен
                            _status = 'FAIL' # Изменение только статуса т.к. в таком случае результат уже есть
                    except : # Если произошла ошибка-текст ошибки выводится в представлении
                        _result = '1' + str(sys.exc_info()[0])
                        _status = 'FAIL'
                elif (testParam.name == '445/TCP порт') :
                    try :
                        if ping_ret == 0: # Если ПК доступен
                            ret_code = checkTcpPort(445, server=ip) # Проверка порта
                            if ret_code == 0 : # Если проверка порта удачна запись результата и удачного статуса
                                _result = '0TCP порт 445 открыт'
                            else :
                                _result = '1TCP порт 445 закрыт или иная ошибка в процессе'
                            _status = 'OK'
                        else : # Если ПК не доступен
                            _status = 'FAIL' # Изменение только статуса т.к. в таком случае результат уже есть
                    except : # Если произошла ошибка-текст ошибки выводится в представлении
                        for strexc in sys.exc_info() :
                            _result += "\n" + str(strexc)
                        _status = 'FAIL'
                elif (testParam.name == 'Конфигурация') :
                    try :
                        if ping_ret == 0:                   # Если ПК доступен
                            ret_code = wmi_util.wmi_error   # запись кода ошибки
                            if not ret_code :               # если текста ошибки WMI нет, то всё ОК
                                _result = "3" + "Процессор:"
                                _result += "\n___Название: " + wmi_util.processor[0]
                                _result += "\n___Максимальная частота: " + wmi_util.processor[1]
                                _result += "\n___Количество ядер: " + wmi_util.processor[2]
                                _result += "\n___Количество логических процессоров: " + wmi_util.processor[3]
                                _result += "\nОперативная память:"
                                _result += "\n___Общий объём: " + human_size(wmi_util.ram[0])
                                _result += "\n___Свободный Объём: " + human_size(wmi_util.ram[1])
                                _status = 'OK'
                            else :                           # Если текст ошибки есть, то выводим его
                                _result = '1' + ret_code
                                _status = 'FAIL'
                        else : # Если ПК не доступен
                            _status = 'FAIL' # Изменение только статуса т.к. в таком случае результат уже есть
                    except : # Если произошла ошибка-текст ошибки выводится в представлении
                        _result = '1'
                        for strexc in sys.exc_info() :
                            _result += "\n" + str(strexc)
                        _status = 'FAIL'
                elif (testParam.name == 'ОС') :
                    try :
                        if ping_ret == 0:                   # Если ПК доступен
                            ret_code = wmi_util.wmi_error   # запись кода ошибки WMI
                            if not ret_code :               # если текста ошибки WMI нет, то всё ОК
                                _result = '3Название ОС: ' + wmi_util.osName + "\nАрхитектура: " + wmi_util.osArchitecture
                                _status = 'OK'
                            else:                           # Если текст ошибки есть, то выводим его
                                _result = '1' + ret_code
                                _status = 'FAIL'
                        else: # Если ПК не доступен
                            _status = 'FAIL' # Изменение только статуса т.к. в таком случае результат уже есть
                    except : # Если произошла ошибка-текст ошибки выводится в представлении
                        _result = '1'
                        for strexc in sys.exc_info() :
                            _result += "\n" + str(strexc)
                        _status = 'FAIL'
                elif (testParam.name == 'Диски') :
                    try :
                        if ping_ret == 0:                   # Если ПК доступен
                            ret_code = wmi_util.wmi_error   # запись кода ошибки WMI
                            if not ret_code:                # если текста ошибки WMI нет, то всё ОК
                                _result = "3Информация о дисках:"
                                for disk in wmi_util.disks:
                                    _result += "\n" + disk.Caption + " " + disk.Description + " [" +  human_size(int(disk.Size or 0)) + "/" +  human_size(int(disk.FreeSpace or 0)) + "]"
                                _status = 'OK'
                            else:                           # Если текст ошибки есть, то выводим его
                                _result = '1' + ret_code
                                _status = 'FAIL'
                        else : # Если ПК не доступен
                            _status = 'FAIL' # Изменение только статуса т.к. в таком случае результат уже есть
                    except : # Если произошла ошибка-текст ошибки выводится в представлении
                        _result = '1'
                        for strexc in sys.exc_info() :
                            _result += "\n" + str(strexc)
                        _status = 'FAIL'
                elif (testParam.name == 'Последняя загрузка ОС') :
                    try :
                        if ping_ret == 0:                   # Если ПК доступен
                            ret_code = wmi_util.wmi_error   # запись кода ошибки WMI
                            if not ret_code:                # если текста ошибки WMI нет, то всё ОК
                                _result = "3" + "Дата последней загрузки ОС: " + wmi_util.lastBootUpTime
                                _status = 'OK'
                            else:                           # Если текст ошибки есть, то выводим его
                                _result = '1' + ret_code
                                _status = 'FAIL'
                        else : # Если ПК не доступен
                            _status = 'FAIL' # Изменение только статуса т.к. в таком случае результат уже есть
                    except : # Если произошла ошибка-текст ошибки выводится в представлении
                        _result = '1'
                        for strexc in sys.exc_info() :
                            _result += "\n" + str(strexc)
                        _status = 'FAIL'

                # Запись параметра, его результата и статуса в БД
                testCase = TestCase(
                    testSuite = testSuite,
                    parameter = testParam,
                    status = TestStatus.objects.get(text=_status),
                    result = _result,
                    start_date = timezone.now(),
                    end_date = timezone.now()
                    )
                testCase.save()

            # поиск ранее созданного списка проверок и запись в него результатов проверки
            testSuiteCases = TestCase.objects.filter(testSuite=testSuite)
            return render(request, 'test.html', {'testsuite': testSuite,
                                                 'user': username,
                                                 'testParams': testParams,
                                                 'testParamTitles': testParamTitles,
                                                 'testSuiteCases': testSuiteCases})
    # Если запрос не GET
    # else:
    #     ip = 0

    # Возвращение отрисованной (готовой) страницы вместе с полученными из бд данными (шаблон+данные=готовая страница)
    # Если это главная страница без нужных запросов - приветствуем пользователя
    return render(request, 'test.html', {'user': username})