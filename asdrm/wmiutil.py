import pythoncom
import wmi
import threading
import time
import sys

# Класс утилит для работы с Инструментарием Управления Виндовс(WMI). Все запросы выполняются строго поочерёдно
# TODO в дальнейшем для каждого параметра будет свой поток и все они будут выполняться асинхронно друг с другом
class WmiUtil(threading.Thread):
    # поля класса утилит. описывают состояние процесса получния данных через инструментарий.
    # Состояние подключения к инструментарию:
    wmi_error = None    # Здесь хранится ошибка, если она возникает
    wmiObject = None    # Здесь хранится объект, посредством которого получаются данные

    # Параметры необходимые для подключения (авторизации)
    _computer = None
    _user = None
    _password = None

    # Состояние - результаты диагностики
    osArchitecture = None
    osName = None
    disks = None
    lastBootUpTime = None
    ram = None
    processor = None

    # Функция инициализации, поскольку ничего делать при запуске не надо,
    # кроме как инициировать поток. то ничего больше и не делается
    def __init__(self) :
        threading.Thread.__init__(self)

    # Функция выполнения потока, его тело.
    def run(self) :
        pythoncom.CoInitialize()    # Подготовка СОМ, это необходимо т.к. реализация WMI на питоне это некоторого рода обёртка на СОМ
        try:
            # Если необходимо проверить ПК
            if(self._computer) :
                self.connect_by_wmi()       # Подключение к ПК
            else :
                self.wmiObject = wmi.WMI()  # Иначе подключение к самому себе (к серверу) и опрос

            # Последовательное получение данных о ПК
            '''___ОС___'''
            self.osArchitecture = getOSArchitecture(self.wmiObject)
            self.osName = getOSName(self.wmiObject)

            '''___Конфигурация___'''
            self.ram = getRAMInfo(self.wmiObject)
            self.processor = getProcessorInfo(self.wmiObject)

            '''___Диски___'''
            self.disks = getDiskInfo(self.wmiObject)

            '''___Последняя загрузка ОС___'''
            self.lastBootUpTime = getLastBootUpTime(self.wmiObject)
        except : # Если ошибка - вывод её в консоль, более ничего не требуется т.к. исключение либо было, либо будет отловлено позже
            print(self.wmi_error)

        finally : # В любом случае
            pythoncom.CoUninitialize() # Отключение СОМ т.к. работа с ней закончена

    # Функция одключение к ПК
    def connect_by_wmi(self) :
        try:
            self.wmiObject = wmi.WMI(computer = self._computer, user = self._user, password = self._password)
        except wmi.x_wmi_timed_out:  # Если ошибка - скорее всего сервер это localhost - его нельзя проверять под уч. данными (только без параметров как указано ниже
            self.wmi_error = "Ошибка WMI - ВРЕМЯ НА ВЫПОЛНЕНИЕ ВЫШЛО."
        except wmi.x_access_denied:
            self.wmi_error = "Ошибка WMI - ДОСТУП ЗАКРЫТ (ErrCode:0x80070005)"
        except wmi.x_wmi_authentication:
            self.wmi_error = "Ошибка WMI - ДАННЫЕ ДЛЯ АУТЕНТИФИКАЦИИ НЕ ВЕРНЫ."
        except wmi.x_wmi:  # Если ошибка - скорее всего сервер это localhost - его нельзя проверять под уч. данными (только без параметров как указано ниже
            self.wmi_error = "Ошибка WMI - НЕИЗВЕСТНАЯ ПРОБЛЕМА. Данные о проблеме:"
            for strexc in sys.exc_info(): # Сохранение деталей ошибки
                self.wmi_error += "\n" + str(strexc)

# Функция отправляет запрос wmi и получает с помощью него архитектуру ОС 32 или 64bit,
# информация о котором находится в классе Win32_OperatingSystem
# Получает как параметр объект wmi, с помощью которого делается запрос
# возвращает строку в форме, которая указана в целевой ОС, строку "32-bit", если выброшено исключение wmi
# (Например, если запись не найдена). Конкретная причина возникновения исключеия не устанавливается.
# или строку "N/A", если данные не доступны по причине WindowsError.
def getOSArchitecture(wmiObject):
    # Запись об архитектуре ОС (32/64 bit) доступна только для ОС Vista и более новых
    try:
        # Далее практичеки аналогично функции getReleaseDate
        osArchitecture = wmiObject.Win32_OperatingSystem(["OSArchitecture"])[0].OSArchitecture
    except WindowsError:
        osArchitecture = "N/A"
    except wmi.x_wmi:  # Если ОС XP, 2003, 2000, 98, 95, ...
        osArchitecture = "32-bit"
    return (osArchitecture)


# Функция отправляет запрос wmi и получает с помощью него название ОС,
# информация о котором находится в классе Win32_OperatingSystem
# Получает как параметр объект wmi, с помощью которого делается запрос
# возвращает строку в форме, которая указана в целевой ОС
# или строку "N/A", если данные не доступны по той или иной причине. Причина неудачной попытки не устанавливается.
def getOSName(wmiObject):
    try:
        for os in wmiObject.Win32_OperatingSystem():
            return os.Caption
    except (WindowsError, wmi.x_wmi, IndexError):
        return "N/A" # Возвращается строка потому что в идеале должна быть строка
# TODO в идеале всё переопределять как None("ничего") в случае неудачи и проверять как is None - быстро и хорошо подходит

# Функция отправляет запрос wmi и получает инфо дисков,
# информация о котором находится в классе Win32_LogicalDisk
# Получает как параметр объект wmi, с помощью которого делается запрос
# возвращает объект - инфо о дисках
# или None, если данные не доступны по той или иной причине. Причина неудачной попытки не устанавливается.
def getDiskInfo(wmiObject):
    try:
        return wmiObject.Win32_LogicalDisk()
    except (WindowsError, wmi.x_wmi, IndexError):
        return None # Возвращается "ничего" потому что в идеале должен быть объект

# Функция отправляет запрос wmi и получает с помощью него дату и время последней загрузки ОС,
# которая находится в классе Win32_OperatingSystem
# Получает как параметр объект wmi, с помощью которого делается запрос
# возвращает дату в формате Coordinated Universal Time (UTC) - YYYYMMDDHHMMSS.MMMMMM(+-)OOO.
# или строку "N/A", если дата не доступна по той или иной причине. Причина неудачной попытки не устанавливается.
def getLastBootUpTime(wmiObject):
    try:
        return getNormalDateTime(wmiObject.Win32_OperatingSystem(["LastBootUpTime"])[0].LastBootUpTime)
    except (WindowsError, wmi.x_wmi, IndexError):
        return "N/A" # Потому что строка

# Функция отправляет запрос wmi и получает инфо о процессоре,
# информация о котором находится в классе Win32_Processor
# Получает как параметр объект wmi, с помощью которого делается запрос
# возвращает объект - инфо о процессоре
# или None, если данные не доступны по той или иной причине. Причина неудачной попытки не устанавливается.
def getProcessorInfo(wmiObject):
    try:
        # https://msdn.microsoft.com/en-us/library/aa394373(v=vs.85).aspx
        processor_name =  str(wmiObject.Win32_Processor()[0].Name)
        processor_clock = str(wmiObject.Win32_Processor()[0].MaxClockSpeed)
        processor_cores = str(wmiObject.Win32_Processor()[0].NumberOfCores)
        processor_logical = str(wmiObject.Win32_Processor()[0].NumberOfLogicalProcessors)
        return [ processor_name, processor_clock, processor_cores, processor_logical ]
    except (WindowsError, wmi.x_wmi, IndexError):
        return None # Потому что объект

# Функция отправляет запрос wmi и получает общий свободный объем ОП ,
# информация о котором находится в классах  Win32_ComputerSystem и Win32_OperatingSystem
# Получает как параметр объект wmi, с помощью которого делается запрос
# возвращает объект - список из 2 чисел, соответственно, общий и свободный объем ОП
# или None, если данные не доступны по той или иной причине. Причина неудачной попытки не устанавливается.
def getRAMInfo(wmiObject):
    try:
        totalPhysicalMemory = wmiObject.Win32_ComputerSystem()[0].TotalPhysicalMemory
        freePhysicalMemory = str(int(wmiObject.Win32_OperatingSystem()[0].FreePhysicalMemory) * 1024) # Данные получены в КБ, перевод в байты
        return [ totalPhysicalMemory, freePhysicalMemory ] # возвращается список...кортеж надёжней
        # (т.к. он защищен от редактирования, в отличии от списка), но список удобней по той же причине
    except (WindowsError, wmi.x_wmi, IndexError):
        return None # Потому что объект

# Функция приводит возвращаемое wmi время в "человеческий" формат
def getNormalDateTime(datetime):
    # строка разбирается в кортеж (year, month, day, hours, minutes, seconds, microseconds, timezone)
    datetime = wmi.to_time(datetime)
    #приводится в понятный вид - добавляются 0, если меньше 10, чтобы было, например, 09
    fixeddatetime = []
    i = 0
    for dt in datetime :
        if(int(dt) < 10):
            fixeddatetime.append("0"+str(datetime[i]))
        else:
            fixeddatetime.append(str(datetime[i]))
        i += 1
    # Формируется строка
    return str(fixeddatetime[2] + "." + fixeddatetime[1] + "." + fixeddatetime[0] + " " +fixeddatetime[3] + ":" + fixeddatetime[4] + ":" + fixeddatetime[5] + " UTC " + fixeddatetime[7])
