# API de Google Play: dar acceso y usarla
**Qué es:** cómo se da a la IA permiso para subir versiones por la Google Play Developer API (androidpublisher v3) y
cómo se usa. **Cuándo leerlo:** la primera vez (Steven tiene que crear la cuenta de servicio) o si una orden `play`
falla. **Estado:** VIVO — SIN COMPROBAR contra Google: falta la credencial (20-oct-2026). Probado sin red: orden de
llamadas, borrado del edit si falla, permisos por pista y cifrado de la credencial (`pruebas/test_movil.py`).
**Fuente de verdad:** `movil.py` (`play_*`, `credencial_*`) y developers.google.com/android-publisher. **Sirve para:**
que las subidas a pruebas no dependan de que Steven pulse nada.

## Lo esencial
- Una **cuenta de servicio** de Google Cloud, invitada en Play Console con permiso de **pistas de prueba**, y su clave
  JSON **cifrada con DPAPI** en `%USERPROFILE%\.secretos-moviles\play-api.dpapi` (solo la descifra el usuario `steve`
  de este PC). El JSON original se borra.
- Ya no hace falta vincular un proyecto de Cloud en la consola: basta invitar el correo de la cuenta de servicio. VERIFICADO.
- La API **no** crea apps ni hace la primera subida ni rellena formularios: eso es de Play Console. VERIFICADO.

## Dar acceso a la API (Steven, una vez; unos 15 minutos)
1. En console.cloud.google.com con su cuenta de Google de desarrollador: crear un proyecto (p. ej. `play-publicacion`).
2. APIs y servicios → Biblioteca → «Google Play Android Developer API» → Habilitar.
3. IAM y administración → Cuentas de servicio → Crear: nombre `publicador-play`; sin roles de Cloud.
4. En esa cuenta → Claves → Agregar clave → JSON. Se descarga un `.json` (es un secreto: no se abre ni se pega en el
   chat). Si Cloud lo bloquea por la política `iam.disableServiceAccountKeyCreation`, avisar a la IA (con un Gmail sin
   organización no debería pasar; SUPUESTO).
5. En Play Console → Usuarios y permisos → Invitar usuarios: el correo de la cuenta de servicio
   (`publicador-play@<proyecto>.iam.gserviceaccount.com`). Permisos, por app o para todas: **«Lanzar apps en pistas de
   prueba»** (Release apps to testing tracks). Solo si se quiere que la IA cambie fichas y capturas: «Gestionar la
   presencia en la tienda». Producción NO: esa la publica Steven o se da más tarde a propósito.
6. Guardar la credencial (Steven en su terminal, o la IA si Steven lo pide):
   `movil.bat play credencial guardar "C:\Users\steve\Downloads\<archivo>.json"` → debe salir `"guardada"` y el
   correo de la cuenta de servicio; nunca la clave privada.
7. Borrar el `.json` original con Mayús+Supr (Steven).
8. Comprobar: `movil.bat play credencial comprobar` → `"ok": true` (pide un token a Google; no lo muestra). Y con una app
   ya creada en la consola: `movil.bat play estado <paquete>` → la lista de pistas.

## Órdenes
| Para qué | Comando | Debe salir |
|---|---|---|
| Pistas y versiones de una app | `movil.bat play estado com.steven.buscadorble` | `pistas` con sus releases |
| Subir a prueba interna | `movil.bat play subir <app> <…-firmado.aab> --notas-es "…"` | `pista: internal`, `version_code` |
| App que nunca se publicó | añadir `--estado draft` y terminar en la consola | `estado: draft` |
| Subir a prueba cerrada | `… --pista alpha --confirmo` (solo tras el «sí» de Steven en el chat) | `pista: alpha` |
| Producción gradual | `… --pista production --estado inProgress --fraccion 0.2 --confirmo-produccion` | `pista: production` |
| Sin enviar a revisión | `… --sin-revision` (Steven la envía en la consola) | `enviado_a_revision: false` |

`play subir` antes de llamar a Google: pasa `revisar` (bloqueos fuera), comprueba que el AAB está firmado con la clave
de subida de esa app y que el paquete coincide con `apps/registro.json`. Si algo falla a mitad, borra el edit abierto.

## Si algo falla
| Síntoma | Causa | Qué hacer |
|---|---|---|
| «No hay credencial de la API de Play en este PC…» (MEDIDO) | Pasos 1-6 sin hacer | Hacerlos |
| «DPAPI falló…» | Otro usuario de Windows u otro PC | Repetir el paso 4 (clave nueva) y el 6 en este PC |
| «Google rechazó la credencial…» | Clave borrada o cuenta de servicio desactivada en Cloud | Clave nueva (paso 4) y `credencial guardar … --reemplazar` |
| «La API de Play respondió 403…» | La cuenta de servicio no está invitada, o sin permiso para esa app, o la invitación aún no se aplicó | Revisar el paso 5; esperar unos minutos (SUPUESTO el tiempo) |
| «…404…» | La app no existe o no tiene primera subida manual | `docs/publicar-en-play.md`, pasos 3-4 |
| «…Only releases with status draft may be created on draft app» (SUPUESTO) | La app nunca se publicó | `--estado draft` |
| «La pista 'alpha' llega a testers: exige --confirmo…» (MEDIDO) | Falta el «sí» de Steven | Preguntarle en el chat |

## Qué NO se toca y por qué
- La IA no abre el JSON ni lo copia: solo lo lee `credencial guardar`, que imprime el correo, nunca `private_key`.
- Cuotas: 3.000 consultas por minuto por grupo (VERIFICADO); no se hacen bucles de reintentos.
- Testers por API: solo Grupos de Google (`edits.testers`), no correos sueltos (VERIFICADO). PENDIENTE: orden
  `play testers` cuando exista el grupo.

## Cómo verificar
`movil.bat play credencial comprobar` → `"ok": true`; `movil.bat play estado <paquete>` → pistas reales.
