# Administrador Móvil

Herramienta de línea de órdenes (Windows) para llevar apps Android de un desarrollador individual hasta Google Play
sin que nadie vea una contraseña:

- **Requisitos de Play verificados** con su fuente y fecha (`docs/requisitos-play.md`): targetSdk, 16 KB, AAB,
  declaraciones, prueba cerrada de las cuentas personales, verificación de desarrolladores de Android.
- **Revisión de un AAB** contra esos requisitos: targetSdk, depurable, versionCode, alineación de 16 KB de las
  librerías nativas (leyendo el ELF) y qué declarará Play Console por los permisos.
- **Firma con la clave de subida** (Play App Signing) con la contraseña guardada en el Administrador de credenciales de
  Windows y verificación de que el AAB lleva una sola firma, íntegra, de esa clave.
- **APK universal** para dar la app fuera de Play.
- **Prueba en un emulador real** a través del laboratorio hermano (`Android Laboratorio`).
- **Subida por la Google Play Developer API v3** a pruebas internas, con puertas explícitas para pistas de testers y
  producción.
- **Protocolo** para que cada app se desarrolle en su propia conversación de IA y pida aquí su publicación
  (`docs/protocolo-apps.md`).

La documentación operativa está escrita para que la maneje una IA: empieza por `AGENTS.md` y `LEEME-INDICE.md`.

## Requisitos
- Windows 10/11.
- Python 3.13 (probado con 3.13.14).
- JDK 17 (keytool y jarsigner). Por defecto `C:\Program Files\Amazon Corretto\jdk17.0.17_10`; otra ruta con la
  variable `MOVIL_JAVA_HOME`.
- Android SDK con `build-tools;36.0.0` y `platforms;android-36` (`ANDROID_HOME`, o por defecto
  `%LOCALAPPDATA%\Android\Sdk`).
- bundletool 1.18.3 (`bundletool-all-1.18.3.jar`, de github.com/google/bundletool) en
  `<ANDROID_LAB_RAIZ>\herramientas\` (por defecto `D:\AndroidLaboratorio\herramientas\`).
- Para `probar`: el laboratorio hermano en `..\Android Laboratorio`.

## Instalar
```
python -m venv .venv
.venv\Scripts\python.exe -m pip install -r requirements.txt
movil.bat doctor
```
`doctor` dice qué falta. La credencial de la API de Play se crea en Google Cloud y se guarda cifrada con DPAPI
(`docs/api-play.md`).

## Uso
```
movil.bat revisar <app-release.aab>
movil.bat firma crear <app> --nombre-comun "<Nombre>"
movil.bat firmar <app> <app-release.aab>
movil.bat probar <aab o apk> --instancia 1 --guion <guion.json>
movil.bat apk-universal <app> <…-firmado.aab>
movil.bat play estado <paquete>
movil.bat play subir <app> <…-firmado.aab> --notas-es "…"
```
Todas imprimen JSON y salen con 0 si todo fue bien. Las apps se registran en `apps/registro.json`.

## Secretos
Nunca están en este repositorio. La contraseña de cada clave de subida vive en el Administrador de credenciales de
Windows (`android-firma-<app>`, «solo este PC»). Los almacenes de claves y la credencial de Play, cifrada con DPAPI,
viven en `%USERPROFILE%\.secretos-moviles\` (otra ruta con `MOVIL_SECRETOS`). La herramienta no los imprime nunca.

## Pruebas
```
.venv\Scripts\python.exe -I -B -m pytest -q -p no:cacheprovider
.venv\Scripts\python.exe -I -B -m pytest -q -p no:cacheprovider -m herramientas
```
La primera es sin red y sin herramientas. La segunda usa keytool, jarsigner y el Administrador de credenciales con
nombres de prueba que se borran al acabar.

No hay ejecutable: es una herramienta de línea de órdenes pensada para que la opere una IA.
