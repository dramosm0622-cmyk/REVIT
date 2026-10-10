# Actividad 3 – BIM Parametrización · Casa Campestre P-892022 (Turbaco)

Paciente: la misma vivienda de la Actividad 1. Objetos: **zapata → columna → viga de cimentación → correa PHR**.

| Producto de la guía | Archivo en este repositorio | Estado |
|---|---|---|
| 1. Matriz final (.xlsx, sin macros) | `PARAM_2026-2_ACT03_GRUPO##_MATRIZ_FINAL.xlsx` | Listo. Faltan los datos en amarillo. |
| 2. Modelo BIM (.rvt / .rfa) | `revit/P89_ACT03.extension/…/ACT03.pushbutton/script.py` (genera el modelo) | Se ejecuta en **su** Revit (ver abajo) |
| 3. Sustentación (video ≤ 5 min) | Guion en `GUION_VIDEO.md` | Lo graba el grupo |

> **Por qué hay un script y no un .rvt:** Revit solo funciona en Windows con licencia de Autodesk. No puede abrirse en la nube donde se preparó esto (Linux).
> Por eso todo el trabajo de Revit quedó en un script que hace la actividad completa con **un clic** en el Revit de ustedes.
> El script **no se ha probado dentro de Revit** porque aquí no hay Revit. Si sale un aviso o un error en la ventana de salida, cópienlo y se corrige.

## Qué hace el script (en un proyecto nuevo)

1. Carga `PARAM_ACT03_ParametrosCompartidos.txt`: 18 parámetros compartidos, con los mismos nombres y GUID de la matriz.
2. **5 parámetros comunes** `PAC_*` (Shared + Project), vinculados a Cimentación estructural, Pilares estructurales y Armazón estructural:
   `PAC_Codigo_Elemento` (I), `PAC_Material_Estructural` (T), `PAC_Resistencia_MPa` (T), `PAC_Nivel_Referencia` (I), `PAC_Clasificacion_IFC_Uniclass` (T).
   `PAC_Norma_Diseno` va una sola vez en *Información de proyecto*.
3. **4 familias propias**, cada una con **3 parámetros particulares** compartidos:
   - `P89_ZAP_Zapata_Aislada`: `ZAP_Lado_B`, `ZAP_Espesor_h` y **`ZAP_Volumen_Concreto = ZAP_Lado_B * ZAP_Lado_B * ZAP_Espesor_h`** (la fórmula). Además Anchura = Longitud = `ZAP_Lado_B` y Espesor = `ZAP_Espesor_h`, de modo que la geometría también es paramétrica.
   - `P89_COL_Columna_Concreto`: `COL_Seccion_bxh`, `COL_Altura_Libre`, `COL_Refuerzo_Longitudinal`
   - `P89_VCI_Viga_Cimentacion`: `VCI_Seccion_bxh`, `VCI_Eje_Estructural`, `VCI_Refuerzo`
   - `P89_COR_Perfil_C_PHR`: `COR_Designacion_Perfil`, `COR_Espesor_Lamina`, `COR_Separacion`
4. Arma el modelo con la **Planta de Cimentaciones del DWG P89-2022**:
   - niveles N+0,00 / N+3,05 / N+6,05 y ejes 1–8 / A–G;
   - 19 zapatas (12 Z-T1, 4 Z-T2, 3 Z-T3) y 19 columnas (8 llegan a N+6,05);
   - 23 tramos de VC 0,30×0,30;
   - 12 correas PHR entre los ejes 7 y 8.
   La imagen de control es `revit/control_planta_modelo.png`.
5. Crea y abre el Schedule multicategoría **`P89_ACT03_VALIDACION`**. Muestra categoría, familia y tipo, los 5 comunes, los particulares y el conteo.

Se puede ejecutar varias veces: no duplica parámetros, tipos ni elementos.

## Cómo ejecutarlo (10 minutos)

1. Instale **pyRevit** (gratis: https://github.com/pyrevitlabs/pyRevit/releases). Necesita Revit 2023 o superior.
2. Descargue este repositorio y copie la carpeta `revit/P89_ACT03.extension` en `%APPDATA%\pyRevit\Extensions\`.
   También puede dejarla donde está y agregar la carpeta `revit` en *pyRevit → Settings → Custom Extension Directories*. Luego presione **Reload**.
3. En Revit: **Nuevo → Proyecto → Plantilla estructural (métrica)**. Use la plantilla en español o en inglés; el script reconoce las dos.
4. Vaya a la pestaña **P89 → Parametrizacion → ACT03** y haga clic.
5. Se abre el Schedule. Revise la ventana de salida de pyRevit: lista lo que se creó y los avisos.
6. Guarde como `PARAM_2026-2_ACT03_GRUPO##_MODELO.rvt`.
7. Para las entregas .rfa por integrante, haga clic derecho sobre la familia en el Navegador de proyectos → *Editar* → *Guardar como* `P89_ZAP_Zapata_Aislada.rfa`, etc. Cada integrante entrega y sustenta su objeto.

Con **RevitPythonShell** se abre `script.py` y se ejecuta igual. Si no encuentra el `.txt`, pide seleccionarlo.

### Si algo falla
- *“No se encontró una familia para …”*: cargue la familia indicada desde *Insertar → Cargar familia → Estructura* y vuelva a ejecutar.
- *“AVISO: campo no disponible en el Schedule”*: agregue ese campo a mano en *Propiedades del Schedule → Campos*.
- Si no hay una familia de perfil C, la correa queda como sección rectangular de 60×160 mm. Sus parámetros funcionan igual. Esto se avisa en la salida.

## Prueba de la fórmula (para el video)
Seleccione una zapata Z-T1 → *Editar tipo*. Cambie `ZAP_Lado_B` de 1,30 a 1,50: la zapata crece y `ZAP_Volumen_Concreto` pasa de 0,592 a 0,788 m³ en el Schedule. Vuelva a 1,30.

## Datos que el grupo debe confirmar (celdas amarillas del Excel)
- Nombres de los integrantes y número de grupo (hoja OBJETOS y nombres de archivo).
- Despiece del refuerzo de columnas, vigas y zapatas (quedó como “VERIFICAR en despiece P-892022”).
- `fy` del perfil PHR: se puso 340 MPa, un valor típico que hay que verificar.
- Conclusiones del foro de la Actividad 2 (hoja AJUSTES_ACT1_ACT2).
- **Discrepancia:** en el DWG la zapata Z-T2 está dibujada de 1,50 m, pero la matriz de la Act. 1 dice 1,60 m. El modelo usa 1,60 m.
- Las vigas VC se trazaron entre columnas consecutivas de un mismo eje (23 tramos). Compárelas con las VC-01 a VC-18 del plano.
