from datetime import datetime, timedelta
from typing import Optional
from jose import JWTError, jwt
import bcrypt

# Clave secreta y algoritmo para JWT
SECRET_KEY = "mi_super_clave_secreta_para_el_portafolio_de_ciberseguridad_123"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

# verificacion de hash - contraseña
def verificar_password(password_plano: str, password_hasheado: str) -> bool:
    # bcrypt trabaja con bytes, por lo que convertimos los strings usando .encode('utf-8')
    return bcrypt.checkpw(password_plano.encode('utf-8'), password_hasheado.encode('utf-8'))

# Encriptacion
def obtener_password_hash(password: str) -> str:
    # Generamos un "salt" y hasheamos la contraseña, luego la decodificamos a string para la BD
    return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

#funcion token
def crear_token_acceso(data: dict, expires_delta: Optional[timedelta] = None):
    para_encriptar = data.copy()
    if expires_delta:
        expiracion = datetime.utcnow() + expires_delta
    else:
        expiracion = datetime.utcnow() + timedelta(minutes=15)
    
    # Añadimos la fecha de expiración al token
    para_encriptar.update({"exp": expiracion})
    
    #codificacion de key
    token_jwt = jwt.encode(para_encriptar, SECRET_KEY, algorithm=ALGORITHM)
    return token_jwt