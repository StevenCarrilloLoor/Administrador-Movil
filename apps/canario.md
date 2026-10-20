# Ficha: Canario del laboratorio (`com.steven.canario`)
**Qué es:** la app mínima que prueba el laboratorio y la cadena de firma; NO se publica. **Cuándo leerlo:** al cambiar
el laboratorio, `movil.py` o las versiones de Android, para comprobar que todo sigue funcionando.
**Estado:** VIVO — comprobado el 20-oct-2026. **Fuente de verdad:** `..\Android Laboratorio\canario\`.

## Qué hace
Un texto «Canario del laboratorio», un contador «Pulsaciones: N» guardado en `shared_prefs/canario.xml` (clave
`pulsaciones`), un botón «Pulsar» (`Log.i("Canario", "pulsacion N")`) y otro «Fallar» que lanza
`RuntimeException("CANARIO_FALLO_PROVOCADO")`.

## Cómo se usa (MEDIDO el 20-oct-2026)
| Para qué | Comando | Resultado |
|---|---|---|
| Compilar | `( cd "…\Android Laboratorio\canario" && JAVA_HOME="C:\Program Files\Amazon Corretto\jdk17.0.17_10" ./gradlew.bat assembleDebug bundleRelease testDebugUnitTest lintDebug )` | BUILD SUCCESSFUL: 231 s en frío y 4 s en caliente; 5/5 pruebas |
| Humo completo en el laboratorio | `python lab.py guion guiones\canario-humo.json --instancia 0` | 20/20 en 42 s; con dos instancias a la vez, 20/20 en cada una |
| Cadena de firma | `movil.bat revisar` → `firmar canario` → `probar …-firmado.aab --guion guiones\canario-humo-sin-instalar.json` → `apk-universal canario` | revisar sin bloqueos (2 .so de Compose alineadas a 16 KB); firma con sha256 `8E:96:C8:5A:…:38:AD`; probar 8/8, arranque en frío 971 ms; APK verificado |

Clave de subida de PRUEBA: `android-firma-canario` y `%USERPROFILE%\.secretos-moviles\firmas\canario\`. Solo para esto.

## Versiones
| versionCode | Fecha | Qué | Dónde |
|---|---|---|---|
| 1 | 20-oct-2026 | Primera, AGP 9.4.0 / Gradle 9.6.0 / Kotlin 2.4.21 / BOM 2026.06.01 | Solo laboratorio (`D:\AndroidLaboratorio\construcciones\canario-1\`) |
