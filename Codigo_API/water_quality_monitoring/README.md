# API Sistema de Monitoreo de calidad del agua

## Descripción

Esta API está configurada para inicializarse automáticamente al encender la Raspberry. Utiliza una base de datos en memoria, ubicada en `/home/pi/water_quality_monitoring/instance/water_quality_monitoring.db`.

Si el servicio se arraca por primera vez, se crea la instancia de bases de datos, es posible eliminar el archivo de base de datos, por lo que se perdería toda la información.

Los reportes se almacenan en `/home/pi/water_quality_monitoring/reports`

Puedes visualizar la base de datos abriéndola en `DB Browser for SQLite`

## Endpoints

Para conocer la IP de la Raspberry:

```bash
hostname -I
```


```
<IP_RASPBERRY>:5000/measurements Incluye métodos para agregar, editar y visualizar mediciones
<IP_RASPBERRY>:5000/report Genera y descarga reportes según un sensor y fecha dadas
<IP_RASPBERRY>:5000/sensors Incluye métodos para agregar, editar y visualizar sensores

```


## Configuración Rápida

1. **Activar entorno virtual:**
   ```bash
   # Windows
   .\\venv\\Scripts\\activate
   
   # Unix/Linux/Mac
   source venv/bin/activate
   ```

2. **Instalar dependencias:**
   ```bash
   pip install -r requirements
   ```

3. **Ejecutar la API Localmente:**
   ```bash
   python3 run.py
   ```

## Producción

Para producción, usar Gunicorn:

```bash
gunicorn -w 4 -b 0.0.0.0:5000 run:app
```

### Raspberry con servicio de ejecución

Existe un servicio llamado `api.service` que está configurado para iniciar la API al encender el sistema

#### Verificar estado

```bash
sudo systemctl status api.service
```

#### Iniciar servicio manualmente

```bash
sudo systemctl start api.service
```

#### Detener el servicio

```bash
sudo systemctl stop api.service
```

#### Reiniciar el servicio

```bash
sudo systemctl restart api.service
```

#### Revisar logs

```bash
sudo journalctl -u api.service
```


