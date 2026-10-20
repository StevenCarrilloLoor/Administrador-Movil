# Firma de las apps: clave de subida, contraseña y copia de seguridad
**Qué es:** cómo se crean, guardan, usan y recuperan las claves con las que se firman las apps. **Cuándo leerlo:** al
crear la clave de una app, al firmar, al dar un APK a un amigo o si se pierde o filtra una clave.
**Estado:** VIVO — comprobado el 20-oct-2026 con el canario (clave de prueba `canario`, firma de un AAB real y APK
universal verificados; pruebas `-m herramientas` 2/2). **Fuente de verdad:** `movil.py` (`firma_crear`, `firmar`,
`apk_universal`). **Sirve para:** firmar sin que nadie vea una contraseña y no perder nunca la capacidad de actualizar.

## Lo esencial
- **Play App Signing:** Google guarda la clave que firma lo que reciben los usuarios; nosotros solo tenemos la **clave
  de subida** de cada app. Si se pierde, Google la cambia (más abajo); si se filtra, se cambia igual.
- **Dónde vive:** el almacén en `%USERPROFILE%\.secretos-moviles\firmas\<app>\upload.p12` (fuera de TRABAJOS GENERATIVOS,
  que barren los agentes) y su contraseña en el Administrador de credenciales como `android-firma-<app>`, usuario
  `upload`, persistencia «solo este PC». Alias de la clave: `upload`. RSA 4096, validez 10 000 días.
- **Nadie ve la contraseña:** `movil.py` la genera (32 bytes aleatorios), la pasa a keytool/jarsigner por variable de
  entorno del proceso hijo (`-storepass:env`) y a bundletool por un archivo temporal que borra al momento.
- **Las apps no firman su release:** su Gradle no lleva `signingConfig` de release; entregan el AAB sin firmar y lo
  firma `movil.bat firmar`. Así ninguna conversación de app toca una clave.

## Cómo se hace (pasos)
1. Crear la clave de una app (una sola vez): `movil.bat firma crear <app> --nombre-comun "<Nombre de la app>"` → debe
   salir `sha256` y `certificado_publico`. Se niega si ya existe («No se pisa»).
2. Comprobarla: `movil.bat firma comprobar <app>` → `"ok": true` con la misma `sha256`.
3. Firmar un AAB de release sin firmar: `movil.bat firmar <app> <ruta\app-release.aab>` → crea
   `<nombre>-firmado.aab` al lado y comprueba que lo firmó la clave de subida de esa app (huella igual). Se niega si
   el AAB es depurable, de otro paquete o ya viene firmado.
4. APK para pasar a alguien fuera de Play: `movil.bat apk-universal <app> <ruta\…-firmado.aab>` → crea
   `<nombre>-universal.apk`, verificado con apksigner.

## Copia de seguridad (Steven, una vez por app)
La contraseña está solo en este PC. Si el PC muere, la clave de subida se pierde (se recupera con el restablecimiento,
pero tarda). Para evitarlo, Steven guarda fuera del PC (USB cifrado o su gestor de contraseñas):
- la carpeta `%USERPROFILE%\.secretos-moviles\firmas\<app>\`;
- la contraseña. Verla es decisión suya, en su terminal: `cmdkey` no la muestra; puede leerla con el Administrador de
  credenciales de Windows (Credenciales de Windows → `android-firma-<app>` → Mostrar). La IA nunca la lee ni la muestra.
PENDIENTE: hacerlo en cuanto exista la clave de la primera app publicable.

## Si se pierde o se filtra la clave de subida
0. No borrar nada de lo que quede.
1. Dejar sitio a la nueva (Steven, porque pisa una clave): mover la carpeta vieja a `firmas\<app>.antigua-<fecha>` y
   borrar la entrada `android-firma-<app>` del Administrador de credenciales. Luego la IA: `movil.bat firma crear <app>`.
2. Steven, en Play Console: Protegido con Play > Protección de Play Store > Administrar la firma de apps de Play →
   «Request upload key reset», con el motivo y el PEM nuevo (`upload_certificate.pem` de la carpeta). Google no da plazo.
3. Hasta que Google lo confirme, las subidas fallan por firma. Fuente: support.google.com/googleplay/android-developer/answer/9842756 (VERIFICADO).

## Si algo falla
| Síntoma (mensaje literal) | Causa | Qué hacer |
|---|---|---|
| «Ya hay una clave de subida para <app>… No se pisa» (MEDIDO) | Ya existe | Usarla; reemplazarla solo con el procedimiento de arriba |
| «No hay nada guardado como android-firma-<app>…» | PC nuevo o se borró la entrada | Restaurar la copia de seguridad, o restablecer la clave |
| «El bundle ya viene firmado (¿con la clave debug?)…» (MEDIDO) | El Gradle de la app firma el release | Quitar el `signingConfig` de release de la app |
| «El bundle es depurable…» | Se entregó el de debug | Entregar el de `bundleRelease` |
| «La firma no se verifica o no es la clave de subida…» | Firmado con otra clave | Volver a firmar desde el AAB sin firmar |

## Qué NO se toca y por qué
- **TRAMPA: un APK universal va firmado con la clave de SUBIDA, no con la que usa Play.** Quien lo instale no podrá
  actualizar desde Play: tendrá que desinstalarlo (y pierde sus datos). Se dice siempre al pasarlo.
- La contraseña no va nunca a un archivo del proyecto, a una variable de entorno global, al chat ni a la salida de una
  orden. Probado: la salida de `firma crear` no la contiene (prueba `test_firma_crear_comprobar_y_no_pisar`).
- La clave del canario (`android-firma-canario`) es de prueba: solo firma el fixture del laboratorio.

## Cómo verificar
`movil.bat firma comprobar <app>` → `"ok": true`; `movil.bat revisar <…-firmado.aab>` → `"firmado": true` y la misma
`sha256_firmante`.
