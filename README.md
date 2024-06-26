# PFED - Plot Fenix Evacuation Density

> Язык: **Python**

> Интерфейс: **нативный**

## Особенности и описание работы утилиты
Утилита позволяет вывести единый график плотности людских потоков для выбранных временных промежутков независимо от разметки сценариев, а также определить продолжительность людских скоплений.

![firegoaway_pfed_demo_gif-min](https://raw.githubusercontent.com/firegoaway/Plot_Fenix_Evac_Density/main/.gitpics/pfed_demo_gif-min.gif)

### Метод
**ВНИМАНИЕ!** На графиках отображаются ВСЕ людские скопления, где плотность хотя бы у 2 человек на одной и той же временной отметке превышает 0.5 м2/м2.

Ширина i-го участка и интенсивность движения людей на i-м участке для j-го контингента **уже учтена**. Утилита показывает **все существующие скопления за всё время эвакуации (сухие данные)**.

**При использовании утилиты, имейте ввиду**, что время существования скоплений расчитывается аналитически и вычисляется в зависимости от положений той или иной математической модели эвакуации людей.

### Поддерживаемые версии Fenix+
> **Fenix+ 3**

> **Fenix+ 2**

> **Fenix+**

## Как установить и пользоваться
|	№ п/п	|	Действие	|
|---------|---------|
|	1	|	Скачайте последнюю версию **PFED.exe** в разделе [Releases](https://github.com/firegoaway/Plot_Fenix_Evac_Density/releases)	|
|	2	|	Запустите **PFED.exe**	|
|	3	|	Откроется окно выбора файлов. Выберите все нужные вам файлы формата TSV **peoples_detailed_nnnnnn_0.tsv**	|
|	4	|	Немного подождите, пока утилита анализирует данные, содержащиеся в файлах. Время анализа зависит от объёма данных.	|
|	5	|	По окончании анализа откроется окно с отрисованным графиком и пользовательским интерфейсом. Вы сможете отмасштабировать график как вам нужно и сохранить в формате **.png**	|
|	6	|	При необходимости вы можете запустить несколько окон **PFED.exe**, чтобы проанализировать каждый файл отдельно или массив файлов по данным из нескольких сценариев сразу.	|

## Статус разработки
> **Альфа**

## Профилактика вирусов и угроз
- Утилита **"PFED"** предоставляется **"как есть"**.
- Актуальная версия утилиты доступна в разделе [**Releases**](https://github.com/firegoaway/Plot_Fenix_Evac_Density/releases).
- Файлы, каким-либо образом полученные не из текущего репозитория, несут потенциальную угрозу вашему ПК.
- Файл с расширением **.exe**, полученный из данного репозитория, имеет уникальную Хэш-сумму, позволяющую отличить оригинальную утилиту от подделки.
- Хэш-сумма обновляется только при обновлении версии утилиты и всегда доступна в конце файла **README.md**.

# Актуальная Хэш-сумма
> **965ef88a6d7d3a1e05cd4697f9d0a457**