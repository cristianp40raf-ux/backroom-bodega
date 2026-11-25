# Backroom Bodega

Simulador 3D de la bodega, la trastienda y la sala (Three.js), con los modelos hechos en Blender.

## Estructura
- `index.html` y los `.json` de la raíz: el simulador tal como se publica (versión v87).
- `blender/edificio/`: `build_plano.py` (edificio, red húmeda, bandejas del plano), `plano_final2.json`, texturas `tex2k/` y generadores `gen/`.
- `blender/trastienda/`: `build_tras.py` (kit de la trastienda y el patio), texturas y mapa.
- `modelos/`: los `.glb` que exporta Blender (edificio y kit).
- `docs/`: bitácora de ajustes, esquema de bugs y mapa de reemplazos.

## Reglas del proyecto
- El modelo se hace en Blender. Sin logos ni marcas reales; personas solo como IDs.
- No bajar la calidad de las texturas.
- Lo no verificado se marca SUPUESTO.
