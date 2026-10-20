# Plantilla: política de privacidad (apps que no sacan datos del teléfono)
**Qué es:** borrador en español de la política de privacidad que Google Play exige a toda app, incluso si no recoge
nada. **Cuándo leerlo:** al preparar la ficha de una app (paso 5 de `docs/publicar-en-play.md`). **Estado:** BORRADOR —
20-oct-2026, sin revisar por Steven; NO es asesoría legal. **Sirve para:** publicarla en una URL pública y declararla
en Play Console.

## Cómo se usa (la IA)
1. Copiar el bloque de abajo, sustituir cada `<…>` con datos reales de la app (lo que hace, permisos, qué se guarda).
2. Si la app **sí** envía algo fuera del teléfono (servidor propio, analítica, anuncios, informes de fallos, SDK de
   terceros), esta plantilla NO vale tal cual: hay que listar cada dato, a quién va y para qué, y lo mismo en Seguridad
   de los datos. Se dice a Steven.
3. Que coincida con Seguridad de los datos en Play Console y con lo que hace el código (se comprueba con los permisos
   que lista `movil.bat revisar`).
4. La publica Steven en la URL que elija (PENDIENTE S4) y la IA comprueba que la URL abre sin iniciar sesión.

---

# Política de privacidad de <Nombre de la app>
Última actualización: <dd de mes de aaaa>

<Nombre de la app> («la app») la desarrolla <nombre legal del desarrollador, como figura en Google Play>, en Ecuador.
Contacto: <correo de desarrollador de Google Play>.

## Qué datos trata la app
La app no recoge, no guarda en servidores ni comparte con nadie datos personales. Todo lo que usa se procesa
**solo dentro de tu teléfono**:
- <Ejemplo: señales de dispositivos Bluetooth cercanos (nombre, dirección y potencia) para mostrarlos y medir la
  distancia.>
- <Ejemplo: tus ajustes de la app, guardados en el almacenamiento interno de la app.>

## Permisos que pide y para qué
- <Permiso en palabras normales, p. ej. «Dispositivos cercanos (Bluetooth)»>: <para qué exactamente>.
- <…>
La app solo usa cada permiso para lo descrito y puedes retirarlo en los ajustes de Android en cualquier momento.

## Lo que no hace
- No tiene cuentas de usuario ni inicio de sesión.
- No incluye anuncios, analítica ni herramientas de seguimiento de terceros.
- No vende ni cede datos a nadie.

## Conservación y borrado
Los datos guardados en el teléfono se borran al borrar los datos de la app o desinstalarla.

## Menores
La app no está dirigida a menores de 13 años y no recoge datos de nadie.

## Cambios
Si la app cambia lo que hace con los datos, se actualizará esta página y su fecha antes de publicar esa versión.
