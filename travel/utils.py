# travel/utils.py
import qrcode
from io import BytesIO
from django.core.files.base import ContentFile
import base64

def generate_qr_code(data):
    """Generar código QR para voucher"""
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=10,
        border=4,
    )
    qr.add_data(data)
    qr.make(fit=True)
    
    img = qr.make_image(fill_color="black", back_color="white")
    
    # Convertir a base64 para mostrar en template
    buffer = BytesIO()
    img.save(buffer, format='PNG')
    img_str = base64.b64encode(buffer.getvalue()).decode()
    
    return f"data:image/png;base64,{img_str}"

def format_voucher_code(trip_id, segment_id):
    """Generar código de voucher único"""
    from datetime import date
    today = date.today()
    return f"AT-{trip_id:02d}-{today.strftime('%y%m%d')}-{segment_id:03d}"