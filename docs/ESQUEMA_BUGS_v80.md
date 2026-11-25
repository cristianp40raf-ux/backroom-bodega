# Esquema de corrección · colección de bugs (22-11-2026)
Base: simulador v79 (versión 104). Fotos reales: «fotos comparativas» (pilar6, pocaluzcielotrastienda, trastienda, 20261117_143551) + galería de referencias.
Inventario de la escena hecho con prueba automática (3.080 mallas con nombre, grupo, material y caja) para saber de dónde sale cada error.

## De dónde sale cada error (origen)
| # | Bug (tu número / captura) | Origen encontrado | Qué haré |
|---|---|---|---|
| 6 | 2 redes húmedas · «reddebombasnoconectaconnada», «bug» | Hay dos redes visibles: la de Blender (red_humeda + rociadores, la que hicimos) y la vieja del simulador (rociadores de la sala a 6,8 m y el montante rojo de 6 tubos en x −4, z 2 = la «red de bombas»). | Borrar toda la red vieja del simulador. Rehacer en Blender el montante de bombas conectado a la matriz. Auditar la red de Blender tramo por tramo. |
| 10 | Red húmeda en la reja de entrada · «eliminarestaredhumeda» | Gabinete de la red de Blender en x 0, z 7,5. | Quitar gabinete y su bajada. En bodega queda solo el de la ochava. |
| 8 | Red húmeda de la ochava mal dibujada · «paredocheava…» | Carrete rojo plano + tubo que baja del cielo. | Gabinete real (caja roja con puerta de vidrio, carrete dentro, válvula) conectado a la matriz. |
| 23 | Red húmeda en mitad del pasillo · «redhumedaenmitaddepasillo» | Bajada de la red de Blender cruzando el pasillo de panadería. | Re-rutear pegada al muro. |
| 18 | Bandeja y red atraviesan muros; viga del círculo; vigas bajo el 2º nivel · «redhumedabandeja…» | Vigas: las agregué en v79 bajo la losa (error, no van a la vista). Viga del círculo: viga de techo del simulador. | Quitar vigas bajo el 2º nivel y la viga marcada. Revisar cruces de bandejas y red con muros. |
| 14 | Estructura oscura que tapa el techo de la trastienda · «estrcuturaoscura…» | Por confirmar con captura: muro alto del simulador sobre las cámaras + sombreado de entretecho. | Eliminarla. |
| 2 | Cimientos de pilares; pilares de bodega en bruto · «cimientos de los pilares…» | Pilares de la bodega (modelo de bodega) con dado/base. | Quitar dados (los pilares nacen del subterráneo) y texturizar hormigón pintado como pilar6. |
| 4 | Pilares muy claros · «pilaresmuyclaros…» | Pintura blanca casi pura en pilares de bodega y sala. | Hormigón pintado gris claro con manchas, roces de grúa y desgaste (foto pilar6). |
| 9 | Extintores con estructura | Extintores sobre soporte/poste amarillo. | Quitar soporte: extintor colgado de su gancho en el pilar/muro. |
| 7 | Pared de la ochava sin la textura ni la continuidad de las demás | Muro distinto al resto de la bodega. | Mismo material y juntas que los muros de bodega, continuo. |
| 13/20 | Muro interno de trastienda distinto al de bodega; muros «hormigón en bruto pintado» · «paredbugeada…», «paredderecepcion» | Muros del simulador con blanco liso y franja gris cortada. | Hormigón en bruto pintado: blanco sucio arriba, franja gris oscura de ~1,2 m abajo, continua en esquinas (foto pocaluzcielotrastienda). |
| 12 | Muro de cierre sobre el cielo falso de vinos; trastienda separada de la sala por muro oscuro · «sobreelcielofalsodevinos…» | Falta el cierre sobre el cielo falso. | Agregar muro de cierre oscuro desde el cielo falso hasta la cubierta. |
| 19 | Patio: muro movido deja espacio, puertas y objetos fuera de lugar · «patiobordepared…» | Muro del patio de Blender en x −59,2 vs trastienda del simulador en x −60,8 (1,6 m de diferencia). | Alinear: muro, puertas y objetos al mismo borde. |
| 3 | Racks centrales con fierros cruzados de más · «error rackcentrales» | Por confirmar: arriostramiento en X en la cara del rack doble. | Dejar solo el arriostramiento real del bastidor (fotos bodega). |
| 15 | Objetos insertos en pilares y muros · «rackinsertoenpilar», «cajasinsertas» | Kit de trastienda (rack vs pilar) y pallets de bodega. | Auditoría automática de choques (cajas contra pilares/muros) y corrección. |
| 11 | Objetos flotando · «hacerseguimiento…», «incoherenciasvisuales» | Varios (varilla suelta, plano en V, tramos de tubo cortados). | Auditoría automática de objetos sin apoyo + revisión visual. |
| 16 | Objetos no modelados ni texturizados (merma y todo) · «objetosnomodelados…», «rackmetalicomaldibujado», «paredfueradelugarcamarademerma» | Cajas del simulador (lavamanos, dispensador, repisa metálica) y un muro de panel fuera de lugar. | Modelar en Blender lo visible; corregir el muro. |
| 17 | Canaletas dentro de la trastienda · «objetoatraviesarack» | Por confirmar: bajadas de aguas lluvia del techo de Blender caen dentro por la diferencia de 1,6 m del muro. | Moverlas al exterior real. |
| — | Rack sin color · «racksincolor» | Rack de trastienda con vigas crema; la foto muestra vigas naranjas. | Vigas naranjas. |
| 1/20 | Luminosidad excesiva («hospital») y cielo oscuro | Luz general alta + brillo propio en muros y cubierta que agregué para el contraste con la calle. | Bajar luz general y brillo propio; cielo más oscuro con la altura (las luces cuelgan más abajo). |

## Orden de ejecución (cada paso condiciona el siguiente)
1. Respaldo de v79 (versión 104).
2. Borrar duplicados y estructura que sobra: red vieja (6), gabinete de la reja (10), vigas bajo el 2º nivel y viga marcada (18), estructura oscura (14), dados de pilares (2), soportes de extintores (9). Primero lo que se quita, para no texturizar lo que va a desaparecer.
3. Red húmeda única en Blender: montante de bombas conectado, gabinete de la ochava, bajada del pasillo pegada al muro, auditoría de cruces (6, 8, 23, 18).
4. Muros y pilares: alineación del patio (19), ochava (7), muros de trastienda y recepción (13/20), cierre sobre vinos (12), pilares en hormigón pintado (2, 4).
5. Objetos: racks centrales (3), rack sin color, choques con pilares/muros (15), flotantes (11), canaletas (17), objetos sin modelar de merma y muro fuera de lugar (16).
6. Luz al final (1, 20), porque depende de los materiales nuevos.
7. QA: capturas a 1600 px en los mismos lugares de cada bug + lado a lado con las fotos; veredicto por bug; publicar; respaldo y bitácora.

## Nota de rendimiento (no estaba en la lista)
En tus capturas con la sala a la vista el contador marca 59–62 ms por cuadro (~16 FPS) y 2.500 llamadas de dibujo: bajo el mínimo de 35 FPS. Lo reviso al final sin bajar calidad de texturas.

## Estado tras v80 (publicada como versión 106, 22-11-2026)
| # | Estado | Verificación |
|---|---|---|
| 6 | Red vieja del sim oculta (rociadores de sala + montante de 6 tubos). Montante de bombas rehecho en Blender y unido a la matriz. | Captura c21: tubos suben y empalman al colector. |
| 10 | Gabinete de la reja eliminado. | Captura b04. |
| 8 | Carrete de la ochava en Blender (marco amarillo, tambor, válvula, bajada desde la matriz). Se reemplazó el carrete plano del modelo de bodega. | Captura c15. Nota: hice carrete abierto con marco (foto «manguera junto al pilar 3»), no caja con vidrio. |
| 23 | Bajada de la entrada pegada al muro (x −58,8). | No verificado visualmente. |
| 18 | Vigas bajo el 2º nivel eliminadas. | Capturas c22, e22. |
| 14 | Cielos planos del sim a 7,38 m ocultos (tapaban la cubierta); sombreado de entretecho suavizado a 55 %. | Capturas c06 → e06. |
| 2 / 4 | Pilares sin dado/placa/pernos, hormigón con base pintada blanco gastado (textura rehecha, sin manchas tipo camuflaje). | Capturas c03, c15. |
| 9 | Extintores colgados de gancho, sin soporte; accesorios flotantes del modelo de bodega ocultos. | Capturas c03, c15. |
| 7 / 13 / 20 | Muros interiores de bodega/trastienda/recepción: hormigón en bruto pintado con juntas de moldaje y franja gris 0,9 m. | c15, e22. Recepción no verificada después del cambio de textura. |
| 12 | Muro de cierre oscuro sobre el cielo de vinos y tabiques del 2º nivel oscuros. | b24 (antes del cambio de luz). |
| 19 | Muro poniente del sim alineado al de Blender (−59,07/−59,33). | c19 alto: la plataforma llega al muro. Vista cenital no tomada. |
| 3 | Diagonales en X del modelo de bodega eliminadas; queda el zig-zag del rack Blender. | c05. |
| 15 | Racks y líneas de pallets de trastienda recortados para no entrar en pilares (6 casos). Pallets insertos en racks de bodega («cajasinsertas»): pendiente (dato de operación del sim). | No verificado visualmente. |
| 16 | Merma: lavamanos inox, dispensadores, basurero de pedal y repisa de alambre modelados en Blender; cajas del sim anuladas. Rincón de aseo (vestíbulo) y otros objetos del resto de la simulación: pendiente. | c14. |
| 17 | Canaletas al lado exterior. | No verificado visualmente. |
| — | Rack claro con vigas naranjas; celosía del kit en zig-zag. | No verificado visualmente. |
| 1 / 20 | Luz: sol 1,9→1,7; rebote falso de bodega al 45 %; cubierta 0,8→0,36; losa del 2º nivel 0,28; charco de bodega a la mitad. | c01, e06. Sin lado a lado con foto. |
| 11 | Auditoría de varillas: las varillas oscuras del techo de bodega son colgadores de bandeja/matriz (Blender); no encontré piezas sueltas. | Captura del bug no reproducida. |
| Rendimiento | Sin cambios; pendiente. | — |
