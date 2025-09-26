from flask import request, send_file
from flask.views import MethodView
from flask_smorest import Blueprint, abort
import os
from datetime import datetime
from reportlab.lib.pagesizes import A4, landscape
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np
from reportlab.lib.utils import ImageReader
from reportlab.pdfgen import canvas
from models.measurement import MeasurementModel
from models.sensor import SensorModel
from db import db

blp = Blueprint('reports', __name__)

def generate_sensor_report_pdf(filepath, sensor, date_str, measurements):
    # PDF horizontal
    c = canvas.Canvas(filepath, pagesize=landscape(A4))
    width, height = landscape(A4)

    # Titulo centrado superior
    title = f"REPORTE DE {sensor.sensor_type.upper()} DE {sensor.location.upper()} ({date_str})"
    c.setTitle(title)
    c.setFont("Helvetica-Bold", 24)  # Aumentar tamano y negrita
    c.drawCentredString(width/2, height - 40, title)

    # Preparar datos para el grafico
    measurements.sort(key=lambda x: x.date_time)  # Ordenar por hora
    datetimes = [m.date_time for m in measurements]
    values = [m.value for m in measurements]
    unit_field = measurements[0].unit if measurements else sensor.unit_name

    # Calcular el promedio para la linea horizontal
    avg_val = round(sum(values)/len(values), 2) if values else 0
    
    # Crear grafico con matplotlib
    fig, ax = plt.subplots(figsize=(8, 4))
    
    # Crear array de minutos para el eje X
    start_time = datetime.combine(datetimes[0].date(), datetime.min.time())
    minutes = np.array([(dt - start_time).total_seconds() / 60 for dt in datetimes])
    
    # Graficar usando los minutos como coordenadas X
    ax.plot(minutes, values, color='blue', linewidth=1)
    ax.axhline(y=avg_val, color='red', linestyle='--', alpha=0.5)
    ax.set_title(f"{sensor.sensor_type.upper()} DE {sensor.location.upper()}")
    ax.set_xlabel("Hora")
    ax.set_ylabel(f"{sensor.sensor_type} Sensor [{unit_field}]")
    
    # Configurar eje X para mostrar intervalos exactos de 15 minutos
    fixed_minutes = np.arange(0, 24*60+1, 15)
    ax.set_xticks(fixed_minutes[::2])  # por ejemplo cada 30 minutos para que quepan
    ax.set_xticklabels([f"{int(m//60):02d}:{int(m%60):02d}" for m in fixed_minutes[::2]],rotation=45)
    ax.set_xlim(0, 24*60)
    
    # Ajustar los limites del eje X para mostrar solo el rango de datos (en minutos)
    if len(minutes) > 0:
        min_x = max(0, minutes.min() - 5)
        max_x = min(24*60, minutes.max() + 5)
    else:
        min_x = 0
        max_x = 24*60
    ax.set_xlim(min_x, max_x)
    
    # Agregar etiqueta del promedio al final de la linea (en el ultimo punto)
    if len(minutes) > 0:
        ax.text(minutes[-1], avg_val, f'Promedio {avg_val}', 
                verticalalignment='bottom',
                horizontalalignment='right',
                color='red',
                fontsize=10)

    plt.grid(True, linestyle='--', alpha=0.7)  # Agregar grid
    plt.tight_layout()

    # Guardar grafico temporal
    img_path = filepath + "_plot.png"
    plt.savefig(img_path)
    plt.close(fig)

    # Insertar grafico en PDF
    c.drawImage(ImageReader(img_path), 60, 120, width=width-120, height=height-250, preserveAspectRatio=True)

    # Calcular estadisticas
    max_val = max(values) if values else 0
    min_val = min(values) if values else 0
    avg_val = round(sum(values)/len(values), 2) if values else 0

    # Dibujar recuadros al pie
    box_width = 200
    box_height = 60
    box_y = 60
    box_xs = [width/2 - box_width - 10, width/2, width/2 + box_width + 10]
    labels = [
        f"Max de {sensor.sensor_type} Sensor [{unit_field}]",
        f"Min de {sensor.sensor_type} Sensor [{unit_field}]",
        f"Prom de {sensor.sensor_type} Sensor [{unit_field}]"
    ]
    vals = [max_val, min_val, avg_val]
    for i in range(3):
        c.setStrokeColorRGB(0,0,0)
        c.setFillColorRGB(0.95,0.95,0.95)
        c.rect(box_xs[i]-box_width/2, box_y, box_width, box_height, fill=1)
        c.setFont("Helvetica-Bold", 12)
        c.setFillColorRGB(0,0,0)
        c.drawCentredString(box_xs[i], box_y+box_height-20, labels[i])
        c.setFont("Helvetica", 16)
        c.drawCentredString(box_xs[i], box_y+box_height/2-5, str(vals[i]))

    # Eliminar imagen temporal
    try:
        os.remove(img_path)
    except Exception:
        pass

    c.save()



@blp.route('/report')
class SensorReport(MethodView):
    def get(self):
        sensor_id = request.args.get('sensor_id', type=int)
        date_str = request.args.get('date')
        if not sensor_id or not date_str:
            abort(400, message="sensor_id and date are required. Date format: MM/DD/YYYY")
        try:
            report_date = datetime.strptime(date_str, "%m/%d/%Y")
        except Exception:
            abort(400, message="Invalid date format. Use MM/DD/YYYY")

        # Buscar sensor
        sensor = SensorModel.query.get(sensor_id)
        if not sensor:
            abort(404, message="Sensor not found")

        # Rango de la fecha solicitada
        range_start = datetime.combine(report_date.date(), datetime.min.time())
        range_end = datetime.combine(report_date.date(), datetime.max.time())

        # Obtener mediciones del sensor en esa fecha
        measurements = MeasurementModel.query.filter(
            MeasurementModel.sensor_id == sensor_id,
            MeasurementModel.date_time >= range_start,
            MeasurementModel.date_time <= range_end
        ).order_by(MeasurementModel.date_time.asc()).all()

        # Validar si el archivo existe y la fecha es menor a hoy
        reports_dir = os.path.join(os.path.dirname(__file__), '..', 'reports')
        os.makedirs(reports_dir, exist_ok=True)
        # Generar nombre del archivo
        clean_date = date_str.replace('/', '-')
        file_title = f"REPORTE_DE_{sensor.sensor_type.upper()}_DE_{sensor.location.upper()}_{clean_date}"
        filename = f"{file_title}.pdf"
        filepath = os.path.join(reports_dir, filename)

        today = datetime.now().date()
        if report_date.date() < today and os.path.exists(filepath):
            return download_report_file(filename)

        # Generar el reporte
        generate_sensor_report_pdf(filepath, sensor, date_str, measurements)
        return download_report_file(filename)

@blp.route('/report/download/<string:filename>')
class ReportDownload(MethodView):
    def get(self, filename):
        return download_report_file(filename)


def download_report_file(filename):
    # Forzar extensión PDF
    if not filename.lower().endswith('.pdf'):
        filename = filename + '.pdf'
    reports_dir = os.path.join(os.path.dirname(__file__), '..', 'reports')
    filepath = os.path.join(reports_dir, filename)
    if not os.path.exists(filepath):
        abort(404, message="Report not found")
    return send_file(filepath, as_attachment=True)
