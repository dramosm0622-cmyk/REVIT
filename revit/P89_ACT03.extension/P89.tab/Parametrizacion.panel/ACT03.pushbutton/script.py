# -*- coding: utf-8 -*-
"""ACTIVIDAD 3 - BIM PARAMETRIZACION | Paciente: Casa Campestre P-892022 (Turbaco)

Hace en el proyecto Revit abierto, en un solo paso:
  1. Carga el archivo de parametros compartidos PARAM_ACT03_ParametrosCompartidos.txt
  2. Vincula los 5 parametros COMUNES (PAC_*) al proyecto (Shared + Project) y
     PAC_Norma_Diseno a Informacion de proyecto.
  3. Crea las 4 familias del paciente (P89_ZAP, P89_COL, P89_VCI, P89_COR) a partir
     de las familias estructurales de concreto de la plantilla/biblioteca y les agrega
     sus 3 parametros PARTICULARES. En la zapata crea la FORMULA
        ZAP_Volumen_Concreto = ZAP_Lado_B * ZAP_Lado_B * ZAP_Espesor_h
     y amarra Anchura = Longitud = ZAP_Lado_B, Espesor = ZAP_Espesor_h.
  4. Crea niveles, ejes 1-8 / A-G, tipos y elementos tomados de la Planta de
     Cimentaciones del plano P89-2022 (19 zapatas, 19 columnas, vigas VC, correas).
  5. Crea el Schedule multicategoria P89_ACT03_VALIDACION y lo abre.

Uso: pyRevit (boton ACT03) o RevitPythonShell (abrir y ejecutar este archivo).
Revit 2023 o superior. Abrir un proyecto NUEVO con la plantilla ESTRUCTURAL metrica.
Se puede ejecutar varias veces: no duplica parametros, tipos ni elementos.
"""
__title__ = "ACT03\nParametrizar"
__doc__ = "Actividad 3 BIM Parametrizacion - crea parametros, modelo, formula y Schedule"

import os
import glob
import tempfile
import clr
clr.AddReference("RevitAPI")
clr.AddReference("RevitAPIUI")
from Autodesk.Revit.DB import (
    BuiltInCategory, BuiltInParameter, CategorySet, ElementId, ElementType, Family,
    FamilySymbol, FilteredElementCollector, GroupTypeId, IFamilyLoadOptions,
    InstanceBinding, Level, Line, Grid, Material, SaveAsOptions, ScheduleFieldType,
    ScheduleSortGroupField, ScheduleFilter, ScheduleFilterType, StorageType,
    Transaction, TypeBinding, UnitTypeId, UnitUtils, ViewSchedule, XYZ)
from Autodesk.Revit.DB.Structure import StructuralType, StructuralInstanceUsage

uiapp = __revit__  # noqa: F821  (lo define pyRevit / RevitPythonShell)
app = uiapp.Application
uidoc = uiapp.ActiveUIDocument
doc = uidoc.Document

# Si el script se ejecuta desde RevitPythonShell y no encuentra el .txt,
# escriba aqui la ruta completa del archivo de parametros compartidos:
RUTA_TXT_MANUAL = r""

# ---- DATOS GENERADOS DESDE LA MATRIZ (no editar a mano salvo CORREAS) ----
NOMBRE_TXT = 'PARAM_ACT03_ParametrosCompartidos.txt'
NOMBRE_SCHEDULE = 'P89_ACT03_VALIDACION'
NORMA = 'NSR-10 Titulos B y C'
NIVELES = [('N+0,00', 0.0), ('N+3,05', 3.05), ('N+6,05', 6.05)]
TOPE_ZAPATA = -0.65  # desplante 1,00 m - h 0,35 m (cara superior de la zapata)
PERALTE_VIGA = 0.30
NOMBRES_DESFASE = ['Height Offset From Level', 'Desfase de altura desde nivel', 'Desfase']
PARAMS = [{'cp': 'Comun',
  'formula': '',
  'grupo': 'Datos de identidad',
  'nombre': 'PAC_Codigo_Elemento',
  'objetos': ['ZAP', 'COL', 'VCI', 'COR'],
  'ti': 'Instancia'},
 {'cp': 'Comun',
  'formula': '',
  'grupo': 'Datos de identidad',
  'nombre': 'PAC_Material_Estructural',
  'objetos': ['ZAP', 'COL', 'VCI', 'COR'],
  'ti': 'Tipo'},
 {'cp': 'Comun',
  'formula': '',
  'grupo': 'Datos de identidad',
  'nombre': 'PAC_Resistencia_MPa',
  'objetos': ['ZAP', 'COL', 'VCI', 'COR'],
  'ti': 'Tipo'},
 {'cp': 'Comun',
  'formula': '',
  'grupo': 'Restricciones',
  'nombre': 'PAC_Nivel_Referencia',
  'objetos': ['ZAP', 'COL', 'VCI', 'COR'],
  'ti': 'Instancia'},
 {'cp': 'Comun',
  'formula': '',
  'grupo': 'Datos IFC',
  'nombre': 'PAC_Clasificacion_IFC_Uniclass',
  'objetos': ['ZAP', 'COL', 'VCI', 'COR'],
  'ti': 'Tipo'},
 {'cp': 'Proyecto',
  'formula': '',
  'grupo': 'Datos de identidad',
  'nombre': 'PAC_Norma_Diseno',
  'objetos': [],
  'ti': 'Instancia (Informacion de proyecto)'},
 {'cp': 'Particular',
  'formula': '',
  'grupo': 'Cotas',
  'nombre': 'ZAP_Lado_B',
  'objetos': ['ZAP'],
  'ti': 'Tipo'},
 {'cp': 'Particular',
  'formula': '',
  'grupo': 'Cotas',
  'nombre': 'ZAP_Espesor_h',
  'objetos': ['ZAP'],
  'ti': 'Tipo'},
 {'cp': 'Particular',
  'formula': 'ZAP_Lado_B * ZAP_Lado_B * ZAP_Espesor_h',
  'grupo': 'Cotas',
  'nombre': 'ZAP_Volumen_Concreto',
  'objetos': ['ZAP'],
  'ti': 'Tipo'},
 {'cp': 'Particular',
  'formula': '',
  'grupo': 'Cotas',
  'nombre': 'COL_Seccion_bxh',
  'objetos': ['COL'],
  'ti': 'Tipo'},
 {'cp': 'Particular',
  'formula': '',
  'grupo': 'Cotas',
  'nombre': 'COL_Altura_Libre',
  'objetos': ['COL'],
  'ti': 'Instancia'},
 {'cp': 'Particular',
  'formula': '',
  'grupo': 'Datos de identidad',
  'nombre': 'COL_Refuerzo_Longitudinal',
  'objetos': ['COL'],
  'ti': 'Tipo'},
 {'cp': 'Particular',
  'formula': '',
  'grupo': 'Cotas',
  'nombre': 'VCI_Seccion_bxh',
  'objetos': ['VCI'],
  'ti': 'Tipo'},
 {'cp': 'Particular',
  'formula': '',
  'grupo': 'Datos de identidad',
  'nombre': 'VCI_Eje_Estructural',
  'objetos': ['VCI'],
  'ti': 'Instancia'},
 {'cp': 'Particular',
  'formula': '',
  'grupo': 'Datos de identidad',
  'nombre': 'VCI_Refuerzo',
  'objetos': ['VCI'],
  'ti': 'Tipo'},
 {'cp': 'Particular',
  'formula': '',
  'grupo': 'Datos de identidad',
  'nombre': 'COR_Designacion_Perfil',
  'objetos': ['COR'],
  'ti': 'Tipo'},
 {'cp': 'Particular',
  'formula': '',
  'grupo': 'Cotas',
  'nombre': 'COR_Espesor_Lamina',
  'objetos': ['COR'],
  'ti': 'Tipo'},
 {'cp': 'Particular',
  'formula': '',
  'grupo': 'Cotas',
  'nombre': 'COR_Separacion',
  'objetos': ['COR'],
  'ti': 'Instancia'}]
FAMILIAS = {'COL': {'ayuda': 'pilar de hormigon rectangular (M_Pilar de hormigon-Rectangular / '
                  'M_Concrete-Rectangular-Column)',
         'claves': ['Concrete-Rectangular-Column',
                    'Pilar de hormig',
                    'Rectangular-Column',
                    'Hormig',
                    'Concreto',
                    'Concrete'],
         'nombre': 'P89_COL_Columna_Concreto'},
 'COR': {'ayuda': 'perfil C laminado en frio (opcional; si no hay se usa la viga rectangular)',
         'claves': ['Cold Formed-C', 'CFS-C', 'LGS-C', 'Perfil C', 'C-Channel', 'Canal'],
         'nombre': 'P89_COR_Perfil_C_PHR'},
 'VCI': {'ayuda': 'viga de hormigon rectangular (M_Viga de hormigon-Rectangular / M_Concrete-Rectangular '
                  'Beam)',
         'claves': ['Concrete-Rectangular Beam',
                    'Viga de hormig',
                    'Rectangular Beam',
                    'Hormig',
                    'Concreto',
                    'Concrete'],
         'nombre': 'P89_VCI_Viga_Cimentacion'},
 'ZAP': {'ayuda': 'cimentacion aislada rectangular (M_Zapata-Rectangular / M_Footing-Rectangular)',
         'claves': ['Footing-Rectangular', 'Zapata-Rectangular', 'Zapata rectangular', 'Zapata', 'Footing'],
         'nombre': 'P89_ZAP_Zapata_Aislada'}}
AMARRES = {'ZAP': [(['Width', 'Anchura', 'Ancho'], 'ZAP_Lado_B'),
         (['Length', 'Longitud'], 'ZAP_Lado_B'),
         (['Foundation Thickness',
           'Thickness',
           'Grosor de cimentación',
           'Espesor de cimentación',
           'Grosor de cimentacion',
           'Grosor',
           'Espesor'],
          'ZAP_Espesor_h')]}
CLASIFICACION = [('ZAP', 'IfcFooting.PAD_FOOTING | EF_20_10'),
 ('COL', 'IfcColumn.COLUMN | EF_25_10'),
 ('VCI', 'IfcBeam.BEAM | EF_20_10'),
 ('COR', 'IfcMember.PURLIN | EF_30_10')]
TIPOS = [['ZAP', 'Z-T1', 1.3, 0.35, "Concreto reforzado f'c 21 MPa", 21, 'VERIFICAR en despiece P-892022'],
 ['ZAP', 'Z-T2', 1.6, 0.35, "Concreto reforzado f'c 21 MPa", 21, 'VERIFICAR en despiece P-892022'],
 ['ZAP', 'Z-T3', 1.7, 0.35, "Concreto reforzado f'c 21 MPa", 21, 'VERIFICAR en despiece P-892022'],
 ['COL', 'C-30x30', 0.3, 0.3, "Concreto reforzado f'c 21 MPa", 21, 'VERIFICAR en despiece P-892022'],
 ['COL', 'C-25x40', 0.25, 0.4, "Concreto reforzado f'c 21 MPa", 21, 'VERIFICAR en despiece P-892022'],
 ['COL', 'C-40x25', 0.4, 0.25, "Concreto reforzado f'c 21 MPa", 21, 'VERIFICAR en despiece P-892022'],
 ['VCI', 'VC-TIPO', 0.3, 0.3, "Concreto reforzado f'c 21 MPa", 21, 'VERIFICAR en despiece P-892022'],
 ['COR', 'PHR C 160x60x20', 0.06, 0.16, 'Acero laminado en frio PHR', 340, 'e = 1,50 mm']]
EJES_X = [('1', 0.0), ('2', 2.001), ('3', 3.07), ('4', 5.511), ('5', 6.1), ('6', 7.5), ('7', 11.6), ('8', 15.56)]
EJES_Y = [('A', 0.0), ('B', 0.38), ('C', 2.48), ('D', 3.98), ('E', 6.86), ('F', 11.18), ('G', 11.88)]
# Planta de cimentaciones P89-2022: origen = interseccion ejes 1-A, metros
COLUMNAS = [{'dlab': 1.14, 'eje': '3-F', 'n3': True, 'sec': 'C-30x30', 'x': 3.07, 'y': 11.18, 'zap': 'Z-T3'},
 {'dlab': 0.86, 'eje': '5-F', 'n3': True, 'sec': 'C-30x30', 'x': 6.1, 'y': 11.18, 'zap': 'Z-T1'},
 {'dlab': 0.86, 'eje': '7-G', 'n3': False, 'sec': 'C-30x30', 'x': 11.6, 'y': 11.88, 'zap': 'Z-T1'},
 {'dlab': 0.86, 'eje': '8-G', 'n3': False, 'sec': 'C-25x40', 'x': 15.56, 'y': 11.88, 'zap': 'Z-T1'},
 {'dlab': 1.0, 'eje': '1-E', 'n3': True, 'sec': 'C-25x40', 'x': 0.0, 'y': 6.86, 'zap': 'Z-T2'},
 {'dlab': 1.0, 'eje': '3-E', 'n3': True, 'sec': 'C-30x30', 'x': 3.07, 'y': 6.86, 'zap': 'Z-T2'},
 {'dlab': 1.0, 'eje': '6-E', 'n3': True, 'sec': 'C-30x30', 'x': 7.5, 'y': 6.86, 'zap': 'Z-T2'},
 {'dlab': 1.0, 'eje': '7-E', 'n3': True, 'sec': 'C-30x30', 'x': 11.6, 'y': 6.86, 'zap': 'Z-T2'},
 {'dlab': 0.86, 'eje': '8-E', 'n3': False, 'sec': 'C-30x30', 'x': 15.56, 'y': 6.86, 'zap': 'Z-T1'},
 {'dlab': 0.86, 'eje': '8-D', 'n3': False, 'sec': 'C-30x30', 'x': 15.56, 'y': 3.98, 'zap': 'Z-T1'},
 {'dlab': 1.14, 'eje': '7-D', 'n3': True, 'sec': 'C-30x30', 'x': 11.6, 'y': 3.98, 'zap': 'Z-T3'},
 {'dlab': 1.14, 'eje': '6-D', 'n3': True, 'sec': 'C-30x30', 'x': 7.5, 'y': 3.98, 'zap': 'Z-T3'},
 {'dlab': 0.86, 'eje': '6-A', 'n3': False, 'sec': 'C-30x30', 'x': 7.5, 'y': 0.0, 'zap': 'Z-T1'},
 {'dlab': 0.86, 'eje': '7-A', 'n3': False, 'sec': 'C-30x30', 'x': 11.6, 'y': 0.0, 'zap': 'Z-T1'},
 {'dlab': 0.86, 'eje': '8-A', 'n3': False, 'sec': 'C-30x30', 'x': 15.56, 'y': 0.0, 'zap': 'Z-T1'},
 {'dlab': 0.86, 'eje': '2-C', 'n3': False, 'sec': 'C-30x30', 'x': 2.0, 'y': 2.48, 'zap': 'Z-T1'},
 {'dlab': 0.86, 'eje': '1-C', 'n3': False, 'sec': 'C-25x40', 'x': 0.0, 'y': 2.48, 'zap': 'Z-T1'},
 {'dlab': 0.86, 'eje': '1-B', 'n3': False, 'sec': 'C-40x25', 'x': 0.0, 'y': 0.38, 'zap': 'Z-T1'},
 {'dlab': 0.86, 'eje': '4-B', 'n3': False, 'sec': 'C-40x25', 'x': 5.51, 'y': 0.38, 'zap': 'Z-T1'}]
VIGAS = [{'cod': 'VCI-VC-1-B/C', 'eje': '1', 'x1': 0.0, 'x2': 0.0, 'y1': 0.38, 'y2': 2.48},
 {'cod': 'VCI-VC-1-C/E', 'eje': '1', 'x1': 0.0, 'x2': 0.0, 'y1': 2.48, 'y2': 6.86},
 {'cod': 'VCI-VC-3-E/F', 'eje': '3', 'x1': 3.07, 'x2': 3.07, 'y1': 6.86, 'y2': 11.18},
 {'cod': 'VCI-VC-6-A/D', 'eje': '6', 'x1': 7.5, 'x2': 7.5, 'y1': 0.0, 'y2': 3.98},
 {'cod': 'VCI-VC-6-D/E', 'eje': '6', 'x1': 7.5, 'x2': 7.5, 'y1': 3.98, 'y2': 6.86},
 {'cod': 'VCI-VC-7-A/D', 'eje': '7', 'x1': 11.6, 'x2': 11.6, 'y1': 0.0, 'y2': 3.98},
 {'cod': 'VCI-VC-7-D/E', 'eje': '7', 'x1': 11.6, 'x2': 11.6, 'y1': 3.98, 'y2': 6.86},
 {'cod': 'VCI-VC-7-E/G', 'eje': '7', 'x1': 11.6, 'x2': 11.6, 'y1': 6.86, 'y2': 11.88},
 {'cod': 'VCI-VC-8-A/D', 'eje': '8', 'x1': 15.56, 'x2': 15.56, 'y1': 0.0, 'y2': 3.98},
 {'cod': 'VCI-VC-8-D/E', 'eje': '8', 'x1': 15.56, 'x2': 15.56, 'y1': 3.98, 'y2': 6.86},
 {'cod': 'VCI-VC-8-E/G', 'eje': '8', 'x1': 15.56, 'x2': 15.56, 'y1': 6.86, 'y2': 11.88},
 {'cod': 'VCI-VC-A-6/7', 'eje': 'A', 'x1': 7.5, 'x2': 11.6, 'y1': 0.0, 'y2': 0.0},
 {'cod': 'VCI-VC-A-7/8', 'eje': 'A', 'x1': 11.6, 'x2': 15.56, 'y1': 0.0, 'y2': 0.0},
 {'cod': 'VCI-VC-B-1/4', 'eje': 'B', 'x1': 0.0, 'x2': 5.51, 'y1': 0.38, 'y2': 0.38},
 {'cod': 'VCI-VC-C-1/2', 'eje': 'C', 'x1': 0.0, 'x2': 2.0, 'y1': 2.48, 'y2': 2.48},
 {'cod': 'VCI-VC-D-6/7', 'eje': 'D', 'x1': 7.5, 'x2': 11.6, 'y1': 3.98, 'y2': 3.98},
 {'cod': 'VCI-VC-D-7/8', 'eje': 'D', 'x1': 11.6, 'x2': 15.56, 'y1': 3.98, 'y2': 3.98},
 {'cod': 'VCI-VC-E-1/3', 'eje': 'E', 'x1': 0.0, 'x2': 3.07, 'y1': 6.86, 'y2': 6.86},
 {'cod': 'VCI-VC-E-3/6', 'eje': 'E', 'x1': 3.07, 'x2': 7.5, 'y1': 6.86, 'y2': 6.86},
 {'cod': 'VCI-VC-E-6/7', 'eje': 'E', 'x1': 7.5, 'x2': 11.6, 'y1': 6.86, 'y2': 6.86},
 {'cod': 'VCI-VC-E-7/8', 'eje': 'E', 'x1': 11.6, 'x2': 15.56, 'y1': 6.86, 'y2': 6.86},
 {'cod': 'VCI-VC-F-3/5', 'eje': 'F', 'x1': 3.07, 'x2': 6.1, 'y1': 11.18, 'y2': 11.18},
 {'cod': 'VCI-VC-G-7/8', 'eje': 'G', 'x1': 11.6, 'x2': 15.56, 'y1': 11.88, 'y2': 11.88}]
# Trazado aproximado (zona ejes 7-8 de la planta N+3,05; separacion ~1,00 m segun etiquetas PHR del plano). Ajustar si se requiere.
CORREAS = {'nivel': 'N+3,05',
 'separacion': 1.0,
 'x1': 11.6,
 'x2': 15.56,
 'y': [0.5, 1.5, 2.5, 3.5, 4.5, 5.5, 6.5, 7.5, 8.5, 9.5, 10.5, 11.5]}
CAMPOS_SCHEDULE = ['Categoria',
 'Familia y tipo',
 'PAC_Codigo_Elemento',
 'PAC_Material_Estructural',
 'PAC_Resistencia_MPa',
 'PAC_Nivel_Referencia',
 'PAC_Clasificacion_IFC_Uniclass',
 'ZAP_Lado_B',
 'ZAP_Espesor_h',
 'ZAP_Volumen_Concreto',
 'COL_Seccion_bxh',
 'COL_Altura_Libre',
 'COL_Refuerzo_Longitudinal',
 'VCI_Seccion_bxh',
 'VCI_Eje_Estructural',
 'VCI_Refuerzo',
 'COR_Designacion_Perfil',
 'COR_Espesor_Lamina',
 'COR_Separacion',
 '#']

LOG = []


def log(msg):
    LOG.append(msg)
    print(msg)


def m(v):
    """metros -> unidades internas (pies)"""
    return UnitUtils.ConvertToInternalUnits(float(v), UnitTypeId.Meters)


def mm(v):
    return UnitUtils.ConvertToInternalUnits(float(v), UnitTypeId.Millimeters)


GRUPOS = {
    "Datos de identidad": GroupTypeId.IdentityData,
    "Cotas": GroupTypeId.Geometry,
    "Restricciones": GroupTypeId.Constraints,
    "Datos IFC": GroupTypeId.Ifc,
}

BIC = {
    "ZAP": BuiltInCategory.OST_StructuralFoundation,
    "COL": BuiltInCategory.OST_StructuralColumns,
    "VCI": BuiltInCategory.OST_StructuralFraming,
    "COR": BuiltInCategory.OST_StructuralFraming,
}


# ---------------------------------------------------------------- utilidades
def ruta_txt():
    cands = []
    try:
        cands.append(os.path.join(os.path.dirname(__file__), NOMBRE_TXT))
    except NameError:
        pass
    if RUTA_TXT_MANUAL:
        cands.insert(0, RUTA_TXT_MANUAL)
    for c in cands:
        if os.path.exists(c):
            return c
    # ultimo recurso: dialogo para elegir el archivo
    clr.AddReference("System.Windows.Forms")
    from System.Windows.Forms import OpenFileDialog, DialogResult
    dlg = OpenFileDialog()
    dlg.Title = "Seleccione " + NOMBRE_TXT
    dlg.Filter = "Parametros compartidos (*.txt)|*.txt"
    if dlg.ShowDialog() == DialogResult.OK:
        return dlg.FileName
    raise Exception("No se encontro " + NOMBRE_TXT)


def leer_definiciones(path):
    anterior = app.SharedParametersFilename
    app.SharedParametersFilename = path
    dfile = app.OpenSharedParameterFile()
    if dfile is None:
        app.SharedParametersFilename = anterior
        raise Exception("Revit no pudo leer el archivo de parametros compartidos: " + path)
    defs = {}
    for g in dfile.Groups:
        for d in g.Definitions:
            defs[d.Name] = d
    faltan = [p["nombre"] for p in PARAMS if p["nombre"] not in defs]
    if faltan:
        raise Exception("Faltan en el .txt: " + ", ".join(faltan))
    return defs, anterior


def lookup(elem, nombres):
    """Devuelve el primer parametro que exista entre varios nombres (EN/ES)."""
    for n in nombres:
        p = elem.LookupParameter(n)
        if p is not None:
            return p
    return None


def set_val(elem, nombre, valor, unidad="m"):
    p = lookup(elem, nombre) if isinstance(nombre, (list, tuple)) else elem.LookupParameter(nombre)
    if p is None or p.IsReadOnly:
        return False
    st = p.StorageType
    if st == StorageType.String:
        p.Set(str(valor))
    elif st == StorageType.Double:
        if unidad == "m":
            p.Set(m(valor))
        elif unidad == "mm":
            p.Set(mm(valor))
        else:
            p.Set(float(valor))
    elif st == StorageType.Integer:
        p.Set(int(valor))
    elif st == StorageType.ElementId:
        p.Set(valor)
    return True


def set_bip(elem, bip, valor):
    p = elem.get_Parameter(bip)
    if p is None or p.IsReadOnly:
        return False
    if isinstance(valor, ElementId):
        p.Set(valor)
    else:
        p.Set(m(valor))
    return True


def simbolos(bic):
    return list(FilteredElementCollector(doc).OfClass(FamilySymbol).OfCategory(bic))


def familia_por_nombre(bic, nombre):
    for s in simbolos(bic):
        if s.Family.Name == nombre:
            return s.Family
    return None


def buscar_familia(bic, claves, excluir=()):
    """Familia ya cargada cuyo nombre contenga alguna clave (por orden)."""
    fams = {}
    for s in simbolos(bic):
        fams[s.Family.Name] = s.Family
    for c in claves:
        for n, f in sorted(fams.items()):
            if c.lower() in n.lower() and not n.startswith("P89_") and n not in excluir:
                return f
    return None


def cargar_de_biblioteca(bic, claves):
    """Busca el .rfa en la biblioteca de Revit instalada y lo carga."""
    raices = glob.glob(r"C:\ProgramData\Autodesk\RVT *\Libraries")
    raices = sorted(raices, reverse=True)
    for raiz in raices:
        for c in claves:
            for dp, dn, fn in os.walk(raiz):
                for f in fn:
                    if f.lower().endswith(".rfa") and c.lower() in f.lower():
                        t = Transaction(doc, "P89 cargar familia")
                        t.Start()
                        ok = doc.LoadFamily(os.path.join(dp, f))
                        t.Commit()
                        if ok:
                            log("  Familia cargada de biblioteca: " + f)
                            return buscar_familia(bic, [os.path.splitext(f)[0]])
    return None


class OpcionesCarga(IFamilyLoadOptions):
    def OnFamilyFound(self, familyInUse, overwriteParameterValues):
        overwriteParameterValues.Value = True
        return True

    def OnSharedFamilyFound(self, sharedFamily, familyInUse, source, overwriteParameterValues):
        overwriteParameterValues.Value = True
        return True


def fparam(fm, nombres, solo_longitud=False):
    for n in nombres:
        p = fm.get_Parameter(n)
        if p is not None:
            return p
    return None


def preparar_familia(base, nuevo_nombre, codigo, defs):
    """Edita la familia base, agrega los parametros particulares compartidos,
    formulas y amarres, la guarda como P89_xxx y la carga al proyecto."""
    fdoc = doc.EditFamily(base)
    fm = fdoc.FamilyManager
    t = Transaction(fdoc, "P89 parametros particulares " + codigo)
    t.Start()
    if fm.Types.Size == 0:
        fm.NewType(nuevo_nombre)
    nuevos = []
    for p in PARAMS:
        if p["cp"] != "Particular" or codigo not in p["objetos"]:
            continue
        fp = fm.get_Parameter(p["nombre"])
        if fp is None:
            fp = fm.AddParameter(defs[p["nombre"]], GRUPOS[p["grupo"]], p["ti"] == "Instancia")
            nuevos.append(p["nombre"])
    # valores iniciales en todos los tipos (evita geometria en cero antes de la formula)
    amarres = AMARRES.get(codigo, [])
    for ft in fm.Types:
        fm.CurrentType = ft
        for destino_nombres, origen in amarres:
            dp = fparam(fm, destino_nombres)
            op = fm.get_Parameter(origen)
            if dp is not None and op is not None:
                v = ft.AsDouble(dp)
                if v:
                    fm.Set(op, v)
    # amarres: el parametro nativo queda controlado por el compartido
    for destino_nombres, origen in amarres:
        dp = fparam(fm, destino_nombres)
        if dp is None:
            log("  AVISO: la familia no tiene " + "/".join(destino_nombres) + " (no se amarro a " + origen + ")")
            continue
        try:
            fm.SetFormula(dp, origen)
            log("  Amarre: " + dp.Definition.Name + " = " + origen)
        except Exception as e:
            log("  AVISO amarre " + dp.Definition.Name + ": " + str(e))
    for p in PARAMS:
        if p["formula"] and codigo in p["objetos"]:
            fm.SetFormula(fm.get_Parameter(p["nombre"]), p["formula"])
            log("  FORMULA: " + p["nombre"] + " = " + p["formula"])
    t.Commit()
    if nuevos:
        log("  Parametros particulares agregados: " + ", ".join(nuevos))
    if not fdoc.Title.startswith(nuevo_nombre):
        ruta = os.path.join(tempfile.gettempdir(), nuevo_nombre + ".rfa")
        op = SaveAsOptions()
        op.OverwriteExistingFile = True
        fdoc.SaveAs(ruta, op)
    fam = fdoc.LoadFamily(doc, OpcionesCarga())
    fdoc.Close(False)
    return familia_por_nombre(BIC[codigo], nuevo_nombre) or fam


def material(claves):
    mats = list(FilteredElementCollector(doc).OfClass(Material))
    for c in claves:
        for mt in mats:
            if c.lower() in mt.Name.lower():
                return mt.Id
    return None


def nivel(nombre, elev):
    for lv in FilteredElementCollector(doc).OfClass(Level):
        if lv.Name == nombre:
            return lv
    for lv in FilteredElementCollector(doc).OfClass(Level):
        if abs(lv.Elevation - m(elev)) < 0.01 and not lv.Name.startswith("N+"):
            lv.Name = nombre
            return lv
    lv = Level.Create(doc, m(elev))
    lv.Name = nombre
    return lv


def tipo(fam, nombre):
    syms = [doc.GetElement(i) for i in fam.GetFamilySymbolIds()]
    for s in syms:
        if s.Name == nombre:
            return s
    return syms[0].Duplicate(nombre)


def codigos_existentes():
    cods = set()
    for bic in set(BIC.values()):
        for e in FilteredElementCollector(doc).OfCategory(bic).WhereElementIsNotElementType():
            p = e.LookupParameter("PAC_Codigo_Elemento")
            if p is not None and p.AsString():
                cods.add(p.AsString())
    return cods


# ------------------------------------------------------------------- proceso
def main():
    if doc.IsFamilyDocument:
        raise Exception("Abra un PROYECTO (.rvt), no una familia.")
    path = ruta_txt()
    log("1) Parametros compartidos: " + path)
    defs, anterior = leer_definiciones(path)

    # 2) parametros comunes -> proyecto
    log("2) Vinculando parametros comunes al proyecto")
    t = Transaction(doc, "P89 parametros comunes")
    t.Start()
    cats = CategorySet()
    for bic in (BuiltInCategory.OST_StructuralFoundation, BuiltInCategory.OST_StructuralColumns,
                BuiltInCategory.OST_StructuralFraming):
        cats.Insert(doc.Settings.Categories.get_Item(bic))
    for p in PARAMS:
        if p["cp"] == "Comun":
            b = app.Create.NewInstanceBinding(cats) if p["ti"] == "Instancia" else app.Create.NewTypeBinding(cats)
        elif p["cp"] == "Proyecto":
            pc = CategorySet()
            pc.Insert(doc.Settings.Categories.get_Item(BuiltInCategory.OST_ProjectInformation))
            b = app.Create.NewInstanceBinding(pc)
        else:
            continue
        d = defs[p["nombre"]]
        if not doc.ParameterBindings.Insert(d, b, GRUPOS[p["grupo"]]):
            doc.ParameterBindings.ReInsert(d, b, GRUPOS[p["grupo"]])
        log("  " + p["nombre"] + " (" + p["ti"] + ")")
    t.Commit()

    # 3) familias del paciente
    log("3) Familias del paciente")
    fams = {}
    for codigo in ("ZAP", "COL", "VCI", "COR"):
        nombre = FAMILIAS[codigo]["nombre"]
        bic = BIC[codigo]
        base = familia_por_nombre(bic, nombre)
        if base is None:
            base = buscar_familia(bic, FAMILIAS[codigo]["claves"])
        if base is None:
            base = cargar_de_biblioteca(bic, FAMILIAS[codigo]["claves"])
        if base is None and codigo == "COR":
            # sin perfil C en la biblioteca: se parte de la viga de concreto,
            # se guarda como familia propia y se le da la seccion 0,06 x 0,16
            base = buscar_familia(bic, FAMILIAS["VCI"]["claves"])
            log("  AVISO: no se encontro familia de perfil C; la correa se representa con seccion rectangular 60x160 mm")
        if base is None:
            raise Exception("No se encontro una familia para " + codigo + ". Cargue una familia de "
                            + FAMILIAS[codigo]["ayuda"] + " (Insertar > Cargar familia) y vuelva a ejecutar.")
        log(" " + codigo + ": base '" + base.Name + "' -> " + nombre)
        fams[codigo] = preparar_familia(base, nombre, codigo, defs)

    # 4) modelo
    log("4) Niveles, ejes, tipos y elementos")
    t = Transaction(doc, "P89 modelo")
    t.Start()
    lv = {}
    for n, e in NIVELES:
        lv[n] = nivel(n, e)
    grids = set(g.Name for g in FilteredElementCollector(doc).OfClass(Grid))
    for n, x in EJES_X:
        if n not in grids:
            g = Grid.Create(doc, Line.CreateBound(XYZ(m(x), m(-1.8), 0), XYZ(m(x), m(13.8), 0)))
            g.Name = n
    for n, y in EJES_Y:
        if n not in grids:
            g = Grid.Create(doc, Line.CreateBound(XYZ(m(-1.8), m(y), 0), XYZ(m(17.4), m(y), 0)))
            g.Name = n

    conc = material(["Concreto", "Hormig", "Concrete"])
    acero = material(["Acero", "Steel"])
    clas = dict((o, v) for o, v in CLASIFICACION)
    sym = {}
    for cod, nom, b, h, mat, fc, ref in TIPOS:
        s = tipo(fams[cod], nom)
        if not s.IsActive:
            s.Activate()
        set_val(s, "PAC_Material_Estructural", mat)
        set_val(s, "PAC_Resistencia_MPa", fc, unidad=None)
        set_val(s, "PAC_Clasificacion_IFC_Uniclass", clas[cod])
        mid = acero if cod == "COR" else conc
        if mid is not None:
            p = s.get_Parameter(BuiltInParameter.STRUCTURAL_MATERIAL_PARAM)
            if p is not None and not p.IsReadOnly:
                p.Set(mid)
        sec = ("%.2fx%.2f" % (b, h)).replace(".", ",")
        if cod == "ZAP":
            set_val(s, "ZAP_Lado_B", b)
            set_val(s, "ZAP_Espesor_h", h)
        elif cod == "COL":
            set_val(s, ["b", "Anchura", "Width"], b)
            set_val(s, ["h", "Profundidad", "Depth"], h)
            set_val(s, "COL_Seccion_bxh", sec)
            set_val(s, "COL_Refuerzo_Longitudinal", ref)
        elif cod == "VCI":
            set_val(s, ["b", "Anchura", "Width"], b)
            set_val(s, ["h", "Altura", "Height", "Depth"], h)
            set_val(s, "VCI_Seccion_bxh", sec)
            set_val(s, "VCI_Refuerzo", ref)
        elif cod == "COR":
            set_val(s, ["b", "Anchura", "Width"], b)
            set_val(s, ["h", "Altura", "Height", "Depth"], h)
            set_val(s, "COR_Designacion_Perfil", nom)
            set_val(s, "COR_Espesor_Lamina", 1.50, unidad="mm")
        sym[nom] = s
    doc.Regenerate()

    hechos = codigos_existentes()
    n0, n3, n6 = lv[NIVELES[0][0]], lv[NIVELES[1][0]], lv[NIVELES[2][0]]
    cont = {"ZAP": 0, "COL": 0, "VCI": 0, "COR": 0}

    def comunes(e, codigo, nivel_txt):
        set_val(e, "PAC_Codigo_Elemento", codigo)
        set_val(e, "PAC_Nivel_Referencia", nivel_txt)

    for c in COLUMNAS:
        eje = c["eje"]
        z_cod = "ZAP-" + c["zap"].replace("-", "") + "-" + eje
        if z_cod not in hechos:
            z = doc.Create.NewFamilyInstance(XYZ(m(c["x"]), m(c["y"]), 0), sym[c["zap"]], n0, StructuralType.Footing)
            ok = False
            for bip in (BuiltInParameter.INSTANCE_FREE_HOST_OFFSET_PARAM,
                        BuiltInParameter.INSTANCE_ELEVATION_PARAM,
                        BuiltInParameter.FLOOR_HEIGHTABOVELEVEL_PARAM):
                if set_bip(z, bip, TOPE_ZAPATA):
                    ok = True
                    break
            if not ok:
                set_val(z, NOMBRES_DESFASE, TOPE_ZAPATA)
            comunes(z, z_cod, NIVELES[0][0])
            cont["ZAP"] += 1
        c_cod = "COL-" + c["sec"].replace("-", "").replace("x", "X") + "-" + eje
        if c_cod not in hechos:
            col = doc.Create.NewFamilyInstance(XYZ(m(c["x"]), m(c["y"]), 0), sym[c["sec"]], n0, StructuralType.Column)
            top = n6 if c["n3"] else n3
            set_bip(col, BuiltInParameter.FAMILY_TOP_LEVEL_PARAM, top.Id)
            set_bip(col, BuiltInParameter.FAMILY_TOP_LEVEL_OFFSET_PARAM, 0.0)
            set_bip(col, BuiltInParameter.FAMILY_BASE_LEVEL_OFFSET_PARAM, TOPE_ZAPATA)
            alt = round(UnitUtils.ConvertFromInternalUnits(top.Elevation, UnitTypeId.Meters) - PERALTE_VIGA, 2)
            set_val(col, "COL_Altura_Libre", alt)
            comunes(col, c_cod, NIVELES[0][0])
            cont["COL"] += 1

    for v in VIGAS:
        if v["cod"] in hechos:
            continue
        ln = Line.CreateBound(XYZ(m(v["x1"]), m(v["y1"]), 0), XYZ(m(v["x2"]), m(v["y2"]), 0))
        b = doc.Create.NewFamilyInstance(ln, sym["VC-TIPO"], n0, StructuralType.Beam)
        set_val(b, "VCI_Eje_Estructural", v["eje"])
        comunes(b, v["cod"], NIVELES[0][0])
        cont["VCI"] += 1

    nivel_cor = lv[CORREAS["nivel"]]
    for i, y in enumerate(CORREAS["y"], 1):
        cod = "COR-PHR-%02d" % i
        if cod in hechos:
            continue
        ln = Line.CreateBound(XYZ(m(CORREAS["x1"]), m(y), nivel_cor.Elevation),
                              XYZ(m(CORREAS["x2"]), m(y), nivel_cor.Elevation))
        r = doc.Create.NewFamilyInstance(ln, sym["PHR C 160x60x20"], nivel_cor, StructuralType.Beam)
        try:
            r.StructuralUsage = StructuralInstanceUsage.Purlin
        except Exception:
            pass
        set_val(r, "COR_Separacion", CORREAS["separacion"])
        comunes(r, cod, CORREAS["nivel"])
        cont["COR"] += 1

    set_val(doc.ProjectInformation, "PAC_Norma_Diseno", NORMA)
    t.Commit()
    log("  Elementos nuevos: " + str(cont))

    # 5) schedule
    log("5) Schedule de validacion")
    t = Transaction(doc, "P89 schedule")
    t.Start()
    vs = None
    for v in FilteredElementCollector(doc).OfClass(ViewSchedule):
        if v.Name == NOMBRE_SCHEDULE:
            vs = v
    if vs is None:
        vs = ViewSchedule.CreateSchedule(doc, ElementId.InvalidElementId)
        vs.Name = NOMBRE_SCHEDULE
        sd = vs.Definition
        disp = list(sd.GetSchedulableFields())
        ids = {}
        for sf in disp:
            if sf.FieldType == ScheduleFieldType.Count:
                ids["#"] = sf
                continue
            pid = sf.ParameterId
            if pid == ElementId(BuiltInParameter.ELEM_CATEGORY_PARAM):
                ids["Categoria"] = sf
            elif pid == ElementId(BuiltInParameter.ELEM_FAMILY_AND_TYPE_PARAM):
                ids["Familia y tipo"] = sf
            else:
                ids.setdefault(sf.GetName(doc), sf)
        agregados = {}
        for nombre in CAMPOS_SCHEDULE:
            if nombre in ids:
                agregados[nombre] = sd.AddField(ids[nombre])
            else:
                log("  AVISO: campo no disponible en el Schedule: " + nombre)
        if "Categoria" in agregados:
            sd.AddSortGroupField(ScheduleSortGroupField(agregados["Categoria"].FieldId))
        if "PAC_Codigo_Elemento" in agregados:
            sd.AddSortGroupField(ScheduleSortGroupField(agregados["PAC_Codigo_Elemento"].FieldId))
            try:
                sd.AddFilter(ScheduleFilter(agregados["PAC_Codigo_Elemento"].FieldId, ScheduleFilterType.HasValue))
            except Exception:
                pass
        sd.IsItemized = True
    t.Commit()
    app.SharedParametersFilename = anterior
    uidoc.ActiveView = vs
    log("LISTO. Revise el Schedule '" + NOMBRE_SCHEDULE + "' y la hoja QA_QC de la matriz.")


try:
    main()
except Exception as ex:
    import traceback
    log("ERROR: " + str(ex))
    print(traceback.format_exc())
    try:
        from Autodesk.Revit.UI import TaskDialog
        TaskDialog.Show("ACT03", "Error: " + str(ex))
    except Exception:
        pass
