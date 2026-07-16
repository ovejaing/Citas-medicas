from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from database import Base
import datetime

class Usuario(Base):
    __tablename__ = "usuarios"

    id = Column(Integer, primary_key=True, index=True)
    nombre = Column(String, nullable=False)
    email = Column(String, unique=True, index=True, nullable=False)
    password_hash = Column(String, nullable=False)  # Aquí guardaremos la contraseña encriptada
    rol = Column(String, nullable=False)  # 'admin', 'medico' o 'paciente'
    telefono = Column(String, nullable=True)

    # Relaciones: Un usuario médico o paciente puede tener muchas citas
    citas_como_paciente = relationship("Cita", foreign_keys="Cita.paciente_id", back_populates="paciente")
    citas_como_medico = relationship("Cita", foreign_keys="Cita.medico_id", back_populates="medico")


class Especialidad(Base):
    __tablename__ = "especialidades"

    id = Column(Integer, primary_key=True, index=True)
    nombre = Column(String, unique=True, index=True, nullable=False)
    descripcion = Column(String, nullable=True)

    # Relación: Una especialidad puede estar en muchas citas
    citas = relationship("Cita", back_populates="especialidad")


class Cita(Base):
    __tablename__ = "citas"

    id = Column(Integer, primary_key=True, index=True)
    paciente_id = Column(Integer, ForeignKey("usuarios.id"), nullable=False)
    medico_id = Column(Integer, ForeignKey("usuarios.id"), nullable=False)
    especialidad_id = Column(Integer, ForeignKey("especialidades.id"), nullable=False)
    
    fecha_hora = Column(DateTime, nullable=False)  # Fecha y hora programada de la cita
    motivo = Column(String, nullable=True)
    estado = Column(String, default="pendiente")  # 'pendiente', 'completada', 'cancelada'

    # Definición de relaciones para acceder fácilmente a los objetos relacionados
    paciente = relationship("Usuario", foreign_keys=[paciente_id], back_populates="citas_como_paciente")
    medico = relationship("Usuario", foreign_keys=[medico_id], back_populates="citas_como_medico")
    especialidad = relationship("Especialidad", back_populates="citas")