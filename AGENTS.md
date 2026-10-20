# Administrador Móvil — guía para IAs
**Qué es:** el centro desde el que una IA administra las apps móviles de Steven: requisitos de Google Play, firma,
revisión, pruebas en el laboratorio y publicación por la API. Cada app se desarrolla en su propia conversación y le
responde a este administrador (`docs/protocolo-apps.md`). **Cuándo leerlo:** siempre que se trabaje en publicar o
administrar una app móvil. **Estado:** VIVO — comprobado el 20-oct-2026: laboratorio y cadena de firma probados de punta
a punta con el canario, auditados en contexto limpio y corregidos (`CAMBIOS.md` nº 2); API de Play SIN COMPROBAR (falta
la credencial, la crea Steven). **Fuente de verdad:** `movil.py`,
`apps/registro.json` y los documentos de `docs/`.

## Lee primero, en este orden
1. Este archivo. 2. `LEEME-INDICE.md` (qué documento contesta cada pregunta). 3. `docs/protocolo-apps.md` si hay una app
de por medio. 4. `docs/requisitos-play.md` antes de dar algo por publicable. 5. `PENDIENTES.md`.

## Situación (20-oct-2026)
- Cuenta de Google Play **personal** de Steven (desde el 20-oct-2026). iOS todavía no: no tiene Mac
  (`docs/tecnologia-e-ios.md`).
- Apps: `apps/registro.json` (canario = fixture; buscador-geiger = en desarrollo, le falta targetSdk 36 y AGP 9).
- Esta conversación de administración: «Administrador de proyectos móviles», `local_1c874961-23f5-4bc4-910d-17ace6117b46`.

## Órdenes de casi todas las sesiones
`movil` = `& "C:\Users\steve\Desktop\TRABAJOS GENERATIVOS\Aplicaciones propias\Moviles\Administrador Movil\movil.bat"`
en PowerShell (sin el `&` no se ejecuta). `lab` = `python "C:\Users\steve\Desktop\TRABAJOS GENERATIVOS\Aplicaciones propias\Moviles\Android Laboratorio\lab.py"`.
Todas imprimen JSON y salen con 0 si todo fue bien.

| Para qué | Comando | Debe salir (MEDIDO el 20-oct-2026 salvo SUPUESTO) |
|---|---|---|
| ¿Está todo instalado? | `movil doctor` | `"ok": true`; «credencial Play» FALTA hasta que Steven la cree |
| ¿Hay solicitudes de apps? | `movil solicitudes` | `"pendientes": [...]` |
| ¿Cumple Play este AAB? | `movil revisar <app-release.aab>` | `"ok": true` o `bloqueos` y `declaraciones_play` |
| Crear la clave de subida de una app | `movil firma crear <app> --nombre-comun "<Nombre>"` | `sha256` |
| Firmar | `movil firmar <app> <aab sin firmar>` | `<…>-firmado.aab` con la `sha256` de su clave |
| Probar en el laboratorio | `movil probar <aab o apk> [--guion <json>] [--instancia N]` | `"ok": true`, sin `cierres` |
| APK para un amigo | `movil apk-universal <app> <…-firmado.aab>` | `"verificado": true` (ver TRAMPA en `docs/firma-y-claves.md`) |
| Estado en Play | `movil play estado <paquete>` | pistas (SUPUESTO: sin credencial aún) |
| Subir a prueba interna | `movil play subir <app> <…-firmado.aab> --notas-es "…"` | `pista: internal` (SUPUESTO) |
| Pruebas de esta herramienta | `.venv\Scripts\python.exe -I -B -m pytest -q -p no:cacheprovider` (desde esta carpeta) | `31 passed, 2 deselected`; con `-m herramientas`, `2 passed` y después `cmdkey /list:android-firma-prueba*` → `* NONE *` |
| Laboratorio | `lab estado` · `lab arrancar --instancia N` · `lab apagar --instancia N` | detalle en `..\Android Laboratorio\AGENTS.md` |

## Reglas (con su porqué)
- **Las apps se desarrollan en su conversación; aquí se decide qué se publica.** Lo pidió Steven el 20-oct-2026. Esta
  conversación no edita el código de una app salvo que Steven lo pida: le contesta por `publicacion/RESPUESTA.md`.
- **Nada sale de la pista interna sin el «sí» de Steven en el chat para esa versión.** Llega a otras personas.
  `movil play subir` lo hace cumplir con `--confirmo` y `--confirmo-produccion`.
- **La IA nunca ve un secreto.** Contraseñas de firma en el Administrador de credenciales (`android-firma-<app>`), la
  credencial de Play cifrada con DPAPI en `%USERPROFILE%\.secretos-moviles\`. Prohibido: `cmdkey` con algo que no sea
  `/list`, leer esos archivos con Read/`cat`, imprimir el entorno. Lo que lee la IA queda en el historial.
- **Ninguna app firma su release.** Entrega el AAB sin firmar; así ninguna conversación de app toca una clave.
- **Formularios de Play Console los envía Steven.** La IA prepara los textos (son declaraciones legales suyas).
- **Requisitos con fecha:** `docs/requisitos-play.md` se revisa cada trimestre (próxima: ene-2027) y en el mismo
  commit se cambian `MIN_TARGET_SDK`, `PAGINA_16K` y `PERMISOS_DECLARABLES` de `movil.py`.
- **Un solo SDK para todo** (`%LOCALAPPDATA%\Android\Sdk`, el de Android Studio): dos `adb` de versiones distintas se
  matan el servidor el uno al otro (SUPUESTO conocido). Los AVD del laboratorio sí van aparte (`D:\AndroidLaboratorio\avd`).
- **Se instala solo lo que Steven aprueba** (descarga con nombre, origen y tamaño). Aprobado el 20-oct-2026: cmdline-tools,
  imagen `android-36;google_apis;x86_64`, platform 36, build-tools 36.0.0, bundletool 1.18.3, librerías de la API.

## Dónde vive cada cosa
| Qué | Dónde |
|---|---|
| Este hub (git local) | `C:\Users\steve\Desktop\TRABAJOS GENERATIVOS\Aplicaciones propias\Moviles\Administrador Movil` |
| Laboratorio (git local) y canario | `…\Moviles\Android Laboratorio` |
| AVD, evidencias, construcciones, bundletool | `D:\AndroidLaboratorio\` (`avd`, `evidencias\<fecha>`, `construcciones`, `herramientas`; `pruebas-fuego` = ensayos desechables) |
| Firmas y credencial de Play | `%USERPROFILE%\.secretos-moviles\` (`firmas\<app>\`, `play-api.dpapi`, `tmp\` que se vacía solo) + Administrador de credenciales |
| SDK / JDK | `%LOCALAPPDATA%\Android\Sdk` / `C:\Program Files\Amazon Corretto\jdk17.0.17_10` |
| Apps | Carpeta propia de cada una (`apps/registro.json`, campo `carpeta`); las nuevas en `…\Moviles\<Nombre>` |
| GitHub (20-oct-2026, con el «sí» de Steven) | `StevenCarrilloLoor/Administrador-Movil` (público), `Android-Laboratorio` (privado), `Buscador-Bluetooth-Geiger` (público, Release `v4.0-fase4` con el APK firmado con su clave de subida). Antes de cada `push`: `revisar_secretos.py <carpeta> --todo` y `--historia` con ALTO 0 (`TRABAJOS GENERATIVOS\_archivo\orden-20261020\SUBIR-A-GITHUB.md`) |

## Trampas ya pisadas (detalle en el documento enlazado)
- **TRAMPA: `java` del PATH es Java 8.** Todo lo que compile pone `JAVA_HOME` a Corretto 17.
- **TRAMPA: `sdkmanager` 23 ya no es sdkmanager:** reenvía a la Android CLI (`cmdline-tools\latest\bin\android.exe`) y,
  por ser `.bat`, cmd parte `system-images;android-36;…` por los `;` («Package android-36 not found»). Instalar con
  `& "<SDK>\cmdline-tools\latest\bin\android.exe" --no-metrics sdk install "<paquete>"`.
- **TRAMPA: Compose BOM 2026.09+ exige compileSdk 37** (`docs/tecnologia-e-ios.md`).
- **TRAMPA: un APK universal no se actualiza desde Play** (firma de subida ≠ firma de Play).
- **TRAMPA (MEDIDA): `jarsigner -verify -strict` sale con 4 en TODA clave de Android** (son autofirmadas). La firma se
  da por buena con código 0, «jar verified», sin «unsigned entries» y con UN solo firmante: el de la clave de subida.
- **Pistas de producción también son `wear:production`, `tv:production`, `automotive:production`:** piden
  `--confirmo-produccion`. Las pistas cerradas pueden tener nombre propio: piden `--confirmo`.
- La auditoría del 20-oct-2026 y sus 22 arreglos: `CAMBIOS.md` nº 2 (y el del laboratorio).
- Las del laboratorio (instancias de solo lectura, instantáneas que se cuelgan): `..\Android Laboratorio\AGENTS.md`.
- **Una sesión no deja un `cd` puesto en estas carpetas** (regla 7 de `TRABAJOS GENERATIVOS\MAPA.md`): rutas absolutas.

## Glosario
- **Clave de subida:** la clave propia con la que se firma el AAB que se sube; Google re-firma con la de la app.
- **Pista:** `internal` (prueba interna), `alpha` (prueba cerrada), `beta` (abierta), `production`.
- **Instancia:** emulador del laboratorio n.º N (puerto 5570+2N); la 0 es del administrador.
- **Solicitud / Respuesta:** `publicacion/SOLICITUD.md` (la escribe la app) y `publicacion/RESPUESTA.md` (este hub).
- **Ficha:** `apps/<app>.md`, el estado de publicación de una app.
- **Canario:** la app mínima que prueba el laboratorio y la firma; nunca se publica.
