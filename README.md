## OTUServer

HTTP-сервер на основе многопоточной архитектуры, с использованием высокоуровневого модуля concurrent.futures


### Возможности

- Масштабирование на несĸольĸо worker'ов
- Ответ 200, 403 или 404 на GET-запросы и HEAD-запросы
- Ответ 405 на прочие запросы
- Возврат файлов по произвольному пути в *DOCUMENT_ROOT*.
- Вызов */file.html* возвращает содержимое *DOCUMENT_ROOT/file.html*
- Возврат *index.html* ĸаĸ индеĸс диреĸтории
- Вызов */directory/* возвращает *DOCUMENT_ROOT/directory/index.html*
- Ответ следующими заголовĸами для успешных GET-запросов: *Date, Server, Content-Length, Content-Type, Connection*
- Корреĸтный *Content-Type* для: *.html, .css, .js, .jpg, .jpeg, .png, .gif, .swf*
- Понимает пробелы и *%XX* в именах файлов
-------------

## Запуск сервера
*httpd.py [-i HOST] [-p PORT] [-w WORKERS] [-r DOCUMENT_ROOT]*

### Параметры

- *HOST* - хост (по умолчанию 'localhost') 

- *PORT* - номер порта для работы сервера (по умолчанию 8080)

- *WORKERS* - количество worker'ов (по умолчанию 5)

- *DOCUMENT_ROOT* - document_root для сервера (по умолчанию '.')


### Нагрузочное тестирование
ab -n 50000 -c 100 -r http://localhost:8080/httptest/dir2/

workers: 10

#### Результат:
````
Server Software:        OTUServer      
Server Hostname:        localhost      
Server Port:            8080           
                                       
Document Path:          /httptest/dir2/
Document Length:        34 bytes

Concurrency Level:      100
Time taken for tests:   346.145 seconds
Complete requests:      50000
Failed requests:        0
Total transferred:      8650000 bytes
HTML transferred:       1700000 bytes
Requests per second:    144.45 [#/sec] (mean)
Time per request:       692.291 [ms] (mean)
Time per request:       6.923 [ms] (mean, across all concurrent requests)
Transfer rate:          24.40 [Kbytes/sec] received

Connection Times (ms)
              min  mean[+/-sd] median   max
Connect:        0    0   0.1      0       9
Processing:     7  692 104.9    676    1858
Waiting:        7  692 104.9    676    1858
Total:         10  692 104.9    676    1858

Percentage of the requests served within a certain time (ms)
  50%    676
  66%    686
  75%    696
  80%    704
  90%    756
  95%    845
  98%    995
  99%   1173
 100%   1858 (longest request)
````
### Сквозное тестирование

http://localhost:8080/httptest/wikipedia_russia.html


### Тестирование кода
*pytest -v httptest.py*

Репозиторий данных для тестов: 
https://github.com/s-stupnikov/http-test-suite

#### Результат:
````
platform linux -- Python 3.10.4, pytest-7.1.2, pluggy-1.0.0 -- /usr/bin/python3
cachedir: .pytest_cache
rootdir: /mnt/c/Users/Rom/PycharmProjects/hw_OTUServer
plugins: asyncio-0.19.0, Faker-14.1.0, anyio-3.6.1
asyncio: mode=strict
collected 23 items
   
httptest.py::HttpServer::test_directory_index PASSED                                        [  4%]
httptest.py::HttpServer::test_document_root_escaping PASSED                                 [  8%]
httptest.py::HttpServer::test_empty_request PASSED                                          [ 13%]
httptest.py::HttpServer::test_file_in_nested_folders PASSED                                 [ 17%]
httptest.py::HttpServer::test_file_not_found PASSED                                         [ 21%]
httptest.py::HttpServer::test_file_urlencoded PASSED                                        [ 26%]
httptest.py::HttpServer::test_file_with_dot_in_name PASSED                                  [ 30%]
httptest.py::HttpServer::test_file_with_query_string PASSED                                 [ 34%]
httptest.py::HttpServer::test_file_with_slash PASSED                                        [ 39%]
httptest.py::HttpServer::test_file_with_spaces PASSED                                       [ 43%]
httptest.py::HttpServer::test_filetype_css PASSED                                           [ 47%]
httptest.py::HttpServer::test_filetype_gif PASSED                                           [ 52%]
httptest.py::HttpServer::test_filetype_html PASSED                                          [ 56%]
httptest.py::HttpServer::test_filetype_jpeg PASSED                                          [ 60%]
httptest.py::HttpServer::test_filetype_jpg PASSED                                           [ 65%]
httptest.py::HttpServer::test_filetype_js PASSED                                            [ 69%]
httptest.py::HttpServer::test_filetype_png PASSED                                           [ 73%]
httptest.py::HttpServer::test_filetype_swf PASSED                                           [ 78%]
httptest.py::HttpServer::test_head_method PASSED                                            [ 82%]
httptest.py::HttpServer::test_index_not_found PASSED                                        [ 86%]
httptest.py::HttpServer::test_large_file PASSED                                             [ 91%]
httptest.py::HttpServer::test_post_method PASSED                                            [ 95%] 
httptest.py::HttpServer::test_server_header PASSED                                          [100%] 

================================= 23 passed in 0.40s ========================================