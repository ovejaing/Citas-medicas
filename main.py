from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from typing import List
from datetime import timedelta
from jose import jwt, JWTError

import models, schemas, security
from database import engine, get_db

#tablas
models.Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Sistema de Gestión de Citas Médicas",
    description="API RESTful segura con JWT para la gestión de citas.",
    version="1.0.0"
)

# Definicion de esquema oauth2
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")


# Proteccion de rutas
def obtener_usuario_actual(db: Session = Depends(get_db), token: str = Depends(oauth2_scheme)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="No se pudo validar el token de acceso",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        # Decodificamos el token usando nuestra clave secreta
        payload = jwt.decode(token, security.SECRET_KEY, algorithms=[security.ALGORITHM])
        email: str = payload.get("sub")
        if email is None:
            raise credentials_exception
        token_data = schemas.TokenData(email=email)
    except JWTError:
        raise credentials_exception
    
    # Buscamos al usuario dueño del token en la base de datos
    usuario = db.query(models.Usuario).filter(models.Usuario.email == token_data.email).first()
    if usuario is None:
        raise credentials_exception
    return usuario


# Endpoint Raíz
@app.get("/")
def inicio():
    return {"mensaje": "Bienvenido a la API de Gestión de Citas Médicas"}


#Generación de sesion

@app.post("/token", response_model=schemas.Token)
def login_para_obtener_token(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    # Buscamos al usuario por su email (que FastAPI recibe en el campo 'username')
    usuario = db.query(models.Usuario).filter(models.Usuario.email == form_data.username).first()
    
    # Validamos usuario y contraseña encriptada
    if not usuario or not security.verificar_password(form_data.password, usuario.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Correo o contraseña incorrectos",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # tiempo limite
    tiempo_expiracion = timedelta(minutes=security.ACCESS_TOKEN_EXPIRE_MINUTES)
    
    # Generamos el Token JWT guardando el email del usuario en el payload ('sub')
    access_token = security.crear_token_acceso(
        data={"sub": usuario.email}, expires_delta=tiempo_expiracion
    )
    
    return {"access_token": access_token, "token_type": "bearer"}


#EP usuarios


@app.post("/usuarios/", response_model=schemas.UsuarioResponse, status_code=status.HTTP_201_CREATED)
def crear_usuario(usuario: schemas.UsuarioCreate, db: Session = Depends(get_db)):
    usuario_existente = db.query(models.Usuario).filter(models.Usuario.email == usuario.email).first()
    if usuario_existente:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="El correo electrónico ya está registrado."
        )
    
    hashed_password = security.obtener_password_hash(usuario.password)

    nuevo_usuario = models.Usuario(
        nombre=usuario.nombre,
        email=usuario.email,
        password_hash=hashed_password,
        rol=usuario.rol,
        telefono=usuario.telefono
    )

    db.add(nuevo_usuario)
    db.commit()
    db.refresh(nuevo_usuario)
    return nuevo_usuario


# Ruta Protegida: Solo usuarios logueados pueden listar usuarios
@app.get("/usuarios/", response_model=List[schemas.UsuarioResponse])
def listar_usuarios(db: Session = Depends(get_db), usuario_actual: models.Usuario = Depends(obtener_usuario_actual)):
    return db.query(models.Usuario).all()


#EP especialiedades

@app.post("/especialidades/", response_model=schemas.EspecialidadResponse, status_code=status.HTTP_201_CREATED)
def crear_especialidad(especialidad: schemas.EspecialidadCreate, db: Session = Depends(get_db)):
    esp_existente = db.query(models.Especialidad).filter(models.Especialidad.nombre == especialidad.nombre).first()
    if esp_existente:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Esta especialidad ya está registrada."
        )
    
    nueva_especialidad = models.Especialidad(
        nombre=especialidad.nombre,
        descripcion=especialidad.descripcion
    )
    db.add(nueva_especialidad)
    db.commit()
    db.refresh(nueva_especialidad)
    return nueva_especialidad


@app.get("/especialidades/", response_model=List[schemas.EspecialidadResponse])
def listar_especialidades(db: Session = Depends(get_db)):
    return db.query(models.Especialidad).all()


#EP citas protegidas

# Ahora la cita se agenda automáticamente al Paciente que está logueado en el sistema
@app.post("/citas/", response_model=schemas.CitaResponse, status_code=status.HTTP_201_CREATED)
def agendar_cita(
    cita: schemas.CitaCreate, 
    db: Session = Depends(get_db), 
    usuario_actual: models.Usuario = Depends(obtener_usuario_actual)
):
    # Validación: Verificar que quien agenda sea realmente un Paciente
    if usuario_actual.rol != "paciente":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Solo los pacientes registrados pueden agendar citas."
        )

    # Validación 2: Verificar que el médico exista y tenga el rol correcto
    medico = db.query(models.Usuario).filter(models.Usuario.id == cita.medico_id).first()
    if not medico or medico.rol != "medico":
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="El médico especificado no existe o no tiene el rol correcto."
        )

    # Validación 3: Verificar que la especialidad exista
    especialidad = db.query(models.Especialidad).filter(models.Especialidad.id == cita.especialidad_id).first()
    if not especialidad:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="La especialidad especificada no existe."
        )

    # Citas usando id
    nueva_cita = models.Cita(
        paciente_id=usuario_actual.id,
        medico_id=cita.medico_id,
        especialidad_id=cita.especialidad_id,
        fecha_hora=cita.fecha_hora,
        motivo=cita.motivo
    )
    
    db.add(nueva_cita)
    db.commit()
    db.refresh(nueva_cita)
    return nueva_cita


# Listas de citas 
@app.get("/citas/", response_model=List[schemas.CitaResponse])
def listar_citas(
    db: Session = Depends(get_db), 
    usuario_actual: models.Usuario = Depends(obtener_usuario_actual)
):
    if usuario_actual.rol == "paciente":
        # Ver solo mis citas
        return db.query(models.Cita).filter(models.Cita.paciente_id == usuario_actual.id).all()
    elif usuario_actual.rol == "medico":
        # Ver las citas que tengo programadas como médico
        return db.query(models.Cita).filter(models.Cita.medico_id == usuario_actual.id).all()
    else:
        # Administradores pueden ver todas
        return db.query(models.Cita).all()