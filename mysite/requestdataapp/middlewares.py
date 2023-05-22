from django.http import HttpRequest
from time import time
from django.shortcuts import render


def set_useragent_on_request_middleware(get_response):

    print(f"Initial call")

    def middleware(request: HttpRequest):
        print(f"before get response")
        request.user_agent = request.META["HTTP_USER_AGENT"]
        response = get_response(request)
        print(f"after get response")
        return response

    return middleware


class CountRequestsMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response
        self.requests_count = 0
        self.responses_count = 0
        self.exceptions_count = 0

    def __call__(self, request: HttpRequest):
        self.requests_count += 1
        print(f"count requests: ", self.requests_count)
        response = self.get_response(request)
        self.responses_count += 1
        print(f"count responses: ", self.responses_count)
        return response

    def process_exception(self, request: HttpRequest, exception: Exception):
        self.exceptions_count += 1
        print(f'got {self.exceptions_count} exceptions so far')


class ThrottlingMiddleware:

    def __init__(self, get_response):
        self.get_response = get_response
        self.request_time = {}
        self.time_delay = 0.1

    def __call__(self, request: HttpRequest):
        # Определение IP-адреса пользователя
        ip_address = request.META.get('REMOTE_ADDR')
        # Если последний запрос был сделан недавно, то вернуть ошибку
        if not self.request_time:
            print(f"Первый запрос после запуска сервера. Словарь пуст.")
        else:
            if self.request_time.get('ip_address') == ip_address and time() - self.request_time.get('time') < self.time_delay:
                print('Прошло менее 10 секунд, после вашего последнего запроса.')
                return render(request, 'requestdataapp/error-request.html')

        # Получение времени последнего запроса с этого IP-адреса
        self.request_time = {'time': round(time()), 'ip_address': ip_address}

        response = self.get_response(request)
        # Возврат ответа
        return response

# class ThrottlingMiddleware:
#     THROTTLE_TIME = getattr(settings, 'THROTTLE_TIME', 10)  # время в секундах
#     THROTTLE_LIMIT = getattr(settings, 'THROTTLE_LIMIT', 10)  # максимальное количество запросов
#
#     def __init__(self, get_response):
#         self.get_response = get_response
#
#     def __call__(self, request):
#         # Определение IP-адреса пользователя
#         ip_address = request.META.get('REMOTE_ADDR')
#
#         # Получение времени последнего запроса с этого IP-адреса
#         last_request_time = request.session.get(ip_address)
#
#         # Если последний запрос был сделан недавно, то вернуть ошибку
#         if last_request_time and (datetime.now() - last_request_time) < timedelta(seconds=self.THROTTLE_TIME):
#             return HttpResponseForbidden()
#
#         # Сохранение времени текущего запроса
#         request.session[ip_address] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
#
#         # Проверка количества запросов
#         requests_count = request.session.get('requests_count', 0)
#         if requests_count >= self.THROTTLE_LIMIT:
#             return HttpResponseForbidden()
#
#         # Увеличение счетчика запросов
#         request.session['requests_count'] = requests_count + 1
#
#         # Обработка запроса
#         response = self.get_response(request)
#
#         # Возврат ответа
#         if isinstance(response.content, bytes):
#             response_content = response.content.decode('utf-8')
#         else:
#             response_content = response.content
#
#         try:
#             json.loads(response_content)
#             return response
#         except ValueError:
#             return response
