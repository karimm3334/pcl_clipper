# PCL Clipper & Visualizer

Этот проект предоставляет средство для фильтрации 3D-точек относительно плоскостей и их визуализации в Docker-контейнере.

## Сборка Docker-образа

```bash
git clone https://github.com/karimm3334/pcl_clipper.git
cd pcl_clipper/
docker build -t pcl_clipper:1.0.0 .
```

альтернативно можно скачать с помощью

```bash
docker pull skarius/pcl_clipper:1.0.0
```

## Запуск фильтрации

Для фильтрации точек относительно плоскостей:

```bash
docker run --rm -v "$(pwd)/data:/app/data" pcl_clipper:1.0.0 ./data/points.txt ./data/planes.txt -t
```

- `<points.txt>` — файл с исходными 3D-точками  
- `<planes.txt>` — файл с точками, задающими две плоскости (должен содержать ровно 6 точек — по 3 на плоскость)  
- `-t` — опциональный флаг, включающий вывод подробного времени выполнения каждого этапа программы  

Или с явным указанием команды:

```bash
docker run --rm -v "$(pwd)/data:/app/data" pcl_clipper:1.0.0 clip ./data/points.txt ./data/planes.txt -t
```

> Входные файлы должны находиться в папке `data/`  
> Результат будет сохранён так же в директорию `data/`.

## Запуск визуализации

Для визуализации точек и плоскостей (требуется X11):

```bash
docker run --rm \
    -e DISPLAY=$DISPLAY \
    -v /tmp/.X11-unix:/tmp/.X11-unix \
    -v "$(pwd)/data:/app/data" \
    pcl_clipper:1.0.0 visualize ./data/points.txt ./data/planes.txt
```

===

## Использование Entrypoint

Образ поддерживает два режима:

- `clip` — фильтрация точек  
- `visualize` — визуализация

Примеры:

```bash
# Фильтрация (по умолчанию)
docker run ... pcl_clipper:1.0.0 clip <файл_точек> <файл_плоскостей> [-t]

# Визуализация
docker run ... pcl_clipper:1.0.0 visualize <файл_точек> <файл_плоскостей>
```

---

### Использование visualize.py

```bash
usage: visualize.py [-h] [--voxel_size VOXEL_SIZE] points_filename [planes_filename]

positional arguments:
  points_filename       Имя файла с точками (например, points.txt)
  planes_filename       Имя файла с плоскостями (например, planes.txt)

optional arguments:
  -h, --help            Показать справку и выйти
  --voxel_size VOXEL_SIZE
                        Размер вокселя (по умолчанию 0.01)
```

Пример запуска:

```bash
visualize.py points.txt planes.txt --voxel_size 0.02
```

- `points.txt` — файл с 3D-точками для визуализации  
- `planes.txt` — файл с точками, определяющими плоскости  
- `--voxel_size` — опциональный параметр, регулирующий размер вокселя для визуализации  

---

### Использование clip (C++ программа)

```bash
Usage: clip <points.txt> <planes.txt> [-t]
```

- `<points.txt>` — файл с исходными 3D-точками  
- `<planes.txt>` — файл с точками, задающими две плоскости (должен содержать ровно 6 точек — по 3 на плоскость)  
- `-t` — опциональный флаг, включающий вывод подробного времени выполнения каждого этапа программы  

Пример запуска:

```bash
docker run --rm -v "$(pwd)/data:/app/data" pcl_clipper:1.0.0 ./data/points.txt ./data/planes.txt -t
```

---

### Что делает программа clip?

1. Загружает 3D-точки из файла points.txt  
2. Загружает 6 точек из planes.txt — по 3 точки для каждой из двух плоскостей  
3. Проверяет, что planes.txt содержит ровно 6 точек (иначе ошибка)  
4. Создаёт объекты плоскостей по этим точкам  
5. Классифицирует каждую точку из points.txt: если точка принадлежит хотя бы одной плоскости — помещает в "valid" (good), иначе — в "invalid" (wrong)  
6. Сохраняет классифицированные точки в файлы `<base>_good.txt` и `<base>_wrong.txt`, где `<base>` — имя исходного файла с точками без расширения  
7. При включённом флаге `-t` выводит тайминги по этапам работы  

---

Если нужна помощь с конкретными файлами или параметрами — обращайтесь!
