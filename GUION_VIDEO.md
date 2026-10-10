# Guion del video (máx. 5 min) – Luis David Arroyo Anaya

Use la presentación `PARAM_2026-2_ACT03_PRESENTACION.pptx`. Lo que debe decir está también en las **notas del orador** de cada diapositiva.

**0:00 – 1:00 · Paciente y objetos (diapositivas 1 y 2)**
- "Buenos días. Soy Luis David Arroyo Anaya, de la Maestría en Patología de la Construcción de la Universidad Santo Tomás. Presento la Actividad 3 de BIM Parametrización sobre el mismo paciente de la Actividad 1: la Casa Campestre P-892022 en Turbaco."
- "Es una vivienda de dos niveles en ladera, con pórticos de concreto y cubierta en perfilería PHR. Elegí cuatro objetos que forman la cadena de carga: la correa PHR recibe la cubierta, la columna baja la carga, la viga de cimentación amarra las zapatas y la zapata la entrega al suelo."
- "Cada objeto tiene su color: zapatas gris, columnas azul, vigas de cimentación verde y correas rojo. Para completar el modelo agregué las vigas aéreas en naranja y la losa de entrepiso en amarillo. Todo sale de los planos P89-2022."
- En pantalla: la vista **3D P89 ACT03 - Colores por objeto**.

**1:00 – 2:00 · Criterios (diapositivas 3 y 4)**
- "Uso prefijos: PAC_ para lo común a todo el paciente y ZAP_, COL_, VCI_ y COR_ para lo particular de cada objeto."
- "Los cinco comunes son parámetros compartidos vinculados al proyecto. Tienen el mismo GUID en todos los objetos, así el Schedule y el IFC los leen como un solo campo. El código y el nivel son de instancia porque cambian pieza a pieza; material, resistencia y clasificación son de tipo."
- "Cada objeto tiene máximo tres particulares, compartidos y guardados dentro de su propia familia. La viga de cimentación y la correa están en la misma categoría; si fueran de proyecto, cada una mostraría los de la otra."
- "La norma NSR-10 pasó a Información de proyecto y retiré lo que Revit ya calcula, para no duplicar información."

**2:00 – 4:00 · Implementación y fórmula (diapositivas 5 y 6)**
- En Revit: editar la familia **P89_ZAP_Zapata_Aislada** → *Tipos de familia*. Decir: "El volumen es lado por lado por espesor. Además la anchura y la longitud dependen de ZAP_Lado_B, así que la geometría también es paramétrica."
- En el proyecto: *Editar tipo* de Z-T1, cambiar ZAP_Lado_B de 1,30 a 1,50. Decir: "La zapata crece y el volumen pasa de 0,592 a 0,788 m³." Volver a 1,30.
- Mostrar *Gestionar → Parámetros de proyecto* (los 5 PAC_) y las propiedades de una columna: "COL_Altura_Libre es de instancia: 2,75 m en las que llegan a N+3,05 y 5,75 m en las que suben a N+6,05."

**4:00 – 5:00 · Schedule y conclusiones (diapositivas 7 y 8)**
- Abrir **P89_ACT03_VALIDACION**: "Los cinco comunes están llenos en todas las categorías y cada objeto tiene solo sus particulares. Hay 19 zapatas y 19 columnas, y 13,72 m³ de concreto en zapatas, igual que en la matriz."
- "En conclusión: con una sola matriz, un solo archivo de parámetros compartidos y un solo Schedule, la información queda consistente y sin duplicados. Muchas gracias."
