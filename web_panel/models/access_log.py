"""
QR Access Control PRO - Access Log Model
Operations for the accesos_log table.

Actual DB columns: id, qr_texto, resultado, fecha_hora, user_id
"""
from config.database import execute_query
from datetime import datetime, timedelta


def create_log(qr_texto, resultado, user_id=None, **kwargs):
    """Create an access log entry."""
    query = """
        INSERT INTO accesos_log (qr_texto, resultado, user_id)
        VALUES (%s, %s, %s)
    """
    return execute_query(query, (qr_texto, resultado, user_id), commit=True)


def get_recent(limit=20):
    """Get recent access logs with user info."""
    query = """
        SELECT a.id, a.qr_texto, a.resultado, a.fecha_hora, a.user_id,
               u.nombre, u.correo
        FROM accesos_log a
        LEFT JOIN usuarios u ON a.user_id = u.id
        ORDER BY a.fecha_hora DESC
        LIMIT %s
    """
    return execute_query(query, (limit,), fetch_all=True)


def get_stats_today():
    """Get today's access statistics."""
    query = """
        SELECT
            COUNT(*) as total,
            SUM(CASE WHEN resultado = 'permitido' THEN 1 ELSE 0 END) as permitidos,
            SUM(CASE WHEN resultado = 'denegado' THEN 1 ELSE 0 END) as denegados
        FROM accesos_log
        WHERE DATE(fecha_hora) = CURDATE()
    """
    result = execute_query(query, fetch_one=True)
    return {
        'total': result['total'] or 0,
        'permitidos': int(result['permitidos'] or 0),
        'denegados': int(result['denegados'] or 0)
    }


def get_stats_week():
    """Get access statistics for the last 7 days."""
    query = """
        SELECT
            DATE(fecha_hora) as fecha,
            COUNT(*) as total,
            SUM(CASE WHEN resultado = 'permitido' THEN 1 ELSE 0 END) as permitidos,
            SUM(CASE WHEN resultado = 'denegado' THEN 1 ELSE 0 END) as denegados
        FROM accesos_log
        WHERE fecha_hora >= DATE_SUB(CURDATE(), INTERVAL 7 DAY)
        GROUP BY DATE(fecha_hora)
        ORDER BY fecha ASC
    """
    results = execute_query(query, fetch_all=True)

    # Fill in missing days with zeros
    today = datetime.now().date()
    days = {}
    for i in range(6, -1, -1):
        day = today - timedelta(days=i)
        days[day.isoformat()] = {'fecha': day.isoformat(), 'total': 0, 'permitidos': 0, 'denegados': 0}

    if results:
        for row in results:
            day_key = row['fecha'].isoformat() if hasattr(row['fecha'], 'isoformat') else str(row['fecha'])
            if day_key in days:
                days[day_key] = {
                    'fecha': day_key,
                    'total': row['total'],
                    'permitidos': int(row['permitidos'] or 0),
                    'denegados': int(row['denegados'] or 0)
                }

    return list(days.values())


def get_stats_by_hour_today():
    """Get hourly breakdown for today."""
    query = """
        SELECT
            HOUR(fecha_hora) as hora,
            COUNT(*) as total,
            SUM(CASE WHEN resultado = 'permitido' THEN 1 ELSE 0 END) as permitidos,
            SUM(CASE WHEN resultado = 'denegado' THEN 1 ELSE 0 END) as denegados
        FROM accesos_log
        WHERE DATE(fecha_hora) = CURDATE()
        GROUP BY HOUR(fecha_hora)
        ORDER BY hora ASC
    """
    return execute_query(query, fetch_all=True) or []


def get_all_filtered(fecha_inicio=None, fecha_fin=None, resultado=None, user_id=None, limit=100):
    """Get filtered access logs."""
    query = """
        SELECT a.id, a.qr_texto, a.resultado, a.fecha_hora, a.user_id,
               u.nombre, u.correo
        FROM accesos_log a
        LEFT JOIN usuarios u ON a.user_id = u.id
        WHERE 1=1
    """
    params = []

    if fecha_inicio:
        query += " AND a.fecha_hora >= %s"
        params.append(fecha_inicio)
    if fecha_fin:
        query += " AND a.fecha_hora <= %s"
        params.append(fecha_fin)
    if resultado:
        query += " AND a.resultado = %s"
        params.append(resultado)
    if user_id:
        query += " AND a.user_id = %s"
        params.append(user_id)

    query += " ORDER BY a.fecha_hora DESC LIMIT %s"
    params.append(limit)

    return execute_query(query, tuple(params), fetch_all=True)


def count_total():
    """Count total access logs."""
    result = execute_query("SELECT COUNT(*) as total FROM accesos_log", fetch_one=True)
    return result['total'] if result else 0
