# usuarios/validaciones.py

def validar_rol_para_api(usuario):
    if usuario.rol and usuario.rol.nombre in ["Administrador", "Gerente"]:
        return False
    return True
