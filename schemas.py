from pydantic import BaseModel
from datetime import datetime
from typing import Optional

#esquema de usuarios
class UsuarioBase(BaseModel):
    nombre: str
    email: str
    rol: str
    telefono: Optional[str] = None

class UsuarioCreate(UsuarioBase):
    password: str

class UsuarioResponse(UsuarioBase):
    id: int

    class Config:
        # Compatibilidad doble para Pydantic v1 y v2
        orm_mode = True
        from_attributes = True


#esquema de especialidades
class EspecialidadBase(BaseModel):
    nombre: str
    descripcion: Optional[str] = None

class EspecialidadCreate(EspecialidadBase):
    pass

class EspecialidadResponse(EspecialidadBase):
    id: int

    class Config:
        orm_mode = True
        from_attributes = True


#esquema de citas
class CitaBase(BaseModel):
    medico_id: int
    especialidad_id: int
    fecha_hora: datetime
    motivo: Optional[str] = None

class CitaCreate(CitaBase):
    pass

class CitaResponse(CitaBase):
    id: int
    paciente_id: int
    estado: str

    class Config:
        orm_mode = True
        from_attributes = True


#Esquemas de seguridad
class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    email: Optional[str] = None