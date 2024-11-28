from datetime import datetime
from typing import Optional
from pydantic import BaseModel
from sqlmodel import Field, SQLModel

class DFCombined(SQLModel, table=True):
    __tablename__ = "combined_table"

    id: Optional[int] = Field(default=None, primary_key=True)
    hras_fact: Optional[float]
    socio_responsable: Optional[str]
    descrip_ceco_x: Optional[str]
    # cpt_std: Optional[int]
    descrip_funcion: Optional[str]
    ceco_emisor: Optional[str]
    id_socio_r: Optional[str]
    gerente: Optional[str]
    cuota_x: Optional[float]
    no_personal_validacion: Optional[int]
    counter: Optional[int]
    empleado: Optional[str]
    fecha_mod: Optional[datetime]
    funcion: Optional[str]
    razon_social: Optional[str]
    hra_mod: Optional[str]
    descrip_orden: Optional[str]
    moneda_x: Optional[str]
    ceco_orden: Optional[str]
    oficina: Optional[str]
    fecha: Optional[datetime]
    mes: Optional[int]
    idgerente: Optional[int]
    status_tratamiento: Optional[str]
    hon_bruto: Optional[float]
    hras_no_fact: Optional[float]
    importe_hras_no_fact: Optional[float]
    texto_explicativo_pt1: Optional[str]
    honb_cancplan: Optional[float]
    # modificado_por: Optional[str]
    # unidad_org: Optional[int]
    # creado_por: Optional[str]
    porc_canc: Optional[float]
    descrip_unidad_org: Optional[str]
    cl_pres_abs: Optional[float]
    descrip_operacion_cl_pres_abs: Optional[str]
    no_sap: Optional[float]
    nombre_completo: Optional[str]
    sociedad: Optional[str]
    desc_soc: Optional[str]
    pais_soc: Optional[str]
    marketplace_x: Optional[str]
    negocio: Optional[str]
    ceco_personal: Optional[str]
    descrip_ceco_y: Optional[str]
    descrip_area: Optional[str]
    especializacion: Optional[str]
    descrip_larga_func: Optional[str]
    categoria_global: Optional[str]

class DFPersonal(SQLModel, table=True):
    id: int = Field(default=None, primary_key=True)
    No_SAP: int = Field(default=None)
    Nombre_completo: str = Field(default=None)
    Sociedad: str = Field(default=None)
    Desc_Soc: str = Field(default=None)
    Pais_Soc: str = Field(default=None)
    Marketplace: str = Field(default=None)
    Negocio: str = Field(default=None)
    Ce_Co: str = Field(default=None)
    Descripc_Ce_Co: str = Field(default=None)
    Descripc_area_organi: str = Field(default=None)
    Especializacion: str = Field(default=None)
    Descripc_larga_Func: str = Field(default=None)
    Categoria_Global: str = Field(default=None)
    Desc_Subdiv_pers: str = Field(default=None)
    Oficina: str = Field(default=None)
    Oficina_fisica: str = Field(default=None)
    Fec_ingres: datetime = Field(default=None)
    email: str = Field(default=None)


class __DFSeunViejo(SQLModel, table=True):
    id: int = Field(default=None, primary_key=True)
    Market_Place: str = Field(default=None)
    Pais: str = Field(default=None)
    No_CeCo: str = Field(default=None)
    Descripcion_CeCo: str = Field(default=None)
    SEUN_Lider_Pais: str = Field(default=None)
    Linea_de_Servicios: str = Field(default=None)


class DFSeun(SQLModel, table=True):
    id: int = Field(default=None, primary_key=True)
    Codigo_CeCo: str = Field(default=None)
    Descripcion_CeCo: str = Field(default=None)
    Market_Place: str = Field(default=None)
    Pais: str = Field(default=None)
    Oficina_Admin: str = Field(default=None)
    Linea_de_Servicios: str = Field(default=None)
    SAP_Seun: int = Field(default=None)
    Seun: str = Field(default=None)


class DFUtilizacion(SQLModel, table=True):
    id: int = Field(default=None, primary_key=True)
    No_personal: float = Field(default=None)
    Hrs_Real_Per: float = Field(default=None)
    Hrs_Est_Per: int = Field(default=None)
    Porc_Meta_Util: float = Field(default=None)
    Porc_Real_Ut_Acu: float = Field(default=None)
    Fecha_Baja: Optional[datetime] = Field(default=None, nullable=True)


class DFValidacion(SQLModel, table=True):
    id: int = Field(default=None, primary_key=True)
    Hras_fact: float = Field(default=None)
    Descrip_CeCo_Emisor: str = Field(default=None)
    Descrip_Funcion: str = Field(default=None)
    CeCo_emisor: str = Field(default=None)
    No_personal: int = Field(default=None)
    Empleado: str = Field(default=None)
    Fecha: datetime = Field(default=None)
    Mes: int = Field(default=None)
    Hras_no_fact: float = Field(default=None)
    HonB_CancPlan: float = Field(default=None)
    Porc_Canc: float = Field(default=None)
    Texto_Explicativo_PT1: str = Field(default=None)


class DFTotalSocios(SQLModel, table=True):
    id: int = Field(default=None, primary_key=True)
    SAP: int = Field(default=None)
    Profesional: str = Field(default=None)
    Pais: str = Field(default=None)
    Oficina: str = Field(default=None)
    Linea: str = Field(default=None)
    Tiene_Grupo_Asignado: str = Field(default=None)


class DFReporteEmpleados(SQLModel, table=True):
    id: int = Field(default=None, primary_key=True)
    SAP: int = Field(default=None)
    Profesional: str = Field(default=None)
    Marketplace: str = Field(default=None)
    Pais: str = Field(default=None)
    Oficina_Admin: str = Field(default=None)
    Linea_De_Servicio: str = Field(default=None)
    Categoria: str = Field(default=None)
    CeCo: str = Field(default=None)
    Fecha_De_Ingreso: int = Field(default=None)
    SAP_Socio: int = Field(default=None)
    Asignacion_FY25: int = Field(default=None)


class DFUtilizacionActual(SQLModel, table=True):
    id: int = Field(default=None, primary_key=True)
    SAP: int = Field(default=None)
    Profesional: str = Field(default=None)
    Marketplace: str = Field(default=None)
    Pais: str = Field(default=None)
    Oficina: str = Field(default=None)
    Linea_de_Servicio: str = Field(default=None)
    Categoria: str = Field(default=None)
    CeCo: str = Field(default=None)
    Horas_Facturables_Mes: float = Field(default=None)
    Horas_Teoricas_Mes: float = Field(default=None)
    Porcentaje_Utilizacion_Mes: str = Field(default=None)
    Horas_Facturables_Periodo: float = Field(default=None)
    Horas_Teoricas_Periodo: float = Field(default=None)
    Porcentaje_Utilizacion_Periodo: str = Field(default=None)


class Hash(SQLModel, table=True):
    file: str = Field(primary_key=True)
    hash: str


class AggregatedValidationData(BaseModel):
    Descrip_CeCo_Emisor: str = Field(default=None)
    Hras_fact: float = Field(default=None)


class AggregatedSeunData(SQLModel, table=True):
    __tablename__ = "aggregated_seun_data"

    id: Optional[int] = Field(default=None, primary_key=True)
    Mes: Optional[int] = Field(default=None)
    Market_Place: str = Field(default=None)
    Linea_de_Servicios: str = Field(default=None)
    Pais: str = Field(default=None)
    Oficina_fisica: str = Field(default=None)
    No_CeCo: str = Field(default=None)
    Descripcion_CeCo: str = Field(default=None)
    reportes_no_entregados: int = Field(default=None)
    profesionales_no_entregaron: int = Field(default=None)
    No_SAP: Optional[int] = Field(default=None)
    Nombre_completo: Optional[str] = Field(default=None)
    email: Optional[str] = Field(default=None)


class MarketPlaceData(SQLModel, table=True):
    __tablename__ = "aggregated_market_place_data"

    id: Optional[int] = Field(default=None, primary_key=True)
    Mes: Optional[int] = Field(default=None)
    Market_Place_Filtrado: str = Field(default=None)
    Cantidad_Paises: int = Field(default=None)
    reportes_no_entregados: int = Field(default=None)
    profesionales_no_entregaron: int = Field(default=None)
    cantidad_seunes: int = Field(default=None)


class AggregatedSocioData(SQLModel, table=True):
    __tablename__ = "aggregated_socio_data"

    id: Optional[int] = Field(default=None, primary_key=True)
    Mes: Optional[int] = Field(default=None)
    SAP_Socio: int = Field(default=None)
    Socio: str = Field(default=None)
    Linea: str = Field(default=None)
    Pais: str = Field(default=None)
    Oficina: str = Field(default=None)
    reportes_no_entregados: int = Field(default=None)
    profesionales_no_entregaron: int = Field(default=None)
    Tiene_Grupo_Asignado: str = Field(default=None)


class AggregatedPaisData(SQLModel, table=True):
    __tablename__ = "aggregated_pais_data"

    id: Optional[int] = Field(default=None, primary_key=True)
    Mes: Optional[int] = Field(default=None)
    Pais: str = Field(default=None)
    Cantidad_Empleados: int = Field(default=None)
    Cantidad_Registros: int = Field(default=None)
    email: Optional[str] = Field(default=None)
