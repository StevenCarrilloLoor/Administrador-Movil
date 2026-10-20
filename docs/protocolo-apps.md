# Protocolo entre las conversaciones de cada app y el Administrador Móvil
**Qué es:** cómo trabajan juntas la conversación de administración y la de cada app, y cuándo una versión está
«lista para subir». **Cuándo leerlo:** al abrir la conversación de una app nueva, antes de pedir una publicación y al
revisar una solicitud. **Estado:** VIVO — acordado con Steven el 20-oct-2026; SIN COMPROBAR con una solicitud real.
**Fuente de verdad:** este documento, `apps/registro.json` y los archivos `publicacion/` de cada app.
**Sirve para:** que cada app avance en su propia conversación y solo se publique lo que el administrador da por bueno.

## Lo esencial
- **Filosofía de Steven (20-oct-2026):** «cada aplicación en desarrollo va a tener su propia conversación para revisarla
  y mejorarla, y ellas deberán responder a ti, ya que tú eres quien las administra y sabe cuándo están listas para subir».
- **Un dueño por cosa.** La conversación de una app es dueña de su carpeta. La de administración es dueña de este hub,
  del laboratorio, de las firmas, de la credencial de Play y de lo que se sube. Steven decide lo que llega a otras personas.
- **El canal que dura son archivos:** la app escribe `publicacion/SOLICITUD.md` en SU carpeta; el administrador
  contesta en `publicacion/RESPUESTA.md` de esa misma carpeta (cada archivo tiene un solo escritor). Los mensajes entre
  conversaciones solo avisan.
- **Administración:** conversación «Administrador de proyectos móviles», id `local_1c874961-23f5-4bc4-910d-17ace6117b46`
  (puede cambiar si Steven abre otra: el título manda; `movil.bat solicitudes` funciona sin ella).

## Quién hace qué
| | Conversación de la app | Administrador Móvil | Steven |
|---|---|---|---|
| Código, pruebas, lint | Sí | Revisa la evidencia | — |
| Laboratorio | Su instancia (`instancia_lab` del registro), nunca la 0 | Instancia 0 y mantenimiento (`preparar`, `renovar-limpia`) | — |
| Firmas, credencial de Play | **Nunca** | Sí | Copia de seguridad |
| Subir a prueba interna | No | Sí, cuando la versión está lista | — |
| Subir a cerrada/abierta/producción | No | Sí, tras su «sí» en el chat | Decide |
| Formularios de Play Console | Aporta datos (permisos, qué se recoge) | Redacta | Rellena y envía |
| Ficha `apps/<app>.md` y `registro.json` | Lee | Escribe | — |

## Rutas fijas de cada app (las da por hechas todo el protocolo)
| Qué | Dónde |
|---|---|
| AAB de release sin firmar | `<carpeta de la app>\app\build\outputs\bundle\release\app-release.aab` (Gradle; Expo: `android\app\build\…`) |
| Guion del laboratorio, sin paso `instalar` | `<carpeta de la app>\pruebas-lab\humo.json` (formato en `..\Android Laboratorio\AGENTS.md`, «Guiones») |
| Solicitud / respuesta | `<carpeta de la app>\publicacion\SOLICITUD.md` / `RESPUESTA.md` |
| Instancia del laboratorio | `instancia_lab` en `apps/registro.json`; si está ocupada (`lab estado`), otra libre de la 2 a la 7, dicha en la solicitud. La 0 es del administrador (y del canario, que es suyo) |
La hora de las solicitudes es la del reloj del PC, que está en hora de Ecuador (MEDIDO: keytool imprime `ECT`).

## Cómo se hace (una versión, de la app a Play)
1. **La app desarrolla** en su conversación con su `AGENTS.md` (que incluye el bloque de `plantillas/AGENTS-app.md`).
   Compilar es cosa suya, en su carpeta.
2. **La app se prepara** y pega en la solicitud lo que salga:
   - su compilación con pruebas y lint (su `verificar` o `gradlew.bat bundleRelease testReleaseUnitTest lintRelease`)
     → BUILD SUCCESSFUL;
   - `movil.bat revisar <app-release.aab>` → `"ok": true` (o los bloqueos, explicados);
   - **la prueba de ESTA versión en el laboratorio, con el AAB de release** (no el APK de depuración):
     `movil.bat probar <app-release.aab> --instancia <N> --guion <carpeta>\pruebas-lab\humo.json` → `"ok": true`.
     Instala el AAB limpio con bundletool, lo abre, comprueba que no se cierra y corre el guion. Después
     `python lab.py apagar --instancia <N>`. Un release no es depurable: `archivo_app` y `datos` leen con root, que el
     laboratorio permite;
   - si usa hardware que el emulador no tiene (Bluetooth), su lista de pruebas en el teléfono real, con fecha.
3. **La app escribe la solicitud**, copiando `plantillas/SOLICITUD.md` a `<su carpeta>\publicacion\SOLICITUD.md`, con
   `Estado: PENDIENTE`, y avisa: busca con `ListAgents` la conversación «Administrador de proyectos móviles» y le manda
   con `SendMessage` una línea como «Solicitud PENDIENTE de <app> versión <n> en <ruta>, instancia usada <N>». Si no
   aparece, pide a Steven que avise. El archivo manda: `movil.bat solicitudes` la ve aunque nadie avise.
4. **El administrador revisa** (`movil.bat solicitudes` → la app sale en `pendientes`): pasa la lista de abajo, repite
   `movil.bat revisar` y `movil.bat probar <aab> --instancia 0 --guion <guion de la app>`, y contesta en
   `publicacion/RESPUESTA.md` con `Veredicto: FALTA` (qué, concreto) o `LISTA`.
5. **Si está LISTA:** `movil.bat firmar` → `movil.bat probar <…-firmado.aab>` → `movil.bat play subir` a la pista
   interna. Para cualquier otra pista, se pregunta antes a Steven en el chat. El resultado va a `RESPUESTA.md`
   (`Veredicto: SUBIDA`, pista y versionCode), a la tabla de versiones de `apps/<app>.md` y a `CAMBIOS.md`.
6. **La app lee la respuesta** al empezar cada turno de trabajo sobre publicación, y no vuelve a pedir hasta corregir.

## Lista «lista para subir» (todas las casillas, con evidencia pegada)
- [ ] AAB de `bundleRelease`, **sin firmar**, no depurable, versionCode mayor que el último de la ficha.
- [ ] `movil.bat revisar` sin bloqueos: targetSdk ≥ 36, 16 KB, versionCode válido.
- [ ] Compila; pruebas en verde; lint sin errores. Prueba nueva para cada arreglo con síntoma.
- [ ] `movil.bat probar` en verde con el AAB de ESTA versión y su guion (`evidencia` JSON citado). Un cierre que el
      guion provoca a propósito va con `espera_fallo` + `debe_contener`; cualquier otro cierre suspende.
- [ ] Hardware que el emulador no tiene: lista manual en teléfono real con fecha y resultado.
- [ ] Permisos nuevos o cambiados: listados con su declaración (`declaraciones_play`) y su efecto en Seguridad de los datos.
- [ ] La política de privacidad cubre lo que hace esta versión.
- [ ] Notas de la versión en español (`es-419`), concretas, sin promesas.
- [ ] Si cambió lo que se ve: capturas nuevas sacadas con `lab.py captura` (para la ficha de Play).
- [ ] Icono propio de la app (regla 11 del CLAUDE.md global).
- [ ] Nada de secretos en el repo de la app (búsqueda de `password`, `api_key`, `.jks`, `.p12`, `.json` de servicio).

## Qué NO se toca y por qué
- La conversación de una app no edita este hub, ni `registro.json`, ni la carpeta de otra app, ni la instancia 0 del
  laboratorio: dos escritores en el mismo sitio se pisan.
- La conversación de una app no apaga instancias que no son la suya (`lab.py apagar --todas` solo lo usa el administrador).
- Nadie sube nada saltándose la lista: el administrador es el único que sabe qué hay en cada pista.

## Cómo verificar
`movil.bat solicitudes` → `pendientes: []` después de contestar todas; la ficha de cada app con su última versión.
