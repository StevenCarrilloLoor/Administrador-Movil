# Bitácora del Administrador Móvil
**Qué es:** por qué cada cosa es como es, numerado, con su verificación y su commit. **Cuándo leerlo:** antes de
cambiar algo que parece raro. **Estado:** VIVO.

## 1 — 20-oct-2026: nace el Administrador Móvil
**Motivación.** Steven consiguió su cuenta de Google Play (personal) y nombró a la IA administradora de sus apps
móviles, con esta filosofía: cada app en desarrollo tiene su propia conversación, que responde al administrador, y el
administrador decide cuándo está lista para subir. iOS queda para después (no tiene Mac). Autorizó descargar las
herramientas oficiales (~3 GB).

**Qué se hizo.**
- Inventario del PC: Android Studio 2025.3, SDK con platforms 35/36.1, emulador 36.4.9, WHPX activo, JDK Corretto 17,
  Node 22, Python 3.13; app ya existente `Buscador Bluetooth Geiger`.
- Investigación con 5 agentes Sonnet y verificación adversarial con otros 5 (`docs/investigacion-20261020.*`): Play exige
  targetSdk 36 desde el 31-ago-2026, 12 testers × 14 días para cuentas personales, 16 KB desde el 1-feb-2027, etc.
  (`docs/requisitos-play.md`).
- Instalado: cmdline-tools 23.0 (sha1 comprobado contra el catálogo de Google), `platforms;android-36`,
  `build-tools;36.0.0`, `system-images;android-36;google_apis;x86_64`, bundletool 1.18.3 (sha256 comprobado contra
  GitHub), venv con google-api-python-client 2.201.0, google-auth 2.62.0, keyring 25.7.0, pytest 9.1.1.
- `movil.py`: doctor, solicitudes, firma crear/comprobar, firmar, apk-universal, revisar (targetSdk, depurable,
  versionCode, 16 KB por ELF, declaraciones por permisos), probar (en el laboratorio), play credencial/estado/subir.
- Laboratorio hermano `..\Android Laboratorio` (su propio git) y el canario (agente Opus, AGP 9.4.0).
- Documentos: protocolo con las apps, requisitos, publicar paso a paso, firma, API, tecnología e iOS; fichas y registro.

**Verificación (MEDIDA).** Hub: `pytest -q` 17 passed; `-m herramientas` 2 passed (clave real de prueba creada,
firmado un AAB real, huella comprobada, sin restos en la bóveda). Cadena con el canario: revisar sin bloqueos → firmar
(sha256 `8E:96:C8:5A:…:38:AD`) → probar en el laboratorio con el AAB firmado (8/8, arranque en frío 971 ms) →
APK universal verificado. API de Play: SIN COMPROBAR (falta la credencial de Steven).

**Commit:** `c9e9a1e`.

## 2 — 20-oct-2026: auditoría en contexto limpio y arreglos
**Motivación.** Regla «verificar como un auditor»: 2 revisores Opus (`lab.py`, `movil.py`), 1 verificador Opus que
intentó refutar cada hallazgo, y 2 pruebas de fuego Sonnet que hicieron tareas reales solo con la documentación
(manejar el laboratorio; hacer de conversación de app y preparar una solicitud). 22 hallazgos, todos confirmados
(14 del laboratorio, en su `CAMBIOS.md` nº 2; 8 de aquí). Lo grave del laboratorio (LAB-01): el paso que debía
demostrar «cierre provocado detectado» pasaba sin cierre. Las pruebas de fuego terminaron sin órdenes fallidas, pero
tuvieron que adivinar rutas y reglas.
**Qué se hizo aquí** (primero una prueba que fallara por cada hallazgo, en `pruebas/test_movil.py`):
- PUE-01: `wear:production`, `tv:production`, `automotive:production` y `Production` exigen `--confirmo-produccion`.
- FIR-01: se leen TODAS las huellas de firmantes (debe haber una, la de subida); `_firmado` exige código 0, «jar
  verified» y ninguna «unsigned entries». TRAMPA MEDIDA: `jarsigner -verify -strict` sale con 4 con cualquier clave de
  Android (autofirmada), así que no sirve.
- FIR-02: `firmar` borra el `-firmado.aab` si no verifica; `apk-universal` valida el AAB y su paquete antes de leer la
  clave y verifica el APK (huella incluida) antes de moverlo a su destino.
- FIR-03: el temporal con la contraseña va a `%USERPROFILE%\.secretos-moviles\tmp` y se limpian restos al empezar.
- PUE-02: `play subir` exige `"publicable": true`. PUE-03: los edits se borran también con fallo de `list` y con Ctrl+C.
- SOL-01: `leer_solicitud` se para en la cabecera y no pisa claves; `solicitudes` salta apps sin carpeta.
- Documentación: rutas fijas de cada app (AAB, `pruebas-lab\humo.json`), la app prueba SU versión con
  `movil.bat probar <app-release.aab>`, instancia libre si la suya está ocupada, cómo avisar por `ListAgents`, hora
  del PC = Ecuador, borrador de política de privacidad.
**Verificación (MEDIDA).** `pytest -q` 31 passed; `-m herramientas` 2 passed sin restos en la bóveda; mutación
dirigida 14/14 mutantes muertos (sobrevivió uno al principio, «la solicitud pisa claves»: se añadió su prueba). Cadena
real con el canario: firmar → revisar (`firmado: true`, un firmante) → APK universal verificado (0 restos en `tmp`) →
`play subir canario` rechazado por no publicable → firmar dos veces rechazado.
**Commit:** `e94169b`.

## 3 — 20-oct-2026: subida a GitHub (orden de Steven, coordinada por «ADMINISTRADOR DE GITHUB Y CARPETAS»)
**Motivación.** Steven: «hay que subirlos para que se documente todo, con su exe, sus instrucciones y sus dependencias
de instalación; por ahora los entrenadores van en privado y lo demás en público; cuidado con subir credenciales».
Llegó reenviada por la sesión coordinadora, así que el «sí» se le pidió a Steven en esta conversación, con los
nombres, la visibilidad y la firma del APK: «Sí, los tres así» y «Con su clave de subida».
**Qué se hizo.**
- README para personas en el hub y en el laboratorio; `.gitignore` de secretos en el laboratorio y en el Buscador.
- Clave de subida del Buscador creada.
- El Buscador recompilado (`verificar.bat` en verde), con su AAB de release revisado, firmado, convertido en APK
  universal y probado en el laboratorio.
- Repos creados: `Administrador-Movil` (público), `Android-Laboratorio` (privado) y `Buscador-Bluetooth-Geiger`
  (público), este con la Release `v4.0-fase4`.

**TRAMPA (MEDIDA).** Un comentario del `.gitignore` que empezaba por la palabra «Secretos» seguida de dos puntos y
otra palabra parece una asignación de clave y dio ALTO 1 en `revisar_secretos.py`. Se corrigió la redacción y se
rehízo el commit, que aún no estaba subido, para que el historial quedara limpio.

**TRAMPA (MEDIDA): la misma frase citada en esta bitácora volvió a dar ALTO 1, y se subió.** El guion encadenaba
`revisar_secretos.py … | tail -1` y después `git push`; la tubería devolvía el código de `tail` (0), así que `set -e`
no paró. No había ningún secreto, solo la cita de la frase de arriba. El commit `6848468` quedó en el historial público
con ese falso positivo: no se reescribe, porque nada de `push --force` y no hay nada que ocultar. Desde el commit
siguiente el árbol vuelve a dar ALTO 0, y `--historia` seguirá marcando ALTO 1 en `6848468 CAMBIOS.md`, que es
**falso positivo conocido**. Regla nueva: antes de un `push`, el escáner se comprueba por su código de salida
(`python -I revisar_secretos.py <carpeta> --todo && python -I revisar_secretos.py <carpeta> --historia && git push`),
nunca con una tubería delante. Después, la sesión coordinadora cambió dos cosas:
- el escáner ya no toma por clave una palabra suelta en comentarios ni en `.md`;
- la guía lleva ya la regla del `&&`.

La huella del aviso de `6848468` (`683b0ed030f8`) está en `.secretos-revisados`, con su motivo, y `--historia` vuelve a
dar ALTO 0.

**Verificación (MEDIDA).**
- `revisar_secretos.py --todo` y `--historia`: ALTO 0 en los tres.
- `gh repo view`: visibilidades y temas correctos.
- El APK descargado de la Release tiene el mismo SHA-256 que el local (`4FBACD98…E8AD05`).

**Commit:** el de esta entrada.
