# Guion de sustentación (máx. 5 min)

**0:00–1:00 · Paciente y objetos** (integrante 1)
- Vivienda campestre de dos niveles en ladera, Cañaveral, Turbaco (proyecto P-892022). Pórticos de concreto DMI y cubierta en perfilería PHR.
- Cuatro objetos que forman la cadena de carga: correa PHR → columna → viga de cimentación VC → zapata aislada. Mostrar la vista 3D y la planta de cimentación con los ejes 1–8 / A–G.

**1:00–2:00 · Criterios de parametrización** (integrante 2) – mostrar la hoja ESTRATEGIA
- Prefijos: `PAC_` = común al paciente; `ZAP_`, `COL_`, `VCI_`, `COR_` = particular de cada objeto.
- 5 comunes como **compartidos vinculados al proyecto**: un solo GUID para los 4 objetos, para que el Schedule y el IFC los lean como un solo campo.
- 3 particulares por objeto, **compartidos dentro de cada familia**. Viga y correa comparten la categoría Armazón estructural; si se vincularan al proyecto, cada una mostraría los parámetros de la otra.
- **Tipo** = igual para todas las piezas del tipo (material, f'c, sección, refuerzo). **Instancia** = cambia pieza a pieza (código, nivel, altura libre, eje, separación).
- La norma NSR-10 pasa a Información de proyecto. Se retiraron los datos que Revit ya calcula (longitud, niveles base/superior), para no duplicarlos.

**2:00–4:00 · Implementación y fórmula** (integrante 3)
- Abrir *Gestionar → Parámetros de proyecto* y mostrar los 5 `PAC_`.
- Editar la familia `P89_ZAP_Zapata_Aislada` → *Tipos de familia*. Mostrar la fórmula `ZAP_Volumen_Concreto = ZAP_Lado_B * ZAP_Lado_B * ZAP_Espesor_h` y que Anchura y Longitud dependen de `ZAP_Lado_B`.
- En el proyecto: *Editar tipo* de Z-T1, cambiar `ZAP_Lado_B` de 1,30 a 1,50. La zapata crece y el volumen pasa de 0,592 a 0,788 m³. Volver a 1,30.
- Mostrar las propiedades de una columna (`COL_Altura_Libre` de instancia: 2,75 m o 5,75 m) y de una correa.

**4:00–5:00 · Schedule y conclusiones** (integrante 4)
- Abrir `P89_ACT03_VALIDACION`: los 5 comunes están llenos en las 4 categorías y cada objeto muestra solo sus particulares.
- Comparar los conteos y volúmenes con la hoja VALORES_POR_TIPO: 19 zapatas y 13,72 m³ de concreto en zapatas (con Z-T2 = 1,60 m).
- Conclusión: una sola matriz, un solo archivo compartido y un solo Schedule. Así la información es consistente y no se duplica entre los objetos.
