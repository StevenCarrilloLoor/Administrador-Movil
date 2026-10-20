# Ficha: Buscador Bluetooth Geiger (`com.steven.buscadorble`)
**Qué es:** el estado de publicación del Buscador y lo que le falta para Play. **Cuándo leerlo:** antes de hablar con su
conversación o de revisar una solicitud suya. **Estado:** VIVO — revisión documental del 20-oct-2026 (se leyeron
`app/build.gradle.kts` y `AndroidManifest.xml`; NO se compiló ni se probó). **Fuente de verdad:** su carpeta
`C:\Users\steve\Desktop\TRABAJOS GENERATIVOS\Aplicaciones propias\Buscador Bluetooth Geiger` (git local, 5 commits,
último `d2127f6` «Fase 4»).

## Objetivos de Steven (20-oct-2026)
Sus palabras: «mejoremos el proyecto, corrige bugs, mejora la precisión usando matemática súper avanzada, haz pruebas
súper rigurosas, que sea súper precisa y que sea una herramienta potente y efectiva; además hay un montón de
aplicaciones de ese estilo en la Play Store pero son todas de modelos de suscripción; algo tan útil como para buscar
unos audífonos que se te pierden o algún aparato siempre es bienvenido; además mejorar la usabilidad y la
identificación para que sea más fácil de usar para el usuario promedio». Se encargó a su conversación propia
(«Baliza: precisión, pruebas y listo para Play», nombre `buscador-geiger`), que primero mide y escribe un `SPEC.md`.

## Datos
- Nombre de la app: **Baliza** (buscador Bluetooth + administrador de la red WiFi). Fases 1-4 cerradas según su README.
- Kotlin + Jetpack Compose, BLE nativo; reglas propias en su `CLAUDE.md` (prohíbe migrar a multiplataforma).
- `compileSdk 35`, `targetSdk 35`, `minSdk 26`, versionCode 4 (`4.0-fase4`); AGP 8.x de 2024, Gradle 8.9, Compose BOM
  2024.10.01, Room 2.6.1, KSP.
- Release: sin `signingConfig` y sin minify (bien para el protocolo).
- Laboratorio: instancia 1. El emulador no tiene radio Bluetooth: la prueba de verdad es en un teléfono físico
  (su `PRUEBAS_MANUALES.md`).

## Lo que le falta para Play (lista para su conversación)
1. **targetSdk 36 y compileSdk 36** (bloqueo duro desde el 31-ago-2026) y probar los cambios de Android 16
   (edge-to-edge obligatorio, entre otros).
2. **Migrar a AGP 9.4.0 + Gradle 9.6.0 + Kotlin 2.4.21** (Kotlin integrado en AGP 9: quitar
   `org.jetbrains.kotlin.android`; KSP compatible con Kotlin 2.4). Patrón que ya funciona: el canario
   (`..\Moviles\Android Laboratorio\canario\`).
3. **Declaraciones que pedirá Play Console** por su manifiesto: servicio en primer plano `connectedDevice` (descripción,
   impacto y **vídeo**), `FOREGROUND_SERVICE_CONNECTED_DEVICE`, Bluetooth con `neverForLocation` (bien: no cuenta como
   ubicación), `ACCESS_FINE/COARSE_LOCATION` solo hasta API 30, `POST_NOTIFICATIONS`. El escáner de red wifi
   (`INTERNET`, `CHANGE_WIFI_MULTICAST_STATE`) va en Seguridad de los datos si algo sale del teléfono.
4. **Política de privacidad** pública (aunque no recoja nada) y Seguridad de los datos.
5. **Icono propio** y nombre de ficha (≤ 30 caracteres).
6. **Guion del laboratorio** para lo que no necesita Bluetooth (navegación, ajustes, persistencia) y lista manual en
   teléfono real para lo demás.
7. **Nombre de paquete:** `com.steven.buscadorble` se conserva si Play lo acepta al crear la app (es único en Play).
8. AAB de release sin firmar + `movil.bat revisar` sin bloqueos + solicitud (`docs/protocolo-apps.md`).

## Versiones
| versionCode | Fecha | Qué | Pista |
|---|---|---|---|
| 4 | jul-2026 | Fase 4 (inventario de red, identificación por capas) | Sin publicar |

## Comentarios de testers
(vacío: se rellena durante la prueba cerrada; Google los pide al solicitar producción)
