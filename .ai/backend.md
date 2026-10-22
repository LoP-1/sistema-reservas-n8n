# Especificación del Sistema: Backend de Reservas & Automatización con n8n (Vía Telegram)

## 1. Objetivo General
Backend modular en FastAPI con persistencia en PostgreSQL que actúa como motor de datos, cálculo de disponibilidad y reglas de negocio para un asistente comercial en Telegram orquestado mediante n8n.

---

## 2. Definición de Endpoints

### Módulo: Reservas y Citas (`/citas`) - Uso Interno / Consumo por n8n

* **`GET /citas/disponibles`**
  * **Propósito:** Calcular y devolver los horarios libres para una fecha dada (consulta directa a PostgreSQL).
  * **Query Params:** `fecha` (YYYY-MM-DD), `servicio_id` (opcional).
  * **Respuesta JSON:**
    ```json
    {
      "fecha": "2026-10-15",
      "horarios_libres": ["09:00", "11:00", "15:00"]
    }
    ```

* **`POST /citas`**
  * **Propósito:** Registrar una nueva reserva confirmada en la base de datos.
  * **Body JSON:** 
    ```json
    {
      "cliente_nombre": "Carlos Perez",
      "cliente_contacto": "@carlosperez / +51999888777",
      "servicio": "Consulta General",
      "fecha_hora": "2026-10-15T10:00:00"
    }
    ```
  * **Lógica:** Valida que el turno no esté duplicado, guarda con estado `CONFIRMADO` y devuelve el ID generado.

* **`PATCH /citas/{id}/cancelar`**
  * **Propósito:** Actualización parcial para liberar el horario.
  * **Lógica:** Cambia únicamente el campo `estado` a `CANCELADO`.

---

### Módulo: Webhook y Mensajería (`/bot`) - Conexión Telegram

* **`POST /bot/mensaje`**
  * **Propósito:** Receptor de eventos entrantes de Telegram (Update object).
  * **Payload esperado (Esquema simplificado de Telegram):**
    ```json
    {
      "update_id": 10000,
      "message": {
        "message_id": 136,
        "from": {
          "id": 1111111,
          "first_name": "Carlos",
          "username": "carlosperez"
        },
        "chat": {
          "id": 1111111,
          "type": "private"
        },
        "text": "Hola, quiero agendar una cita"
      }
    }
    ```
  * **Lógica:** Extrae el `chat.id`, el nombre del usuario y el `text`. Responde `200 OK` de inmediato y despacha los datos a n8n en segundo plano (BackgroundTasks o HTTP) para procesar el flujo.

---

### Módulo: Base de Conocimiento del Negocio (`/negocio`) - Respuestas IA

* **`POST /negocio/datos`**
  * **Propósito:** Ingesta de información operativa del negocio (horarios, precios, servicios, preguntas frecuentes).
  * **Body JSON:** `{"seccion": "Precios", "contenido": "Consulta general S/ 50..."}`.
  * **Lógica:** Guarda los textos de referencia en PostgreSQL.

* **`POST /negocio/preguntar`**
  * **Propósito:** Búsqueda de respuestas directas sobre la información del negocio.
  * **Body JSON:** `{"pregunta": "¿Cuánto cuesta la consulta?"}`.
  * **Respuesta:** Devuelve el fragmento de texto con la información relevante para que n8n redacte la respuesta final.

---

## 3. Modelo de Datos Mínimo (PostgreSQL / SQLAlchemy)

1. **Tabla `citas`**:
   * `id`: Integer (Primary Key)
   * `cliente_nombre`: String
   * `cliente_contacto`: String (Guarda el @username o ID de Telegram)
   * `servicio`: String
   * `fecha_hora`: DateTime
   * `estado`: String (ej. "CONFIRMADO", "CANCELADO")
   * `creado_en`: DateTime

2. **Tabla `negocio_informacion`**:
   * `id`: Integer (Primary Key)
   * `seccion`: String (ej. "Precios", "Horarios", "Políticas")
   * `contenido`: Text