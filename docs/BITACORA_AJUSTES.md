# Bitácora de ajustes — réplica 3D de la bodega

Registro vivo de **qué sirve y qué no**, con los valores exactos de cada ajuste, para no perder nada entre conversaciones.
Se actualiza en cada versión. La más reciente va arriba en "Estado actual".
Complementa a `CONTEXTO_PROYECTO_BODEGA.md` (que explica el proyecto completo).

---

## Estado actual

| Pieza | Versión vigente | Dónde está |
|---|---|---|
| Web "Backroom Recorrido" | v25 (artefacto versión 25) — **plano v3 de Cristian (02-11-2026)**: pilares enfrentados, racks reacomodados, pilares de la fila 020 dentro del pasillo 2, racks 003/001–006 de 4 niveles, camilla de una pieza | https://claude.ai/artifact/1wJGwaivRnun4ET8k8ACyt |
| Fuente web | `web_fuente\v25_plano3\` (v24 intacta en `web_fuente\v24_interfaz\`) · antes: `web_fuente\v24_interfaz\` (template.html, sim.js, med.js, fx.js, fx2.js, hud.js, wear.js, scan.js, turno.js, maq2.js, occ.js, **ui.js**, build.py, index.html). La v22 queda intacta en `web_fuente\v22_estructura\` | PC |
| Escena Blender | `blender\bodega_backroom_v8.blend` (la original `bodega_backroom.blend` nunca se sobrescribe) | PC |
| Script de animación | `blender\mc_build.py` (= `mc_build_v14.py`) + `blender\mc_props.py` (cascos y bordes) | PC |
| Script de la entrada | `blender\bk_entrada.py` (reja + trastienda) y `blender\bk_detalle_tras.py` (pallets, carros, elevador nuevo); vistas de control con `ent_prev.py` | PC |
| Orden para exportar | `blender -b bodega_backroom.blend --python bk_plano3.py --python bk_entrada.py --python bk_detalle_tras.py --python bk_estructura.py --python mc_props.py --python mc_build.py -- save` (**bk_plano3.py va primero**: carga `bk_data3.json` y rehace racks, etiquetas, jaulas y líneas) | — |
| Datos del plano v3 | `blender\bk_data3.json` (generado por `blender\gen_bl3.py` desde `blender\plano_v3_editor.json`, que es el plano del editor de Cristian) | PC |
| Luz horneada del piso | `blender\lm_bake3.py` (cadena: bk_plano3 + bk_entrada + bk_detalle_tras + lm_bake3 `-- 2048 640 128`) → `lm_piso3_raw.npy` → `luz_piso.webp` (k = percentil 99,5, gamma 1/2,2, volteado en vertical) | PC |
| Respaldo antes del plano v3 | `respaldos\2026-11-02_v24_antes_plano3\` (bk_estructura v22, bk_data, blend v8, glb v22, bitácora y contexto) | PC |
| Respaldo antes de la entrada | `respaldos\2026-10-26_v16_antes_entrada\` (blend, glb v12, scripts, web v16) | PC |
| Exportación | `blender\web\bodega_v8.glb` → copia `bodega_v22.glb` | PC |

---

## 1. Lo que SIRVE (mantener)

### Personajes y movimiento
| Ajuste | Valor / detalle | Resultado |
|---|---|---|
| Caminata de la supervisora | Captura CMU **07_02** (caminata normal) + IK de 2 huesos con pies fijos al piso | Resbalón del pie apoyado: **mediana 2,4 cm** (antes 24 cm) |
| Elegir la captura por métricas | velocidad 1,6 piernas/s, rodilla máx. 180°, razón altura de cadera 1,065 | 07_02 fue la más parecida al recorrido real entre 12 caminatas |
| Fase del paso ligada a la distancia | `ph = distancia / zancada`; zancada = 1,171 m | Los pies no patinan a velocidad constante |
| Bajar la cadera según el pie más bajo | mínimo de tobillo/punta en cada cuadro | Pies pegados al piso |
| Cuello y cabeza al caminar | 45–60 % hacia la postura neutra | Ya no camina mirando el suelo |
| Pose de escribir | Video de Gemini → MediaPipe `pose_landmarker_heavy` (2D/3D) | Sirve para posturas **quietas** (de pie anotando) |
| Brazo del lápiz al caminar | balanceo procedural: `th=-(0.05+0.26·cos)`, `flex=0.30+0.22·max(0,cos)` | Natural, sin rigidez |
| Tabla al costado al caminar | dirección media del brazo izquierdo en el video de caminata | Ya no va pegada al pecho |
| Agarres de dedos | 'tabla' (izq.), 'lapiz' (der.), operador 'manilla' (der.) y 'suave' (izq.) | Los dedos cierran sobre los objetos |
| Parpadeo | hueso `orbicularis03`, rotación **X negativa**, 0,5 rad, cada 70–140 cuadros + movimientos de ojos | Cara viva |
| Brazo deformado | usar la rotación del pecho `Rc = pose.matrix_rot @ ml_rot.T`, no los ejes de la columna | Corregido |
| Operador | manos por IK: derecha en el control (1,10 m), izquierda en el tablero (1,0 m); respiración en `spine02` | Correcto |
| Operador mira | en la web: cabeza y `spine03` hacia donde va la grúa o hacia las horquillas (giro ±1,6, inclinación −0,5..0,6; 35 %/65 %) | Correcto |
| Cascos | medio elipsoide por cabeza, borde a `cabeza_alto − 0,072`, visera corta, solidify 3–4 mm | Proporción correcta |
| Bordes del chaleco | quitar caras "oreja" + suavizado Laplaciano del borde + proyección a la malla | Sin dientes |

### Web
| Ajuste | Valor / detalle | Resultado |
|---|---|---|
| Superar 16 MB | escena en `bodega_datos.json` + trozos `bodega_bin_N.json` de 10 MB (`pack.mjs`) | Sin límite práctico (256 MB por versión) |
| Materiales de personajes | opacos (`transparent=false`); `alphaTest 0.5` solo en pelo, cejas, pestañas y ojos | Se acabó la boca/ojos rojos sobre la cara |
| Animación | `AnimationMixer`, cada clip `LoopRepeat` con su duración | Sin saltos |
| Grúa | aceleración 0,6 / 0,45 m/s², máx. 2,0 / 1,5 m/s | Velocidad realista |
| Física | `cannon-es` 0.20.0 con tiempo propio (`e.pt`) | Cajas caen bien |
| Luz horneada del piso | Cycles DIFFUSE, cajas sustitutas de racks; material Standard clonado con `lightMap` (canal 1), albedo 0,3, intensidad 12,5 | Mejora visual moderada, sin costo de FPS |
| Texturas | ~~piel 2048, resto de personajes 1024, bodega 768, webp q72 · Peso controlado~~ | **DEROGADA 2026-11-15** (ver regla nueva al final) |

### Estética de la simulación (v15, archivo `fx.js`)
| Ajuste | Valor / detalle | Resultado |
|---|---|---|
| Vista maqueta | cámara orbital fov 34°, techo/vigas/LED ocultos, muros y columnas cortados a 2,4 m con plano de recorte **y una sola cara** (doble cara se veía negra por dentro), patio gris #5A636A | Tipo juego de gestión; se ve todo el flujo |
| Estilo caricatura | MeshToonMaterial con rampa de 4 tonos, saturación ×1,25, luz hemisférica ×1,55; contorno con 2.ª pasada `overrideMaterial` (normales invertidas, grosor 0,0024 × distancia) | Look de juego; en la prueba fue **más rápido** que el realista |
| Gráficos "Bueno" (por defecto) | sombras de contacto (pallets en piso, grúa, supervisora, tijera, carros), marcas de neumáticos en pasillos, polvo 520 partículas, bruma 22–95 m, viñeta CSS | Más profundidad, costo bajo |
| Gráficos "Cine" | sombras reales 2048 + GTAO + bloom (umbral 2,2) | ~2,4 veces más lento que Bueno en la prueba; vuelve solo a Bueno si baja de 18 FPS durante unos segundos |
| Sonido | sintetizado con WebAudio (sin archivos): ventilación, zumbido LED 100 Hz, motor y chirrido de la grúa según velocidad, hidráulica al subir/extender, pitido en reversa, derrumbe, choque, alarma de colapso, bocina de camión, pasos | Ambiente sin costo |
| Marcadores | pines DOM sobre incidentes activos (clic = ir al lugar) y etiqueta de tarea de la grúa en maqueta o al seguirla | Lectura tipo juego |
| Preferencias | gráficos, estilo y sonido se recuerdan en el navegador | — |
| **FPS medidos por Cristian (v15, HD 620)** | Básico 70 · Bueno 47–50 · Cine 18 | Bueno jugable; Cine no |
| Cine más liviano (v16) | GTAO a media resolución y 8 muestras (antes 12), sombras 1024 (antes 2048) | pendiente de medir en el PC |
| Resolución automática (v16) | cada 2 s: si FPS < meta−3 baja la resolución interna ×0,88 (mínimo 0,55); si FPS > meta+14 la sube ×1,07. Meta 40 (Básico/Bueno) y 30 (Cine). Cine vuelve a Bueno solo si al mínimo sigue bajo 22 FPS. Se apaga en el panel de la prueba | pendiente de medir en el PC |
| Prueba de rendimiento (v16) | botón "Probar rendimiento": misma vista, 18 cuadros por configuración, mediana de ms con `readPixels` para esperar a la tarjeta (no depende del límite de FPS de la pantalla) | da el costo de cada efecto en el PC real |

### Entrada y trastienda (v17, `bk_entrada.py`)
Fuente: fotos `fotos_entrada_2026-10-26` (01–09), 3 fotos limpiadas con Gemini (`limpias_gemini`) y el dibujo del recorrido de Cristian (`dibujo_recorrido_cristian.jpg`).
| Elemento | Valor | Origen |
|---|---|---|
| Recorrido | se entra desde la sala por puertas de vaivén abajo a la izquierda del plano, se sube por fuera del costado izquierdo con la **reja a la derecha** y se dobla a la derecha al acceso | Cristian (dibujo + respuestas) |
| Reja | **solo** el costado del acceso (x = 0); los otros lados siguen siendo muro. Parantes blancos cada ~2,5 m, vigas naranjas a 0,12 / 1,32 / 2,57 m, malla gris hasta 2,65 m; postes del acceso de 3,6 m con viga a 3,45 m; tablero de afiches en el tramo norte | fotos 03–05, 07 |
| Acceso | abertura z 1,74–4,19 m (la misma del plano) | plano |
| Puertas de la sala | vano de 2,0 m (x −2,7 a −0,7) en z ≈ 13,4 m, a menos de 10 m del acceso; hojas de vaivén con ventanilla y zócalo negro; tiras de PVC arriba. En la web se abren al acercarse | Cristian (< 10 m), fotos 01 y 07 |
| Pasillo | ~4,4 m de ancho entre la reja y el muro poniente | **estimado** de fotos |
| Cuarto blanco | x −7,4 a −3,0, z 9,3 a 13,4, 3 m de alto, plancha diamantada 1 m, puerta y dispensador de agua | foto 07 — **estimado** |
| Salida de emergencia | puerta doble de 1,8 m en el muro norte (x −2,6 a −0,8), escalón de concreto, doble línea amarilla, letrero SALIDA, parche de yeso | fotos 02/06 |
| Red de incendio | 6 matrices rojas con válvulas en jaula de malla negra, al poniente de la salida | foto 02/06 |
| Pasillo lateral | hacia el poniente (z 0 a 5) con banderines | fotos 08/09 — **estimado** |
| Elevador de tijera | sale de la bodega y queda estacionado junto a la reja, cerca de las puertas | fotos 03, 07, 08 |
| Web | se parte en las puertas de la sala mirando a la bodega; colisiones de la trastienda; minimapa incluye la trastienda; el recorrido automático empieza en la sala | — |

### Detalle de la trastienda (v18, `bk_detalle_tras.py`)
| Elemento | Valor | Origen |
|---|---|---|
| Pallets | 2 pallets envueltos en film transparente contra el muro poniente (girados, 1,0 m en z), 1 pallet con cajas abiertas en el pasillo lateral; cajas de cartón mezcladas con etiquetas blancas | fotos 07, 08, 09 |
| Gavetas y tablero | 2 columnas de 4 gavetas (gris y negra) y un tablero de madera apoyado | foto 08 |
| Carros | 3 carros de supermercado con mercadería (junto a la red de incendio, junto a la reja frente al acceso, pasillo lateral); mismo diseño que los de la bodega | fotos 02, 05, 08 |
| Transpaleta | manual, con las horquillas bajo un pallet | foto 09 |
| Instalaciones | bandeja de cables a 5,55 m, 3 cámaras domo colgadas, extintor y pulsador junto a la salida, conduits, afiche junto al cuarto, letreros de piso mojado plegados | fotos 02, 07 |
| Elevador de tijera | **rehecho** estilo GS-1930: 1,83 × 0,76 m, plataforma a 1,0 m, baranda a 2,0 m, 4 niveles de tijera con pasadores, ruedas macizas, caja de control, peldaños. Sin marcas ni el "1930" | fotos 03, 07 |
| Web | colisiones y sombras de contacto para cada objeto nuevo; el camino puertas → acceso sigue libre | — |

### Pantalla completa y paneles (v19, `hud.js`)
| Ajuste | Valor | Resultado |
|---|---|---|
| Inicio compacto | arranca con el panel de simulación plegado (solo reloj y velocidad), sin ayuda ni botones; barra con Menú / Solo bodega / Pantalla completa | se ve la bodega |
| Teclas | H = solo bodega (oculta todo), F = pantalla completa | — |
| HTML independiente | `build_local.py` mete la escena y la luz del piso dentro de un solo archivo (~11 MB); necesita internet solo para three.js y las fuentes | abre con doble clic, sin servidor |
| Pantalla completa dentro de claude.ai | puede estar bloqueada por el marco de la página | usar el HTML independiente o F11 |

### Identidad propia (v20): herramientas hechas para este proyecto
Motivo: Cristian notó que el proyecto "se ve como cualquier proyecto de IA". Se eligió diferenciar con contenido y técnicas propias, no con software ajeno.
| Herramienta | Cómo funciona | Ajustes que sirvieron |
|---|---|---|
| Desgaste del piso (`wear.js`) | Lienzo de 50 × 14 m a 20 px/m sobre el piso. Cada rueda real de la grúa (posición leída de la malla) deja goma al avanzar y más al girar; pasos de personas = suciedad; transpaletas del andén = rayas; grúa estacionada = gotas de aceite; polvo de base junto a muros, reja y pies de racks. Se engancha al paso de la simulación (funciona a ×60 y con "simular un turno"); se guarda en el navegador | goma: halo 0,20 m alfa 0,006 + huella 0,075 m alfa 0,010; giro: 0,24 m alfa 0,014 + 0,09 m alfa 0,022; opacidad del lienzo 0,72 (el primer intento con alfa 0,035/0,13 quedó **negro y gráfico**: no sirve) |
| Escáner de bins (`scan.js`, tecla E) | Terminal de escaneo genérico (sin marca) con etiqueta de bin tipo impresora térmica y código de barras decorativo. Escanea bin (estado, pallet PLT-, cajas, tiempo en ubicación, quiebre y reserva sugerida) o pallet en el piso | pestañas ESCANEAR / FLOTANTE / BUSCAR |
| Stock flotante | lista de pallets sin bin (tránsito y pasillo) ordenada por antigüedad, más los que esperan en el andén; toque = ir a verlo. Pensado para conectarse a los **bins virtuales** de Cristian con datos reales y autorización | — |
| Modo turno (`turno.js`) | cuando la grúa queda libre se pausa y ofrece hasta 3 trabajos en conflicto (despejar pasillo, reponer quiebre, ubicar tránsito) con tiempo estimado y consecuencia; a las 8 h imprime una boleta y la compara con el piloto automático en la misma semilla | puntaje = 1000 − 20/h de quiebre (suma de pisos vacíos) − 2/min colapsada − 60/incidente − 15/pallet máx. en pasillo + 2/ubicado + 3/reposición. **Puntaje sin calibrar con datos reales** |
| Lenguaje visual | negro #16181A, amarillo de seguridad #FFD23F, franjas de peligro, papel de boleta, tipografía mono de etiqueta | reemplaza el panel "de vidrio" genérico en las piezas nuevas |

### Maqueta como vista principal y huellas corregidas (v21)
| Ajuste | Valor | Origen / resultado |
|---|---|---|
| **Huellas de ruedas** | el apilador eléctrico usa ruedas de **poliuretano, no caucho**: casi no marcan. Roce gris: halo 0,20 m alfa 0,0022 + huella 0,075 m alfa 0,0032; giro 0,005 / 0,008. Se descartó el desgaste guardado antes (clave nueva `bodegaDesgaste2`) | corrección de Cristian |
| Cámara de la maqueta | destino y cámara separados con suavizado (k = 1 − e^(−7·dt)); inercia al soltar; zoom hacia el cursor (3,2 a 80 m); girar con clic derecho, Shift o dos dedos; inclinar 0,28–1,53 rad | — |
| Clic en la maqueta | vuela hacia el pallet o bin bajo el cursor y lo abre en el escáner; ignora los muros cortados (el rayo los tocaba sobre 2,4 m) | — |
| Panel de cámara | ⟲ ⟳ ▲ ▼ ＋ － y vistas: Todo, Planta, Pasillo 1, Pasillo 2, Tránsito, Trastienda; teclas Q/E, T/G, +/−, C | — |
| Nombres de zonas | pasillos, cruce, tránsito, acceso, trastienda, sala, salida, red de incendio, cuarto; tamaño según distancia | — |
| Calidad | resolución ×1,6 (máx. 2) con la cámara quieta; sombras reales 2048 en la maqueta; filtrado anisotrópico ×8; se apagan solos bajo 22 FPS | FPS en la HD 620 **sin medir** |

### Estructura de la nave (v22, `bk_estructura.py` + `occ.js`)
Fuente: plano de Cristian del 26-10 (pilares y vigas numerados, recorte) + carpeta `Detalles` (19 fotos).
| Elemento | Valor | Origen |
|---|---|---|
| Pilares | P1 x 3,58–4,46 · P2 20,18–21,26 (fila 001, z 0,30–1,36) · P3 35,95–36,80 (z 0,30–1,20) · P4 38,45–39,32 · P5 17,55–18,70 · P6 2,78–3,60 (fila 020, z ~10,7–11,6). Hormigón; panel blanco hasta 2,45 m con 2 franjas amarillas, extintor y letreros; P5 y P6 pintados enteros; demarcación amarilla en el piso | plano + fotos pilar1–6 |
| Vigas superiores | blancas 0,32 × 0,68 m a 6,62–7,30 m por los ejes de pilares: fila 001 (z 0,83) hasta P3, diagonal hasta (x 39,12; z 4,46), sobre el rack 002 hasta P4, y fila 020 (z 11,17) | plano |
| Cielo | plancha ondulada (textura `techo_ondulado.png`, nervios a lo largo de los pasillos), correas transversales cada 1,6 m, riostras en X en 3 paños | fotos cielo/viga |
| Red húmeda | ramales rojos transversales cada 3 m a 6,92 m con rociadores cada 2,8 m, 2 matrices junto a los muros, colgadores; carrete de manguera con marco amarillo y montante en el muro del recorte junto a P3 | fotos manguera / viga pilar 3 |
| Recorte | esquina posterior cortada en diagonal de (36,8; 0,075) a (39,52; 2,6): muros, piso, techo y cañerías cortados con plano; muro diagonal nuevo; colisión en la web | plano |
| Rejas de la isla | malla azul con marcos y cruces en el frontis (x 7,94) y el fondo (x 34,86), las dos caras de la isla, hasta 5,62 m | foto "front del rack con reja" |
| Cama baja | 003/001/001 a 003/006/002 (12 posiciones): vigas a 0,20–0,32 m, tablero a 0,34 m, cajas sueltas hasta ~1,45 m; **sin pallets** (en la simulación quedan fijas y fuera de la grúa; el escáner las muestra como "CAMA BAJA") | dato de Cristian + fotos |
| Tapa de acero | 1,2 × 1,2 m en el cruce posterior (x 36,0–37,2; z 5,4–6,6) | foto |
| Luz en los racks | sombreador: máscara en planta de los racks (desenfoque 0,3 m) × factor de altura: 30 % de luz al piso → 100 % arriba (smoothstep 0,02–0,95 de 5,5 m) | pedido de Cristian + foto "oclusión rack abajo" |
| No sirvió | probar el efecto de luz a los 4–6 s en el renderizador por software: los sombreadores aún no compilaban y parecía no funcionar | — |

### Plano v3 de Cristian (v25, 02-11-2026) — **manda sobre todo lo anterior**
Fuente: `plano_editor_2.html` (versión 3) + elevación de la fila 003. Si algo de antes contradice esto, vale el plano v3.
| Ajuste | Valor | Origen / resultado |
|---|---|---|
| Escala del editor | x_m = (x_plano + 0,7) × 1,3283 (el muro del acceso −0,7 → x 0 y el muro del fondo 29,05 → x 39,517). Cada posición = 1,328 m (1,248 libre + parante 0,08). Profundidad de las filas igual que antes (001: z 0,3–1,4; central 4,8–5,9; 003: 6,05–7,15; 020 y 600: 10,55–11,65) | el editor no está en metros; se fijó con los muros |
| **Pilares** | 1 y 6 enfrentados (x 3,25–4,12); 2 y 5 enfrentados (x 19,00–19,86); 3 x 34,54–35,40; 4 x 38,26–39,12. Fila 001: z 0,30–1,36. **Fila 020 (4, 5, 6): z 10,05–10,97, sobresalen ~0,5 m dentro del pasillo 2 a propósito** (así es la bodega: no se corrige) | plano v3 |
| Pasillo 2 con pilares | colisión al caminar, pallets dejados en el pasillo y rutas consideran los pilares (las posiciones de pasillo que chocaban se corren); la línea amarilla del pasillo pasa junto a ellos | pedido de Cristian |
| **Rack 002 (corrección 02-11 tarde)** | pegado al muro del fondo, con el frente en la línea del pilar 4: x 38,26–39,48 (slots 38,30–39,44). Pasillo de cruce al centro: x 36,20. Parantes solo en los límites de cada tramo (antes se agregaban 7 parantes repartidos que cruzaban los pallets) | foto de Cristian |
| Racks reacomodados | fila 001: 001/001 x 0,37–2,95 · 001/002–007 hasta 18,76 · 001/008–012 x 20,89–34,10. Isla (001/013–022 y 003) x 7,61–34,10. Fila 020: 600/300 x 0,37–2,95 · 020/013–009 x 4,22–17,43 · 020/008 17,51–18,76 · 020/007 20,89–22,14 · 020/006–001 hasta 38,08. Rack 002 x 37,06–38,26. Pasillo de cruce al centro: x 35,60 | plano v3 |
| **Racks 003/001–006 (4 niveles)** | 001 camilla (largo completo, solo cajas) · 002 nivel 2 largo completo, solo cajas, sobre bandeja de malla a 1,65 m · 003/004 nivel 3 desde 3,05 m · 005/006 nivel 4 desde 5,10 m **sin barra superior**. Vigas a 1,65 / 3,05 / 5,10 m. En la simulación 001 y 002 son fijas (sin pallets ni grúa); 003–006 reciben pallets | plano v3 + elevación |
| Racks 003/007–010 | sin cambios: 3 niveles, 001/002 piso, 003/004 medio, 005/006 alto (vigas 1,65 / 3,5 / 5,4) | plano v3 |
| **Camilla** | elemento propio (sin número): **una sola pieza** de 003/001/001 a 003/006/002 (x 7,61–23,47 = 15,86 m), largueros y cubierta continuos a 0,20–0,34 m, patas cortas cada 1,3 m. Encima van las cajas de la posición 001 | corrección de Cristian (antes estaba dividida por posición) |
| Ubicaciones | 256 con número, todas únicas; 60 en la fila 003. Se ignoró el 003/001/005 duplicado que quedaba suelto en la elevación | plano v3 |
| Alturas estimadas | camilla 0,34 m, vigas de 4 niveles 1,65 / 3,05 / 5,10 m y nivel 4 hasta ~6,3 m: la elevación es esquemática, falta medirlas | **sin medir** |
| No sirvió | hornear la luz del piso con `bk_estructura.py` cargado: el piso queda casi negro (k 0,11 en vez de ~10). Se hornea sin la estructura y con los pilares como cajas | prueba |
| No sirvió | el pipeline web viejo `anim.mjs` (del 25-10): borraba la caminata de la supervisora y del operador (quedaban 27 canales). Ahora `anim2.mjs` deja exactamente los 126 canales de la v22 (lista en `anim_keep_v22.json`) | foto de Cristian |
| No sirvió | el pallet `Pallet_ubicado` de la animación de video quedaba flotando dentro del rack 003/005 (a 3,5 m, entre las vigas nuevas): se quita en `strip.mjs` (la web usa los pallets de la simulación) | foto de Cristian |
| No sirvió | rehacer las jaulas con 8 filas de producto: la escena subía de 61 a 72 MB. Ahora 2 filas (las que se ven por la malla) | prueba |

### Interfaz, cámara desde arriba y pallets editables (v24, `ui.js`)
Se partió desde la v22 (paleta, piso y local **sin cambios**; lo que se rechazó de la v23 archivada fue sobre todo lo visual: paleta clara, local de contexto). Solo cambia la interfaz y la interacción.
| Ajuste | Valor | Origen / resultado |
|---|---|---|
| **Marcas del piso en "Bueno"** | eliminadas las franjas fijas de neumáticos (`fx_huellas`, opacidad 0,55: eran las marcas que se veían). Desgaste: línea única 0,07 m alfa 0,0021; giro 0,08 m alfa 0,0026; capa al 50 %; aceite 0,05; pisadas 0,012; clave nueva `bodegaDesgaste3` (borra lo acumulado). Tras 8 h simuladas el piso queda casi limpio | corrección de Cristian (apilador con ruedas de poliuretano) |
| Vista al abrir | siempre desde arriba, con vuelo de entrada desde lejos; la 1ª persona queda en la barra (tecla V). Al bajar se para donde mira la cámara o frente al pallet elegido | pedido de Cristian |
| Barra superior | panel flotante cristal oscuro `#1E293B` (alfa 0,86, desenfoque 14 px, radio 14): marca, Desde arriba / 1ª persona, buscador, reloj y velocidad, **"• Mostrar paneles" naranja `#FF6A00`**, menú ⋯ (pantalla completa, ocultar interfaz, atajos) | pedido de Cristian |
| Paneles | ocultos al partir: izquierda Simulación (indicadores, provocar, parámetros, registro), derecha Opciones (Cámara, Imagen, Herramientas). Tecla P | interfaz más simple |
| Esquinas | arriba izq.: mini tablero del turno (tránsito, pasillo, racks, pisos vacíos, riesgo); abajo der.: brújula + escala + coordenadas X/Z bajo el cursor, sobre el minimapa | — |
| Cámara | barra abajo: girar 45°, inclinar, acercar/alejar, encuadrar selección (Z), giro automático (O), seguir grúa, "Ir a" (1–7: todo, planta, pasillo 1, pasillo 2, cruce, tránsito, trastienda); brújula = norte arriba (N). La cámara ahora puede mirar a un punto en altura (MQ.y) | — |
| Mover / eliminar | clic en un pallet → jaula naranja + tarjeta (Mover M, Eliminar Supr, Escanear, Pararse aquí). Mover: destinos libres en verde (filtro Piso/Medio/Alto), fantasma verde y arco; respeta cama baja y reservas de la grúa; si no cabe en altura baja cajas. Ubicación vacía: "Poner pallet". Todo queda en el registro y se puede **Deshacer** (7 s) | pedido de Cristian |
| Búsqueda | sugerencias mientras escribes (bins ordenados, pallets PLT-, posiciones); baliza: columna de luz, 3 anillos, etiqueta que salta con distancia desde el acceso; trayectoria con flechas animadas desde el acceso por los carriles de la grúa; cámara: muestra el recorrido completo → se acerca → gira ±0,5 rad alrededor del pallet | pedido de Cristian |
| Nombres de zonas | máx. 18 px y se ocultan bajo 15 m de distancia (antes tapaban la vista cercana) | prueba |
| No sirvió | cinta de la trayectoria con cara simple (no se veía desde arriba) → doble cara; `pkill -f chrom` en las pruebas mata la propia terminal | prueba |

### Herramientas y flujo
| Ajuste | Detalle |
|---|---|
| Blender largo | proceso aparte: `blender -b archivo --python a --python b -- preview|save` (el conector se cae a los ~60 s) |
| Copiar al PC | **siempre nombre nuevo** (`_r2`, `_r3`…), `force`, y verificar md5 en el PC |
| Capturas de movimiento | CMU vía cgspeed (sin restricciones de uso) — github.com/Shriinivas/cmubvh |
| Videos de referencia | Gemini (Chrome): sirve para pose quieta; cupo bajo (2 videos) |

---

## 2. Lo que NO SIRVE (no repetir)

| Intento | Por qué falló | Qué se hizo en vez |
|---|---|---|
| Piernas desde el video de Gemini con MediaPipe **3D (world)** | comprime las rodillas → "camina como gorila" | captura CMU + IK |
| Piernas desde MediaPipe **2D** en vista lateral | MediaPipe intercambia izquierda/derecha cuando las piernas se cruzan → resbalón 24 cm | captura CMU + IK |
| Meshopt / Draco para comprimir | necesitan WebAssembly; la carga se cuelga por la política de seguridad | cuantización + webp |
| `blob:` / `data:` en la web | bloqueados; `createImageBitmap` falla | desactivar `createImageBitmap` durante la carga |
| Archivos `.glb` publicados directo | no se permiten | JSON con base64 |
| `gltf-transform prune` normal | borra UV de materiales sin textura (jaula opaca) | `prune({keepAttributes:true})` |
| Material Basic con luz horneada | perdía el dibujo de la baldosa | Standard clonado |
| Materiales transparentes en caras | dibujaba boca y ojos internos en rojo | opacos + alphaTest |
| Copiar al PC con el mismo nombre temporal | responde "guardado" sin guardar | nombre nuevo + md5 |
| Paneles de luz de 37 m | sombras estiradas | tubos individuales |
| Calidad alta EEVEE en la HD 620 | 50–160 s por cuadro | 16 muestras, sombras 0,5, 60 % resolución |
| Reintentar Gemini sin cupo | error "I'm having a hard time" | esperar renovación del cupo |
| Capturar pestañas de Chrome en segundo plano | se cuelga | una sola pestaña al frente |
| `OutlineEffect` de three.js para el contorno | no soporta mallas instanciadas (pallets y cajas) | 2.ª pasada con `overrideMaterial` propio |
| Muros cortados con material de doble cara | se ve el interior negro de muros y columnas | una sola cara en maqueta |
| Medir rendimiento en el servidor (SwiftShader) | dibuja con CPU; los ms no se parecen a una tarjeta real (ej. Caricatura salía más rápida) | medir en el PC de Cristian |
| Elevador de tijera antiguo (v1) | plataforma que parecía flotar, brazos blancos sueltos | rehecho en v18 |
| Gemini: 4.ª foto seguida | "hay mucha demanda", cambia a un modelo sin imagen | basta con 3; reintentar más tarde |
| Subir a Gemini un archivo adjunto o de outputs | la extensión solo acepta archivos del área de subidas | `device_stage_files` y subir desde `/mnt/user-data/uploads/...` |
| Vigilar un archivo del PC con Monitor | Monitor corre en la nube, no ve el PC | consultar con `device_bash` |
| `page.click` de Playwright con SwiftShader | se cuelga por cuadros muy lentos | clic por JavaScript en las pruebas |
| Escala de la tabla al reemparentar | se perdía y quedaba gigante | `Matrix.Diagonal(SC)` |
| Casco con punta | cresta en pico | cresta suave |

---

## 3. Límites conocidos (todavía abiertos)

- Sin expresiones de boca.
- Resbalón de pies de hasta 35 cm al detenerse o girar (transición caminar ↔ quieta).
- Video del operador en Gemini pendiente (cupo).
- Pendiente para la identidad: fotos proyectadas (pide permiso), interfaz completa con lenguaje de bodega (falta el panel principal), sonido y gestos reales grabados por Cristian.
- Medidas **estimadas**: altura de vigas del techo (6,62–7,30), separación de correas y ramales; con el plano v3, cuánto sobresalen los pilares 4-5-6 en el pasillo 2 (~0,5 m), altura de la camilla y de las vigas de los racks de 4 niveles. Las x salen del editor escalado a los muros (±0,3 m).
- Falta: medidas reales de la trastienda (ancho del pasillo, distancia exacta puertas–acceso, tamaño del cuarto blanco).
- Falta: FPS de Caricatura y tabla de "Probar rendimiento" en el PC (v16).
- Tarjeta Intel HD 620: techo de calidad en tiempo real. Unity/Unreal no compensan con este equipo (evaluación del 26-10-2026).

---

## 4. Historial de versiones web

| Versión | Fecha | Cambio |
|---|---|---|
| v8 | 25-10 | simulación con eventos al azar |
| v9 | 25-10 | medición del turno + prueba de luz horneada |
| v10–v11 | 25-10 | personajes con cara, parpadeo, cascos, dedos; escena por trozos (>16 MB) |
| v12–v13 | 26-10 | pose de escribir del video Gemini; tabla al costado; brazo del lápiz |
| v14 | 26-10 | piernas con CMU 07_02 + IK (resbalón mediana 2,4 cm) |
| v25 | 02-11 | plano v3: pilares 1-6 y 2-5 enfrentados, racks reacomodados, pilares de la fila 020 dentro del pasillo 2, 003/001–006 de 4 niveles, camilla de una pieza, rack 002 movido, luz del piso horneada de nuevo |
| v24 | 02-11 | abre desde arriba, barra superior #1E293B, paneles a pedido, mover/eliminar/poner pallets con deshacer, búsqueda con baliza y trayectoria, sin franjas de neumáticos (desde v22; la v23 sigue archivada) |
| v22 | 27-10 | estructura: pilares, vigas, cielo, red húmeda, recorte, rejas isla, cama baja, tapa de acero, luz decreciente en racks |
| v21 | 26-10 | maqueta principal: panel de cámara, vistas, zoom al cursor, clic-acerca con escáner, nombres de zonas, más resolución quieta, sombras; huellas de poliuretano |
| v20 | 26-10 | desgaste del piso generado por la simulación, escáner con stock flotante, modo turno con boleta vs piloto automático |
| v19 | 26-10 | paneles desplegables, solo bodega (H), pantalla completa (F), HTML independiente |
| v18 | 26-10 | trastienda con pallets, carros, transpaleta, gavetas, cámaras, extintor; elevador de tijera rehecho |
| v17 | 26-10 | entrada desde la sala: reja en el costado del acceso, trastienda, puertas de vaivén, salida de emergencia, red de incendio |
| v16 | 26-10 | prueba de rendimiento, resolución automática, Cine más liviano |
| v15 | 26-10 | vista maqueta, estilo caricatura, niveles gráficos (Básico/Bueno/Cine), sonido sintetizado, marcadores de incidentes |

## 2026-10-28 · Plano del local (contexto de la bodega)
- Nuevo artifact "Plano del Local": plano editable sobre la foto del cartel del local (logo tapado). Datos en su base (plano/actual).
- SIRVE: escala fijada con Ruta 1 = 142,27 m (Google Earth, medido por Cristian) → 9,715 px/m. Foto cubre ~167 × 89 m.
- Ruta 1 · Trastienda: 142,3 m, ancho de 1 pallet, sin cruces con clientes. Óptima pero angosta.
- Ruta 2 · Sala por pasillo 28: 141,2 m, la más usada (más ancha) pero peligrosa para clientes. Llega directo a las puertas de vaivén.
- Ambas rutas miden casi lo mismo: la diferencia es ancho/flujo/riesgo, no distancia.
- Un tráiler = 18 pallets, descarga con transpaleta, pallet por pallet → ~5,1 km a pie por tráiler.
- Vista "Local 3D": góndolas (1,83–2,13 m, módulos 1,22 m, pasillos 2,4 m supuesto), cajas, frescos, cámaras, andén con tráiler 13,6 m, bodega, rutas y descarga animada con clientes.
- SUPUESTOS (no medidos): 0,8 m/s cargado, 1,2 m/s vacío, 1 operador por ruta, frena a 1/3 con cliente a <2,4 m. Resultado ilustrativo: trastienda ~89 min, sala ~110 min por tráiler.
- NO SIRVE / POR CORREGIR: rectángulo de la bodega en el plano (sacado del dibujo del cartel, 21,8 × 14,6 m; real ~39,5 m de largo). Falta ubicarla desde las puertas de vaivén.
- PENDIENTE: tiempo real de descarga de un tráiler y n.º de personas, para calibrar.

## 2026-10-29 · v23 — vista superior principal, local como contexto, paleta clara
- SIRVE: el plano del local calza con la simulación: el final de la Ruta 2 (pasillo 28) cae en las puertas de vaivén (x −1,7; z 13,9). El plano queda girado 180° respecto de la bodega (la vista "Local" usa la orientación del cartel).
- Local dibujado como adorno: góndolas grises sin productos, cajas, frescos, cámaras, andén con tráiler y 18 pallets, rutas en el piso (Ruta 1 turquesa, Ruta 2 azul). Medidas del plano por foto (±3 m).
- Paleta: piso #F8FAFC con cuadrícula de 1,2 m, racks #1D4ED8, vigas #F97316, cartón #C19A6B/blanco/azul, máquinas (grúa, transpaleta, tijera) amarillo #FACC15. Cambio por código sobre los materiales; el .blend no se tocó.
- Interfaz: barra oscura #1E293B (Superior/1ª persona, Modo turno, Escáner, Buscar, Mostrar paneles naranja, Pantalla completa); tarjeta de turno arriba a la izquierda; paneles antiguos solo con "Mostrar paneles" (tecla H). V cambia de vista.
- Nuevo: clic en un pallet (vista superior) → tarjeta con Mover (destinos libres marcados en turquesa, valida altura, cama baja y reservas de la grúa) y Eliminar (pide confirmar). Queda en el registro.
- Nuevo: búsqueda con baliza (columna de luz, anillos, pin), trayectoria con flechas desde las puertas de la sala y cámara que gira hacia el pallet.
- OJO: la Ruta 1 en el plano entra a la trastienda por el poniente (z≈10), donde la simulación tiene muro/cuarto. Por confirmar si existe esa entrada.
- PENDIENTE: FPS en el PC de Cristian con la v23; tiempo real de descarga de un tráiler.
- Fuentes: web_fuente/v23_vista_superior.zip

## 2026-11-01 · Vuelta a v22
- NO SIRVE (a juicio de Cristian): el resultado visual de la v23 (vista superior, local de contexto, paleta clara, interfaz nueva). Se volvió a publicar la v22.
- La v23 queda archivada en web_fuente/v23_vista_superior.zip por si se rescata alguna pieza suelta (mover/eliminar pallets, búsqueda con trayectoria, alineación del plano del local con las puertas de vaivén).

## 2026-11-02 · v24 — interfaz y cámara desde arriba (sobre la v22)
- Pedido de Cristian: marcas del piso sutiles, vista desde arriba como inicio con más controles, barra oscura #1E293B con "Mostrar paneles" naranja, interfaz simple, mover y eliminar pallets con clic, búsqueda vistosa con trayectoria.
- Se construyó sobre la v22, no sobre la v23 archivada: se mantienen paleta, piso, local y estructura. Fuentes en `web_fuente\v24_interfaz\`.
- PENDIENTE: FPS en el PC de Cristian con la v24 (en el servidor no se puede medir).

## 2026-11-02 · v25 — plano v3 (corregido por Cristian)
- El plano anterior tenía pilares desfasados: ahora 1-6 y 2-5 están enfrentados y los racks se reacomodaron. Todo el modelo y la simulación salen del plano v3.
- Pilares de la fila 020 sobresalen dentro del pasillo 2 a propósito: se respetan en el modelo, la colisión y los pallets dejados en el pasillo.
- Racks 003/001–006 de 4 niveles (001 y 002 de largo completo, solo cajas); camilla de una sola pieza bajo esos 6 racks.
- PENDIENTE: medidas reales de la camilla, de las vigas de los racks de 4 niveles y de cuánto entran los pilares al pasillo 2; FPS en el PC.
- NO SIRVE: copiar al PC un .webp con la herramienta de archivos: lo vuelve a comprimir (cambia el md5). Se manda en base64 y se decodifica en el PC.

## 2026-11-02 (tarde) · v25b — correcciones de Cristian sobre la v25
- Rack 002 pegado al muro del fondo, en la línea del pilar 4; sin parantes que crucen los pallets.
- Quitado el pallet de la animación de video que quedaba dentro de otro cerca de 003/005/004.
- Devuelta la caminata y la postura de la supervisora (y del operador): el paso de animaciones del pipeline las estaba borrando.
- Luz del piso horneada otra vez con el rack 002 en su lugar.
- PUNTO DE RECUERDO: `PUNTO_DE_RECUERDO_2026-11-02.md` + respaldo completo en `respaldos\2026-11-02_v25b_punto_de_recuerdo\`.

## 2026-11-02 (noche) · Operación — PASO 1: parámetros, malla anónima y jornadas
Archivos en `operacion\paso1\`: `parametros_operacion.json` (cada valor con etiqueta), `malla_anonima_sep2026.csv` (solo IDs), `malla.js` (cargador + catálogo de jornadas, semilla visible), `test_paso1.js` (39 pruebas, todas pasan), `orden_colapso.png` (orden de llenado sobre el plano v3).
- [MALLA] La malla anónima reproduce las cifras del prompt v6: 26 días operativos; M 1–4 (prom. 2,6); T 1–4 (prom. 2,5); N = 1 las 26 noches; 1 sola en la mañana 13-sep y 23-sep; 1 sola en la tarde 30-sep; domingos M 1/4/3/4 y T 2/3/2/3; racha máx. 6 (OP1 y JEFE); 4 cambios T→M.
- [DERIVADO] Catálogo de jornadas cuadra: semanas de 5 y 6 días = 42 h; OP5 = 30 h; part-time = 18 h.
- [DICHO 02-11] Conteos del plano v3: 76 piso, 76 medio, 92 alto, 12 nivel 4 (reemplaza 82/82/92 del prompt).
- [DICHO 02-11] Tránsito = 16. Línea del pilar 6 (plano v3, fila 020, x 3,25–4,12): 3 pallets partiendo del pilar hacia el pasillo 1, por la franja verde. [CONFIRMAR] umbral de desborde 19 (el prompt decía 18).
- [DICHO 02-11] Nuevo orden de colapso: pasillo 2 desde el fondo hacia el principio → cruce → pasillo 1 (001/001–001/012 hasta el fondo del cruce) → líneas libres. [CONFIRMAR] sentido del pasillo 1 (se puso desde el fondo).
- [SUPUESTO] Huella del pallet 1,2 × 1,0 m con 0,1 m entre pallets → pasillo 2: 25; cruce: 12; pasillo 1: 27; líneas libres: 96. [PENDIENTE] contar los reales.
- [DICHO 02-11] Rack 003: posiciones 001/002 de 003/001–006 a mano; el resto con grúa (piso con transpaleta).
- [DICHO 02-11] Mientras no exista el plano del andén, los pallets entran desde la sala por las puertas de vaivén.
- [SUPUESTO] Tarde en semanas de 5 días 12:30–22:00; semana con feriado = larga; días con hora menos sorteados con semilla 20260907; eléctrica 4 min de ida (solo para E8); grúa 6 min por operación (solo ocupa el equipo); demanda 20 min e-commerce / 15 min externos (se recalibra en el paso 2).
- Anonimato: el CSV y el JSON no llevan nombres; las personas se asignan por posición de fila (mismo orden que el Excel).

## 2026-11-02 (noche) · Correcciones al paso 1 (medidas en terreno)
- [DICHO 02-11] Tránsito = 16 EN TOTAL contando la línea del pilar 6, pegada al resto. Modelado: 3 columnas × 4 filas (1–12) + línea del pilar 6 de 4 (13–16, salida estrecha). Desde el 17 se desborda. Las 16 celdas del plano v3 no son huellas de pallet.
- [DICHO 02-11] Zona a evitar frente a la puerta de acceso (filas 2 y 3 del pasillo 1, x 0,25–3,0): no se dejan pallets.
- [DICHO 02-11] Zonas verdes donde sí van pallets: fondo del pasillo 1 junto al cruce (6, se suma al cruce) y cabecera de la isla delante de 001/022 y 003/001 (4; [SUPUESTO] 2×2 con huella girada, deja ~0,9 m de paso junto a la línea del pilar 6).
- [DICHO 02-11] El pasillo 2 también llega al muro del fondo: 1 pallet entre el fin del rack 002 y el pilar 4 (P2-00, primero en llenarse; cabe justo según el plano).
- Archivos: `operacion\paso1\*_v2.*` (los v1 quedan como estaban).

## 2026-11-02 (noche) · Operación — PASO 2: motor determinista
Archivos en `operacion\paso2\`: `motor.js` (motor, sin IA, paso de 1 minuto), `test_motor.js` + `test_motor_salida.txt` (26 pruebas, todas pasan), `calibracion.json`.
- Prioridades [DICHO]: demanda → camión → (reingreso de noche) → salida a sala desde las 21:00 [SUPUESTO: antes que procesar] → procesar.
- Capacidad de procesar = por turno, de arriba hacia abajo [DICHO 3 / 1 / 0]: carga = solicitudes que necesitan a la bodega en la mañana por persona. Referencias [SUPUESTO]: tranquilo (3 personas, 10 externos, 6 e-commerce) = 3; cargado (2 personas, 10 externos, 12 e-commerce) = 1; 0 con 1 persona o carga ≥ 1,5 veces más allá del cargado. Nochero: 4 en una noche normal con 13 reingresos.
- NO SIRVIÓ: calibrar la duración de una solicitud por "minutos libres". Con 6–12 e-commerce y 10 externos no hay duración que baje el rendimiento a 1 por persona (probado hasta 200 min por solicitud). Se cambió a la capacidad por turno que baja con la carga (lo que pide la regla 7).
- Prueba de coherencia (sección 8) REPRODUCIDA: con 3 por persona se acumulan 10,5 pallets/día (esperado 8–11); con 1 por persona, 14,0/día (esperado 14–15); el colapso aparece en la primera semana.
- [CONFIRMAR] Si la tarde procesara igual que la mañana, la acumulación baja a ~0,2/día y NO hay colapso estructural. Por eso la tarde no procesa por defecto (factor 0).
- Septiembre completo con la malla real: el piso llega a ~157–175 pallets (bodega bloqueada), 7,3 pallets movidos por pick, on-time 88,5 % con Fillrate 95,4 % (contraste E10).
- Huecos de cobertura que salen de la malla y del catálogo: 06:30–07:30 cuando el nochero tiene hora menos; 21:00–22:00 cuando toda la tarde sale a las 21:00.
- [SUPUESTO] nuevos: salida a sala 3+3 min; vuelven de sala 4 h después; reingreso 3+3 min; mover un pallet que tapa 5 min; plazo e-commerce 120 min; colación a mitad del turno; 20 min por pallet procesado (solo ocupa y anima, no decide cuántos); grúa 6 min por operación; un pallet en el pasillo a la altura de una posición la tapa; una columna con las 3 filas ocupadas obliga a mover 1 pallet para pasar.

## 2026-11-02 (noche) · Ajustes al motor tras la respuesta sobre la tarde
- [DICHO 02-11] La tarde SÍ procesa pallets si la demanda es baja y hay tiempo. Modelado: la tarde acumula capacidad solo en sus minutos libres (sin camión, demanda ni salida a sala), con la misma curva 3 / 1 / 0 según el e-commerce por persona de la tarde.
- Resultado: con dotación máxima habitual (3 M + 3 T) la acumulación baja a ~5 pallets/día (sigue habiendo colapso, más lento). Con la malla real de septiembre la bodega vuelve a llenarse (≈130–157 pallets en piso al final del mes).
- NO SIRVIÓ: dejar que la tarde procesara los pallets del camión del día: se "comía" los que debían salir a sala a las 21:00 (salían 16 en vez de 18). Ahora los primeros 18 del camión quedan reservados para la salida.
- [SUPUESTO] Orden de procesar: primero la línea del pilar 6 (libera la salida estrecha), luego el bloque del tránsito, luego el desborde del último al primero. La salida a sala saca primero los del día que quedaron en el desborde.

## 2026-11-02 (noche) · v26 — PASO 3: panel de dotación y línea de tiempo
- Botón "Dotación" en la barra superior. Panel con: día (malla de septiembre), semilla visible, cargar otra malla en CSV (si trae nombres, se cambian por P1, P2…), restablecer día, día vacío (casos hipotéticos).
- Personas por turno con entrada y salida editables, "hora menos", quitar y agregar (de la malla o persona hipotética EXTRA). Lo editado queda guardado en el navegador.
- Línea de tiempo de 06:00 a 06:00: turno de cada persona, colación, lo que hace según el motor (traslado, demanda, procesar, sala, reingreso), fila de presentes con los huecos sin nadie en rojo, llegada del camión y salida de las 21:00.
- Resumen del día con etiquetas de origen; mini plano cenital con cada persona y su tarea en la hora elegida (clic o arrastre en la línea de tiempo, o "Recorrer" a 1 hora por segundo) y los pallets en el piso (café = tránsito, rojo = desborde).
- El motor corre en el navegador desde el 07-sep hasta el día elegido (≈0,1–1 s).
- Fuentes: `web_fuente\v26_dotacion\` (dot.js, malla.js, motor.js, op_datos.js). Respaldo previo: `respaldos\2026-11-02_v25b_antes_dotacion\`.
- PENDIENTE: ver las personas y su tarea en la escena 3D (paso 4); probar en el PC y el celular de Cristian.

## 2026-11-02 (noche) · v27 — PASO 4: la operación en la bodega 3D
- "Ver en 3D" en el panel de Dotación (o el botón Dotación del tablero) muestra el día elegido en la escena, desde la hora marcada. Velocidades ×1, ×10, ×60 (pedidas) y ×300 (agregada para recorrer rápido). Al terminar el día pasa solo al siguiente.
- Trabajadores = copias del operador del modelo (mismo esqueleto, 1,74 m), con chaleco del color del turno (M amarillo, T naranjo, N lila) y su ID encima (tamaño fijo en pantalla). Animación por código, sin Blender: caminar, empujar la transpaleta, bombear para subir o bajar, desarmar un pallet (se inclina y toma cajas) y estar parado. Se descartó hacer clips en Blender por ahora: copiar el esqueleto y animarlo por código no agrega peso al archivo y sigue al motor minuto a minuto. Blender queda para el video final.
- Todo sale del registro del motor: traslado desde el andén (la persona sale por la puerta de la sala, el viaje de 147,9 m se cuenta en el tablero y entra empujando el pallet hasta su lugar justo a la hora del motor), salida a sala, reingreso, pedidos (va a la posición) y procesar (el pallet se desarma capa por capa).
- 3 transpaletas manuales que aparecen con quien las usa; la eléctrica estacionada con el aviso "fuera de servicio". La Raymond va al punto de trabajo y sube el mástil durante sus 6 min; sin trabajo se estaciona en el cruce trasero. La BT Staxio es un ícono (no está modelada).
- Pallets en el piso con cajas en capas; el desborde se marca en rojo en el piso (pasillo 2, cruce, pasillo 1, líneas libres). Tablero: etapa de colapso, tránsito /16 y salida estrecha, pallets en el piso, personas en la bodega, camión (pallets por traer), quién está en el andén, pallets movidos para llegar a una posición, kilos movidos a mano, e-commerce atrasados y la nota fija "Indicador de exposición, no medición de personas".
- Al entrar se detiene la simulación antigua y se vacían su tránsito y pasillos (ahora manda el motor); al salir se reinicia como antes.
- [SUPUESTO visual] Velocidad caminando 1,2 m/s, empujando cargado 0,8 m/s, vacío 1,0 m/s; la persona va 1,85 m detrás del centro del pallet; lugares de espera de cada persona frente a la isla; transpaletas estacionadas frente a 001/002 (lugar real PENDIENTE).
- NO SIRVIÓ: copiar el operador con la pose de enlace del esqueleto (skeleton.pose()): quedaba de 14 m de alto. Se copia con la animación detenida, en su pose de reposo de pie.
- NO SIRVIÓ: dejar la Raymond donde la tenía la simulación antigua: quedaba en medio del pasillo 2 y los trabajadores la atravesaban.
- Probado: un día completo cuadro a cuadro sin errores (peor cuadro 15 ms en el servidor de pruebas), paso de un día al siguiente, capturas de cerca y desde arriba. PENDIENTE: FPS en el PC y el celular de Cristian.
- Fuentes: `web_fuente\v27_operacion3d\` (op3d.js nuevo). Respaldo previo: `respaldos\2026-11-02_v26_antes_operacion3d\`.

## 2026-11-03 (madrugada) · v28 — tiempos medidos, pallets superpuestos, trabajadores de Blender y BT Staxio en 3D
- [DICHO 03-11] Traslado medido: 2 min 30 s de ida con carga y 2 min de vuelta (antes 5–6). Cuando llega el camión, todo el turno va a descargar y la demanda espera. Si faltan transpaletas se consigue otra de otra sección (sin tope).
- Prueba a mano: 1 persona y 18 pallets = 79 min; 3 personas = 25 min; 3 personas y 36 pallets = 52 min; 4 personas y 36 = 38,5 min. 30 pruebas del motor correctas.
- [SUPUESTO] Eléctrica: 2,0 min de ida y 1,6 de vuelta (solo para comparar en E8).
- BUG corregido: pallets "apilados" en el tránsito. Era el pallet que se desarmaba seguía dibujado y el motor ya había dejado otro en su lugar (237 veces en 10 días). Ahora el pallet ocupa su lugar hasta terminar de desarmarlo y el de la salida a sala hasta que sale por la puerta: 0 superposiciones.
- NO SIRVIÓ: la animación por código de los trabajadores (se veía de robot). Reemplazada por:
  - 8 trabajadores en MPFB 2 (blender\personajes\pj_build.py): 1,61–1,68 m, polera negra, pantalón cargo (verde, caqui, gris o negro, con bolsillos laterales), casco blanco, zapatos oscuros; distintas contexturas, edades y rasgos. Sin nombres: OP1, OP2… usan siempre la misma variante.
  - 8 animaciones de Mixamo (cuenta gratis de Cristian): caminar, parado, empujar carga pesada, tirar, recoger, mirar alrededor, palanca (bombear la transpaleta) y llevar caja. Pasadas al esqueleto de MPFB con pj_anim.py (alineando la pose de reposo en T del X Bot con la pose en A de MPFB).
  - En la web la persona se ubica para que sus manos queden en el timón de la transpaleta (la inclinación del timón sigue la altura de las manos).
- NO SIRVIÓ (en el camino): agregar la ropa antes del esqueleto (la ropa no se movía con el cuerpo); clasificar polera/pantalón por color (las roturas del jeans quedaban como manchas negras) → se clasifica por geometría y se suaviza la textura (sin estampados ni logos).
- BT Staxio en 3D (blender\personajes\pj_bt.py), según las fotos: apiladora de timón, carcasa naranja, base y batería negras, mástil triple que sube por etapas, horquillas y piernas de apoyo. Sin logos ni textos. La persona camina detrás del timón; estacionada frente a 001/003 [SUPUESTO].
- Peso: la página publicada carga la bodega primero y después 2 archivos de personas y máquinas (9,3 y 8,4 MB). El HTML independiente pesa 29 MB (sin límite en el PC).
- Fuentes: web_fuente\v28_trabajadores\ y blender\personajes\. Respaldo previo: respaldos\2026-11-03_v27_antes_trabajadores\.
- PENDIENTE: ver fluidez en el PC y el celular con 6–8 trabajadores animados; lugar real donde se estacionan las transpaletas y la BT.

## 2026-11-03 · v29 — tirar de la transpaleta, límites físicos y caras corregidas (reporte de Cristian con fotos)
- Caras deformadas (manchas rojas en boca y ojos): los materiales de los personajes venían con mezcla transparente. Ahora todos opacos; recorte alfa solo en ojos, cejas, pestañas, pelo y ropa (sin el recorte el cuello de la polera mostraba manchas).
- La transpaleta se TIRA como en la bodega real: la persona va adelante caminando, con el brazo derecho atrás en el timón (cinemática inversa simple) y el pallet detrás. Solo en el último tramo gira el timón y empuja el pallet a su lugar; al sacar un pallet de su lugar lo saca empujando y luego se pone adelante.
- Límites físicos y lógica humana: nadie atraviesa pallets del piso, la Raymond, la BT ni el pallet que lleva otro; las personas se separan entre sí; cada una camina por su propio carril (centro, izquierda o derecha del pasillo) para no ir en fila una dentro de otra; en primera persona los trabajadores tampoco te atraviesan; la supervisora se corre al costado cuando se acerca alguien.
- La Raymond se estaciona donde no hay pallets en el piso y al trabajar se corre por el pasillo si la posición frente al rack está tapada.
- NO SIRVIÓ: un comentario // dentro de una línea de código compacta dejó la página sin funcionar (se usó /* */).
- PENDIENTE: ver en el PC si la persona tirando se ve natural; ajustar la distancia del timón si la mano no llega.

## v30 — 2026-11-03 — Supervisora estable, manos en el timón, actividades sin tarea y puertas de vaivén
Respaldo previo: respaldos/2026-11-03_v29_antes_v30. Fuentes: web_fuente/v30_puertas_actividades.
- Supervisora: ya no parpadea ni salta. Se mete una sola vez en un grupo propio y el desvío para dar paso se suaviza en ese grupo; la animación original sigue moviendo a la persona por dentro.
- NO SIRVIÓ (v29): reponer la posición de la supervisora en cada cuadro chocaba con su propia animación y causaba el parpadeo.
- Empujar la transpaleta: ahora camina con las dos manos en el timón (cinemática inversa en ambos brazos), parado más atrás (1,9 m del centro del pallet) y con el timón más inclinado.
- NO SIRVIÓ (v29): la animación "empujar" de Mixamo empuja con el cuerpo y dejaba las manos sueltas, parecía empujar con el estómago.
- Sin trabajadores quietos: en los tiempos sin tarea cada uno (con semilla propia, repetible) alterna recorrer un pasillo mirando los racks, inspeccionar una ubicación o un pallet, o conversar con quien esté cerca mirándolo. [SUPUESTO visual: no cambia ningún cálculo del motor]
- Entrada y salida de pallets: los traslados a sala y los reingresos empiezan y terminan en la sala, pasando por la trastienda y la puerta de vaivén; las puertas se abren también para los trabajadores. [SUPUESTO: recorrido por el centro de la trastienda]
- Prueba: 720 cuadros con todas las velocidades, 0 errores, peor cuadro 23 ms.
- PENDIENTE: confirmar en el PC que las manos tocan el timón; el cuello de la polera aún muestra pequeñas manchas claras; el casco se ve algo alto.

## v31 — 2026-11-03 — Revisión de todas las animaciones
Respaldo previo: respaldos/2026-11-03_v30_antes_v31. Fuentes: web_fuente/v31_animaciones.
- Causa del trabajador sin postura (captura del teléfono, 21:31): era el muñeco antiguo de reserva. La operación se abrió antes de que terminaran de cargar los personajes nuevos (unos 17 MB) y esos trabajadores quedaron con el muñeco viejo para siempre. Ahora: los personajes cargan en paralelo con la escena; mientras cargan, el tablero dice "cargando modelos…" y no se muestra el muñeco viejo; si ya había uno, se reemplaza; si la carga falla se reintenta 2 veces y el tablero lo avisa.
- Brazos: cinemática inversa real de dos huesos (hombro, codo y muñeca). Antes el codo quedaba congelado en una pose cualquiera de la animación y la mano no llegaba (error medido de 9 a 35 cm). Ahora el error medido es 0 cm al tirar, al empujar, al bombear y con la BT.
- Tirar: la mano derecha va a la barra (antes apuntaba al lado izquierdo); timón algo más alto y persona 4 cm más cerca.
- Bombear: el timón sigue a las manos de la animación y las manos quedan en la barra; persona más cerca del pallet.
- Giro al final (de tirar a empujar) y al salir de un lugar: la persona rodea la transpaleta por el costado (antes la atravesaba) y gira el cuerpo de forma gradual (antes se daba vuelta de golpe).
- En las esquinas el cuerpo gira de a poco al caminar.
- BT Staxio: ya no aparece sola en el pasillo. La persona la va a buscar a su estacionamiento [SUPUESTO], la lleva tirando del timón (timón abajo), gira y entra de frente al rack, sube el mástil con las dos manos en las manillas y la devuelve. El timón original quedaba a 1,70 m de alto y la persona dentro de él: corregido.
- Raymond: ya no salta de un lugar a otro; conduce por los pasillos a 1,5 m/s [SUPUESTO visual] y solo sube la carga al llegar. La persona que la usa va arriba (no se duplica a pie).
- Caminatas cortas (menos de 1 s) no se dibujaban y la persona saltaba 0,4–0,7 m: corregido (revisados 6 días: 0 huecos, 0 saltos, 0 velocidades imposibles).
- Pies: las animaciones dejaban la planta 4 cm bajo el piso: subida.
- Sin trabajadores quietos: quien espera sin nadie cerca mira alrededor; al final del turno sigue recorriendo hasta salir. Personas quietas de pie: de 33 % a 8 % de las muestras, y ese 8 % son conversaciones de a dos.
- Transpaletas estacionadas con el timón vertical (antes el timón quedaba en el suelo, donde esperan las personas).
- Ropa: se eliminaron las manchas claras del cuello y las costuras (líneas claras del mapa de textura y piel que asomaba al moverse).
- Tablero: el texto del andén decía "5–6 min por viaje"; ahora toma los tiempos medidos (ida 2,5 min, vuelta 2 min).
- NO SIRVIÓ: bajar el casco 2,5 cm hacía asomar el pelo por arriba; se dejó igual.
- Prueba: 720 cuadros a ×1, ×10, ×60 y ×300, 0 errores, peor cuadro 15 ms; día completo muestreado cada 3 min.
- PENDIENTE: no hay animación de "conversar" (gestos); las conversaciones usan la pose de pie y mirar alrededor. Se puede bajar "Talking" de Mixamo con permiso.

## v32 — 2026-11-05 — Sala de ventas alrededor de la bodega
Respaldo: respaldos/2026-11-05_v31_antes_v32. Fuentes: web_fuente/v32_sala (sala.js, sala_datos.json, parse.py, layout.json). Utilería de Blender: blender/sala/sala_assets.py → out_sala (atlas de productos + muebles).
- Plano PDF de la tienda leído en vectores: 1.403 módulos (góndolas, vitrinas, islas, mesas de fruta, bins, pallets), cada uno con su temática según los rótulos del plano (abarrotes, bebidas, licores, lácteos, carnes, congelados, frutas, panadería, limpieza, papeles, perfumería, bebé, mascotas, electro, hogar, vestuario, juguetes, librería, ferretería).
- Escala: 1 módulo de góndola = 1,25 m [SUPUESTO deducido, calza con los 40 m de la bodega, el vano de las puertas de vaivén y la imagen satelital]. Alto de sala 6,8 m [SUPUESTO]. Sala de unos 95 × 56 m [ESTIMADO por la escala].
- La bodega queda en el borde sur de la sala, como en el rectángulo amarillo; las puertas de vaivén calzan con el vano del plano.
- Productos genéricos sin marcas (atlas hecho en Blender), letreros colgantes por sección, cajas, carros, pilares, luminarias, sala bien iluminada.
- Corregido en la revisión: las góndolas de muro del anexo de vinos miraban al muro (se veía un muro negro); ahora se dan vuelta solas si su frente queda fuera de la sala. Las tapas de los productos estiraban el dibujo; ahora son de color sólido.
- Botón "Sala" en la fila de efectos para ocultarla en el teléfono si va lento (se recuerda en el navegador).
- PENDIENTE: medir el alto real de la sala y confirmar la escala con una medida (por ejemplo, el largo de un pasillo). Rendimiento en teléfono sin medir.

## v33 — 2026-11-05 — Techo, muralla y piso de la sala
- Techo de la sala a la misma altura que el de la bodega (se lee del modelo: 7,4 m).
- Muralla gris entre la sala y la bodega (antes blanca).
- Vista desde arriba: los muros de la sala se recortan igual que los de la bodega y el cielo se oculta.
- Piso de la sala: la misma baldosa de la bodega, más clara, limpia y con brillo; la junta ya no queda negra.

## v34 — 2026-11-05 — Sala abierta en la vista desde arriba
- Falla de v33 (captura del teléfono): si la página abría ya en "Desde arriba", la sala terminaba de cargar después y quedaba con techo y muros completos (bloque blanco). Ahora la sala revisa la vista sola cada 0,3 s: desde arriba oculta cielo y luminarias y corta sus muros a 2,4 m, igual que la bodega. Probado abriendo en "Desde arriba" antes de que cargue la sala.

## v35 — 2026-11-06 — Bugs de la operación (lista de Cristian)
- 1 Trabajadores dentro de pallets: si un pallet está al medio del tránsito, la persona se para en el lugar libre más cercano (anillos de 15 cm, sin pallet, rack ni muro). Prueba de 17 h en dos días: 0 cuadros con una persona dentro de una carga.
- 2 Timón: ahora gira a los lados hacia la persona (dirige como las ruedas reales) y se inclina según la distancia; la transpaleta dobla en curva (rumbo por cuerda ±0,55 m) y no gira 90° de golpe. Si el timón queda a la izquierda, lo toma con la mano izquierda. Error de manos >5 cm bajó de 13 % a 6 % (09-07); quedan errores breves al rodear la transpaleta.
- 4 Resolución: antes subía al soltar la cámara y bajaba al moverla (eso se veía como "baja sola" y hacía parpadear las sombras al rehacer los buffers). Ahora se decide una vez tras 6 s de medición; la automática baja solo tras 6 s seguidos bajo la meta y sube solo tras 10 s muy sobre ella. La sombra ya no se rehace dos veces en Cine. PARPADEO: POR CONFIRMAR en el teléfono/PC (no se puede ver desde la prueba automática).
- 5 Pallets que desaparecían: al desarmar, clasificar y binear, el pallet se esfumaba al final. Ahora la Raymond va al pallet, lo levanta y lo sube al bin; la BT lo toma del piso con su persona y lo sube. Lo que queda tras separar (~1/3) es lo que se binea. Prueba: 0 desapariciones sin evento del motor (antes 5 en 09-08).
- 6 Vida propia: cada persona tiene ritmo, velocidad (±10 %), estatura (±3,5 %), postura y fase de animación propias; al esperar usa escáner de mano, mira, se estira o cambia el peso; JEFE supervisa mirando al más cercano; al conversar uno gesticula y el otro asiente, por turnos. Al desarmar: toma una caja, gira, la deja en rumas desordenadas a los costados (hasta 4 rumas de 8) y vuelve; las cajas quedan 8 min y luego se llevan a la sala [SUPUESTO visual].
- 3 Más controles de cámara: queda para la etapa de cámaras (GSAP), no es un bug.
- Lo que NO resultó: elegir mano izquierda/derecha con el eje invertido (corregido en la misma versión).

## v36 — 2026-11-07 — Escáner y Raymond
- Escáner: ahora va en la palma, alineado con la mano (hueso muñeca→dedo medio) y los dedos se cierran sobre él; antes quedaba centrado en la muñeca y la atravesaba. Visual POR CONFIRMAR.
- Raymond trabada: recalculaba su ruta cada cuadro y en algunos puntos oscilaba sin avanzar (caso 08-09 10:13, quedó a 1 m del pallet todo el tiempo). Ahora la ruta queda fija por destino. Prueba 08-09 de 08:00 a 21:00 a paso real: 3 de 3 pallets recogidos a tiempo. Respaldo: si no llega al 60% del tiempo, igual toma el pallet.

## v37 — 2026-11-07 — Límites de la sala y detalles de las fotos
- Línea 1: la sala ahora parte exactamente en el muro exterior de la bodega (x = 39,82; antes 41,1, quedaba 1,3 m afuera). Escala del plano recalculada con dos anclas medidas: Línea 1 y centro de las puertas de vaivén (K 0,219 → 0,2124 m/pt; 1 módulo ≈ 1,21 m, sigue SUPUESTO).
- Línea de separación: muro de 5 cm pegado al muro norte de la nave (z 12,03–12,08); antes había 1,2 m de vacío. Frente a la trastienda el muro sigue el frente del modelo (z 13,70) con las puertas: queda un escalón de 1,6 m en x = 0 — PENDIENTE confirmar si en la realidad la trastienda está en la misma línea.
- Piso de la sala: granito/terrazo gris moteado (fotos), juntas cada 1,2 m [SUPUESTO]; vestuario con piso laminado gris tipo madera.
- Góndolas blancas/gris claro; vinos con muebles negros. Papeles en estantería alta (3,6 m SUPUESTO).
- Muros: panel blanco abajo, franja azul (2,6–3,1 m) y revestimiento pardo arriba [alturas SUPUESTO]. Pilares blancos.
- Cielo: losa metálica parda, tiras LED lineales continuas, ductos blancos y cañería roja de rociadores. Zona de vinos: cielo falso blanco a 3,6 m [SUPUESTO] con focos redondos y franja roja en los muros.
- No se usaron fotos como textura (marcas). Videos del camión: no procesados aún.

## v38 — 2026-11-07 — Línea recta, rack continuo, zonas en detalle
- Trastienda: su frente y las puertas de vaivén pasan a la línea recta (z 12,03), igual que la nave (Cristian: "es recta, no sobresale"). Últimos 40 cm movidos 1,62 m; franja 9,5–13,25 comprimida (cuarto 2,5 m de fondo) [SUPUESTO]. Rutas y choques de la trastienda ajustados (TR.zs 11,78).
- Rack metálico continuo de la Línea 1 al marco de la puerta (~40 m, 15 vanos de ~2,7 m, alto 4,2 m, fondo 1,1 m) [SUPUESTO por foto]: montantes perforados, diagonales, vigas, malla; papeles con pallets de madera y fardos genéricos (5 colores, extremos con rollos, plástico brillante); muebles con cajas planas kraft y muebles exhibidos (cómoda, velador, repisa). Sin pallets delante de los muebles.
- Vinos: ~5.000 botellas 3D (vino y destilado) con vidrio reflectante, etiqueta y cápsula, en muebles negros y vitrinas; precios rojos colgantes genéricos.
- Sombras reales en esas zonas: sombra del sol ampliada a toda la zona y mapa 2048/4096.
- Piso laminado solo en el bloque principal de vestuario.
- Prueba de operación 08-09: sin errores, 0 personas dentro de cargas, 0 desapariciones.

## v39 — 2026-11-07 — Zonas según fotos (no según plano)
- Rack metálico solo en papeles (Línea 1 → inicio de muebles). Corrección de Cristian: los muebles no van en rack.
- Muebles (fotos): estantería metálica gris baja (1,15 m) con malla y cajas planas de productos genéricos; mesón de madera con exhibición (pisos-puff de animal, organizadores de cubos, repisas); panel blanco ranurado con divisiones y cabezales negros; franja azul "Encuentra más muebles y decoración" y letrero "Muebles"; clóset de madera junto a papeles; cajas de futón apoyadas. Sin pallets.
- Zona contigua a la puerta (fotos): reemplaza los pallets del plano por exhibición de carbón: 3 pallets con sacos apilados (café y negros con film), sacos caídos, panel negro con letrero "CARBÓN", letrero colgante, baranda de acero y robot de limpieza junto a la puerta.
- Muro de vinos que faltaba: el bolsillo al oeste del cuarto (x -10,25 a -7,65, z 5,25 a 12) pasa a ser sala; estantería negra de muro de 7 niveles con botellas y cabezales. El muro oeste de la trastienda ahora llega solo al ala sur [SUPUESTO ubicación exacta].
- Vinos (fotos): cabeceras con estuches (verde/negro/blanco), carteles rojos "Precio rebajado" en postes sobre cabeceras, cabezales negros con texto genérico en estanterías; franja roja corregida (quedaba por fuera del muro); cielo bajo termina en z 15,4.

## v40 — 2026-11-07 — Puertas de doble vaivén y auditoría interna
- Vano de las puertas en el muro de la sala = ancho real de las dos hojas (x -2,80 a -0,60); antes era 25 cm más angosto y las hojas chocaban con el muro al abrir hacia la sala. Espacio libre de 1 m junto a la puerta (muebles empiezan más lejos; robot y baranda corridos).
- Auditoría (entorno virtual): 0 errores de página/consola; operación 08-09 sin personas dentro de cargas ni pallets perdidos; vistas en 1ª persona y desde arriba revisadas.
- Bugs hallados y corregidos: cortina de PVC y aviso amarillo de la trastienda quedaban en la sala (se cargan después del ajuste de la línea): ahora se reubican al aparecer. Carteles rojos y letrero de carbón se leían al revés por detrás: ahora tienen dos caras. Letrero "Muebles" tapaba la franja azul. Inicio en 1ª persona quedaba fuera de la trastienda nueva.
- Mejoras visuales: sombra de contacto pintada bajo góndolas, rack, muebles, carbón y muro de vinos; piso de granito con menos brillo propio para que se lea el moteado.
- Pendiente: ubicación real de los pasillos de vinos (fotos no permiten medir); vitrinas de frío y cabecera amarilla aún simples; FPS en teléfono por confirmar.

## v41 — 2026-11-07 — Texturas reales CC0 (ambientCG)
- Piso de la sala: granito/terrazo real (Terrazzo005, 2K) con relieve (normal) y brillo irregular (roughness), junta cada 1,2 m.
- Chapa ondulada real (CorrugatedSteel009) en la parte alta de los muros, teñida parda como en las fotos.
- Cartón real (Cardboard004) en cajas de sobrestock y cajas planas; madera real (Wood094) en pallets, mesón, organizadores y clóset, con relieve.
- Licencia: CC0 (dominio público), sin atribución obligatoria. Fuente: ambientcg.com. Copia de las texturas en web_fuente/v41_texturas/texturas_ambientCG.
- Peso: +2,2 MB. Sin errores de página en la prueba.
- Pendiente: modelos de Sketchfab (vitrinas de frío, carros) requieren cuenta de Sketchfab para descargar; revisar licencia modelo a modelo.

## v42 — 2026-11-07 — Modelos de Sketchfab (CC BY 4.0)
- Vitrinas de frío con 6 puertas de vidrio ("Beverage Coolers", jimbogies): solo puertas, marco y repisas (sin sala ni letrero); marco negro, interior iluminado, botellas propias en 5 niveles; en el muro oeste del anexo de vinos (foto "Zona cooler"), reemplaza las 2 vitrinas simples del plano.
- Carro metálico ("Metal Shopping Cart", Codanum_): reemplaza los 17 carros simples (1,0 m de alto SUPUESTO); texturas 2K webp.
- Créditos CC BY visibles abajo a la izquierda de la página (requisito de la licencia).
- Descargas: dos archivos de 1,7 KB fallidos quedaron en Descargas (sk_vitrinas_frio_jimbogies.glb, sk_carro_codanum.glb): se pueden borrar. Los buenos: beverage_coolers.glb y metal_shopping_cart.glb.
- Personajes: los gratis de Sketchfab son escaneos estáticos sin esqueleto; se mantienen los MPFB + Mixamo.

## 2026-11-07 — v42 descartada
- Cristian: los modelos de Sketchfab no marcan gran diferencia y los créditos en pantalla sobran. Se vuelve a la v41 (copia de la v42 en respaldos/2026-11-07_v42_descartada).

## v43 — 2026-11-07 — Trastienda, cámaras, recepción y patio (sin planos)
- Fuente: fotos y 4 videos de la carpeta "Trastienda Recepc" + mapa de riesgos (ruta amarilla). Todas las medidas son SUPUESTO calzadas a la bodega y la sala.
- Ruta: puertas de la bodega → pasillo sur (z 0–4,8, detrás del anexo de vinos; muro blanco con zócalo gris 1 m; racks de vigas naranjas con cajas contra el muro exterior; cinta amarilla/negra) → pasillo este (x −55,9 a −60,9, detrás de las cámaras) → recepción (x −52 a −68, z 47,5–66,5).
- El muro oeste de la trastienda se abrió al pasillo (queda solo la esquina).
- Cámaras de frío de panel blanco 3,2 m con puerta metálica, evaporador y letrero: merma, carnicería, fiambrería (pasillo sur); lácteos, panadería, frutas (pasillo este) [nombres y orden SUPUESTO salvo merma/carnicería/panadería].
- Recepción: piso de concreto, techo de cerchas blancas a 5 m, oficina con ventana de atención y mesón, 2 andenes con portón enrollable (uno abierto con cortina PVC), nivelador, topes, borde amarillo, pallets envueltos esperando; jaula de malla al final del pasillo.
- Patio hundido 1,2 m bajo el andén (asfalto real CC0): muelle, rampa peatonal con baranda, camión genérico en el andén 1, torres de pallets azules/rojos/madera, bandejas plásticas, contenedor verde sin marca, focos en el muro, árboles; muros exteriores de chapa ondulada gris oscura (blancos por dentro). El terreno se recorta sobre el patio.
- Vista desde arriba: ahora se puede desplazar hasta la recepción y el patio.
- Pendiente: medidas reales (largo de pasillos, tamaño de recepción, separación de andenes, desnivel del andén); orientación real de los andenes; rutas de los trabajadores hacia el andén por el pasillo nuevo.

## v44 — 2026-11-07 — Detalles de la trastienda según videos
- Pilares de hormigón 0,6 m en la línea de racks (cada 8 m [SUPUESTO]) y bolardos de acero junto a cada puerta de cámara.
- Cámaras: panel blanco 3 m, zócalo de chapa diamante 0,5 m, baranda amarilla sobre el techo, puerta corredera frigorífica entreabierta (riel, manilla vertical, burlete negro) con cortina de PVC.
- Puerta de vaivén de la trastienda a la sala (doble hoja gris con ventana y zócalo negro, video del camión) en el muro este de la sala, junto a la recepción; vestíbulo libre frente a ella.
- Techo: losa gris oscura, vigas de acero cada 6 m, 3 cañerías rojas, bandeja portacables de malla, tubos LED colgados a ~4,3 m con cables, letreros verdes de salida.
- Muros exteriores por dentro: blanco abajo y hormigón beige con manchas arriba (videos).
- Pallets envueltos en film en el piso, torres de jabas rosadas y grises, casilleros grises en la recepción, oficina con puerta gris con ventana.

## v45 — 2026-11-07 — Trastienda corregida (comparación fotos)
- Puertas de cámara: hoja abisagrada pesada (bisagras, manilla, cantos acero) + bolardos.
- Piso trastienda más oscuro y pulido; carga mayormente en pallets envueltos a piso (solo 2 tramos de rack).
- Techo: vigas finas, 4 bandejas de cables, 3 cañerías rojas, LED fríos a 4,3 m; extintores en pilares; barandas grises sobre cámaras.
- Puerta vaivén a sala más clara, sin letrero ni franja.
- Recorrible en 1ª persona (pasillo sur → pasillo este → recepción) con colisiones.
- Medidas parametrizadas (CFG) + plano_trastienda.html para ajustarlas. Pasillos, cámaras, recepción, andenes = SUPUESTO.

## v46 — 2026-11-08 — Trastienda desde 3 videos nuevos
- Corregido: el muro de la sala tapaba las cámaras del pasillo sur.
- Pasillo sur (bodega→fondo): montante de rociadores en jaula negra, basureros rojos + fregadora, estantería clara, racks naranjos, jaula de materiales, cámaras carnicería/fiambrería, pallets envueltos 2 alto, fondo con cajas sueltas en pallets rojos/azules, salida, parlante.
- Pasillo este (sur→norte): merma en la esquina con lavamanos inox, dispensador, bolardo, basurero, repisa inox con bandejas; lácteos, frutas, sala de máquinas (celosía), jaula de materiales, panadería, alcoba con cortina PVC, gas amarillo, trampa UV, zócalo café, vestíbulo de vaivén con letrero de colores sin texto. Lado exterior: racks azul/naranja y naranja, jabas rosadas, canastos negros de pan, jabas grises, perchero de chaquetas, tablero, casilleros.
- Techo: sur 2 matrices rojas + ramales cada 3 m y losa clara; este bandeja ancha central, 1 cañería roja, vigas de hormigón bajas.
- Pasos medidos: ~1,6–1,7 pasos/s. Pasillo sur ~58–70 pasos (40–55 m), pasillo este ~73 pasos (47–55 m). Recepción movida a z 49,5 (SUPUESTO).

## v48 — 2026-11-10 — Trastienda reconstruida desde el plano 2D (calzado con el plano de sala)
- Todo se arma desde el mapa de Cristian (104 objetos): cámaras, salas, jaulas, racks, pallets, jabas, pilares, puertas, muros, oficinas, caseta, escalera, ascensor, recepción, andenes, plataforma y rampa metálica.
- Altura 3 m para cámaras, salas, oficinas y tabiques (vestíbulo → oficina recepción); el ascensor llega al techo. Muros exteriores y de sala a toda altura.
- Vestíbulo con las líneas de la sala: anexo de vinos hasta x −5,84; se quitó el muro intermedio en x −4,4.
- Vanos en el muro de sala según el plano: vaivén este (z 43,4–45,6), puerta sur a sala de proceso carnicería, puerta norte a panadería.
- Detalle por foto: vaivén gris con ventana, marco blanco y cortina PVC; cámaras con chapa diamante, evaporador, caja eléctrica y baliza; jaulas de malla con estantería naranja; rincón de aseo (fregadora, carro, basurero rojo, mesón inox); red de incendio en jaula negra; extintores con marco amarillo; baño con cerámica; escalera negra con nariz amarilla y baranda blanca; andenes con portón seccional y abrigo negro/amarillo; rampa y plataforma de chapa diamante con baranda gris.
- Recorrible en 1ª persona bodega ↔ recepción, probado sin bloqueos.
- "Escalera salida (patio)" → Rampa metálica.

## v49 — 2026-11-10 — Correcciones de la revisión en el celular
- Vestíbulo y muros del anexo de vinos hacia la trastienda a 3 m (como las cámaras); cielo bajo de vinos también a 3 m.
- Se quitó el muro viejo (x −4,4) y la carga del vestíbulo se corrió a la línea del muro nuevo.
- Sin muebles inox delante de la puerta de escape; rincón de aseo en el orden de la foto.
- Rincón del lavamanos de merma en panel blanco continuo.
- Eliminados los "pilares" sobre los letreros de cámaras (dinteles fantasma de vanos).
- Pasillo este: carril libre = 1 pallet (1,20 m) + 3 cm por lado desde los bolardos → muro exterior y todo lo estacionado se corrió 1,65 m hacia las cámaras; rampa y plataforma acompañan el muro.
- Baño, monitores y oficina de recepción en blanco como antes.
- Escalera al segundo nivel invertida.
- Recepción termina en la línea de las oficinas (se eliminó la franja extra); pallets pegados al muro norte.
- Sala de proceso carnicería ya no entra en la sala.

## v50 — 2026-11-10 — Vestíbulo limpio y cielo según fotos
- Vestíbulo: eliminada la carga vieja (pallets "invisibles", film, transpaleta desarmada, jabas, poste) y el pedazo de muro (z 5,0–5,25); sin pallet en el paso al pasillo sur. Nuevo: 3 pallets envueltos contra el muro del anexo + transpaleta amarilla completa.
- Cielo: losa gris clara con viguetas blancas cada 1,5 m sobre el pasillo sur y sobre las cámaras (antes no había losa ahí y se veía blanco); pasillo este y recepción con losa oscura.
- Marco de acero café sobre los muros bajos del anexo de vinos y sobre el bloque caseta/oficinas (fotos).
- Cielo de vinos a 3 m con palmetas 60×60 y focos redondos (foto).
- Pasillo sur: pallets de madera apoyados, carro con mantas y jaba con papas bajo el rack naranja; carros con mantas contra el muro del anexo.

## v51 — 2026-11-10
- Quitado el último trozo de muro viejo del vestíbulo (z 5,0–5,25, venía desde x −10).
- Sin carros a medio dibujar (pasillo sur y recepción) ni mantas sueltas.
- Piso: toda la trastienda y la recepción con el mismo piso y textura de la bodega (reemplaza el granito que se deformaba).
- Bolardos solo en la zona de merma.
- Pasillo sur bodega→merma igual de angosto que merma→recepción (1,82 m libres frente a las cámaras): muro exterior y todo lo estacionado se corrió 1,44 m hacia las cámaras, con quiebre del muro en el pilar x −13,55.

## v52 (2026-11-10)
- Muro exterior sur recto (da a la calle): el quiebre pasa del pilar x −13,55 a la esquina del anexo de vinos (x −5,84, punto real del plano de sala). Bodega y plano de sala sin cambios.
- Paso al pasillo sur recortado 1,44 m del lado exterior; lo que el modelo viejo tenía al sur de la línea nueva quedó fuera.
- Red de incendio (jaula negra) y rincón de aseo corridos contra el muro: red x −5,94 a −9,64, aseo x −9,74 a −13,05 (aseo acortado de ~5 m a 3,3 m, mismo orden de objetos).
- Cámaras y salas cerradas por arriba: en la vista desde arriba se ven con cubierta (no se cortan a 2,4 m).
- Editor de plano actualizado con el mapa v51.

## v53 (2026-11-10)
- Bodega con pasillos angostos (foto desde arriba): en cada pasillo cabe una fila de pallets junto al rack y un carril para un solo pallet. Pasillos de 3,4 m a 2,57 m; la bodega pierde 1,665 m de fondo por el sur. Racks, pilares, ubicaciones y el frente hacia la sala no cambian; solo se angosta el centro de cada pasillo.
- Muro de la calle recto en una sola línea: bodega, vestíbulo y pasillo sur (cara interior z ≈ 1,73). Se eliminó el quiebre.
- Red de incendio: queda solo la original del vestíbulo, junto a la puerta de escape (como en la foto). Se eliminó la jaula negra que sobresalía en el pasillo. El rincón de aseo vuelve a x −8,2 a −13,05.
- Simulación: carriles al centro del espacio libre; filas de piso a y b (la fila c ya no cabe: con dos filas el pasillo queda tapado); cruce con 5 filas (antes 6); tránsito con 14 posiciones (las 2 de fondo junto al pilar 6 no caben). CONFIRMAR: el tránsito medido era 16.
- La reja de acceso a la bodega queda de 1,6 m (antes 2,45 m), porque sigue a los muros que la enmarcan. CONFIRMAR.
- Desgaste del piso guardado en el navegador se reinicia (cambió el plano).

## v54 (2026-11-10)
- Rack 002 (fondo, frente al cruce) se traslada entero: ya no queda aplastado por el angostamiento del pasillo 2.
- Red de incendio del vestíbulo rehecha según foto: 6 montantes rojos con válvula, manómetro y volante, dos colectores y reja negra; ahora se ve también en la vista desde arriba.
- Supervisora: su posición venía de la animación en el plano viejo (quedaba en el frente del rack); ahora está al centro del pasillo 1.
- Grúa a escala 0,8 (la persona que la maneja en la simulación no se achica); en la operación la cola ya no entra al rack del frente al girar.
- Revisión de geometría: ningún rack ni ubicación queda deformado; solo se angostan muros, piso, cielo, cañerías y vigas largas.
- PENDIENTE de confirmar con Cristian: sector carbón/muro de vinos y rediseño de la entrada (rectángulo rojo).

## v55 (2026-11-10)
- Entrada de la bodega rediseñada (rectángulo rojo de Cristian): la abertura de la reja va del poste junto al pilar 1 al poste siguiente (4,1 m, antes 1,6 m). La reja sigue desde ese poste hacia el norte. La entrada queda despejada: se retiraron la transpaleta estacionada, los carros y lo suelto frente a la reja.
- Tránsito alrededor de la entrada libre: columnas 1 a 3 con dos filas al fondo y la línea del pilar 6 con tres filas (9 posiciones; antes 16 medidas). El simulador antiguo queda con 4.
- Carbón (sala) alineado al frente del cuarto, entre la esquina de vinos y la puerta de vaivén; pallets de costado; robot de limpieza al lado.
- Góndola de vinos del muro sur prolongada hasta la esquina; se une con el muro de vinos del bolsillo.

## v56 (2026-11-10)
- Frente a la puerta de vaivén a sala (junto a pollos y deli): las "jabas rosadas" pasan a ser un rack de montante blanco con una viga naranja a 1,75 m, cajas encima y, debajo, torres de bandejas rosadas de panadería sobre carros con ruedas (foto desde la puerta). Mismo espacio del objeto.
- Vestíbulo de la trastienda con el mismo piso y textura de la bodega.
- PENDIENTE: capacidad real del tránsito alrededor de la entrada (hoy 9, medido 16); sombra tenue en el piso donde estaba la transpaleta.

## v57 (2026-11-10) · Recepción detallada (9 fotos, en Trastienda Recepc/Recepcion_v57 con nombre por contexto)
- Muros: volcanita blanca con franjas de empaste beige en las juntas (bordes irregulares, manchas blancas, puntos de tornillo) y zócalo gris.
- Cielo: losa clara con cerchas blancas de acero cada 4,5 m (cordones, montantes, diagonales) y correas; cañerías rojas y tubos LED colgados.
- Andén 1 (abierto): portón seccional blanco alto; caseta de acero inoxidable con cortina de tiras de PVC y franjas rojas; dos puertas grises abatibles con cartel genérico; nivelador de chapa diamante con marco y pintura amarilla; camión atracado con caja abierta: piso de tablas, paredes con rieles de amarre, travesaños en el techo, dos pallets al fondo y luces rojas.
- Andén 2: igual pero cerrado.
- Puerta de entrada: cortina metálica enrollable gris con caja y guías, tiras de PVC por dentro y aviso.
- Casilleros: dos muebles grises 3 x 3 con celosías, candados, papeles y algunas puertas abiertas; pasamanos de acero inoxidable.
- Columna de hormigón al medio del muro del fondo [posición SUPUESTO]; dos carros de supermercado con devoluciones.
- Sin logos ni marcas (carteles genéricos).

## v58 — 2026-11-11 · Recepción: cielo, caseta, escalera, oficina y bandeja portacables
Respaldo previo: respaldos/2026-11-11_v57_antes_v58
- Cielo blanco (panadería → oficinas): sobre los cuartos de 3 m se veía el vacío hacia el exterior. Se cerró con un muro alto en x −52 (detrás de panadería, ascensor, caseta y oficinas), otro al norte de las oficinas y un cielo sobre la parte de la panadería que sobresale.
- Caseta de guardia rehecha según fotos: muro blanco, ventanal de aluminio de 2 hojas con vidrio real (se ve dentro), mesón con canto amarillo/negro sobre ménsulas, zócalo de laminado café con guardapié de aluminio, citófono, letrero azul genérico, archivador azul y papeles; dentro escritorio, monitor, silla, diario mural, mueble con vitrina, puerta interior y tubo LED. Arriba antepecho blanco con ventana alta (2º nivel). [medidas SUPUESTO]
- Escalera rehecha en U, girando a la izquierda al subir: tramo 1 pegado a la caseta desde el pasillo, descanso al fondo, tramo 2 de vuelta hasta el 2º nivel (3 m). Peldaños negros con nariz amarilla, losa blanca por debajo, baranda blanca de tubo con barras horizontales, pasamanos de muro y panel azul genérico bajo el tramo 2. [peldaños SUPUESTO: 2 tramos de 9 contrahuellas de ~17 cm]
- Puerta de la oficina de recepción: ahora igual a la de CCTV (gris con celosía y vidrio); antes salía como puerta de andén por un error de nombre.
- Ventana corredera de aluminio de 2 hojas en el muro de la oficina hacia la recepción, con alféizar; dentro escritorio, monitor y mueble.
- El marco café de arriba ahora va sobre los muros de baño, CCTV y oficina (antes flotaba frente a la caseta).
- Bandeja portacables de rejilla blanca (alambres cada 10 cm, colgadores de varilla con perfil, cables de colores dentro y lazos de cable negro colgando) por toda la trastienda: pasillo sur, pasillo de cámaras y recepción. Reemplaza las bandejas planas anteriores. [alturas SUPUESTO]
- Verificado: recorrido a pie sin bloqueos, sin errores de consola. Mapa del editor sin cambios (v53).

## v59 — 2026-11-11 · Sombreado del entretecho, sin marco sobre oficinas, escalera junto al ascensor
Respaldo previo: respaldos/2026-11-11_v58_antes_v59
- Sombreado por zonas (en el shader, según la posición): el entretecho sobre las cámaras del lado este y sur, la panadería, el ascensor, la caseta y sobre baño/CCTV/oficina de recepción se oscurece con la altura y la profundidad (hasta ~70 % más oscuro junto al techo). También los rincones con poca luz: el del ascensor y el del baño de recepción. Fuera de esas zonas no cambia nada.
- Eliminado el marco de fierro café sobre la oficina de recepción, CCTV y el baño (no existe). Se mantiene el de los muros de la sala.
- Escalera: sigue en U girando a la izquierda en el descanso; el 2º tramo sube pegado al ascensor. La llegada arriba ahora es más amplia (0,9 m) y en el 2º nivel se agregó la puerta del ascensor junto a la llegada de la escalera. [posición de la puerta del 2º nivel SUPUESTO]
- Verificado: recorrido a pie sin bloqueos, sin errores de consola.

## v60 — 2026-11-11 · Recepción más chica, patio cerrado, pesa y tableros de andén
Respaldo previo: respaldos/2026-11-11_v59_antes_v60
- Mapa nuevo de Cristian aplicado (recepción x −58,2 a −74,65 y z 73,6 a 82,5; andenes, puertas, plataforma, rampa y pilares movidos; editor del plano actualizado, clave planoTras_v55).
- Patio cerrado por los muros marcados; afuera queda la calle del barrio:
  - Piso de hormigón con juntas cada 4,5 m, grietas, manchas, rejilla de desagüe y restos de pintura amarilla.
  - Cerco oriente: paneles de acero gris oscuro con marco, postes cada 3,2 m y reja de barrotes abajo (~6 m sobre el patio).
  - Sur: muro de hormigón gris claro de 3 m con portón corredizo de rejas [posición del portón SUPUESTO].
  - Fachada del edificio: chapa gris oscura, zócalo de hormigón, focos LED, cañería de gas y caja eléctrica; escalas de hormigón en las 2 puertas de escape al patio [SUPUESTO].
  - Andenes: fachada gris, alero con frontón y focos, triángulo rojo/blanco sobre cada abrigo.
  - Plataforma y rampa de chapa diamante sobre patas, barandas de 7 barras; la rampa ahora sube hacia la plataforma (antes estaba invertida).
  - Torres de pallets vacíos (plásticos azules, algunos rojos, de madera y verdes) donde están en el plano.
  - Contenedor verde de cartones (tolva con nervios, borde, chasis y cartón encima; sin marcas).
  - Maxisacos, árboles del barrio por fuera del cerco y cielo con nubes y el cerro al sur.
  - Nueva vista "Patio" en "Ir a".
- Recepción:
  - Pesa industrial de piso (chapa diamante negra, 4 patas, cable a un visor en columna [visor SUPUESTO]).
  - Tableros de control entre los dos andenes, uno por andén: botonera del portón (subir/parar/bajar) y del nivelador (parada de emergencia, botón y luz), con ductos [SUPUESTO, sin fotos].
  - Rack de bandejas rosadas nuevo y pilar del plano; se quitó la columna supuesta de la v57.
  - Carros y pallets en espera reacomodados para no chocar con la pesa.
- Verificado: recorrido a pie sin bloqueos (la ruta de prueba pasa a z 78,6 por el pilar movido), sin errores de consola.

## v61 — 2026-11-11 · Rendimiento (auditoría A+B parcial), patio de asfalto, tránsito de 16 y reja de 3,0 m
Punto de restauración: respaldos/2026-11-11_RESTAURACION_v60 (para volver: copiar su Backroom_Recorrido.html a la carpeta principal).
Resolución: sin cambios (no se bajó).
- Rendimiento, medido antes → después (triángulos por cuadro): desde arriba 2,36 M → 0,70 M; bodega 2,41 M → 0,23 M; pasillo sur 2,38 M → 0,33 M; pasillo de cámaras 2,39 M → 0,48 M; recepción 2,38 M → 0,26 M. Llamadas de dibujo: bodega 334 → 169, pasillo sur 540 → 407, pasillo de cámaras 1.026 → 941, recepción 468 → 264; desde arriba 616 → 660 (sube un poco por los bloques).
  - Las copias se parten en bloques de ~9 m con descarte por cámara (antes se dibujaba todo siempre).
  - Botellas con 3 niveles de detalle (192 / 60 / 16 triángulos; completo a menos de 7 m).
  - La sombra del sol se recalcula 1 de cada 3 cuadros.
  - Sombreadores precompilados al terminar de cargar.
  - Cambiar de vista ya no marca todos los materiales para recompilar.
  - La revisión periódica de materiales baja de cada 2 s a cada 30 s tras 2 min.
- El archivo Backroom_Recorrido.html ahora abre sin internet (three.js, sus módulos y la física van dentro). La versión publicada en línea sigue usando el servidor externo.
- Patio rehecho desde las fotos de la carpeta patio: piso de asfalto (textura real CC0) con juntas, grietas y manchas; cerco de paneles gris claro acanalados con bastidor oscuro; muro de contención de hormigón con forro bajo la chapa del edificio; segundo contenedor verde; pallets de mercadería envueltos, jabas rojas, pila de bandejas envuelta, filas de carros, 2 estanques blancos, caseta amarilla con portón rojo, grúa horquilla naranja genérica y marcas amarillas gastadas [posiciones SUPUESTO].
- Tránsito: 16 posiciones (9 en bodega en 3 filas, 3 en la línea del pilar 6 y 4 después de la reja, en el vestíbulo). La reja no delimita el tránsito.
- Reja de entrada: abertura de 3,0 m = 2 pallets y medio por su lado de 1,2 m [SUPUESTO; si es por el lado de 1,0 m serían 2,5 m]. Se agregó un poste intermedio.
- Verificado: recorrido a pie sin bloqueos, prueba de estrés sin errores, botellas revisadas de cerca y de lejos.
- No hecho: personajes de Tripo/Meshy (no encontré los archivos), fusión de mallas sueltas de la trastienda, simulación independiente de los FPS, luz horneada.

## v62 — 2026-11-11 · Patio rehecho desde el plano del patio
Respaldo previo: respaldos/2026-11-11_v61_antes_v62/
- El patio se arma desde plano_patio (patio_map.js inyectado por splice58.py). Mover un objeto en el plano y reconstruir lo mueve en 3D.
- Portones corredizos de barrotes en el cerco oriente (z 23,2–30,1 y 31,7–45,3, el de 13,6 m en 2 hojas), con riel, ruedas y postes; puerta peatonal de trabajadores entre ambos.
- Cerco de paneles gris cortado en los vanos; rejas cortas de malla de 2 m alrededor de los estanques.
- Muros de hormigón del sur sin tramos duplicados. Se quitó el portón antiguo del fondo.
- Nuevos: caseta de guardia, grupo electrógeno en cabina, estanques de propano, rack de 3 niveles con malla y 2 puertas, jaula de bicicletas, puerta de emergencia del subterráneo, rejilla de desagüe y rampa de acceso al contenedor con descanso.
- Cargas desde el plano: pallets con mercadería envueltos en film, pilas de bandejas plásticas (gris, negro, azul), jabas rojas, torres de pallets vacíos, carros encajados y maxisacos.
- Escalas de hormigón de las puertas de escape: las líneas dibujadas marcan el borde; descanso y 4 peldaños.
- Afuera del cerco: calle de asfalto con línea central y vereda; árboles más allá.
- Grúa horquilla genérica naranja, sin marca.
- SUPUESTO: alturas (cerco 3,4 m, malla 2 m, rack 4,6 m, generador 2,3 m, caseta 2,6 m), colores del generador y la caseta, ancho de la calle (8 m), número de peldaños y mercadería de cada pallet.

## v63 — 2026-11-11 · Correcciones del patio (plano nuevo + fotos)
Respaldo previo: respaldos/2026-11-11_v62_antes_v63/
- Nivel: el patio queda al nivel de la trastienda (puertas de escape directas, sin escalas) y baja 1,2 m hacia los andenes entre z 50,2 y 56,2. SUPUESTO: dónde y cómo baja.
- Murete en L de 1,6 m en la puerta de escape 2. Escala en bajada solo en la puerta de emergencia del subterráneo (9 peldaños, 1,53 m SUPUESTO).
- Racks del patio cerrados (chapa atrás, lados y techo con alero) con puertas correderas naranjas, 3 niveles; sin reja delante. Fondo 3,25 m según el plano.
- Grupo electrógeno detallado (cabina verde agua genérica, rejillas, puertas, ventanilla, parada de emergencia, patín, escape).
- Sin franja de hormigón en la fachada hacia el patio.
- Portones y puerta peatonal cerrados con chapa: negra por fuera, zinc por dentro, 3,3 m SUPUESTO.
- Rampa del contenedor: la subida es el tramo perpendicular al muro; la pasarela va pegada al muro.
- Asfalto más claro. Calle eliminada. Estanques de propano más altos (≈4,3 m SUPUESTO).
- Tablero de cámara detallado (pantalla de temperatura, pilotos, selector, parada, ductos) SUPUESTO sin foto.

## v64 — 2026-11-11 · Pendiente real, puertas de escape, muros cerrados, barrio
Respaldo previo: respaldos/2026-11-11_v63_antes_v64/
- Pendiente recta desde la puerta de escape 2 (z 50,2) hasta el muro de andenes, 1,2 m de caída. Cerco escalonado, rampa metálica y camión siguen la pendiente.
- Puertas de escape al patio selladas: marco que forra el vano, umbral, hojas exteriores con burletes, bisagras, zócalos, cierrapuertas, letrero y luz. Detalle SUPUESTO.
- Muros exteriores (trastienda-patio y andenes-recepción) cerrados sobre y bajo cada vano, también por fuera.
- Portones a 2,7 m (según la vista de calle). Cañería de gas corrida para no cruzar la puerta 2.
- barrio/osm_lider_sf.json: datos OpenStreetMap a 250 m (calles, huella del edificio, usos). barrio/barrio_osm.png: plano de referencia.

## v65 — 2026-11-11 · Barrio real desde OpenStreetMap
Respaldo previo: respaldos/2026-11-11_v64_antes_v65/
- Calles reales a 250 m del patio con vereda (Pedro Molina frente a los portones, Cinco de Abril al sur, Av. O'Higgins con bandejón y árboles al norte, y las demás). Sin rótulos.
- Calce: esquina sur-oriente del edificio en OSM = esquina del muro sur del patio; la huella del anexo de recepción coincide con ~1,5 m de error.
- Recinto vecino al oriente como muro ciego de 5 m con volumen interior; jardín infantil como volumen bajo.
- SUPUESTO: casas (no vienen en OSM; son volúmenes genéricos), anchos de calzada y vereda, alturas, calle plana (sin pendiente).
- Árboles del cerco movidos a la vereda. Suelo exterior ampliado.

## v66 — 2026-11-12 · Barrio con texturas CC0, autos y grúa nueva
Respaldo previo: respaldos/2026-11-12_v65_antes_v66/
- Texturas CC0 de Poly Haven (road_damaged_clean, concrete_pavement, white_plaster_rough_01, clay_roof_tiles_02, precast_concrete_wall, sparse_grass, withered_grass), reducidas a 512–1024 px y corregidas de color. No se usó la carpeta "texturas" (contenido extraído de un juego).
- Calles con calzada texturada, solera, vereda, postes de hormigón con cables y línea central en las de doble sentido.
- Casas de fachada continua con estuco de color, puerta, ventanas con marco y techo de teja a dos aguas. SUPUESTO: OSM no trae casas.
- Autos estacionados genéricos sin marca (modelo propio), no frente a los portones ni en esquinas.
- Grúa horquilla a gas modelada a mano, sin marca. Camiones: sin cambios (pendiente).


## 2026-11-15 · Regla nueva de texturas (reemplaza el límite de peso)
- El peso del archivo YA NO es límite (probado por Cristian: subir texturas no causó lag).
- Estándar: texturas fotográficas reales 1024×1024 .webp (Color + Normal OpenGL + Roughness). 2048 solo para el lightmap horneado del piso.
- Presupuesto real = memoria de la gráfica integrada (cada mapa 1K ≈ 5,6 MB de VRAM con mipmaps), no los MB de descarga.
- Fuente: CC0 de ambientCG / Poly Haven, carpeta `Proyect 3D\tex_pbr_1k\` (NO usar la carpeta `texturas`, que tiene contenido extraído de un juego).

## v71 · 2026-11-15 · Texturas PBR reales 1K + noche 21:00 (artefacto versión 92, id 1794778051-a885)
- Base: versión 91 (1794668309-b62a). Respaldo para volver atrás: `respaldos\2026-11-15_antes_v71\` (index + calles.json + sala_datos.json); republicar esos 3 archivos.
- Texturas CC0 1K (.webp) en `tex_pbr_1k\` (origen en FUENTES_CC0.json): piso bodega/trastienda/recepción = granito Granite002A con juntas de 45 cm; terrazo sala Terrazzo005; asfalto patio asphalt_floor; muros yeso PaintedPlaster017 (solo relieve, canal uv2, no toca franjas/zócalos); cartón Cardboard004; pallets Wood061; calles: asphalt_02, concrete_pavement, clay_roof_tiles_02, palm_bark, bark_brown_02; frondas y copas rehechas con hojas fotográficas LeafSet024/013 en la misma distribución de UV.
- Noche 21:00: luz ambiente 0,65 (#EEF0F2 / rebote #3A3835); luz general de cielo raso 1,9; brillo propio de pisos/muros al 75 %; 4 acentos sin sombra a 6,5 m (bodega y patio 3200K, sala 2×4500K); coolers con panel frío #DDF4FF y halo en el piso (167); calles al 32 % de color, luminarias encendidas con charco de luz; cielo nocturno con estrellas y cerro en silueta; niebla oscura afuera, clara adentro; fondo de maqueta #0D131F.
- Verificado (sin GPU): llamadas de dibujo +1 a +3 por vista; interior ~16 % más tenue que la versión de día; calles de noche. FPS reales: revisar con #diag en el PC.
- Pendiente: contorno del techo en la maqueta; vehículos no se oscurecieron (regla de no tocarlos); techo del edificio visto desde arriba en primera persona se ve claro; bloom sin cambios.

## v72 · 2026-11-15 · Techo fantasma en la maqueta
- Estructura de acero (viga de amarre perimetral en la corona de muros y = 7,6 m, cerchas cada 6 m, costaneras, cumbreras, lucernarios, 2 ductos) + cristal que se desvanece (0,07 en el alero → 0 en la cumbrera). 2 llamadas de dibujo (1 de líneas, 1 de cristal), sin sombras, no bloquea clics.
- [SUPUESTO] naves a dos aguas de 10°: 4 naves de ~21,6 m sobre sala/bodega, 1 sobre el ala este de fachada, 1 sobre el ala oeste; no hay plano de la estructura real.
- Solo visible en vista maqueta con cámara sobre 8,5 m; botón "Techo: visible/oculto" en la barra de la maqueta. Pilares fantasma unen el corte de muros (2,4 m) con la viga.
- Cambio respecto del pedido: líneas #3F6F99 al 62 % y #56789A al 34 % (los colores pedidos #9EC5E5/30 % y #7A9BB8/14 % no se veían sobre el piso blanco iluminado).
- Para quitarlo: borrar el bloque v72 o republicar respaldos\2026-11-15_v71_publicada\index_v71.html.

## v73 · 2026-11-16 · Piso sin mancha + techo ficticio retirado (artefacto versión 94, id 1794800127-326d)
- La mancha blanca en el piso de bodega era el reflejo de las 4 luces puntuales de v71 sobre el granito pulido. Se reemplazaron por charcos de luz falsos (sin brillo especular, casi sin costo por píxel) y el granito quedó con rugosidad mínima 0,55.
- Se retiró el techo fantasma de v72 (se basaba en naves supuestas).
- FPS en el PC de Cristian antes del cambio: 23 FPS con 1.520 llamadas de dibujo (Gráficos Bueno 70 %). Meta: 60 FPS, mínimo aceptable 35.
- Techo nuevo en Blender: Fase 1 (plano técnico) entregada para validar; no se modela hasta que Cristian elija la dirección de pendiente y responda la franja frontal, recepción, patio y alcance.
- Respaldo: respaldos\2026-11-16_v73_publicada\index_v73.html

## 2026-11-16 · Plano técnico del techo v2 (decisiones de Cristian)
- Cumbrera Norte–Sur por el centro (eje 5, x = −13,55), desde el frente hasta Cinco de Abril. Aguas hacia Riquelme (4,0 %) y hacia el patio (6,7 %). Aleros +7,55, cumbrera +9,68. Cinco de Abril y el fondo de sala quedan como hastiales.
- Dos aguas solo entre x −45,2 y Riquelme (z 1,5 → 66,6). Franja técnica plana (x −59,2 → −45,2) con ductos y condensadores. Franja frontal (locales, dentro del edificio) plana a +7,40 con volumen de entrada más alto (x −31,4 → −22,7).
- Recepción plana. Patio con malla raschel (z ≈ 14 → 36).
- Frontis a modelar: corredor con alero (pilares negros, cielo de listones madera oscura con LED), mall chino (tienda), automotora en la esquina, octágono con 2 restaurantes (uno da a O'Higgins), conector con 2 tragaluces, estacionamiento con rampa al subterráneo. Letreros genéricos sin marcas.
- Frontis medido en el satelital (±5 m); OSM es anterior al paseo comercial.
- (v3 del plano, 16-11) Frontis corrido +4,1 m: mall chino z 82,5 → 124 (empieza donde termina la recepción); fachada del súper en z 92,1. Entrada junto al octágono bajo el letrero (x 4 → 20,3). Octágono: local de pollo frito hacia O'Higgins + pizzería. Aviso: la calzada de O'Higgins del modelo de calles (z ≈ 161) queda ~35 m más al norte que en el satelital (≈ 126); revisar al modelar el frontis.
- (v4 del plano, 16-11) Frente re-medido en la foto rectificada del otro chat (u=(45−x)/125·1422, v=(125−z)/128·1456; ±2 m): fachada z 92–94; recepción z 69,6–84; mall chino x −74,5 → −51,7, z 84 → 128; automotora x −51,7 → −44,7; octágono x 21 → 40,5, z 103,5 → 128; tragaluces z 95,5–100,4; estacionamiento x −40 → 20, z 96 → 128; rampa x −31,5 → −8,2, z 113 → 123,7; dos aguas terminan en z ≈ 72 (plancha) / 76 (membrana); franja técnica desde x −43.
- El modelo de calles solo tiene la calzada norte de O'Higgins (z ≈ 161–169); faltan la calzada sur (z ≈ 128–134) y el bandejón. Muros: se mantiene 7,40 m medido (el 8,2 del brief era supuesto).

## 2026-11-16 — v74 publicada (artefacto versión 95, id 1794810285-3c2d)
- Techo y estructura superior hechos en Blender: `techo_blender\build_techo_v3.py` → `techo_local.blend` / `techo_local.glb`; optimizado (instancing+join) → `techo_v74_optimizado.glb`, servido como `techo.json` (base64).
- Grupos: Techo_Exterior, Estructura_Principal, Arriostramientos_MEP, Luminarias_Techo, Frontis, Calle_OHiggins.
- Dos aguas: cumbrera N–S en eje 5 (x −13.55, +9.68), aleros +7.55; 4.0% hacia Riquelme, 6.7% hacia patio/Molina. Recepción plana con malla raschel.
- Frontis según plano v4: acceso junto al octágono, mall chino x −74.5→−51.7 z 84→128, octágono + conector con 2 lucarnas, estacionamiento con rampa, calzada sur de O'Higgins + bandejón (sin árboles).
- Se ocultan los cielos/vigas/LED antiguos de sala, nave y trastienda (no se borran del código). El cielo nuevo usa emisivo = color × k para no verse gris.
- calles.json: se recortaron los triángulos e instancias (árboles, autos simples del GLB) dentro de la franja frontal/estacionamiento (prep_v74.mjs, prep_v74b.mjs). Vehículos del simulador intactos.
- Maqueta: se ocultan los 4 grupos del techo; el Frontis se corta a 2.4 m.
- SUPUESTO: posiciones del frontis ±2 m (foto rectificada); letreros genéricos; interiores del mall chino y del octágono no modelados.
- Revertir: republicar `respaldos\2026-11-16_antes_v74\index_v1794800127-326d.html` como index.html junto con su calles.json (techo.json queda sin uso).


## 2026-11-20 — v75 (artefacto versión 96, id 1795156467-021f): edificio completo desde el plano por capas
- Fuente: plano por capas revisado con Cristian (revisiones 1–3) → `techo_blender\plano_final.json`.
- Blender: `techo_blender\build_plano.py` genera `edificio_plano.blend` / `edificio_plano.glb` (≈64 mil triángulos, 37 materiales).
  Grupos: Frontis (muros con dos caras, locales, cielos, 2º nivel, escalera, frente exterior), Techo_Exterior, Estructura_Principal, Luminarias_Techo, Arriostramientos_MEP (bandejas).
- Texturas fotográficas CC0 a 2K (ambientCG / Poly Haven) en `techo_blender\tex2k` (lista en FUENTES_CC0.json). Sin reducción de calidad.
- Simulador: techo_0/1/2.json = edificio nuevo (GLB en 3 partes por el límite de 16 MB por archivo); calles.json sin la fachada vieja (*_local) ni lo que caía dentro del edificio/estacionamiento.
  TRAS_MAP_DEF y PATIO_MAP_DEF reemplazados por los objetos del plano (racks, pallets, puertas, tableros movidos por Cristian).
  Se esconden (material invisible) los pilares, vigas, LED, bandejas y cielo de vinos viejos del simulador.
- No se tocaron vehículos ni rutas. Calles del plano alineadas a las del simulador (veredas ~3 m; real 6,6/7,1/4,5/1,9 m).
- Red húmeda: no incluida (se rediseña aparte).
- Revertir: republicar `respaldos\2026-11-20_antes_v75\` (index.html + calles.json + techo.json de v74) y quitar techo_0/1/2.json.
# v76 · 2026-11-20 — correcciones de auditoría en Blender, detalle, red húmeda nueva, calles con vereda 4,5 m, botón Techo

Respaldo previo: respaldos\2026-11-20_antes_v76 (index_v75.html, calles_v75.glb, edificio_v75.glb) y respaldos\2026-11-20_antes_v76_blender (build_plano.py, plano_final.json, edificio_plano.glb, texturas 1K reemplazadas).

## Blender (techo_blender\build_plano.py → edificio_plano.glb)
- Lee plano_final2.json: pilares en el eje del simulador (bodega 3,68/19,43/38,69; sala 3,13/20,3), vigas longitudinales con quiebre en el muro bodega/sala, LED del 2º nivel a 3,1 m, bandejas que bajan bajo la losa, salud dental corrida.
- Texturas antiguas a 2K: ladrillo (ambientCG Bricks059), deck (CorrugatedSteel005 teñido), malla raschel (procedural propia). Todas las texturas del modelo quedan en 2048×2048.
- Muros: esquinas cerradas (cada extremo +½ espesor); el antepecho sobre la cubierta lleva la cara exterior.
- Vitrinas por fuera del muro (antes quedaban dentro); faja opaca tras el letrero ESTACIONAMIENTO; downlights cerrados (aro, difusor y carcasa).
- Techo: nervios reales de la chapa cada 25 cm (ondas de la textura alineadas con la pendiente), juntas de membrana, línea de vida en la cumbrera, escotilla (SUPUESTO), canaletas con soportes cada 1 m, tapas, embudos, bajadas con abrazaderas y zapata, condensadores con rieles, serpentines, rejillas de ventilador y seccionador, equipos con base y celosía.
- Estructura: placas base con pernos, cartelas pilar-viga, costaneras perfil C, tensores a media luz entre marcos.
- Frente: topes de estacionamiento, 3 postes de iluminación (SUPUESTO), barandas en la rampa, puerta de escape a Cinco de Abril, vitrinas del octágono hacia O'Higgins y Riquelme (SUPUESTO). Se quitó la losa de vereda de O'Higgins (la pone calles).
- Red húmeda (grupo Red_Humeda): 597 rociadores colgantes, 107 ramales, 13 matrices, 6 montantes, acometida, VCA, 14 gabinetes con conexión a la red, red seca con siamesa; colgadores cada 3 m, coples cada 6 m.
- 198.588 triángulos, 44 materiales.

## Calles (calles_v76.glb desde calles_v71, sin cortes previos)
- Se corta solo el predio (x −74,8..39,9 · z 1,4..120,5) y las piezas _local.
- Vereda pareja ~4,5 m: Riquelme +1,05 m, Cinco de Abril −1,4 m, Pedro Molina −1,4 m, O'Higgins +0,65 m (todo lo que está más allá se traslada; las manzanas vecinas conservan su proporción).
- Vehículos: ejes pm(z) y cz(x) corridos 1,4 m (mismo desplazamiento).

## Simulador (index v76)
- Botón Techo: sin techo se ve el interior desde arriba con muros a altura completa (también en la vista maqueta).
- Muros duplicados ocultos (Riquelme x 39,8 y recepción z 82,6); el muro sala/trastienda bajo el 2º nivel baja a 3,2 m.
- Cubiertas, equipos y fachadas exteriores oscurecidos para las 21:00; suelo general abierto sobre la rampa y la caseta de escaleras.
- Filtrado anisótropo 16× en todas las texturas del modelo. Modelo en 4 partes de ≤15 MB (límite del visor por archivo; se unen sin pérdida).

## Plano (plano_capas v7)
- Tipo nuevo "Montante"; calles y veredas al trazado v76.

## 2026-11-21 · v77 publicada (simulador versión 100) — Fase 1 del plan con la skill blender-arte-bodega
Respaldo previo: respaldos\2026-11-21_antes_v77 (v99). Respaldo de esta versión: respaldos\2026-11-21_v77_publicada.
Blender (build_plano.py):
- Alero nuevo a 4,5 m (SUPUESTO por fotos): cielo de listones de madera clara (7 cm cada 11 cm) con colgadores y luminarias empotradas cada 3,5 m.
- Faja oscura de ~1,2 m con juntas cada 2,4 m, remate de aluminio y banda gris clara hasta la coronación.
- Columnas del alero redondas negras (r 11 cm) con placa base; antes cuadradas blancas.
- Vitrinas de vidrio transparente con interior genérico iluminado 1,4 m detrás (sin marcas).
- Muro del patio (cuerpo principal x −59,2 y recepción z 73,3): chapa ondulada vertical gris oscuro (textura nueva chapa_oscura_diff).
- Bisel 6 mm + normales ponderadas en las piezas nuevas. GLB 42,0 MB, 203.822 triángulos.
Simulador (index.html, solo materiales del techo/fachada; sin tocar la lógica):
- Cubierta menos oscura de noche, tragaluces con brillo ≤ .35, muros exteriores legibles (rebote de luz pública) y sin destellos.
- Cielo de listones y vitrinas con brillo propio de noche; faja con reflejo leve.
- Chapa del patio con tratamiento propio (iluminada por focos).
- Partes del techo: techo_0..3.json (?v=77).
QA (capturas 1600×900 en el simulador): frente/alero APROBADO CON NOTAS; patio APROBADO CON NOTAS; Riquelme APROBADO CON NOTAS; aéreo APROBADO CON NOTAS.
Pendiente / no verificado visualmente: zona oscura sobre la trastienda (objeto del simulador, causa sin confirmar); interior de la automotora usa la misma estantería genérica (SUPUESTO); franja negra en «Desde arriba» (decisión del usuario).

## 2026-11-21 · v78 publicada (simulador versiones 101–102) — decisiones de Cristian + Fase 3 (parte 1)
Respaldo previo: v77 = versión 100 (respaldos\2026-11-21_v77_publicada). Respaldo de esta versión: respaldos\2026-11-21_v78_publicada.
1. Vista «Desde arriba» sin techo: los muros interiores de la sala (incluido el muro sala/bodega de 7,4 m) se cortan a 3 m solo en esa vista; en 1ª persona siguen completos.
2. Alero: cielo de listones ahora gris pardo oscuro como la foto de la clínica (textura nueva listones_oscuro_diff; material listones_oscuro).
3. Fase 3:
- Autos rudimentarios del modelo de calles (30 autos hatch/sedán/SUV de cajas) quitados de calles.json.
- Vehículos de Cristian (camiones, camionetas, autos, montacargas): vidrio tintado con reflejo, pintura con barniz, neumáticos mate, llantas metálicas y sombra de contacto bajo cada pieza. La geometría no se tocó.
- Trastienda en Blender (tras_blender\build_tras.py → tras_0.json, 128 mil triángulos, 18 mallas): 4 racks (montante perforado 80×70 mm, celosía con diagonales, vigas caja con conectores, placas base y anclajes, cubiertas), 2 racks de bandejas rosadas con carros, líneas de pallets de madera (7 tablas, 9 tacos) y plásticos con carga de cartón (4 variantes sin marcas) y film. Lee el mismo plano de la trastienda. En el simulador se ocultan las 18 mallas de cajas que lo reemplaza; obstáculos y lógica intactos.
- Texturas CC0 nuevas (ambientCG): Cardboard004, Wood066, Plastic010, DiamondPlate008A.
- Racks de la bodega: evaluados con fotos y vista aérea; se mantienen (ya eran de Blender). Mejora futura: rejas anticaída y más variedad de producto.
QA (capturas 1600×900): trastienda APROBADO CON NOTAS; alero APROBADO; Desde arriba APROBADO; calles/vehículos APROBADO CON NOTAS.
No verificado visualmente: racks de bodega a nivel de piso (la cámara de prueba quedó dentro de un rack); sombra de contacto de los vehículos (poco visible en la captura).
Pendiente Fase 3 parte 2: cámaras de frío (panel sándwich, chapa diamante, cortina de PVC, bolardos), muros y objetos sueltos de la trastienda.

## 2026-11-21 · v79 publicada (simulador versiones 103–104) — trastienda parte 2 (fotos «trastienda» y «bandeja_cables_bajo_segundo_nivel» de Cristian)
Respaldo previo: v78 = versión 102 (respaldos\2026-11-21_v78_publicada). Respaldo de esta versión: respaldos\2026-11-21_v79_publicada.
Kit de trastienda en Blender (tras_blender\build_tras.py → tras_0.json + tras_1.json, 137 mil triángulos, 40 mallas):
- Cámaras y salas de panel (12): muros de panel sándwich con junta cada 1,15 m, microperfil, suciedad y marcas de carros en la base; zócalo sanitario galvanizado de 15 cm cortado en las puertas; remate de chapa arriba; techo de panel.
- Baranda blanca sobre las cámaras con postes de funda a franjas negras/blancas (foto); no se pone donde la cámara queda bajo la losa del 2º nivel.
- Bandejas portacables de rejilla blanca (dos paralelas, 45 y 40 cm) con mazos de cables de colores, soportes trapecio (canal 41×41 y varillas roscadas cada 1,5 m). En el pasillo de las cámaras bajan con una curva suave antes de la losa del 2º nivel (z 15,4→18,0), pasan bajo la losa a 2,72 m y vuelven a subir después (z 69→71,6) [la subida es SUPUESTO].
- Pilas de canastos negros y jabas grises con ranuras; bolardos galvanizados redondos con placa; cañería amarilla de gas en la cámara de panadería [posición SUPUESTO].
- Sombras de contacto bajo racks, pallets, jabas, bolardos, tableros y en el contorno de las cámaras.
- Film de los pallets más visible (velo blanco con reflejo).
Edificio (build_plano.py): cielo del 2º nivel (cara inferior de la losa) en hormigón gris oscuro con vigas cada 6 m, conduits negros y tubos blancos con abrazaderas (foto «trastienda»).
Simulador: oculta los muros de panel, zócalos diamante de muro, techos, barandas, bandejas, jabas, pan y bolardos que reemplaza el kit (126 piezas); puertas, tableros, balizas y letreros siguen siendo del simulador. El tinte de las texturas (montante azul, cartón, plásticos, jabas) se aplica al cargar porque el glTF no lo trae.
Nota: la zona negra sobre las cámaras es el sombreado por zonas de la v59 (entretecho sin luz), no un error del modelo.
QA (capturas 1600×900): cámaras APROBADO CON NOTAS; bandejas con bajada APROBADO; cielo del 2º nivel APROBADO CON NOTAS (textura algo granulada); jabas APROBADO; racks con tinte correcto APROBADO.

## v80 · 22-11-2026 · publicada como versión 106 (colección de bugs, 20 puntos)
- Respaldo previo: respaldos/2026-11-21_v79_publicada. Respaldo de esta versión: respaldos/2026-11-22_v80_publicada.
- Blender (build_plano): pilares sin dado/placa/pernos con base pintada; extintores colgados; muros interiores en hormigón bruto pintado + franja gris 0,9 m; canaletas al exterior; sin vigas bajo el 2º nivel; gabinete de la reja eliminado; montante de bombas conectado; carrete de la ochava; bajada de entrada pegada al muro; cierre oscuro sobre cielo de vinos. Texturas nuevas: muro_bruto, muro_gris, pilar_pintura (tex_v80b.py).
- Kit trastienda (build_tras): vigas naranjas en rack claro, celosía en zig-zag, racks/pallets recortados frente a pilares, lavamanos/dispensadores/basurero/repisa de merma.
- Simulador (index): muro poniente −59,07/−59,33 (patio); ocultos: red vieja (sala_rociador, tras_montante), accesorios est_* de pilar, cielos planos de trastienda a 7,38 m; cajas de merma anuladas; luz: sol 1,7, rebote bodega 45 %, cubierta 0,36, losa 2º nivel 0,28; entretecho 55 %. Caché v=80.
- Modelo de bodega (bodega_bin_0): diagonales en X de las cabeceras del rack central eliminadas.
- Pendiente: pallets insertos en racks (dato del sim), objetos sin modelar fuera de merma, rendimiento (~16 FPS con la sala a la vista), vista cenital del patio.

## v81 · 22-11-2026 · publicada como versión 107 (bug 16, objetos fuera de merma)
- Respaldo: respaldos/2026-11-22_v81_publicada (v80 = versión 106 en respaldos/2026-11-22_v80_publicada).
- Kit trastienda (build_tras): rincón de aseo (porta útiles con escobas/trapero/secador, balde con estrujador, fregadora de conductor sentado, carro de aseo, contenedor rojo 240 L, mesón inox, gabinete inox), 2 tableros eléctricos RAL 7035 con pilotos y ductos, perchero móvil con chaquetas y chaleco reflectante, dispensador de agua con bidón, pisos plásticos en jaulas. Medidas de catálogo [SUPUESTO, sin foto].
- Simulador: ocultos tras_aseo_*, tras_gal, tras_chaqueta, tras_dispensador, tras_banquito; anuladas instancias tras_blanco/tras_baliza de los tableros. Caché tras v=81 (techo y calles siguen en v=80).
- QA: aseo, tableros y perchero vistos en captura; dispensador y pisos de jaula no verificados visualmente.
- Pendiente: objetos del patio (bultos, pallets, carros, contenedor), pallets insertos en racks de bodega, rendimiento.

## v82 · 22-11-2026 · publicada como versión 108 (patio)
- Respaldo: respaldos/2026-11-22_v82_publicada (v81 = versión 107).
- Kit (build_tras, sección v82, lee el plano del patio): pallets con mercadería envueltos, pilas de bandejas envueltas (gris/negra/azul, sobre el piso), jabas rojas sobre pallets, torres de pallets vacíos (plástico azul/rojo/verde y madera, sin bisel por rendimiento), carros de supermercado encajados con canasto de malla, contenedores verdes de cartón (tolva con nervios, borde, rodillos, gancho, cartón encima), maxisacos de rafia con asas. Asentados en la pendiente del patio (−1,2 m entre z 50,2 y 73,3).
- Simulador: ocultos tras_pallet_vacio, carros, maxisaco, contenedor_nervio, carton_pila y las cajas sueltas de los contenedores; anuladas instancias de patio_pallet_base/bulto/film/jaba/negro en las zonas de pallets y malla_poste en carros. TINTE + jaba azul/roja. Caché tras v=82.
- Triángulos del kit: 160 k → 332 k (no medí FPS).
- QA: bandejas, carros, contenedor zona media, torres y jabas vistos en captura. Maxisacos y recicladora de cerca: no verificados.
- Pendiente: rack del patio con puertas (sigue del sim), pallets insertos en racks de bodega, rendimiento.

## v83 · 22-11-2026 · publicada como versiones 109–110
- Respaldo: respaldos/2026-11-22_v83_publicada (v82 = versión 108).
- Caricatura retirada: botón, guardado y entradas de la prueba de rendimiento; queda siempre en estilo realista.
- Auditoría automática (inventario de 3.080+ mallas contra los 25 muros y 73 pilares del plano, más búsqueda de objetos sin apoyo):
  · cajas del sim (tras_carga_cajas, 729 instancias) duplicadas sobre los pallets del kit en trastienda → anuladas; en recepción y vestíbulo flotaban a 14 cm porque sus pallets estaban ocultos → reemplazadas por pallets del kit.
  · muro de la ochava (est_pintura_blanca/gris) y dintel de drywall del modelo de bodega encimados al muro Blender → ocultos; film suelto sobre la puerta bodega→sala → oculto.
  · puertas de escape del muro poniente (z 12,6 y 50,4) quedaban dentro del muro Blender → puertas dobles nuevas en Blender (marco, barra antipánico, letrero de salida) y 57 piezas del sim ocultas.
  · sin corregir (menores): rack de la sala que entra 6 cm en el muro norte de bodega; muros del baño de recepción coplanares con el muro Blender.
- Mejora visual: modo «Planos de cine» (6 tomas: pasillo de bodega, grúa alta, corredor bajo, corredor sur, travelling del patio, grúa del patio; formato 2,39:1, viñeta, grado de color, mapeo de tono AgX solo en ese modo). Esc o clic para salir.
- QA: planos 0–4 vistos al inicio y al final; plano 5 corregido (inicio quedaba tras la marquesina) y verificado solo cerca de su inicio; puerta de escape z 12,6 no verificada visualmente.

## v84 · 24-11-2026 · publicada como versión 111
- Gabinetes de red húmeda del corredor poniente (rh138 z 10,47 y rh139 z 48,95) quedaban dentro de los pilares: build_plano.py los monta en la cara del pilar hacia el pasillo (x −58,22). Edificio reconstruido en Blender (techo_*.json?v=84).
- Sala: 875 piezas de góndolas, repisas, productos y botellas que atravesaban pilares se anulan (la góndola queda cortada en el pilar). Bloque v84 en index.html, repetido a los 5/16/42 s.
- Patio: murete gris del sim junto a la puerta de escape de z 49,4 que cruzaba el muro poniente: oculto.
- Auditoría con inventario nuevo: kit de Blender sin choques con muros/pilares/cámaras (salvo cables y bandejas que se anclan al muro sur y el perchero colgado del pilar z 60,9: menores).
- Revisado contra «coleccion de bugs»: red húmeda en mitad del pasillo y bandeja/red que atravesaba la viga → corregidas desde v80; cajas insertas en trastienda → v83.
- Respaldo previo: respaldos\2026-11-24_antes_v84.

## v85 · 24-11-2026 · publicada como versiones 112 (kit) y 113 (edificio)
- Red húmeda y bandejas de la trastienda rehechas según fotos «redhumedaybandejadecables…» y videos del recorrido (recepción→bodega, bodega→merma, bodega→cámara deli).
- Pasillo sur: matriz A junto a los pilares del muro de la calle (z 2,9) y matriz B junto al muro de la sala (z 4,4), a 6,5 m; dos bandejas lado a lado al centro (z 3,45 y 3,88, a 6,1 m). Se cruzan junto al montante de bombas (x −3,0).
- Corredor poniente: A (x −58,15) y B (x −57,8) juntas por el lado del muro poniente; bandejas al centro (x −57,2 y −56,77).
- En el pilar del borde del 2º nivel (z ≈ 18): A baja junto al pilar y sigue sola bajo la losa (3,08 m) hasta recepción; B sigue arriba sobre el 2º nivel [SUPUESTO: recorrido de B sobre el 2º nivel, no visible] y alimenta la matriz sala norte.
- Bandejas: bajan pegadas a la losa entre z 15,4 y 18 y suben entre z 69,2 y 71,6 hacia recepción.
- Quitado: matriz al centro del corredor (x −57), ramales duplicados del corredor y las bandejas del plano que corrían en paralelo (o772, o777, bj1–3, bk4–6).
- Respaldo previo: respaldos\2026-11-24_antes_v85 (build_tras) y outputs v85/respaldo.

## v86 · 24-11-2026 · retiro definitivo de objetos antiguos (solo index.html)
- Causa encontrada: lo retirado se ocultaba con visible = false y el cambio de vista (Desde arriba ↔ 1ª persona) volvía a encender todo el grupo del cielo de la trastienda (SALA.techos): reaparecían las cañerías rojas antiguas del sim (cielo_cañeria), los cielos grises a 7,38 m, los cables de los LED viejos, los lazos de bandeja y las barandas de las cámaras.
- Ahora todo lo retirado lleva un material invisible (retirar()), que ningún cambio de vista revierte. Se agregan cielo_cañeria, tras_cable y tras_bandeja a la lista OCU80.
- Patio: restos del contenedor verde y de la recicladora antiguos (8 mallas y 6 patas de plataforma) retirados.
- Ductos de tableros de cámaras que atravesaban la losa del 2º nivel: 10 recortados a 3,18 m.
- Mapa y lista de reemplazos publicados como artefacto aparte (mapa_reemplazos.html).

## v87 · 24-11-2026 · publicada como versión 115 (solo index.html)
- Método: inventario de toda la escena en dos estados (al cargar y tras cambiar de vista, techo, sala y maqueta), comparación por fuente (Blender edificio, kit, modelo base de bodega, simulador) y detección de lo que vuelve a aparecer.
- Bodega: la red húmeda del modelo base (nave_cañeria_roja matriz a 6,3 m, est_cañeria_roja bajadas, est_rociador) nunca se había retirado y quedaba junto a la red de Blender. Retirada con material invisible, junto con est_conduit_gris (conduits del techo viejo) y tras_cañeria_roja (cañerías viejas del montante de bombas del vestíbulo).
- Revisado sin cambios: sala (red y luces viejas ya retiradas; los ductos blancos del simulador no tienen reemplazo y se mantienen), vestíbulo (la bandeja negra es la de Blender), banderines del vestíbulo, racks y jaulas de la bodega (vigentes).
- Pendiente de decisión: muros de la bodega y del vestíbulo del modelo base (9–13 cm delante de los muros de Blender, sin parpadeo).
- Mapa de reemplazos ampliado a bodega y sala (versión 2).
