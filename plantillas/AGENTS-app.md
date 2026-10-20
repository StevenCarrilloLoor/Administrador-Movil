## Publicación (bloque común de las apps móviles; copiar tal cual en el AGENTS.md de cada app)
Esta app la administra el **Administrador Móvil** (`C:\Users\steve\Desktop\TRABAJOS GENERATIVOS\Aplicaciones propias\Moviles\Administrador Movil`).
Esta conversación desarrolla y prueba; publicar lo decide el administrador. Antes de pedir una publicación, leer su
`docs\protocolo-apps.md` entero.

- **Nombre en el registro:** `<app>` · **Paquete:** `<paquete>` · **Instancia del laboratorio:** `<N>` (nunca la 0).
- **Requisitos de Play de hoy:** targetSdk ≥ 36, AAB, 16 KB si hay código nativo; detalle en `docs\requisitos-play.md`
  del administrador.
- **Release sin firmar:** el Gradle de release NO lleva `signingConfig`; la firma la pone el administrador. Esta
  conversación nunca crea, lee ni usa claves de firma ni la credencial de Play.
- **Laboratorio:** `python "C:\Users\steve\Desktop\TRABAJOS GENERATIVOS\Aplicaciones propias\Moviles\Android Laboratorio\lab.py" arrancar --instancia <N>`;
  guion de la app, sin paso `instalar`, en `pruebas-lab\humo.json` de esta carpeta; prueba de una versión con
  `movil.bat probar <app-release.aab> --instancia <N> --guion pruebas-lab\humo.json`; apagar solo la propia con
  `apagar --instancia <N>` (nunca `--todas`).
- **Revisión previa:** `"C:\Users\steve\Desktop\TRABAJOS GENERATIVOS\Aplicaciones propias\Moviles\Administrador Movil\movil.bat" revisar <app-release.aab>` → `"ok": true`.
- **Pedir publicación:** copiar `plantillas\SOLICITUD.md` del administrador a `publicacion\SOLICITUD.md` de esta
  carpeta, rellenarla con evidencia pegada y avisar a la conversación «Administrador de proyectos móviles»
  (`SendMessage`; si no aparece en `ListAgents`, pedir a Steven que avise). La respuesta llega a
  `publicacion\RESPUESTA.md`: leerla antes de seguir.
