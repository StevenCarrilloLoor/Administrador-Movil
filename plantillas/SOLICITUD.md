# Solicitud de publicación
**Estado:** PENDIENTE
**App:** <nombre en apps/registro.json, p. ej. buscador-geiger>
**Versión:** <versionCode> (<versionName>)
**AAB:** <carpeta de la app>\app\build\outputs\bundle\release\app-release.aab (SIN firmar)
**Guion:** <carpeta de la app>\pruebas-lab\humo.json
**Instancia usada:** <N>
**Pista pedida:** internal
**Fecha:** <dd-mmm-aaaa hh:mm, hora de Ecuador>
**Conversación:** <título de la conversación de la app>

## Qué cambia
- <una línea por cambio que note el usuario>

## Evidencia (comando → salida, pegada)
- Compilación, pruebas y lint: `<comando>` → `<BUILD SUCCESSFUL, N pruebas>`
- `movil.bat revisar <aab>` → `"ok": true` (o bloqueos y por qué)
- Laboratorio: `movil.bat probar <aab> --instancia <N> --guion <guion>` → `"ok": true`, evidencia `<ruta del JSON>`
- Teléfono real (si aplica): <lista, fecha y resultado>

## Permisos y datos
- Permisos nuevos o quitados: <ninguno | lista>
- Qué datos salen del teléfono y a dónde: <ninguno | lista>
- ¿Cambia la política de privacidad o Seguridad de los datos?: <no | qué>

## Notas de la versión (es-419, ≤ 500 caracteres)
<texto>

## Riesgos conocidos
- <lo que no se probó y por qué>
