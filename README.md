# Мухтаров Роберт, 11-904

Пояснение:
1. В Object Storage создать бакеты itis-2022-2023-vvot13-photos и itis-2022-2023-vvot13-faces
2. В Message Queue создать очередь vvot13-tasks
3. В Cloud Functions создать облачную функцию vvot13-face-detection:
    - содержимое функции находится в файле vvot13-face-detection.py
    - добавить requirements.txt с `boto3`
    - точка входа: `vvot13-face-detection.handler`
    - добавить переменные окружения `aws_access_key_id`, `aws_secret_access_key`, `queue_url`, `folder_id`, `token`
4. В Managed Service for YDB создать базу данных vvot13-db-photo-face, внутри создать таблицу `face_table` со следующими колонками:        
    - `cropped_face_id` (String, PK) — название изображения с лицом
    - `face_name` (String) — имя для фотографии лица
    - `original_image_id` (String) — название оригинального изображения
5. В Container Registry создать реестр vvot13-registry
6. Собрать образ c использованием файлов Dockerfile и vvot13-face-cut.py, загрузить его в реестр
7. В Serverless Containers создать контейнер vvot13-face-cut:
    - указать URL загруженного образа
    - добавить переменные окружения `aws_access_key_id`, `aws_secret_access_key`, `photos_bucket`, `faces_bucket`, `ydb_endpoint`, `ydb_database`
    - указать сервисный аккаунт vvot13-storageuser
8. В API Gateway создать шлюз, в спецификацию поместить содержимое файла api_gateway.yml