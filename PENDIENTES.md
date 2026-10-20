# Pendientes del Administrador Móvil
**Qué es:** lo que falta, quién lo hace y cómo se sabe que está hecho. **Cuándo leerlo:** al empezar una sesión.
**Estado:** VIVO — 20-oct-2026.

## De Steven (la IA no puede o no debe hacerlo por él)
| # | Qué | Cómo | Hecho cuando |
|---|---|---|---|
| S1 | Verificar su teléfono Android en Play Console (cuenta personal nueva) | Inicio de la consola → QR → app Play Console → Verify | Inicio sin esa tarea |
| S2 | Crear la cuenta de servicio de la API de Play | `docs/api-play.md`, pasos 1-5 (≈15 min) | `movil play credencial comprobar` → `"ok": true` |
| S3 | Reunir 12+ testers con Android dispuestos a 14 días seguidos | Idealmente en un Grupo de Google (`docs/publicar-en-play.md`, paso 6) | Lista o grupo creado |
| S4 | Decidir dónde se publica la política de privacidad (URL pública) | Recomendado: GitHub Pages en un repo público suyo (`StevenCarrilloLoor/...`); la IA redacta el texto | URL que abre |
| S5 | Decidir la app nueva | Idea del 20-oct-2026: que su hermano vea videos musicales en el carro «por CarPlay», transmitiendo la pantalla del teléfono. Diagnóstico dado: CarPlay es de iPhone; Android Auto no admite apps que replican la pantalla (regla PC-1 de la calidad de apps para coches) y solo deja vídeo con el carro parado (beta, Android 16, carros compatibles). Propuesta: «reproductor del asiento de atrás» en una tablet, sin internet, con sonido por Bluetooth al carro. Steven lo está pensando; aún no tiene aparato ni ha decidido de dónde salen los videos | Steven elige enfoque, aparato y origen de los videos; entonces ficha en `apps/` y su conversación |
| S6 | Copia de seguridad de cada clave de subida real | `docs/firma-y-claves.md`, «Copia de seguridad» | Copia fuera del PC |
| S7 | ¿Tiene iPhone para probar iOS algún día? | Respuesta en el chat | Anotado en `docs/tecnologia-e-ios.md` |
| S8 | Revisar el borrador de política de privacidad | `plantillas/politica-privacidad.md` (no es asesoría legal) | Visto bueno o cambios |

## De la IA (administración)
| # | Qué | Hecho cuando |
|---|---|---|
| A1 | Probar `movil play estado/subir` contra Google cuando exista S2 y una app en la consola | Salida real pegada en `docs/api-play.md` y quitado el SUPUESTO |
| A2 | Orden `movil play testers` (Grupo de Google por `edits.testers`) cuando exista el grupo | Probada |
| A3 | Teléfono real en el laboratorio por depuración inalámbrica (Bluetooth del Buscador) | `lab dispositivos` lo lista y un guion corre con `--serial` |
| A4 | Revisar `docs/requisitos-play.md` | Cada trimestre: próxima, ene-2027 |
| A5 | Decidir con Steven si se instala `platforms;android-37.0` (67 MB) para usar Compose BOM 2026.09+ | Instalado o descartado |
| A6 | Mover `Buscador Bluetooth Geiger` dentro de `Aplicaciones propias\Moviles\` | Solo con permiso de Steven y de su conversación («PUEDES MOVER»), regla 5 de MAPA.md |
| A7 | Plantilla de política de privacidad en español para apps sin recogida de datos | HECHO el borrador (20-oct-2026); falta S8 |
| A8 | Abrir la conversación del Buscador Geiger con su lista de `apps/buscador-geiger.md` | Conversación abierta y su `AGENTS.md` con el bloque de `plantillas/AGENTS-app.md` |
