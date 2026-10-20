# Bitácora del Administrador Móvil
**Qué es:** por qué cada cosa es como es, numerado, con su verificación y su commit. **Cuándo leerlo:** antes de
cambiar algo que parece raro. **Estado:** VIVO.

## 1 — 20-oct-2026: nace el Administrador Móvil
**Motivación.** Steven consiguió su cuenta de Google Play (personal) y nombró a la IA administradora de sus apps
móviles, con esta filosofía: cada app en desarrollo tiene su propia conversación, que responde al administrador, y el
administrador decide cuándo está lista para subir. iOS queda para después (no tiene Mac). Autorizó descargar las
herramientas oficiales (~3 GB).

**Qué se hizo.**
- Inventario del PC: Android Studio 2025.3, SDK con platforms 35/36.1, emulador 36.4.9, WHPX activo, JDK Corretto 17,
  Node 22, Python 3.13; app ya existente `Buscador Bluetooth Geiger`.
- Investigación con 5 agentes Sonnet y verificación adversarial con otros 5 (`docs/investigacion-20261020.*`): Play exige
  targetSdk 36 desde el 31-ago-2026, 12 testers × 14 días para cuentas personales, 16 KB desde el 1-feb-2027, etc.
  (`docs/requisitos-play.md`).
- Instalado: cmdline-tools 23.0 (sha1 comprobado contra el catálogo de Google), `platforms;android-36`,
  `build-tools;36.0.0`, `system-images;android-36;google_apis;x86_64`, bundletool 1.18.3 (sha256 comprobado contra
  GitHub), venv con google-api-python-client 2.201.0, google-auth 2.62.0, keyring 25.7.0, pytest 9.1.1.
- `movil.py`: doctor, solicitudes, firma crear/comprobar, firmar, apk-universal, revisar (targetSdk, depurable,
  versionCode, 16 KB por ELF, declaraciones por permisos), probar (en el laboratorio), play credencial/estado/subir.
- Laboratorio hermano `..\Android Laboratorio` (su propio git) y el canario (agente Opus, AGP 9.4.0).
- Documentos: protocolo con las apps, requisitos, publicar paso a paso, firma, API, tecnología e iOS; fichas y registro.

**Verificación (MEDIDA).** Hub: `pytest -q` 17 passed; `-m herramientas` 2 passed (clave real de prueba creada,
firmado un AAB real, huella comprobada, sin restos en la bóveda). Cadena con el canario: revisar sin bloqueos → firmar
(sha256 `8E:96:C8:5A:…:38:AD`) → probar en el laboratorio con el AAB firmado (8/8, arranque en frío 971 ms) →
APK universal verificado. API de Play: SIN COMPROBAR (falta la credencial de Steven).

**Commit:** el primero de este repositorio («Crea el Administrador Móvil…»).
