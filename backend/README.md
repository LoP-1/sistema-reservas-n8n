# Backend de Reservas & Automatización Telegram (n8n)

Backend modular en FastAPI con persistencia en PostgreSQL que actúa como motor de datos, cálculo de disponibilidad y reglas de negocio para el asistente comercial de Telegram orquestado con n8n.

---

## 📁 Estructura del Proyecto

```text
backend/
├── app/
│   ├── api/
│   │   └── v1/
│   │       ├── endpoints/
│   │       │   ├── citas.py      # /citas (disponibilidad, creación, cancelación)
│   │       │   ├── bot.py        # /bot/mensaje (webhook de Telegram y despacho a n8n)
│   │       │   └── negocio.py    # /negocio (ingesta y consulta de datos del negocio)
│   │       └── router.py         # Router central que unifica los endpoints
│   ├── core/
│   │   ├── config.py             # Configuración y variables de entorno
│   │   └── database.py           # Conexión SQLAlchemy y SessionLocal
│   ├── models/
│   │   └── models.py             # Modelos ORM: Cita, NegocioInformacion
│   ├── schemas/
│   │   └── schemas.py            # Esquemas Pydantic de entrada y salida
│   └── main.py                   # Inicialización de FastAPI, CORS y creación de tablas
├── Dockerfile                    # Dockerfile optimizado para producción / dev
├── .dockerignore
├── requirements.txt              # FastAPI, SQLAlchemy, psycopg2, httpx, etc.
└── run.py                        # Script de inicio local rápido
```

---

## 🚀 Despliegue con Docker Compose (Recomendado)

Desde la raíz del repositorio (`D:\Workspace\automation-n8n`):

```powershell
docker compose up --build -d
```

Ver logs:
```powershell
docker compose logs -f
```

Detener servicios:
```powershell
docker compose down
```

---

## 🛠️ Ejecución Local sin Docker (Opcional)

Si ejecutas PostgreSQL localmente o con `docker compose up -d db`:

1. **Crear y activar entorno virtual:**
   ```powershell
   cd backend
   python -m venv .venv
   .\.venv\Scripts\Activate.ps1
   ```

2. **Instalar dependencias:**
   ```powershell
   pip install -r requirements.txt
   ```

3. **Iniciar servidor:**
   ```powershell
   python run.py
   ```

---

## 📖 Endpoints de la API

La documentación Swagger está disponible en: [http://localhost:8000/docs](http://localhost:8000/docs)

### 1. Módulo: Reservas y Citas (`/citas`)

| Método | Endpoint | Descripción | Parámetros / Body |
| :--- | :--- | :--- | :--- |
| `GET` | `/citas/disponibles` | Calcula y retorna horarios disponibles para una fecha | Query: `fecha` (YYYY-MM-DD), `servicio_id` (opcional) |
| `POST` | `/citas` | Registra una nueva reserva confirmada (valida duplicados) | Body: `cliente_nombre`, `cliente_contacto`, `servicio`, `fecha_hora` |
| `PATCH` | `/citas/{id}/cancelar` | Cancela una reserva liberando el horario | Path: `id` |

#### Ejemplo de disponibilidad:
```json
// GET /citas/disponibles?fecha=2026-10-15
{
  "fecha": "2026-10-15",
  "horarios_libres": ["09:00", "11:00", "14:00", "15:00"]
}
```

---

### 2. Módulo: Webhook Telegram (`/bot`)

| Método | Endpoint | Descripción |
| :--- | :--- | :--- |
| `POST` | `/bot/mensaje` | Receptor del webhook de Telegram. Responde `200 OK` de inmediato y despacha los datos a n8n en segundo plano vía `BackgroundTasks`. |

---

### 3. Módulo: Base de Conocimiento del Negocio (`/negocio`)

| Método | Endpoint | Descripción | Body |
| :--- | :--- | :--- | :--- |
| `POST` | `/negocio/datos` | Carga de información operativa (precios, políticas, horarios, FAQ) | `{"seccion": "Precios", "contenido": "Consulta general S/ 50..."}` |
| `POST` | `/negocio/preguntar` | Búsqueda directa de respuestas de conocimiento para que la IA/n8n elabore la respuesta | `{"pregunta": "¿Cuánto cuesta la consulta?"}` |

---

### 4. Health Check
* `GET /health`: Verifica el estado de la API.
