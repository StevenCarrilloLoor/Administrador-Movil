# Publicar una app en Google Play, de cero a producción
**Qué es:** el camino completo para una app nueva con la cuenta PERSONAL de Steven, separando lo que hace Steven en Play
Console de lo que hace la IA. **Cuándo leerlo:** al llevar una app por primera vez a Play, o para saber en qué paso está.
**Estado:** VIVO — SIN COMPROBAR con una app real (el 20-oct-2026 todavía no se ha creado ninguna en la consola); los
requisitos de cada paso están VERIFICADOS en `docs/requisitos-play.md`. **Fuente de verdad:** Play Console y
`docs/requisitos-play.md`. **Sirve para:** no saltarse un paso que bloquea semanas después.

## Lo esencial
- El reloj que manda son los **14 días con 12 testers**: el paso 5 se arranca en cuanto haya una versión mínima digna.
- **Steven** hace lo que exige una persona en Play Console (identidad, crear la app, formularios, testers, pedir
  producción). **La IA** prepara textos, firma, prueba, sube por API y lleva el calendario en la ficha de la app.
- Cada subida pasa antes por `docs/protocolo-apps.md` («lista para subir»).

## Cómo se hace (pasos)
0. **Una vez por cuenta (Steven):** completar identidad, teléfono y correos; verificar el dispositivo con la app Play
   Console en su teléfono Android (Inicio de la consola → QR). Comprobar en Configuración > Cuenta de desarrollador que
   está verificada → debe salir sin tareas pendientes en Inicio.
1. **Una vez por cuenta (Steven + IA):** dar acceso a la API (`docs/api-play.md`) → `movil.bat play credencial comprobar`
   debe decir `"ok": true`.
2. **Antes de crear la app (IA):** la app tiene `targetSdk 36`, su icono propio, su nombre de paquete definitivo (no se
   cambia nunca: para apps nuevas, `io.github.stevencarrilloloor.<app>`, que es único porque la cuenta de GitHub es suya;
   las ya empezadas conservan el suyo si Play lo acepta) y su clave de subida:
   `movil.bat firma crear <app>` → debe salir su `sha256`. Copia de seguridad: `docs/firma-y-claves.md`.
3. **Crear la app (Steven, con textos de la IA):** Play Console → Crear app: nombre, idioma por defecto español
   (Latinoamérica, `es-419`), app o juego, gratis o de pago (gratis ya no puede pasar a pago), aceptar declaraciones.
   La IA le deja preparados en `apps/<app>.md`: nombre (≤ 30), descripción corta (≤ 80) y completa (≤ 4000), categoría,
   correo de contacto y la URL de la política de privacidad.
4. **Primera subida, a mano (Steven) — la API no puede hacer la primera:** la IA deja el AAB firmado
   (`movil.bat firmar <app> <aab>`) y Steven lo sube en Pruebas > Prueba interna > Crear versión, con las notas que le
   pasa la IA. Desde aquí las siguientes las sube la IA: `movil.bat play estado <paquete>` → debe listar la pista
   `internal` con ese versionCode.
5. **Contenido de la app (Steven, con textos de la IA):** política de privacidad (URL pública), Seguridad de los datos,
   clasificación de contenido (cuestionario IARC), público objetivo, anuncios, acceso a la app (credenciales si hay login)
   y las declaraciones que listó `movil.bat revisar` (`declaraciones_play`). Sin esto no se puede pasar a prueba cerrada.
6. **Prueba cerrada con 12+ testers (Steven elige a la gente; la IA sube):** crear la pista cerrada (`alpha`) con una
   lista de testers. Recomendado: un **Grupo de Google** como lista, porque la API solo gestiona testers por grupos
   (`edits.testers`) y así la IA puede añadir gente sin tocar la consola. Cada tester acepta el enlace de opt-in y
   **se queda inscrito 14 días seguidos**. Subir a `alpha` exige el «sí» de Steven en el chat (`--confirmo`). La IA anota
   el día 1 en la ficha de la app y avisa el día 14.
7. **Durante los 14 días (IA):** recoger y resumir los comentarios de los testers en la ficha de la app (Google los
   pregunta en el paso 8), corregir con la conversación de la app y subir versiones a `alpha` con el «sí» de Steven.
8. **Pedir producción (Steven, con el borrador de la IA):** Panel → «Apply for production». La IA redacta las tres
   partes con datos reales de la ficha (cómo se reclutó, cómo usaron la app, qué se cambió por sus comentarios). Google
   responde en ~7 días.
9. **Producción (IA tras el «sí» de Steven para ESA versión):** `movil.bat play subir <app> <aab> --pista production
   --estado inProgress --fraccion 0.2 --confirmo-produccion` (despliegue gradual) y, si no hay cierres, completar.

## Si algo falla
| Síntoma | Causa | Qué hacer | Comando |
|---|---|---|---|
| `play estado`: 404 o «Package not found» (SUPUESTO el texto) | La app no existe en la consola o aún no tiene una primera subida manual | Pasos 3 y 4 | `movil.bat play estado <paquete>` |
| `play subir`: 403 | La cuenta de servicio no tiene permiso en esa app | `docs/api-play.md`, «Si algo falla» | — |
| No aparece «Apply for production» | Faltan días o testers | Ver el contador en el Panel; seguir el paso 7 | — |

## Qué NO se toca y por qué
- La IA no rellena formularios ni pulsa «Enviar» en Play Console por su cuenta: son declaraciones legales de Steven.
- Nada sale de la pista interna sin el «sí» de Steven en el chat para esa versión: llega a otras personas.
- El nombre de paquete y la clave de firma no se cambian después del paso 4.

## Cómo verificar
`movil.bat play estado <paquete>` → la pista y el versionCode esperados; en la ficha `apps/<app>.md`, la tabla de versiones al día.
