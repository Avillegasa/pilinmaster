import hmac
import hashlib
from django.conf import settings

SECRET_QR_KEY = getattr(settings, "QR_SECRET_KEY", "clave-secreta-segura")

def generar_firma_qr(id_visita: int) -> str:
    msg = f"visita:{id_visita}"
    return hmac.new(SECRET_QR_KEY.encode(), msg.encode(), hashlib.sha256).hexdigest()

def verificar_firma_qr(id_visita: int, firma_recibida: str) -> bool:
    firma_valida = generar_firma_qr(id_visita)
    return hmac.compare_digest(firma_valida, firma_recibida)
