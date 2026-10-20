# Requisitos de Google Play vigentes (cuenta PERSONAL de Steven)
**Qué es:** lo que Google Play exige hoy para publicar, con su fuente. **Cuándo leerlo:** antes de decidir si una versión
puede subirse, al planificar una app nueva o si Play Console rechaza algo. **Estado:** VIVO — comprobado el 20-oct-2026
(investigación con 5 agentes y verificación adversarial de cada dato crítico; resultados en la bitácora `CAMBIOS.md` nº 1).
**Fuente de verdad:** las páginas oficiales citadas; las cifras cambian, así que se revisan cada trimestre (próxima: ene-2027).
**Sirve para:** que `movil.bat revisar` y la lista «lista para subir» digan lo mismo que Play.

Etiquetas: **VERIFICADO** = un segundo agente lo confirmó en la página oficial el 20-oct-2026. **SUPUESTO** = deducción o
fuente no oficial; comprobarlo antes de apoyarse en ello.

## Lo esencial
- **Cuenta personal ⇒ prueba cerrada obligatoria:** al menos **12 testers** inscritos **14 días seguidos** antes de poder
  pedir producción. Es el cuello de botella: se arranca en cuanto haya una versión mínima digna. VERIFICADO.
- **targetSdk 36 (Android 16) o más** para apps nuevas y actualizaciones desde el **31-ago-2026**. VERIFICADO.
- **AAB, Play App Signing y clave de subida propia**; nunca un APK. VERIFICADO.
- **Política de privacidad (URL pública) y Seguridad de los datos** obligatorias aunque la app no recoja nada. VERIFICADO.
- **16 KB** para código nativo: obligatorio para actualizaciones desde el **1-feb-2027**. VERIFICADO.

## Cuenta y acceso a producción
| Requisito | Detalle | Fuente | Estado |
|---|---|---|---|
| Prueba cerrada antes de producción | Cuentas personales creadas después del 13-nov-2023: ≥ 12 testers con opt-in continuo ≥ 14 días consecutivos. Uno que sale y vuelve empieza de cero sus 14 días. Producción y prerregistro quedan bloqueados hasta entonces | support.google.com/googleplay/android-developer/answer/14151465 | VERIFICADO |
| Solicitar producción | Botón «Apply for production» en el Panel. Formulario de 3 partes: la prueba cerrada (cómo reclutaste testers, cómo usaron la app, cómo recogiste sus comentarios), la app y la preparación. Google suele responder en ~7 días; puede pedir más pruebas | misma | VERIFICADO |
| Prueba abierta | Solo disponible después de tener acceso a producción | misma | VERIFICADO |
| Verificar un dispositivo | Cuentas personales nuevas: verificar con un **teléfono Android físico** (sin root, Android 10+) en la app Play Console: tarea en el Inicio de la consola web → QR → entrar como propietario → Verify | answer/14316361 | VERIFICADO |
| Datos de contacto | Correo y teléfono de contacto y correo de desarrollador verificados por código y operativos toda la vida de la cuenta. En cuentas personales Play muestra nombre legal, país y correo; la dirección completa si se monetiza | answer/13628312 | VERIFICADO |
| Cobrar | Ecuador admite registro de desarrollador **y de comerciante** (USD). Verificar el método de pago tarda hasta 5 días. Comisión en Ecuador: 15 % el primer millón USD/año y 30 % por encima; suscripciones 15 % | answer/9306917, answer/112622 | VERIFICADO |
| Revisión de apps | Hasta 7 días o más en casos excepcionales; no hay cifra específica para cuentas nuevas | answer/9859751 | VERIFICADO |

## Técnicos (los comprueba `movil.bat revisar`)
| Requisito | Detalle | Fuente | Estado |
|---|---|---|---|
| Nivel de API | Móvil/tableta: **targetSdk ≥ 36** desde el 31-ago-2026 (apps nuevas y actualizaciones). Wear OS y Automotive 35; XR 34; TV 34. Prórroga posible hasta el 1-nov-2026 (formulario en la consola). Una app vieja que no cumpla deja de verse para usuarios nuevos en Android recientes | answer/11926878 | VERIFICADO |
| 16 KB | Apps que apuntan a API 35+ deben funcionar con páginas de 16 KB en 64 bits; desde el **1-feb-2027** no se publican actualizaciones que no lo cumplan. Solo afecta a código nativo (.so). Arreglo: AGP ≥ 8.5.1 y NDK r28+, o `-Wl,-z,max-page-size=16384`. El modo de compatibilidad NO cuenta | developer.android.com/guide/practices/page-sizes | VERIFICADO |
| Formato y firma | AAB obligatorio; Play App Signing: Google guarda la clave de firma de la app y nosotros firmamos con la clave de subida (RSA ≥ 2048). Clave de subida perdida = se pide restablecerla con su PEM (`docs/firma-y-claves.md`) | answer/9842756 | VERIFICADO |
| versionCode | Sube en cada subida; máximo 2.100.000.000 | answer/9859152 | VERIFICADO |
| Ficha | Nombre 30 caracteres, descripción corta 80, completa 4000 | answer/9859152 | VERIFICADO |
| Tamaño | Módulo base 500 MB comprimido; aviso (no bloqueo) > 200 MB con datos móviles | answer/9859372 | VERIFICADO |
| Notas de versión | 500 caracteres por idioma | — | SUPUESTO (comprobar en la consola) |

## Declaraciones en Play Console (las rellena Steven; la IA prepara los textos)
| Declaración | Cuándo | Fuente | Estado |
|---|---|---|---|
| Seguridad de los datos | Obligatoria para pistas cerrada, abierta y producción (la interna está exenta). Exige URL de política de privacidad aunque se declare «no recoge datos» | answer/10787469 | VERIFICADO |
| Eliminación de cuenta | Solo si la app permite crear cuentas: vía dentro de la app + enlace web declarado. Todos responden las preguntas de borrado en Seguridad de los datos | answer/13327111 | VERIFICADO |
| Permisos sensibles | Un bundle con permisos sin declarar bloquea publicar CUALQUIER cambio (incluida la ficha) hasta resolverlo. Piden: función principal, instrucciones, vídeo (YouTube o mp4) y credenciales si hay login. Revisión: hasta varias semanas | answer/9214102 | VERIFICADO |
| Servicio en primer plano | Cada tipo (connectedDevice, dataSync, location…) se declara en App content con descripción, impacto si se interrumpe y vídeo | answer/13392821 | VERIFICADO |
| Clasificación IARC, público objetivo, anuncios, acceso a la app, apps de noticias/salud/finanzas | Toda app nueva | answer/9859152 y enlazadas | SUPUESTO el detalle (no se leyó cada página) |
| Políticas por permiso (ubicación en segundo plano, fotos y vídeos, alarmas exactas, QUERY_ALL_PACKAGES, accesibilidad, VPN) | Si el manifiesto los pide | play.google.com/about/privacy-security-deception/permissions/ | SUPUESTO el detalle |

## Verificación de desarrolladores de Android (instalar fuera de Play)
| Hecho | Detalle | Fuente | Estado |
|---|---|---|---|
| Calendario | Exigencia desde el **30-sep-2026** solo en Brasil, Indonesia, Singapur y Tailandia, para instalaciones desde tiendas participantes (Play, Galaxy Store, Xiaomi, OPPO, vivo, HONOR, Palm) en dispositivos certificados Android 7+. **Global en 2027**, sin fecha. Ecuador no está en la primera fase | developer.android.com/developer-verification/guides | VERIFICADO |
| Apps de Play | La identidad verificada de Play Console cuenta; Play registra el nombre de paquete al crear la app. Comprobar el estado en Inicio y en Configuración > Cuenta de desarrollador | …/guides/google-play-console | VERIFICADO |
| adb | Instalar por adb (laboratorio, teléfono de pruebas) **no** necesita verificación | …/guides/faq | VERIFICADO |
| APK a amigos | Hoy en Ecuador no afecta. Desde 2027: el amigo usa el «flujo avanzado» (espera de 24 h una vez) o la app está registrada; para ≤ 20 dispositivos hay cuenta de distribución limitada (gratis, sin documento) | …/guides/limited-distribution, blog 2026-03 | VERIFICADO el mecanismo; fechas de Ecuador SIN fecha oficial |
| Clave perdida | Una clave de firma perdida no se puede registrar: guardar copia de la clave de subida | …/guides/faq | VERIFICADO |

## Si Play rechaza algo
| Síntoma (mensaje literal cuando se tenga) | Causa | Qué hacer |
|---|---|---|
| La consola no deja crear la versión de producción | Faltan los 12 testers × 14 días o la solicitud de acceso | `docs/publicar-en-play.md`, pasos 6-8 |
| «targetSdkVersion … too low» (SUPUESTO el texto) | targetSdk < 36 | Subir compileSdk/targetSdk a 36 en la app; volver a pasar `movil.bat revisar` |
| Alerta en App content por permisos | Permiso sensible sin declarar | Declarar con vídeo, o quitar el permiso y subir otra versión |
| API: «Only releases with status draft may be created on draft app» (SUPUESTO, conocido de GPP/fastlane) | La app aún no se ha publicado nunca | Subir con `--estado draft` y terminar en la consola |

## Referencias
- `movil.py`: constantes `MIN_TARGET_SDK`, `PAGINA_16K` y `PERMISOS_DECLARABLES` (se cambian a la vez que esta tabla).
- Investigación completa (afirmaciones, fuentes y veredictos): `docs/investigacion-20261020.md` (legible) y
  `docs/investigacion-20261020.json` (crudo). Incluye tecnología, iOS y el laboratorio.
