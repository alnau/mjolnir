# TODO List

- utility.py:52: # но направление мысли верное: TODO: нужно делить сессии, возможно, делать это по времени
- camera_feed_generic.py:41: # TODO: в дальнейшем, необходимо отрабатывать эту ситуацию адекватно
- camera_feed_generic.py:55: # TODO поднять ошибку или вывести в строку логов
- image_processing.py:346: # TODO: возможно, следует добавить проверку на то, что изображение обработано, но для этого нужно сначала убедиться что везде в app это проставляется. Также можно возвращать T/F в app в случае если все ок или не проанализир. изобр
- app.py:224: # TODO: возможно, если подменить на switchImage, решится баг с подгрузкой
- app.py:238: # TODO: надо сделать возможным импорт png и jpg файлов
- app.py:254: # TODO: решил большую часть проблем с подгрузкой, но все еще при открытии загружает правильное изображение, потом переключает его на заглушку. При этом нажатие на кнопки навигации возвращает все на круги своя. Пройдись дебагером и не еби мозги
- app.py:416: # TODO: возможно, можно не передавать image_index в эти функции
- app.py:419: # TODO: убрал 10.02.25 за ненадобностью. Возможно, ошибся
- app.py:544: # подменим app.current_image TODO: раньше было до if
- app.py:631: #     # TODO: Есть сценарии, при которых индекс может вести за пределы массива. Не знаю как решать эту проблему
- app.py:806: # TODO разберись уже с этой функцией, это уже непрофессионально
- app.py:880: # TODO: Вылезает ошибка, но, вроде, обрабатывается исключением
- app.py:887: # TODO на текущий момент исправления в имени файла между захватом изображения и переходом к следующему кадру невозможны
- app.py:1162: # TODO: command = self.master.nextImage - это что-то совсем безбожное
- app.py:1279: # TODO: в случае, когда данные уже были проанализированы и произошел переворот этого флага, необходимо подменить данные только для этого изображения
- app.py:1344: # TODO: все еще грязый трюк, но время 19:44, а я еще на работе. Эта возня с обработкой индексов - единственное, что тормозит новую версию
- app.py:1352: self.main.data_is_external = False # TODO не знаю, нужно ли
- app.py:1395: self.main.manual_drawing = True # TODO добавил на время разработки фичи
- app.py:1612: # TODO: решил все-же убрать запрет захвата изображения. Возможно, зря
