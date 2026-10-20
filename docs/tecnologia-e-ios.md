# Con qué se hace cada app, versiones vigentes e iOS sin Mac
**Qué es:** la regla para elegir tecnología, las versiones de herramientas que funcionan hoy y el camino a iOS sin Mac.
**Cuándo leerlo:** al empezar una app nueva, al migrar una vieja o cuando Steven quiera iOS.
**Estado:** VIVO — versiones comprobadas el 20-oct-2026 (web, verificación adversarial y, las de Android, compilando el
canario). **Fuente de verdad:** `docs/investigacion-20261020.md` y `..\Android Laboratorio\canario\gradle\libs.versions.toml`.
**Sirve para:** no empezar una app con algo que luego impida publicarla o llevarla a iOS.

## Regla de elección (recomendación del administrador; Steven decide por app)
| La app… | Tecnología | Por qué |
|---|---|---|
| Solo Android, o depende de hardware y APIs nativas (Bluetooth, servicios en segundo plano, sensores) | **Kotlin + Jetpack Compose** | Lo que mejor domina Steven, acceso total a Android, todo se compila y publica desde Windows |
| Puede querer iOS más adelante y es sobre todo pantallas y datos | **Expo (React Native + TypeScript)** | Es lo único que compila y sube a iOS desde Windows sin Mac de forma cómoda (EAS en la nube) y Steven ya usa Node |
| Ya existe | Se queda como está | Reescribir no se hace sin motivo (el Buscador prohíbe migrar a multiplataforma en su `CLAUDE.md`) |
Flutter + Codemagic es la alternativa a Expo si Steven lo prefiere; .NET MAUI y Kotlin Multiplatform piden Xcode (Mac o
nube macOS) para iOS: descartados como opción por defecto.

## Versiones que funcionan hoy (Android nativo)
| Pieza | Versión | Estado |
|---|---|---|
| Android Gradle Plugin | 9.4.0 (existe 9.4.1) | MEDIDO: el canario compila |
| Gradle | 9.6.0 | MEDIDO |
| Kotlin | 2.4.21 (AGP 9 trae Kotlin integrado: no se aplica `org.jetbrains.kotlin.android`; sí `org.jetbrains.kotlin.plugin.compose`) | MEDIDO |
| Compose BOM | **2026.06.01** con compileSdk 36. **TRAMPA MEDIDA:** 2026.09.00 (Compose 1.12) y core 1.19 exigen `compileSdk 37` | MEDIDO |
| JDK | 17 (Corretto `C:\Program Files\Amazon Corretto\jdk17.0.17_10`; `java` del PATH es Java 8: no usarlo) | MEDIDO |
| SDK | platforms android-36, build-tools 36.0.0 instalados; `platforms;android-37.0` no (67 MB, para compileSdk 37) | MEDIDO |
| Android Studio | Instalado 2025.3; estable actual «Rabbit 1» 2026.2.1. Si 2025.3 se queja al abrir un proyecto AGP 9.4, actualizarlo es decisión de Steven | SUPUESTO que se queje |
| Expo | SDK 58 (15-oct-2026, React Native 0.88); Expo Go de SDK 58 llega «en semanas», hasta entonces `create-expo-app` crea SDK 57 | VERIFICADO |
| Flutter | 3.47 | VERIFICADO |

## Expo en este PC (cuando una app lo use)
- Android se compila en local: `npx expo prebuild` y luego `android\gradlew.bat bundleRelease`; sale el mismo AAB que
  firma `movil.bat firmar`. **TRAMPA (SUPUESTO hasta probarlo):** la plantilla de React Native firma el release con la
  clave debug; hay que quitar ese `signingConfig` para entregar el AAB sin firmar.
- `eas build --local` no funciona en Windows (SUPUESTO); EAS en la nube sí (cuenta de Expo de Steven).
- El laboratorio prueba igual cualquier APK/AAB, sea Kotlin o Expo.

## iOS sin Mac (cuando Steven lo decida)
1. Steven: Apple Developer Program, cuenta **individual** (99 USD/año, nombre legal real, verificación en 2 pasos;
   aparece su nombre como vendedor). VERIFICADO.
2. App Store Connect exige compilar con **Xcode 26 / SDK iOS 26** desde el 28-abr-2026 y, desde el 9-sep-2026, iOS 13
   como mínimo. Apple sube el mínimo cada primavera: releer developer.apple.com/news/upcoming-requirements antes de
   cada envío. VERIFICADO.
3. Compilar y firmar en la nube: **EAS Build** (plan gratis: 15 builds de iOS y 15 de Android, prioridad baja, 1 Mac a
   la vez, 45 min por build; no está claro si es al mes) o **Codemagic** (500 min de macOS M2 gratis al mes).
   GitHub Actions macOS: 0,062 USD/min. VERIFICADO.
4. Subir a TestFlight con `eas submit --platform ios` (clave de API de App Store Connect). SUPUESTO el detalle.
5. Sin Mac NO se puede: el simulador de iOS ni depurar en un iPhone con Xcode. Se prueba con TestFlight o con builds
   internas de Expo en un iPhone real (requiere registrar su UDID). Steven no tiene iPhone confirmado: PENDIENTE preguntar.

## Qué NO se toca y por qué
- No se sube el Compose BOM a 2026.09+ sin instalar `platforms;android-37.0` y poner compileSdk 37 (targetSdk puede
  quedarse en 36): si no, la compilación falla.
- No se mezcla Java 8 del PATH con Gradle: todas las órdenes ponen `JAVA_HOME` a Corretto 17.
