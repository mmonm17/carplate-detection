---
license: apache-2.0
---
---
# Russian car plate detecting dataset

Car_plate_detecting_dataset - это набор данных из примерно 25,5К изображений российских автомобилей с номерами одного типа (рисунок 1) и разметки в формате YOLO: ```class x_center y_center width height```. Этот набор данных предназначен для обучения нейронных сетей обнаружению (локализации) номера автомобиля на изображении.
Основан на датасете [AUTO.RIA Numberplate Options Dataset](https://nomeroff.net.ua/datasets/autoriaNumberplateDataset-2023-03-06.zip) из проекта [Nomeroff Net](https://nomeroff.net.ua/#).

|![Alt text](resources%2Fimages%2Favto-nomera-02.vv139e.jpg)|
|:-----:|
|Рисунок 1 - Пример номера автомобиля|

Данные разбиты на подвыборки для обучения, тестирования и валидации:

|Типп выборки данных | Количество изображений |
| :----------------: |:----------------------:|
| train |      20505 (80%)       |
| val   |       2563 (10%)       |
| test  |       2564 (10%)       |
| all images |         25632          |

В качестве разметки файлы .txt с именем изображения, внутри которых находится разметка в формате YOLO ```class x_center y_center width height```.
Пример использования данного датасета приведён в проекте [Car_plate_detecting](https://github.com/AY000554/Car_plate_detecting/tree/main).
# Лицензия
Оригинальный датасет распространяется под лицензией CC BY 4.0. Подробнее в файле license.txt.
