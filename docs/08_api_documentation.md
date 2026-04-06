# 8. API документация

## 8.1 Общее описание
- REST API на DRF
- JSON ответы
- работа с изображениями, видео, дефектами, камерами

## 8.2 Аутентификация
- JWT
- Authorization: Bearer <token>

## 8.3 Основные эндпоинты

### Аутентификация
POST /api/auth/login/

### Изображения
POST /api/images/
GET /api/images/

### Видео
POST /api/videos/

### Дефекты
GET /api/defects/
GET /api/defects/{id}/
PATCH /api/defects/{id}/confirm/

### Камеры
GET /api/cameras/
POST /api/cameras/
DELETE /api/cameras/{id}/

### Стриминг
POST /api/streams/start/
POST /api/streams/stop/
GET /api/streams/

### Отчёты
POST /api/reports/
GET /api/reports/

## 8.4 Коды ответов
200, 201, 400, 401, 403, 404, 500

## 8.5 Безопасность
- JWT
- роли (User / Operator / Admin)
- валидация данных


Подробная документация API доступна через Swagger:

http://localhost:8000/swagger/