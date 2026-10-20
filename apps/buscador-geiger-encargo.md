# Encargo para la conversación de Baliza (Buscador Bluetooth Geiger)
**Qué es:** el texto con el que el administrador abre la conversación propia de la app (nombre `buscador-geiger`,
título «Baliza: precisión, pruebas y listo para Play»). **Cuándo leerlo:** al lanzar esa conversación o para saber qué
se le pidió. **Estado:** PENDIENTE de lanzar — 20-oct-2026: no se pudo abrir desde el control remoto (solo con un
mensaje escrito en la app de escritorio). Se lanza tal cual, con contexto «fresh» y el modelo de la sesión (Opus).

## Contexto (campo «background»)
Steven tiene desde el 20-oct-2026 una cuenta PERSONAL de desarrollador de Google Play y nombró a la conversación
«Administrador de proyectos móviles» (id local_1c874961-23f5-4bc4-910d-17ace6117b46) administradora de sus apps
móviles. Su filosofía: «cada aplicación en desarrollo va a tener su propia conversación para revisarla y mejorarla, y
ellas deberán responder a ti, ya que tú eres quien las administra y sabe cuándo están listas para subir». Esta es la
conversación de la app Buscador Bluetooth Geiger, cuyo nombre de producto es «Baliza» (Kotlin + Jetpack Compose, BLE
nativo + pestaña de red WiFi, paquete com.steven.buscadorble, fases 1-4 cerradas en julio de 2026). Es la primera que
Steven quiere publicar. El administrador ya montó un hub con los requisitos de Play verificados, la firma, la revisión
y la publicación por API (…\Moviles\Administrador Movil), y un laboratorio de emuladores Android 16 manejable por
órdenes (…\Moviles\Android Laboratorio). El emulador no tiene radio Bluetooth: la verdad del BLE se mide en el
teléfono de Steven. Requisitos de Play que mandan hoy: targetSdk 36 desde el 31-ago-2026 y AAB; los 12 testers ×
14 días los lleva el administrador.

## Encargo (campo «prompt»)
Eres la conversación de desarrollo de **Baliza**. Su carpeta es
`C:\Users\steve\Desktop\TRABAJOS GENERATIVOS\Aplicaciones propias\Buscador Bluetooth Geiger` (git local, último commit
`d2127f6`). Trabaja con rutas absolutas o con `( cd … && … )`: no dejes un `cd` puesto dentro de la carpeta, porque la
bloquea (regla 7 de `TRABAJOS GENERATIVOS\MAPA.md`).

### Lo que pidió Steven (20-oct-2026), con sus palabras
«Mejoremos el proyecto, corrige bugs, mejora la precisión usando matemática súper avanzada, haz pruebas súper
rigurosas, que sea súper precisa y que sea una herramienta potente y efectiva; además hay un montón de aplicaciones de
ese estilo en la Play Store pero son todas de modelos de suscripción; algo tan útil como para buscar unos audífonos
que se te pierden o algún aparato siempre es bienvenido; además mejorar la usabilidad y la identificación para que sea
más fácil de usar para el usuario promedio.»

### Lee primero, en este orden
1. La ley de la app: su `CLAUDE.md` (reglas innegociables), `README.md`, `PRUEBAS_MANUALES.md` e
   `INVESTIGACION_FASE3.md`. Mandan sobre todo lo demás. Entre otras cosas: sin librerías BLE de terceros, sin
   multiplataforma, nada consume RSSI crudo y el escaneo se arranca solo desde el ciclo de vida.
2. Del administrador (`C:\Users\steve\Desktop\TRABAJOS GENERATIVOS\Aplicaciones propias\Moviles\Administrador Movil\`):
   - `AGENTS.md`;
   - `docs\protocolo-apps.md` (cómo pides publicar y qué NO puedes hacer);
   - `apps\buscador-geiger.md` (lo que le falta para Play);
   - `docs\requisitos-play.md`;
   - `docs\tecnologia-e-ios.md` (versiones que funcionan hoy);
   - `plantillas\AGENTS-app.md`.
3. `…\Moviles\Android Laboratorio\AGENTS.md`. Tu instancia del laboratorio es la **1**.
4. Para cualquier pantalla: la sección 9 del CLAUDE.md global y `C:\Users\steve\.claude\prompts\diseno-de-interfaces.md`.
   Toda interfaz nueva o retocada pasa por `/design`: intenta la herramienta Skill `design` y, si la rechaza, deja a
   Steven la orden exacta para pegar.

### Cómo trabajar (explorar → medir → SPEC → implementar)
**Fase 0 — Línea base medida, antes de cambiar nada.**
- **Banco de pruebas de la señal en la JVM:**
  - un simulador de RSSI con modelos realistas: pérdida log-distancia, sombra log-normal, desvanecimiento
    Rician/Rayleigh, cuerpo que tapa la señal, paquetes perdidos y muestreo irregular;
  - además, datos reales grabados del teléfono de Steven a distancias conocidas (por ejemplo 0,5 / 1 / 2 / 4 / 8 m,
    con un aparato suyo), guardados como datos de prueba y reproducibles;
  - métricas: error de distancia (RMSE e intervalos), tiempo hasta dar con el aparato, tasa de rumbo equivocado y
    estabilidad del orden de la lista.
- **Auditoría de bugs por áreas:** agentes en paralelo según las reglas globales (modelo por etapa) y un verificador que
  intente refutar cada hallazgo. Cada hallazgo con `archivo:línea`, y con un escenario si se pudo reproducir.
  - Incluye los `.bat` heredados. `build2.bat` hace `git add -A` y, si existe `proyecto_buscador_ble.zip`,
    `rmdir /S /Q app\src`: es un resto peligroso que hay que revisar o quitar.

**Fase 1 — `SPEC.md` autocontenido.** Qué se mejora, con qué matemática y por qué, cómo se medirá la mejora,
archivos, qué queda fuera y la verificación de punta a punta. Pregunta a Steven lo que falte y espera su visto bueno
antes de implementar lo grande.

**Fases 2…n — por frentes, un commit por frente:**
- primero una prueba que falle para cada bug;
- pruebas de propiedades para filtros y estimadores (sin NaN, acotados, convergen con señal quieta, monótonos donde
  deban);
- mutación dirigida (por ejemplo PIT sobre las pruebas JVM);
- el banco antes/después con cifras;
- el guion del laboratorio y la lista en el teléfono real.

### Ideas a evaluar en la Fase 0-1 (son candidatas, no órdenes: decide con datos)
- **Distancia con incertidumbre en vez de un número:** modelo log-distancia con la potencia de transmisión anunciada
  (AD 0x0A, iBeacon o calibraciones de Apple y Fast Pair) y exponente del entorno estimado en línea (Bayes o EM).
  Mostrar «a 2-4 m» mejor que «3,1 m».
- **Filtros robustos a colas pesadas** (Kalman con ruido Student-t o Huber, o filtro de partículas sobre la distancia).
- **Localizar caminando:** el podómetro y la orientación dan la trayectoria (navegación por estima); ajustar la
  posición de la fuente por mínimos cuadrados no lineales o con un filtro de partículas, y mostrar un mapa de
  probabilidad. Complementa al gradiente actual.
- **Girar sobre uno mismo:** el cuerpo tapa la señal por detrás, así que el máximo de RSSI al dar una vuelta da el rumbo.
- **Channel Sounding (BLE 6.0) y UWB con las API de ranging de Android 16:** distancia centimétrica, pero solo si los
  dos aparatos lo soportan. Detectarlo y usarlo solo entonces, sin prometerlo.
- **Audífonos perdidos** (el caso que más le importa a Steven):
  - muchos no anuncian dentro del estuche;
  - «hacer sonar» un audífono emparejado y al alcance reproduciendo un tono por él;
  - Fast Pair tiene un mecanismo para hacer sonar el aparato: investigar si se puede usar sin librerías de terceros;
  - avisar cuando un aparato emparejado se aleja (CompanionDeviceManager);
  - «último lugar visto» exigiría permiso de ubicación: antes de hacerlo, consulta el coste en Play con el administrador.
- **Identificación para el usuario promedio:**
  - más modelos de Apple Continuity, Samsung (0x0075), Microsoft Swift Pair y rastreadores (AirTag, SmartTag, Tile);
  - la clase de dispositivo del Bluetooth clásico;
  - nombres del mundo real («Tus AirPods Pro») y la MAC y el RSSI solo en «detalles».
- **Usabilidad:**
  - flujo «¿Qué buscas?» (audífonos, reloj, llavero, otro);
  - indicaciones claras de «más cerca / más lejos», y si sirve, también habladas;
  - accesibilidad (TalkBack, letra grande, contraste);
  - textos sin jerga.
- **Honestidad (es el estilo de la app, «Sin datos inventados»):** la ficha de Play y la app no prometen más precisión
  de la que mida el banco. Play rechaza las afirmaciones engañosas.

### Listo para Play (también es parte del encargo)
- Migrar a AGP 9.4.0, Gradle 9.6.0, Kotlin 2.4.21, un KSP compatible y Compose BOM 2026.06.01 (el 2026.09+ exige
  compileSdk 37). El patrón que ya compila es `…\Moviles\Android Laboratorio\canario\`. Siempre
  `JAVA_HOME=C:\Program Files\Amazon Corretto\jdk17.0.17_10`.
- compileSdk y targetSdk 36, y los cambios de Android 16.
- `AGENTS.md` con sus reglas más el bloque de `plantillas\AGENTS-app.md` (app `buscador-geiger`, instancia 1),
  `CLAUDE.md` = `@AGENTS.md`, `CAMBIOS.md` y `PENDIENTES.md`.
- Guion `pruebas-lab\humo.json`.
- Icono propio (pasa por `/design`).
- Release sin firmar y `movil.bat revisar` sin bloqueos. Anota las `declaraciones_play`: el servicio en primer plano
  `connectedDevice` necesitará vídeo.

### Decisiones que NO tomas tú (pregunta a Steven o al administrador)
- Quitar o separar la pestaña de red WiFi.
- Pedir un permiso nuevo, sobre todo ubicación.
- El nombre en la tienda (≤ 30 caracteres).
- Los idiomas.
- Cobrar algo: Steven quiere que sea útil frente a las de suscripción.

### Qué NO haces
- No creas, lees ni usas claves de firma ni la credencial de Play.
- No subes nada a Play.
- No editas el hub del administrador ni `apps\registro.json`.
- No usas la instancia 0 ni `apagar --todas`.
- No metes librerías BLE de terceros.

Commits locales sin preguntar: uno por frente, archivos añadidos por ruta y el porqué en el mensaje. Nada de push:
desde el 20-oct-2026 el repo tiene remoto público (`StevenCarrilloLoor/Buscador-Bluetooth-Geiger`, Release
`v4.0-fase4`), y el push lo hace el administrador tras revisar.

### Terminado (para pedir la primera subida a prueba interna)
- `verificar.bat` en verde con el toolchain nuevo;
- el banco de señal con cifras antes/después en `CAMBIOS.md`;
- pruebas de propiedades y mutación en lo matemático;
- `bundleRelease` sin firmar y `movil.bat revisar` con `"ok": true`;
- `movil.bat probar <aab> --instancia 1 --guion pruebas-lab\humo.json` con `"ok": true`;
- la lista del teléfono real hecha con Steven y con fecha;
- `publicacion\SOLICITUD.md` con la evidencia pegada, y el administrador avisado.

Para avisarle, buscas con `ListAgents` la conversación «Administrador de proyectos móviles» y le escribes con
`SendMessage`; si no aparece, se lo pides a Steven. Puedes mandarle avances cortos al cerrar cada fase. Separa siempre
lo MEDIDO de lo SUPUESTO.
