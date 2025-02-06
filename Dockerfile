# Используем официальный образ Apache NiFi
FROM apache/nifi:latest

# Устанавливаем необходимые зависимости Python
USER root
RUN apt-get update && apt-get install -y python3-pip python3-venv

# Создаем виртуальное окружение
RUN python3 -m venv /opt/nifi/python-env

# Активируем виртуальное окружение и устанавливаем зависимости
RUN /bin/bash -c "source /opt/nifi/python-env/bin/activate"

# Копируем ваш Python-файл в контейнер
COPY python_extensions/GetDirectoryFilesCount/GetDirectoryFilesCount.py /opt/nifi/nifi-current/extensions/

# Переключаемся на пользователя NiFi
USER nifi