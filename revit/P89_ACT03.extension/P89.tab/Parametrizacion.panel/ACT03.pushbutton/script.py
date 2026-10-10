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
  5. Agrega vigas aereas VG (N+3,05 y N+6,05), losa maciza de entrepiso y correas
     de cubierta; colores por objeto, unidades en metros y nombres en espanol.
  6. Crea el Schedule multicategoria P89_ACT03_VALIDACION y la vista 3D a color.

Uso: Dynamo (abrir ACT03_PARAMETRIZACION.dyn y Ejecutar), pyRevit o RevitPythonShell.
Revit 2023 o superior. Abrir un proyecto NUEVO con la plantilla ESTRUCTURAL metrica.
Se puede ejecutar varias veces: no duplica parametros, tipos ni elementos.
"""
__title__ = "ACT03\nParametrizar"
__doc__ = "Actividad 3 BIM Parametrizacion - crea parametros, modelo, formula y Schedule"

import os
import glob
import clr
clr.AddReference("RevitAPI")
clr.AddReference("RevitAPIUI")
clr.AddReference("System")
import System
from Autodesk.Revit.DB import (
    BuiltInCategory, BuiltInParameter, CategorySet, ElementId, ElementType, Family,
    FamilySymbol, FilteredElementCollector, GroupTypeId,
    InstanceBinding, Level, Line, Grid, Material, SaveAsOptions, ScheduleFieldType,
    ScheduleSortGroupField, ScheduleFilter, ScheduleFilterType, StorageType,
    Transaction, TypeBinding, UnitTypeId, UnitUtils, ViewSchedule, XYZ,
    SpecTypeId, FormatOptions, Color, View3D, ViewFamilyType, ViewFamily, DisplayStyle,
    ViewDetailLevel, ViewPlan, FloorType, Floor, CurveLoop, CompoundStructure,
    MaterialFunctionAssignment, FamilyInstance, EndCapCondition, TransactionStatus)
from System.Collections.Generic import List
from Autodesk.Revit.DB.Structure import StructuralType, StructuralInstanceUsage

try:
    uiapp = __revit__  # pyRevit / RevitPythonShell
    EN_DYNAMO = False
except NameError:
    # Dynamo (nodo Python Script)
    clr.AddReference("RevitServices")
    from RevitServices.Persistence import DocumentManager
    from RevitServices.Transactions import TransactionManager
    uiapp = DocumentManager.Instance.CurrentUIApplication
    TransactionManager.Instance.ForceCloseTransaction()
    EN_DYNAMO = True
app = uiapp.Application
uidoc = uiapp.ActiveUIDocument
doc = uidoc.Document


# ---- DATOS GENERADOS DESDE LA MATRIZ (no editar a mano salvo CORREAS) ----
NOMBRE_TXT = 'PARAM_ACT03_ParametrosCompartidos.txt'
TXT_COMPARTIDOS = "# This is a Revit shared parameter file.\r\n# Do not edit manually.\r\n*META\tVERSION\tMINVERSION\r\nMETA\t2\t1\r\n*GROUP\tID\tNAME\r\nGROUP\t1\tP89_PAC_Comunes\r\nGROUP\t2\tP89_Particulares\r\n*PARAM\tGUID\tNAME\tDATATYPE\tDATACATEGORY\tGROUP\tVISIBLE\tDESCRIPTION\tUSERMODIFIABLE\tHIDEWHENNOEXIST\r\nPARAM\t85472c8c-6490-518b-a29e-b885faa36d93\tPAC_Codigo_Elemento\tTEXT\t\t1\t1\tIdentificador unico del elemento colocado, nomenclatura OBJETO-TIPO-EJE (ej. ZAP-ZT1-1-B, COL-C30X30-6-D, VCI-VC-E-1/3, COR-PHR-01).\t1\t0\r\nPARAM\td86a8141-07c2-5163-b0c5-cc8c18d257b1\tPAC_Material_Estructural\tTEXT\t\t1\t1\tDescripcion del material constitutivo del elemento (concreto reforzado / acero laminado en frio).\t1\t0\r\nPARAM\t79d71a23-b7ca-56d3-bbf6-1a80172370d0\tPAC_Resistencia_MPa\tNUMBER\t\t1\t1\tResistencia de diseno del material: f'c del concreto o Fy del acero, en MPa.\t1\t0\r\nPARAM\tcdd84e08-b753-5092-962e-e539fcc67cef\tPAC_Nivel_Referencia\tTEXT\t\t1\t1\tNivel del proyecto al que se asocia el elemento (N+0,00 / N+3,05 / N+6,05).\t1\t0\r\nPARAM\tb6c0a61c-414b-57c4-b1b4-1013d12b3ee6\tPAC_Clasificacion_IFC_Uniclass\tTEXT\t\t1\t1\tClase IFC 4 y codigo Uniclass 2015 del objeto (ej. IfcFooting.PAD_FOOTING | EF_20_10).\t1\t0\r\nPARAM\t066e6011-2a6d-5560-b4db-2e0ed2444dd1\tPAC_Norma_Diseno\tTEXT\t\t1\t1\tNorma bajo la cual se diseno y se verifica el paciente.\t1\t0\r\nPARAM\t3fc88ade-62a9-5490-9b81-ab62f9bf5ae9\tZAP_Lado_B\tLENGTH\t\t2\t1\tLado en planta de la zapata cuadrada (B = L). Controla la geometria: Anchura = Longitud = ZAP_Lado_B.\t1\t0\r\nPARAM\t965537a6-536c-58a0-bd63-db59f71be075\tZAP_Espesor_h\tLENGTH\t\t2\t1\tAltura del dado de la zapata. Controla el espesor nativo de la familia.\t1\t0\r\nPARAM\t8d34a176-490a-5403-83f0-6fa71f5013a4\tZAP_Volumen_Concreto\tVOLUME\t\t2\t1\tVolumen de concreto de la zapata, calculado por formula.\t1\t0\r\nPARAM\td75f8334-2783-55cb-9ec8-23c7e389d540\tCOL_Seccion_bxh\tTEXT\t\t2\t1\tSeccion transversal de la columna en texto normalizado (ej. 0,30x0,30).\t1\t0\r\nPARAM\t40c3badd-65e0-5065-a86f-611a6c6a2664\tCOL_Altura_Libre\tLENGTH\t\t2\t1\tAltura libre: elevacion del nivel de remate menos el nivel de arranque (N+0,00) menos el peralte de la viga superior (0,30 m). 2,75 m o 5,75 m segun el eje.\t1\t0\r\nPARAM\t0a069ea7-3f17-5c14-a363-d5b9df101717\tCOL_Refuerzo_Longitudinal\tTEXT\t\t2\t1\tCantidad y diametro de barras longitudinales y estribos.\t1\t0\r\nPARAM\t4ec9bf06-1bab-5300-8692-932dc6dfeccf\tVCI_Seccion_bxh\tTEXT\t\t2\t1\tSeccion transversal de la viga de amarre (0,30x0,30).\t1\t0\r\nPARAM\t3d771281-4586-5fcc-891a-b316c46ab842\tVCI_Eje_Estructural\tTEXT\t\t2\t1\tEje de la reticula sobre el que se localiza el tramo de viga (ej. A, 1).\t1\t0\r\nPARAM\t2c83e82a-5e4d-5443-aa71-6c35dfbc77c3\tVCI_Refuerzo\tTEXT\t\t2\t1\tBarras longitudinales y separacion de estribos del tramo.\t1\t0\r\nPARAM\tb46100c4-1696-5b8f-bf7b-367e3aa6a906\tCOR_Designacion_Perfil\tTEXT\t\t2\t1\tDenominacion comercial del perfil laminado en frio.\t1\t0\r\nPARAM\t331132ab-4306-5dd4-b1e3-66230ec73d80\tCOR_Espesor_Lamina\tLENGTH\t\t2\t1\tCalibre / espesor de la lamina del perfil.\t1\t0\r\nPARAM\td1420baf-85ea-5cb2-b69f-0f498712487d\tCOR_Separacion\tLENGTH\t\t2\t1\tSeparacion centro a centro entre correas consecutivas.\t1\t0\r\n"
NOMBRE_SCHEDULE = 'P89_ACT03_VALIDACION'
NORMA = 'NSR-10 Titulos B y C'
NIVELES = [('N+0,00', 0.0), ('N+3,05', 3.05), ('N+6,05', 6.05)]
TOPE_ZAPATA = -0.65  # desplante 1,00 m - h 0,35 m (cara superior de la zapata)
PERALTE_VIGA = 0.30
ALTO_CORREA = 0.16  # la correa se apoya sobre la viga (su cara superior queda 0,16 m sobre el nivel)
NOMBRE_3D = '3D P89 ACT03 - Colores por objeto'
AUTOR = 'Luis David Arroyo Anaya - Maestria en Patologia de la Construccion, Facultad de Ingenieria Civil, Universidad Santo Tomas'
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
         'claves': ['Hormigón-Pilar rectangular',
                    'Hormigon-Pilar rectangular',
                    'Pilar de hormig',
                    'Pilar rectangular',
                    'Concrete-Rectangular-Column',
                    'Rectangular-Column',
                    'Columna rectangular',
                    'Columna de concreto',
                    'Hormigón-Columna',
                    'Pilar',
                    'Columna',
                    'Column'],
         'nombre': 'P89_COL_Columna_Concreto',
         'pistas': ['pilar', 'column']},
 'COR': {'ayuda': 'viga de hormigon rectangular (se usa como base de la correa 60x160 mm)',
         'claves': ['Hormigón-Viga rectangular',
                    'Hormigon-Viga rectangular',
                    'Viga de hormig',
                    'Viga rectangular',
                    'Concrete-Rectangular Beam',
                    'Rectangular Beam',
                    'Viga de concreto'],
         'nombre': 'P89_COR_Correa_PHR',
         'pistas': ['armaz', 'framing', 'viga']},
 'VCI': {'ayuda': 'viga de hormigon rectangular (M_Viga de hormigon-Rectangular / M_Concrete-Rectangular '
                  'Beam)',
         'claves': ['Hormigón-Viga rectangular',
                    'Hormigon-Viga rectangular',
                    'Viga de hormig',
                    'Viga rectangular',
                    'Concrete-Rectangular Beam',
                    'Rectangular Beam',
                    'Viga de concreto'],
         'nombre': 'P89_VCI_Viga_Cimentacion',
         'pistas': ['armaz', 'framing', 'viga']},
 'VIG': {'ayuda': 'viga de hormigon rectangular (M_Viga de hormigon-Rectangular / M_Concrete-Rectangular '
                  'Beam)',
         'claves': ['Hormigón-Viga rectangular',
                    'Hormigon-Viga rectangular',
                    'Viga de hormig',
                    'Viga rectangular',
                    'Concrete-Rectangular Beam',
                    'Rectangular Beam',
                    'Viga de concreto'],
         'nombre': 'P89_VIG_Viga_Aerea',
         'pistas': ['armaz', 'framing', 'viga']},
 'ZAP': {'ayuda': 'cimentacion aislada rectangular (M_Zapata-Rectangular / M_Footing-Rectangular)',
         'claves': ['Zapata-Rectangular', 'Footing-Rectangular', 'Zapata rectangular', 'Zapata', 'Footing'],
         'nombre': 'P89_ZAP_Zapata_Aislada',
         'pistas': ['cimentaci', 'foundation']}}
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
 ('COR', 'IfcMember.PURLIN | EF_30_10'),
 ('VIG', 'IfcBeam.BEAM | EF_20_10')]
TIPOS = [['ZAP', 'Z-T1', 1.3, 0.35, "Concreto reforzado f'c 21 MPa", 21, 'VERIFICAR en despiece P-892022'],
 ['ZAP', 'Z-T2', 1.6, 0.35, "Concreto reforzado f'c 21 MPa", 21, 'VERIFICAR en despiece P-892022'],
 ['ZAP', 'Z-T3', 1.7, 0.35, "Concreto reforzado f'c 21 MPa", 21, 'VERIFICAR en despiece P-892022'],
 ['COL', 'C-30x30', 0.3, 0.3, "Concreto reforzado f'c 21 MPa", 21, 'VERIFICAR en despiece P-892022'],
 ['COL', 'C-25x40', 0.25, 0.4, "Concreto reforzado f'c 21 MPa", 21, 'VERIFICAR en despiece P-892022'],
 ['COL', 'C-40x25', 0.4, 0.25, "Concreto reforzado f'c 21 MPa", 21, 'VERIFICAR en despiece P-892022'],
 ['VCI', 'VC-TIPO', 0.3, 0.3, "Concreto reforzado f'c 21 MPa", 21, 'VERIFICAR en despiece P-892022'],
 ['COR', 'PHR C 160x60x20', 0.06, 0.16, 'Acero laminado en frio PHR', 340, 'e = 1,50 mm'],
 ['VIG', 'VG-30x50', 0.3, 0.5, "Concreto reforzado f'c 21 MPa", 21, 'VERIFICAR en despiece P-892022'],
 ['VIG', 'VG-20x50', 0.2, 0.5, "Concreto reforzado f'c 21 MPa", 21, 'VERIFICAR en despiece P-892022'],
 ['VIG', 'VG-12x50', 0.12, 0.5, "Concreto reforzado f'c 21 MPa", 21, 'VERIFICAR en despiece P-892022']]
VIGAS_AEREAS = [{'cod': 'VIG-VG30X50-N305-01',
  'nivel': 'N+3,05',
  'tipo': 'VG-30x50',
  'x1': 7.5,
  'x2': 15.56,
  'y1': 0.0,
  'y2': 0.0},
 {'cod': 'VIG-VG30X50-N305-02',
  'nivel': 'N+3,05',
  'tipo': 'VG-30x50',
  'x1': 0.0,
  'x2': 5.51,
  'y1': 0.38,
  'y2': 0.38},
 {'cod': 'VIG-VG12X50-N305-03',
  'nivel': 'N+3,05',
  'tipo': 'VG-12x50',
  'x1': 0.0,
  'x2': 5.51,
  'y1': 0.589,
  'y2': 0.589},
 {'cod': 'VIG-VG30X50-N305-04',
  'nivel': 'N+3,05',
  'tipo': 'VG-30x50',
  'x1': 0.0,
  'x2': 2.0,
  'y1': 2.48,
  'y2': 2.48},
 {'cod': 'VIG-VG20X50-N305-05',
  'nivel': 'N+3,05',
  'tipo': 'VG-20x50',
  'x1': 6.162,
  'x2': 9.452,
  'y1': 2.48,
  'y2': 2.48},
 {'cod': 'VIG-VG30X50-N305-06',
  'nivel': 'N+3,05',
  'tipo': 'VG-30x50',
  'x1': 7.5,
  'x2': 15.56,
  'y1': 3.98,
  'y2': 3.98},
 {'cod': 'VIG-VG12X50-N305-07',
  'nivel': 'N+3,05',
  'tipo': 'VG-12x50',
  'x1': 0.152,
  'x2': 3.812,
  'y1': 5.87,
  'y2': 5.87},
 {'cod': 'VIG-VG30X50-N305-08',
  'nivel': 'N+3,05',
  'tipo': 'VG-30x50',
  'x1': 0.0,
  'x2': 15.56,
  'y1': 6.86,
  'y2': 6.86},
 {'cod': 'VIG-VG12X50-N305-09',
  'nivel': 'N+3,05',
  'tipo': 'VG-12x50',
  'x1': 7.652,
  'x2': 11.452,
  'y1': 8.3,
  'y2': 8.3},
 {'cod': 'VIG-VG20X50-N305-10',
  'nivel': 'N+3,05',
  'tipo': 'VG-20x50',
  'x1': -0.003,
  'x2': 3.812,
  'y1': 9.02,
  'y2': 9.02},
 {'cod': 'VIG-VG30X50-N305-11',
  'nivel': 'N+3,05',
  'tipo': 'VG-30x50',
  'x1': -0.003,
  'x2': 5.452,
  'y1': 11.18,
  'y2': 11.18},
 {'cod': 'VIG-VG30X50-N305-12',
  'nivel': 'N+3,05',
  'tipo': 'VG-30x50',
  'x1': 11.6,
  'x2': 15.56,
  'y1': 11.88,
  'y2': 11.88},
 {'cod': 'VIG-VG12X50-N305-13',
  'nivel': 'N+3,05',
  'tipo': 'VG-12x50',
  'x1': 2.062,
  'x2': 5.452,
  'y1': 12.2,
  'y2': 12.2},
 {'cod': 'VIG-VG12X50-N305-14',
  'nivel': 'N+3,05',
  'tipo': 'VG-12x50',
  'x1': -0.063,
  'x2': -0.063,
  'y1': 6.86,
  'y2': 11.03},
 {'cod': 'VIG-VG30X50-N305-15',
  'nivel': 'N+3,05',
  'tipo': 'VG-30x50',
  'x1': 0.002,
  'x2': 0.002,
  'y1': 0.38,
  'y2': 6.86},
 {'cod': 'VIG-VG30X50-N305-16',
  'nivel': 'N+3,05',
  'tipo': 'VG-30x50',
  'x1': 2.002,
  'x2': 2.002,
  'y1': 0.53,
  'y2': 2.48},
 {'cod': 'VIG-VG12X50-N305-17',
  'nivel': 'N+3,05',
  'tipo': 'VG-12x50',
  'x1': 2.002,
  'x2': 2.002,
  'y1': 5.93,
  'y2': 12.14},
 {'cod': 'VIG-VG30X50-N305-18',
  'nivel': 'N+3,05',
  'tipo': 'VG-30x50',
  'x1': 3.072,
  'x2': 3.072,
  'y1': 6.86,
  'y2': 11.18},
 {'cod': 'VIG-VG12X50-N305-19',
  'nivel': 'N+3,05',
  'tipo': 'VG-12x50',
  'x1': 3.872,
  'x2': 3.872,
  'y1': 5.93,
  'y2': 11.03},
 {'cod': 'VIG-VG12X50-N305-20',
  'nivel': 'N+3,05',
  'tipo': 'VG-12x50',
  'x1': 5.512,
  'x2': 5.512,
  'y1': 11.33,
  'y2': 12.14},
 {'cod': 'VIG-VG12X50-N305-21',
  'nivel': 'N+3,05',
  'tipo': 'VG-12x50',
  'x1': 6.102,
  'x2': 6.102,
  'y1': 0.432,
  'y2': 2.38},
 {'cod': 'VIG-VG12X50-N305-22',
  'nivel': 'N+3,05',
  'tipo': 'VG-12x50',
  'x1': 6.102,
  'x2': 6.102,
  'y1': 7.01,
  'y2': 10.508},
 {'cod': 'VIG-VG30X50-N305-23',
  'nivel': 'N+3,05',
  'tipo': 'VG-30x50',
  'x1': 7.502,
  'x2': 7.502,
  'y1': 0.0,
  'y2': 6.86},
 {'cod': 'VIG-VG20X50-N305-24',
  'nivel': 'N+3,05',
  'tipo': 'VG-20x50',
  'x1': 9.552,
  'x2': 9.552,
  'y1': 0.15,
  'y2': 6.71},
 {'cod': 'VIG-VG30X50-N305-25',
  'nivel': 'N+3,05',
  'tipo': 'VG-30x50',
  'x1': 11.602,
  'x2': 11.602,
  'y1': 0.0,
  'y2': 11.88},
 {'cod': 'VIG-VG12X50-N305-26',
  'nivel': 'N+3,05',
  'tipo': 'VG-12x50',
  'x1': 14.222,
  'x2': 14.222,
  'y1': 4.13,
  'y2': 6.71},
 {'cod': 'VIG-VG30X50-N305-27',
  'nivel': 'N+3,05',
  'tipo': 'VG-30x50',
  'x1': 15.562,
  'x2': 15.562,
  'y1': 0.0,
  'y2': 11.88},
 {'cod': 'VIG-VG12X50-N605-01',
  'nivel': 'N+6,05',
  'tipo': 'VG-12x50',
  'x1': 7.652,
  'x2': 11.452,
  'y1': 0.79,
  'y2': 0.79},
 {'cod': 'VIG-VG30X50-N605-02',
  'nivel': 'N+6,05',
  'tipo': 'VG-30x50',
  'x1': 7.5,
  'x2': 11.6,
  'y1': 3.98,
  'y2': 3.98},
 {'cod': 'VIG-VG12X50-N605-03',
  'nivel': 'N+6,05',
  'tipo': 'VG-12x50',
  'x1': 0.152,
  'x2': 3.812,
  'y1': 5.87,
  'y2': 5.87},
 {'cod': 'VIG-VG30X50-N605-04',
  'nivel': 'N+6,05',
  'tipo': 'VG-30x50',
  'x1': 0.0,
  'x2': 3.812,
  'y1': 6.86,
  'y2': 6.86},
 {'cod': 'VIG-VG30X50-N605-05',
  'nivel': 'N+6,05',
  'tipo': 'VG-30x50',
  'x1': 7.5,
  'x2': 11.6,
  'y1': 6.86,
  'y2': 6.86},
 {'cod': 'VIG-VG12X50-N605-06',
  'nivel': 'N+6,05',
  'tipo': 'VG-12x50',
  'x1': 7.652,
  'x2': 11.452,
  'y1': 8.3,
  'y2': 8.3},
 {'cod': 'VIG-VG20X50-N605-07',
  'nivel': 'N+6,05',
  'tipo': 'VG-20x50',
  'x1': -0.003,
  'x2': 3.812,
  'y1': 9.02,
  'y2': 9.02},
 {'cod': 'VIG-VG30X50-N605-08',
  'nivel': 'N+6,05',
  'tipo': 'VG-30x50',
  'x1': -0.003,
  'x2': 5.452,
  'y1': 11.18,
  'y2': 11.18},
 {'cod': 'VIG-VG12X50-N605-09',
  'nivel': 'N+6,05',
  'tipo': 'VG-12x50',
  'x1': 2.062,
  'x2': 5.452,
  'y1': 12.2,
  'y2': 12.2},
 {'cod': 'VIG-VG12X50-N605-10',
  'nivel': 'N+6,05',
  'tipo': 'VG-12x50',
  'x1': -0.063,
  'x2': -0.063,
  'y1': 6.86,
  'y2': 11.03},
 {'cod': 'VIG-VG30X50-N605-11',
  'nivel': 'N+6,05',
  'tipo': 'VG-30x50',
  'x1': 0.002,
  'x2': 0.002,
  'y1': 5.93,
  'y2': 6.86},
 {'cod': 'VIG-VG12X50-N605-12',
  'nivel': 'N+6,05',
  'tipo': 'VG-12x50',
  'x1': 2.002,
  'x2': 2.002,
  'y1': 5.93,
  'y2': 12.14},
 {'cod': 'VIG-VG30X50-N605-13',
  'nivel': 'N+6,05',
  'tipo': 'VG-30x50',
  'x1': 3.072,
  'x2': 3.072,
  'y1': 5.93,
  'y2': 12.14},
 {'cod': 'VIG-VG12X50-N605-14',
  'nivel': 'N+6,05',
  'tipo': 'VG-12x50',
  'x1': 3.872,
  'x2': 3.872,
  'y1': 5.93,
  'y2': 11.03},
 {'cod': 'VIG-VG12X50-N605-15',
  'nivel': 'N+6,05',
  'tipo': 'VG-12x50',
  'x1': 5.512,
  'x2': 5.512,
  'y1': 11.33,
  'y2': 12.14},
 {'cod': 'VIG-VG30X50-N605-16',
  'nivel': 'N+6,05',
  'tipo': 'VG-30x50',
  'x1': 7.502,
  'x2': 7.502,
  'y1': 0.85,
  'y2': 8.24},
 {'cod': 'VIG-VG20X50-N605-17',
  'nivel': 'N+6,05',
  'tipo': 'VG-20x50',
  'x1': 9.552,
  'x2': 9.552,
  'y1': 0.85,
  'y2': 8.24},
 {'cod': 'VIG-VG30X50-N605-18',
  'nivel': 'N+6,05',
  'tipo': 'VG-30x50',
  'x1': 11.602,
  'x2': 11.602,
  'y1': 0.85,
  'y2': 8.24}]
LOSA = {'clasificacion': 'IfcSlab.FLOOR | EF_30_20',
 'espesor': 0.15,
 'poligonos': [[(-0.12, 5.81),
                (3.93, 5.81),
                (3.93, 11.03),
                (5.57, 11.03),
                (5.57, 12.26),
                (1.94, 12.26),
                (1.94, 11.33),
                (-0.12, 11.33)],
               [(7.35, 0.73), (11.75, 0.73), (11.75, 8.36), (7.35, 8.36)]],
 'tipo': 'Losa maciza P89 e=0,15 m'}
MATERIALES = {'COL': ('P89 Concreto - Columnas', (31, 119, 180), 0),
 'COR': ('P89 Acero - Correas PHR', (214, 39, 40), 0),
 'LOS': ('P89 Concreto - Losa de entrepiso', (240, 200, 80), 40),
 'VCI': ('P89 Concreto - Vigas de cimentacion', (44, 160, 44), 0),
 'VIG': ('P89 Concreto - Vigas aereas', (255, 127, 14), 0),
 'ZAP': ('P89 Concreto - Zapatas', (140, 140, 140), 0)}
PROYECTO = [('Name', 'Casa Campestre - Vivienda unifamiliar Cañaveral'),
 ('Number', 'P-892022'),
 ('Address', 'Sector Cañaveral, Turbaco (Bolívar)'),
 ('Author', 'Luis David Arroyo Anaya'),
 ('OrganizationName', 'Universidad Santo Tomás - Facultad de Ingeniería Civil'),
 ('OrganizationDescription', 'Maestría en Patología de la Construcción'),
 ('BuildingName', 'Actividad 3 - BIM Parametrizacion')]
DESCRIPCIONES = {'COL': 'Columna de concreto reforzado',
 'COR': 'Correa de cubierta PHR C 160x60x20',
 'VCI': 'Viga de cimentacion (amarre entre zapatas)',
 'VIG': 'Viga aerea de concreto reforzado',
 'ZAP': 'Zapata aislada de concreto reforzado'}
ENCABEZADOS = {'#': 'Cantidad',
 'COL_Altura_Libre': 'COL Altura libre (m)',
 'COL_Refuerzo_Longitudinal': 'COL Refuerzo',
 'COL_Seccion_bxh': 'COL Sección b x h',
 'COR_Designacion_Perfil': 'COR Perfil',
 'COR_Espesor_Lamina': 'COR Espesor lámina',
 'COR_Separacion': 'COR Separación (m)',
 'Categoria': 'Categoría',
 'Familia y tipo': 'Familia y tipo',
 'PAC_Clasificacion_IFC_Uniclass': 'PAC Clasificación IFC | Uniclass',
 'PAC_Codigo_Elemento': 'PAC Código',
 'PAC_Material_Estructural': 'PAC Material',
 'PAC_Nivel_Referencia': 'PAC Nivel',
 'PAC_Resistencia_MPa': 'PAC Resistencia (MPa)',
 'VCI_Eje_Estructural': 'VCI Eje',
 'VCI_Refuerzo': 'VCI Refuerzo',
 'VCI_Seccion_bxh': 'VCI Sección b x h',
 'ZAP_Espesor_h': 'ZAP Espesor h (m)',
 'ZAP_Lado_B': 'ZAP Lado B (m)',
 'ZAP_Volumen_Concreto': 'ZAP Volumen (m³) = B·B·h'}
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
CORREAS = [{'nivel': 'N+3,05',
  'separacion': 1.0,
  'x1': 11.6,
  'x2': 15.56,
  'y': [0.5, 1.5, 2.5, 3.5, 4.5, 5.5, 6.5, 7.5, 8.5, 9.5, 10.5, 11.5]},
 {'nivel': 'N+6,05', 'separacion': 1.0, 'x1': 7.5, 'x2': 11.6, 'y': [1.3, 2.3, 3.3, 4.3, 5.3, 6.3, 7.3]},
 {'nivel': 'N+6,05', 'separacion': 1.0, 'x1': 0.0, 'x2': 3.07, 'y': [6.4, 7.4, 8.4, 9.4, 10.4]}]
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
    "VIG": BuiltInCategory.OST_StructuralFraming,
}


# ---------------------------------------------------------------- utilidades
def ruta_txt():
    """Escribe el archivo de parametros compartidos (embebido) en la carpeta temporal."""
    ruta = os.path.join(System.IO.Path.GetTempPath(), NOMBRE_TXT)
    System.IO.File.WriteAllText(ruta, TXT_COMPARTIDOS, System.Text.Encoding.Unicode)
    return ruta


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


NO_CONCRETO = ["acero", "steel", "wide flange", "madera", "wood", "timber", "hss", "tubo", "metal", "w-", "ipe", "hea"]


def no_concreto(nombre):
    n = nombre.lower()
    return any(p in n for p in NO_CONCRETO)


def buscar_familia(bic, claves, excluir=()):
    """Familia ya cargada cuyo nombre contenga alguna clave (por orden)."""
    fams = {}
    for s in simbolos(bic):
        fams[s.Family.Name] = s.Family
    for c in claves:
        for n, f in sorted(fams.items()):
            if c.lower() in n.lower() and not n.startswith("P89_") and n not in excluir and not no_concreto(n):
                return f
    return None


_RFA = []


def archivos_biblioteca():
    """Lista (una sola vez) todos los .rfa de las bibliotecas de Revit instaladas."""
    if not _RFA:
        raices = sorted(glob.glob(r"C:\ProgramData\Autodesk\RVT *\Libraries"), reverse=True)
        for raiz in raices:
            for dp, dn, fn in os.walk(raiz):
                for f in fn:
                    if f.lower().endswith(".rfa"):
                        _RFA.append(os.path.join(dp, f))
    return _RFA


def cargar_de_biblioteca(bic, claves, pistas=()):
    """Busca el .rfa en la biblioteca, lo carga y comprueba que sea de la categoria pedida."""
    cands = []
    for ruta in archivos_biblioteca():
        nombre = os.path.basename(ruta).lower()
        if no_concreto(nombre):
            continue
        for i, c in enumerate(claves):
            if c.lower() in nombre:
                en_carpeta = any(p in ruta.lower() for p in pistas)
                cands.append((0 if en_carpeta else 1, i, len(nombre), ruta))
                break
    cands.sort()
    for _a, _b, _c, ruta in cands[:20]:
        t = Transaction(doc, "P89 cargar familia")
        t.Start()
        try:
            doc.LoadFamily(ruta)
            t.Commit()
        except Exception:
            t.RollBack()
            continue
        fam = familia_por_nombre(bic, os.path.splitext(os.path.basename(ruta))[0])
        if fam is not None:
            log("  Familia cargada de biblioteca: " + os.path.basename(ruta))
            return fam
    return None


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
    if True:
        ruta = os.path.join(System.IO.Path.GetTempPath(), nuevo_nombre + ".rfa")
        op = SaveAsOptions()
        op.OverwriteExistingFile = True
        fdoc.SaveAs(ruta, op)
    fam = fdoc.LoadFamily(doc)
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
    for bic in list(set(BIC.values())) + [BuiltInCategory.OST_Floors]:
        for e in FilteredElementCollector(doc).OfCategory(bic).WhereElementIsNotElementType():
            p = e.LookupParameter("PAC_Codigo_Elemento")
            if p is not None and p.AsString():
                cods.add(p.AsString())
    return cods


# ------------------------------------------------------------------- proceso
TRANS = []


def trans(nombre):
    t = Transaction(doc, nombre)
    t.Start()
    TRANS.append(t)
    return t


def unidades_metricas():
    u = doc.GetUnits()
    for spec, unit, acc in ((SpecTypeId.Length, UnitTypeId.Meters, 0.01),
                            (SpecTypeId.Area, UnitTypeId.SquareMeters, 0.01),
                            (SpecTypeId.Volume, UnitTypeId.CubicMeters, 0.001)):
        fo = FormatOptions(unit)
        fo.Accuracy = acc
        u.SetFormatOptions(spec, fo)
    doc.SetUnits(u)


def material_color(codigo):
    nombre, rgb, transp = MATERIALES[codigo]
    mid = None
    for mt in FilteredElementCollector(doc).OfClass(Material):
        if mt.Name == nombre:
            mid = mt.Id
    if mid is None:
        mid = Material.Create(doc, nombre)
    mt = doc.GetElement(mid)
    mt.Color = Color(System.Byte(rgb[0]), System.Byte(rgb[1]), System.Byte(rgb[2]))
    mt.Transparency = transp
    try:
        mt.UseRenderAppearanceForShading = False
    except Exception:
        pass
    try:
        mt.MaterialClass = "Acero" if codigo == "COR" else "Concreto"
    except Exception:
        pass
    return mid


def poner_material(s, mid):
    p = s.get_Parameter(BuiltInParameter.STRUCTURAL_MATERIAL_PARAM)
    if p is not None and not p.IsReadOnly:
        p.Set(mid)
        return
    p = lookup(s, ["Material estructural", "Structural Material", "Material"])
    if p is not None and not p.IsReadOnly and p.StorageType == StorageType.ElementId:
        p.Set(mid)


def linea(x1, y1, x2, y2, z=0.0):
    return Line.CreateBound(XYZ(m(x1), m(y1), z), XYZ(m(x2), m(y2), z))


def main():
    if doc.IsFamilyDocument:
        raise Exception("Abra un PROYECTO (.rvt), no una familia.")
    path = ruta_txt()
    log("1) Parametros compartidos: " + path)
    defs, anterior = leer_definiciones(path)

    # 2) parametros comunes -> proyecto + unidades + informacion de proyecto
    log("2) Parametros comunes, unidades en metros e informacion de proyecto")
    t = trans("P89 parametros comunes")
    unidades_metricas()
    cats = CategorySet()
    for bic in (BuiltInCategory.OST_StructuralFoundation, BuiltInCategory.OST_StructuralColumns,
                BuiltInCategory.OST_StructuralFraming, BuiltInCategory.OST_Floors):
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
    pi = doc.ProjectInformation
    for attr, val in PROYECTO:
        try:
            setattr(pi, attr, val)
        except Exception:
            pass
    set_val(pi, "PAC_Norma_Diseno", NORMA)
    t.Commit()

    # 3) familias del paciente
    log("3) Familias")
    fams = {}
    for codigo in ("ZAP", "COL", "VCI", "COR", "VIG"):
        nombre = FAMILIAS[codigo]["nombre"]
        bic = BIC[codigo]
        ya = familia_por_nombre(bic, nombre)
        if ya is not None:
            log(" " + codigo + ": " + nombre + " ya existe, se reutiliza")
            fams[codigo] = ya
            continue
        base = buscar_familia(bic, FAMILIAS[codigo]["claves"])
        if base is None:
            base = cargar_de_biblioteca(bic, FAMILIAS[codigo]["claves"], FAMILIAS[codigo]["pistas"])
        if base is None:
            raise Exception("No se encontro una familia para " + codigo + ". Cargue una familia de "
                            + FAMILIAS[codigo]["ayuda"] + " (Insertar > Cargar familia) y vuelva a ejecutar.")
        log(" " + codigo + ": base '" + base.Name + "' -> " + nombre)
        fams[codigo] = preparar_familia(base, nombre, codigo, defs)

    # 4) modelo
    log("4) Niveles, ejes, materiales, tipos y elementos")
    t = trans("P89 modelo")
    lv = {}
    for n, e in NIVELES:
        lv[n] = nivel(n, e)
    for v in FilteredElementCollector(doc).OfClass(ViewPlan):
        try:
            if v.IsTemplate or v.GenLevel is None or not v.GenLevel.Name.startswith("N+"):
                continue
            pref = "Planta estructural " if "Engineering" in str(v.ViewType) else "Planta "
            if v.Name != pref + v.GenLevel.Name:
                v.Name = pref + v.GenLevel.Name
        except Exception:
            pass
    grids = set(g.Name for g in FilteredElementCollector(doc).OfClass(Grid))
    for n, x in EJES_X:
        if n not in grids:
            g = Grid.Create(doc, Line.CreateBound(XYZ(m(x), m(-1.8), 0), XYZ(m(x), m(13.8), 0)))
            g.Name = n
    for n, y in EJES_Y:
        if n not in grids:
            g = Grid.Create(doc, Line.CreateBound(XYZ(m(-1.8), m(y), 0), XYZ(m(17.4), m(y), 0)))
            g.Name = n

    mats = dict((k, material_color(k)) for k in MATERIALES)
    clas = dict((o, v) for o, v in CLASIFICACION)
    sym = {}
    for cod, nom, b, h, mat, fc, ref in TIPOS:
        s = tipo(fams[cod], nom)
        if not s.IsActive:
            s.Activate()
        set_val(s, "PAC_Material_Estructural", mat)
        set_val(s, "PAC_Resistencia_MPa", fc, unidad=None)
        set_val(s, "PAC_Clasificacion_IFC_Uniclass", clas[cod])
        poner_material(s, mats[cod])
        try:
            s.get_Parameter(BuiltInParameter.ALL_MODEL_DESCRIPTION).Set(DESCRIPCIONES.get(cod, ""))
        except Exception:
            pass
        sec = ("%.2fx%.2f" % (b, h)).replace(".", ",")
        if cod == "ZAP":
            set_val(s, "ZAP_Lado_B", b)
            set_val(s, "ZAP_Espesor_h", h)
        else:
            set_val(s, ["b", "Anchura", "Width"], b)
            set_val(s, ["h", "Altura", "Profundidad", "Height", "Depth"], h)
        if cod == "COL":
            set_val(s, "COL_Seccion_bxh", sec)
            set_val(s, "COL_Refuerzo_Longitudinal", ref)
        elif cod == "VCI":
            set_val(s, "VCI_Seccion_bxh", sec)
            set_val(s, "VCI_Refuerzo", ref)
        elif cod == "COR":
            set_val(s, "COR_Designacion_Perfil", nom)
            set_val(s, "COR_Espesor_Lamina", 1.50, unidad="mm")
        sym[nom] = s

    # tipo de losa
    ft = None
    for x in FilteredElementCollector(doc).OfClass(FloorType):
        if x.Name == LOSA["tipo"]:
            ft = x
    if ft is None:
        base_ft = [x for x in FilteredElementCollector(doc).OfClass(FloorType)
                   if x.GetCompoundStructure() is not None and not x.IsFoundationSlab][0]
        ft = base_ft.Duplicate(LOSA["tipo"])
    try:
        cs = CompoundStructure.CreateSingleLayerCompoundStructure(
            MaterialFunctionAssignment.Structure, m(LOSA["espesor"]), mats["LOS"])
        try:
            cs.EndCap = EndCapCondition.NoEndCap
        except Exception:
            pass
        ft.SetCompoundStructure(cs)
    except Exception:
        try:
            # alternativa: ajustar la capa estructural del tipo existente
            cs = ft.GetCompoundStructure()
            i = cs.StructuralMaterialIndex if cs.StructuralMaterialIndex >= 0 else 0
            cs.SetLayerWidth(i, m(LOSA["espesor"]))
            cs.SetMaterialId(i, mats["LOS"])
            ft.SetCompoundStructure(cs)
            log("  Losa: se ajusto la capa estructural del tipo base")
        except Exception as e:
            log("  AVISO losa: no se pudo cambiar la estructura del tipo (" + str(e) + "); se usa la del tipo base")
    set_val(ft, "PAC_Material_Estructural", "Concreto reforzado f'c 21 MPa")
    set_val(ft, "PAC_Resistencia_MPa", 21, unidad=None)
    set_val(ft, "PAC_Clasificacion_IFC_Uniclass", LOSA["clasificacion"])
    doc.Regenerate()

    # la correa de la version anterior (perfil de biblioteca) se reemplaza por la nueva
    vieja = familia_por_nombre(BuiltInCategory.OST_StructuralFraming, "P89_COR_Perfil_C_PHR")
    if vieja is not None:
        doc.Delete(vieja.Id)
        log("  Se elimino la correa anterior (P89_COR_Perfil_C_PHR); se crean de nuevo con P89_COR_Correa_PHR")
    doc.Regenerate()

    hechos = codigos_existentes()
    n0, n3, n6 = lv[NIVELES[0][0]], lv[NIVELES[1][0]], lv[NIVELES[2][0]]
    cont = {"ZAP": 0, "COL": 0, "VCI": 0, "VIG": 0, "LOS": 0, "COR": 0}

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
        b = doc.Create.NewFamilyInstance(linea(v["x1"], v["y1"], v["x2"], v["y2"]), sym["VC-TIPO"], n0, StructuralType.Beam)
        set_val(b, "VCI_Eje_Estructural", v["eje"])
        comunes(b, v["cod"], NIVELES[0][0])
        cont["VCI"] += 1

    # vigas aereas VG
    for v in VIGAS_AEREAS:
        if v["cod"] in hechos:
            continue
        nv = lv[v["nivel"]]
        b = doc.Create.NewFamilyInstance(linea(v["x1"], v["y1"], v["x2"], v["y2"], nv.Elevation),
                                         sym[v["tipo"]], nv, StructuralType.Beam)
        comunes(b, v["cod"], v["nivel"])
        cont["VIG"] += 1

    # losa maciza de entrepiso
    for i, poly in enumerate(LOSA["poligonos"], 1):
        cod = "LOS-E%02d-N305-%02d" % (int(round(LOSA["espesor"] * 100)), i)
        if cod in hechos:
            continue
        cl = CurveLoop()
        for (x1, y1), (x2, y2) in zip(poly, poly[1:] + poly[:1]):
            cl.Append(linea(x1, y1, x2, y2, n3.Elevation))
        loops = List[CurveLoop]()
        loops.Add(cl)
        try:
            f = Floor.Create(doc, loops, ft.Id, n3.Id, True, None, 0.0)
            comunes(f, cod, NIVELES[1][0])
            cont["LOS"] += 1
        except Exception as e:
            log("  AVISO losa " + cod + ": " + str(e))

    s_cor = sym["PHR C 160x60x20"]
    k = 0
    for grp in CORREAS:
        nv = lv[grp["nivel"]]
        z = nv.Elevation + m(ALTO_CORREA)
        for y in grp["y"]:
            k += 1
            cod = "COR-PHR-%02d" % k
            if cod in hechos:
                continue
            r = doc.Create.NewFamilyInstance(linea(grp["x1"], y, grp["x2"], y, z), s_cor, nv, StructuralType.Beam)
            try:
                r.StructuralUsage = StructuralInstanceUsage.Purlin
            except Exception:
                pass
            set_val(r, "COR_Separacion", grp["separacion"])
            comunes(r, cod, grp["nivel"])
            cont["COR"] += 1
    t.Commit()
    log("  Elementos nuevos: " + str(cont))

    # 5) limpieza: tipos y familias en ingles sin uso
    t = trans("P89 limpieza")
    usados = set()
    for e in FilteredElementCollector(doc).OfClass(FamilyInstance):
        usados.add(e.Symbol.Id.ToString())
        usados.add(e.Symbol.Family.Id.ToString())
    nuestros = set(tt[1] for tt in TIPOS)
    borrados = 0
    for bic in (BuiltInCategory.OST_StructuralFoundation, BuiltInCategory.OST_StructuralColumns,
                BuiltInCategory.OST_StructuralFraming):
        fams_cat = {}
        for s in simbolos(bic):
            fams_cat[s.Family.Id.ToString()] = s.Family
        for fid, fam in fams_cat.items():
            if fam.Name.startswith("P89_"):
                for sid in list(fam.GetFamilySymbolIds()):
                    el = doc.GetElement(sid)
                    if el.Name not in nuestros and sid.ToString() not in usados:
                        try:
                            doc.Delete(sid)
                            borrados += 1
                        except Exception:
                            pass
            elif fid not in usados:
                try:
                    doc.Delete(fam.Id)
                    borrados += 1
                except Exception:
                    pass
    t.Commit()
    log("  Tipos/familias sin uso eliminados: " + str(borrados))

    # 6) schedule y vista 3D
    log("6) Schedule y vista 3D")
    t = trans("P89 schedule y 3D")
    vs = None
    for v in FilteredElementCollector(doc).OfClass(ViewSchedule):
        if v.Name == NOMBRE_SCHEDULE:
            vs = v
    if vs is None:
        vs = ViewSchedule.CreateSchedule(doc, ElementId.InvalidElementId)
        vs.Name = NOMBRE_SCHEDULE
    sd = vs.Definition
    try:
        sd.ClearSortGroupFields()
        sd.ClearFilters()
    except Exception:
        pass
    while sd.GetFieldCount() > 0:
        sd.RemoveField(0)
    ids = {}
    for sf in sd.GetSchedulableFields():
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
            fld = sd.AddField(ids[nombre])
            fld.ColumnHeading = ENCABEZADOS.get(nombre, nombre)
            agregados[nombre] = fld
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

    v3 = None
    for v in FilteredElementCollector(doc).OfClass(View3D):
        if v.Name == NOMBRE_3D:
            v3 = v
    if v3 is None:
        vft = [x for x in FilteredElementCollector(doc).OfClass(ViewFamilyType)
               if x.ViewFamily == ViewFamily.ThreeDimensional][0]
        v3 = View3D.CreateIsometric(doc, vft.Id)
        v3.Name = NOMBRE_3D
    v3.DisplayStyle = DisplayStyle.ShadingWithEdges
    v3.DetailLevel = ViewDetailLevel.Fine
    for bic in (BuiltInCategory.OST_Grids, BuiltInCategory.OST_Levels):
        try:
            v3.SetCategoryHidden(ElementId(bic), True)
        except Exception:
            pass
    t.Commit()
    app.SharedParametersFilename = anterior
    try:
        uidoc.ActiveView = v3
    except Exception:
        log("  (Abra la vista '" + NOMBRE_3D + "' desde el Navegador de proyectos)")
    log("LISTO. Vista 3D: '" + NOMBRE_3D + "'. Schedule: '" + NOMBRE_SCHEDULE + "'.")


try:
    main()
except Exception as ex:
    import traceback
    for _t in TRANS:
        try:
            if _t.GetStatus() == TransactionStatus.Started:
                _t.RollBack()
        except Exception:
            pass
    log("ERROR: " + str(ex))
    LOG.append(traceback.format_exc())
    try:
        from Autodesk.Revit.UI import TaskDialog
        TaskDialog.Show("ACT03", "Error: " + str(ex))
    except Exception:
        pass

OUT = "\n".join(LOG)
