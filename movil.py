"""Administrador Móvil: firma, revisa, prueba y publica las apps Android de Steven.

Uso:  movil.bat <orden> [opciones]        (órdenes, salidas y reglas en AGENTS.md)

Reglas que este programa hace cumplir (el porqué está en AGENTS.md):
- Los secretos (contraseña de la clave de subida, credencial de la API de Play) nunca se imprimen ni se escriben en
  TRABAJOS GENERATIVOS: la contraseña vive en el Administrador de credenciales («solo este PC») y la credencial de Play
  cifrada con DPAPI en %USERPROFILE%\\.secretos-moviles\\.
- Solo se firma un AAB de release SIN firmar y no depurable; el resultado se verifica con jarsigner y el certificado.
- Subir a una pista que no sea «internal» exige --confirmo (Steven lo dijo en el chat); producción, --confirmo-produccion.
"""
from __future__ import annotations

import argparse
import ctypes
import ctypes.wintypes as wt
import datetime as _dt
import hashlib
import json
import os
import re
import secrets
import shutil
import struct
import subprocess
import sys
import tempfile
import time
import xml.etree.ElementTree as ET
import zipfile
from pathlib import Path

HUB = Path(__file__).resolve().parent
LAB_DIR = HUB.parent / "Android Laboratorio"
SDK = Path(os.environ.get("ANDROID_HOME") or Path(os.environ.get("LOCALAPPDATA", "")) / "Android" / "Sdk")
JAVA_HOME = Path(os.environ.get("MOVIL_JAVA_HOME", r"C:\Program Files\Amazon Corretto\jdk17.0.17_10"))
KEYTOOL = JAVA_HOME / "bin" / "keytool.exe"
JARSIGNER = JAVA_HOME / "bin" / "jarsigner.exe"
BUILD_TOOLS = SDK / "build-tools" / "36.0.0"
BUNDLETOOL = Path(os.environ.get("ANDROID_LAB_RAIZ", r"D:\AndroidLaboratorio")) / "herramientas" / "bundletool-all-1.18.3.jar"
SECRETOS = Path(os.environ.get("MOVIL_SECRETOS", Path.home() / ".secretos-moviles"))
FIRMAS = SECRETOS / "firmas"
CRED_PLAY = SECRETOS / "play-api.dpapi"
REGISTRO = HUB / "apps" / "registro.json"

PREFIJO_FIRMA = "android-firma-"     # entrada del Administrador de credenciales: android-firma-<app>
USUARIO_FIRMA = "upload"
ALIAS = "upload"
LOCAL_MACHINE = 2                    # CRED_PERSIST_LOCAL_MACHINE: «solo este PC» (keyring usaría enterprise)
NOMBRE_APP = re.compile(r"[a-z0-9][a-z0-9-]{1,39}")
PAQUETE = re.compile(r"[a-zA-Z][\w]*(\.[a-zA-Z][\w]*)+")

# Requisitos de Google Play vigentes (fuente y fecha en docs/requisitos-play.md; revisar cada trimestre).
MIN_TARGET_SDK = 36                  # apps nuevas y actualizaciones desde el 31-ago-2026
PAGINA_16K = 16384                   # obligatorio para publicar actualizaciones desde el 1-feb-2027 (código nativo)
ABIS_64 = ("arm64-v8a", "x86_64")
PISTAS_DE_PRUEBA = ("internal", "alpha", "beta")
NS = "{http://schemas.android.com/apk/res/android}"

# Permisos que obligan a declarar algo en Play Console (formulario, vídeo o política). Fuente: docs/requisitos-play.md.
PERMISOS_DECLARABLES = {
    "android.permission.ACCESS_BACKGROUND_LOCATION": "Ubicación en segundo plano: declaración + vídeo + revisión",
    "android.permission.ACCESS_FINE_LOCATION": "Ubicación: Seguridad de los datos (y prominent disclosure si es en segundo plano)",
    "android.permission.ACCESS_COARSE_LOCATION": "Ubicación aproximada: Seguridad de los datos",
    "android.permission.READ_MEDIA_IMAGES": "Fotos y vídeos: declaración (solo si es función principal)",
    "android.permission.READ_MEDIA_VIDEO": "Fotos y vídeos: declaración (solo si es función principal)",
    "android.permission.QUERY_ALL_PACKAGES": "Visibilidad de paquetes: declaración y uso permitido",
    "android.permission.MANAGE_EXTERNAL_STORAGE": "Acceso a todos los archivos: declaración y uso permitido",
    "android.permission.SCHEDULE_EXACT_ALARM": "Alarmas exactas: política de alarmas",
    "android.permission.USE_EXACT_ALARM": "Alarmas exactas: solo apps de reloj/calendario",
    "android.permission.REQUEST_INSTALL_PACKAGES": "Instalar paquetes: declaración",
    "android.permission.BIND_ACCESSIBILITY_SERVICE": "Accesibilidad: declaración",
    "android.permission.BIND_VPN_SERVICE": "VpnService: declaración",
    "android.permission.READ_SMS": "SMS: formulario de permisos (casi nunca se aprueba)",
    "android.permission.READ_CALL_LOG": "Registro de llamadas: formulario de permisos",
    "android.permission.NEARBY_WIFI_DEVICES": "Dispositivos wifi cercanos: Seguridad de los datos",
    "android.permission.BLUETOOTH_SCAN": "Bluetooth: Seguridad de los datos; si no lleva neverForLocation, cuenta como ubicación",
    "android.permission.CAMERA": "Cámara: Seguridad de los datos",
    "android.permission.RECORD_AUDIO": "Micrófono: Seguridad de los datos",
}


class Error(Exception):
    """Fallo explicado en español; main() lo imprime sin traza."""


# ======================================================================== lógica pura (probada en pruebas/)
def validar_app(nombre: str) -> str:
    if not NOMBRE_APP.fullmatch(nombre or ""):
        raise Error("Nombre de app no válido: minúsculas, números y guiones, 2-40 (p. ej. buscador-geiger).")
    return nombre


def validar_paquete(paquete: str) -> str:
    if not PAQUETE.fullmatch(paquete or ""):
        raise Error(f"Nombre de paquete no válido: {paquete!r} (forma com.ejemplo.app).")
    return paquete


def servicio_firma(app: str) -> str:
    return PREFIJO_FIRMA + validar_app(app)


def alineaciones_elf(datos: bytes) -> list[int]:
    """p_align de cada segmento PT_LOAD de un ELF de 64 bits little-endian ([] si no es ELF64)."""
    if len(datos) < 64 or datos[:4] != b"\x7fELF" or datos[4] != 2 or datos[5] != 1:
        return []
    e_phoff = struct.unpack_from("<Q", datos, 0x20)[0]
    e_phentsize, e_phnum = struct.unpack_from("<HH", datos, 0x36)
    res = []
    for i in range(e_phnum):
        off = e_phoff + i * e_phentsize
        if off + 56 > len(datos):
            break
        if struct.unpack_from("<I", datos, off)[0] == 1:          # PT_LOAD
            res.append(struct.unpack_from("<Q", datos, off + 0x30)[0])
    return res


def revisar_16k(aab: Path) -> dict:
    """Librerías nativas de 64 bits del AAB y si sus segmentos LOAD están alineados a 16 KB."""
    malas, buenas = [], []
    with zipfile.ZipFile(aab) as z:
        for nombre in z.namelist():
            partes = nombre.split("/")
            if nombre.endswith(".so") and len(partes) >= 3 and partes[-2] in ABIS_64 and "lib" in partes:
                al = alineaciones_elf(z.read(nombre))
                (buenas if al and min(al) >= PAGINA_16K else malas).append({"so": nombre, "alineaciones": al})
    return {"nativas_64": len(malas) + len(buenas), "sin_16k": malas, "ok": not malas}


def leer_manifiesto(xml: str) -> dict:
    raiz = ET.fromstring(xml)
    usa = raiz.find("uses-sdk")
    app = raiz.find("application")
    permisos = []
    for p in raiz.findall("uses-permission") + raiz.findall("uses-permission-sdk-23"):
        permisos.append({"nombre": p.get(NS + "name"), "flags": p.get(NS + "usesPermissionFlags"),
                         "max_sdk": p.get(NS + "maxSdkVersion")})
    servicios = []
    if app is not None:
        for s in app.findall("service"):
            servicios.append({"nombre": s.get(NS + "name"), "tipo_fgs": s.get(NS + "foregroundServiceType")})

    def entero(v):
        try:
            return int(v)
        except (TypeError, ValueError):
            return None
    return {
        "paquete": raiz.get("package"),
        "version_code": entero(raiz.get(NS + "versionCode")),
        "version_name": raiz.get(NS + "versionName"),
        "min_sdk": entero(usa.get(NS + "minSdkVersion")) if usa is not None else None,
        "target_sdk": entero(usa.get(NS + "targetSdkVersion")) if usa is not None else None,
        "depurable": (app is not None and app.get(NS + "debuggable") == "true"),
        "permisos": permisos,
        "servicios": servicios,
    }


def declaraciones(manifiesto: dict) -> list[str]:
    """Lo que Play Console va a pedir declarar por los permisos y servicios del manifiesto."""
    avisos = []
    for p in manifiesto["permisos"]:
        nombre = p["nombre"] or ""
        if nombre in PERMISOS_DECLARABLES:
            texto = PERMISOS_DECLARABLES[nombre]
            if nombre.endswith("BLUETOOTH_SCAN") and "neverForLocation" in (p.get("flags") or ""):
                texto = "Bluetooth con neverForLocation: Seguridad de los datos (no cuenta como ubicación)"
            if p.get("max_sdk"):
                texto += f" (solo hasta Android API {p['max_sdk']})"
            avisos.append(f"{nombre.rsplit('.', 1)[-1]}: {texto}")
        elif nombre.startswith("android.permission.FOREGROUND_SERVICE_"):
            avisos.append(f"{nombre.rsplit('.', 1)[-1]}: declarar el tipo de servicio en primer plano "
                          f"(descripción, impacto y vídeo)")
    for s in manifiesto["servicios"]:
        if s["tipo_fgs"]:
            avisos.append(f"Servicio {s['nombre']} ({s['tipo_fgs']}): declaración de servicios en primer plano")
    return avisos


def veredicto(manifiesto: dict, r16k: dict) -> list[str]:
    """Bloqueos: lo que Play rechazaría hoy."""
    fallos = []
    if (manifiesto["target_sdk"] or 0) < MIN_TARGET_SDK:
        fallos.append(f"targetSdk {manifiesto['target_sdk']} < {MIN_TARGET_SDK}: Play no acepta apps nuevas ni "
                      f"actualizaciones con menos desde el 31-ago-2026")
    if manifiesto["depurable"]:
        fallos.append("android:debuggable=true: Play rechaza bundles depurables (usa bundleRelease)")
    if not manifiesto["version_code"]:
        fallos.append("sin versionCode")
    elif manifiesto["version_code"] > 2_100_000_000:
        fallos.append("versionCode mayor que 2100000000 (máximo de Play)")
    if not r16k["ok"]:
        fallos.append(f"{len(r16k['sin_16k'])} librería(s) nativas de 64 bits sin alinear a 16 KB: obligatorio para "
                      f"publicar actualizaciones desde el 1-feb-2027 (NDK r28+ o -Wl,-z,max-page-size=16384)")
    return fallos


def cuerpo_pista(pista: str, version_code: int, estado: str, notas: dict[str, str] | None,
                 nombre: str | None, fraccion: float | None) -> dict:
    if estado not in ("draft", "completed", "inProgress", "halted"):
        raise Error("Estado de versión: draft, completed, inProgress o halted.")
    if estado in ("inProgress", "halted"):
        if fraccion is None or not 0 < fraccion < 1:
            raise Error("inProgress/halted exigen --fraccion entre 0 y 1 (sin incluirlos).")
    elif fraccion is not None:
        raise Error("--fraccion solo vale con inProgress o halted.")
    release = {"versionCodes": [str(version_code)], "status": estado}
    if nombre:
        release["name"] = nombre
    if notas:
        release["releaseNotes"] = [{"language": k, "text": v} for k, v in notas.items()]
    if fraccion is not None:
        release["userFraction"] = fraccion
    return {"track": pista, "releases": [release]}


def exigir_permiso_pista(pista: str, confirmo: bool, confirmo_produccion: bool) -> None:
    if pista == "production":
        if not confirmo_produccion:
            raise Error("Subir a producción exige --confirmo-produccion, y solo tras el «sí» de Steven en el chat "
                        "para ESTA versión.")
    elif pista != "internal" and not confirmo:
        raise Error(f"La pista {pista!r} llega a testers: exige --confirmo, y solo tras el «sí» de Steven en el chat.")


def huella_sha256(texto_keytool: str) -> str | None:
    m = re.search(r"SHA256:\s*([0-9A-F:]{95})", texto_keytool)
    return m.group(1) if m else None


def leer_solicitud(texto: str) -> dict:
    """Cabecera de publicacion/SOLICITUD.md: líneas «Clave: valor» hasta la primera línea vacía tras el título."""
    datos = {}
    for linea in texto.splitlines()[1:40]:
        m = re.match(r"\*{0,2}([A-Za-zÁÉÍÓÚáéíóúñ ]+?):\*{0,2}\s*(.+)$", linea.strip())
        if m:
            datos[m.group(1).strip().lower()] = m.group(2).strip()
    return datos


# ======================================================================== utilidades
def _correr(cmd: list, timeout: float = 300, env_extra: dict | None = None) -> subprocess.CompletedProcess:
    env = dict(os.environ)
    env["JAVA_HOME"] = str(JAVA_HOME)
    env["ANDROID_HOME"] = str(SDK)
    if env_extra:
        env.update(env_extra)
    try:
        r = subprocess.run([str(c) for c in cmd], capture_output=True, timeout=timeout, env=env)
    except subprocess.TimeoutExpired as e:
        raise Error(f"Tardó más de {timeout:.0f} s: {Path(str(cmd[0])).name}") from e
    except FileNotFoundError as e:
        raise Error(f"No existe {cmd[0]}: ejecuta `movil.bat doctor`.") from e
    r.stdout = r.stdout.decode("utf-8", errors="replace")
    r.stderr = r.stderr.decode("utf-8", errors="replace")
    return r


def _tapar(texto: str, secreto: str | None) -> str:
    return texto.replace(secreto, "[tapado]") if secreto and secreto in texto else texto


def _bundletool(*args, timeout: float = 600) -> subprocess.CompletedProcess:
    if not BUNDLETOOL.exists():
        raise Error(f"Falta bundletool en {BUNDLETOOL}.")
    return _correr([JAVA_HOME / "bin" / "java.exe", "-jar", BUNDLETOOL, *args], timeout=timeout)


def registro() -> dict:
    if not REGISTRO.exists():
        return {}
    return json.loads(REGISTRO.read_text(encoding="utf-8"))


def ficha_app(app: str) -> dict:
    reg = registro()
    if app not in reg:
        raise Error(f"La app {app!r} no está en {REGISTRO}. Apps: {', '.join(sorted(reg)) or '(ninguna)'}.")
    return reg[app]


# ---------------------------------------------------------------- Administrador de credenciales
class Boveda:
    """CredRead/CredWrite directos con persistencia «solo este PC» (ver la TRAMPA de keyring en Claves API)."""

    def __init__(self):
        from win32ctypes.pywin32 import pywintypes, win32cred
        self._wc, self._err = win32cred, pywintypes.error

    def existe(self, serv: str) -> bool:
        try:
            self._wc.CredRead(TargetName=serv, Type=self._wc.CRED_TYPE_GENERIC)
            return True
        except self._err as e:
            if e.winerror == 1168:
                return False
            raise

    def leer(self, serv: str) -> str:
        try:
            c = self._wc.CredRead(TargetName=serv, Type=self._wc.CRED_TYPE_GENERIC)
        except self._err as e:
            if e.winerror == 1168:
                raise Error(f"No hay nada guardado como {serv} en el Administrador de credenciales.") from e
            raise
        blob = c["CredentialBlob"]
        return blob.decode("utf-16-le") if isinstance(blob, bytes) else blob

    def escribir(self, serv: str, valor: str, comentario: str) -> None:
        try:
            self._wc.CredWrite(dict(Type=self._wc.CRED_TYPE_GENERIC, TargetName=serv, UserName=USUARIO_FIRMA,
                                    CredentialBlob=valor, Comment=comentario, Persist=LOCAL_MACHINE), 0)
        except self._err as e:
            raise Error(f"Windows no pudo guardar {serv} (error {e.winerror}).") from e

    def borrar(self, serv: str) -> bool:
        try:
            self._wc.CredDelete(TargetName=serv, Type=self._wc.CRED_TYPE_GENERIC)
            return True
        except self._err as e:
            if e.winerror == 1168:
                return False
            raise


# ---------------------------------------------------------------- DPAPI (credencial de la API de Play)
class _BLOB(ctypes.Structure):
    _fields_ = [("cbData", wt.DWORD), ("pbData", ctypes.c_void_p)]


def _dpapi(datos: bytes, cifrar: bool) -> bytes:
    crypt32, kernel32 = ctypes.windll.crypt32, ctypes.windll.kernel32
    fn = crypt32.CryptProtectData if cifrar else crypt32.CryptUnprotectData
    fn.argtypes = [ctypes.POINTER(_BLOB), ctypes.c_void_p, ctypes.POINTER(_BLOB), ctypes.c_void_p, ctypes.c_void_p,
                   wt.DWORD, ctypes.POINTER(_BLOB)]
    fn.restype = wt.BOOL
    kernel32.LocalFree.argtypes = [ctypes.c_void_p]
    buf = ctypes.create_string_buffer(datos, len(datos))
    entrada = _BLOB(len(datos), ctypes.cast(buf, ctypes.c_void_p))
    salida = _BLOB()
    if not fn(ctypes.byref(entrada), None, None, None, None, 0x1, ctypes.byref(salida)):   # UI_FORBIDDEN
        raise Error(f"DPAPI falló ({ctypes.GetLastError()}): ¿otro usuario de Windows u otro PC?")
    try:
        return ctypes.string_at(salida.pbData, salida.cbData)
    finally:
        kernel32.LocalFree(salida.pbData)


def dpapi_cifrar(datos: bytes) -> bytes:
    return _dpapi(datos, True)


def dpapi_descifrar(datos: bytes) -> bytes:
    return _dpapi(datos, False)


# ======================================================================== órdenes: firma
def _rutas_firma(app: str) -> dict:
    d = FIRMAS / validar_app(app)
    return {"carpeta": d, "almacen": d / "upload.p12", "certificado": d / "upload_certificate.pem"}


def _huella_almacen(almacen: Path, clave: str) -> tuple[str, str]:
    r = _correr([KEYTOOL, "-list", "-v", "-keystore", almacen, "-storetype", "PKCS12", "-alias", ALIAS,
                 "-storepass:env", "MOVIL_KS"], env_extra={"MOVIL_KS": clave}, timeout=60)
    texto = _tapar(r.stdout + r.stderr, clave)
    if r.returncode != 0:
        raise Error(f"keytool no pudo leer {almacen}: {texto[-300:]}")
    huella = huella_sha256(texto)
    m = re.search(r"Valid from: .+? until: (.+)", texto)
    return huella or "?", (m.group(1).strip() if m else "?")


def firma_crear(app: str, nombre_comun: str | None = None) -> dict:
    rutas = _rutas_firma(app)
    serv = servicio_firma(app)
    bov = Boveda()
    if rutas["almacen"].exists() or bov.existe(serv):
        raise Error(f"Ya hay una clave de subida para {app} ({rutas['almacen']} o {serv}). No se pisa: una clave de "
                    f"subida no se cambia sin pedir el restablecimiento en Play Console.")
    rutas["carpeta"].mkdir(parents=True, exist_ok=True)
    clave = secrets.token_urlsafe(32)
    temporal = rutas["carpeta"] / "upload.p12.nuevo"
    if temporal.exists():
        temporal.unlink()
    dn = f"CN={nombre_comun or app} upload key, C=EC"
    r = _correr([KEYTOOL, "-genkeypair", "-keystore", temporal, "-storetype", "PKCS12", "-alias", ALIAS,
                 "-keyalg", "RSA", "-keysize", "4096", "-validity", "10000", "-dname", dn,
                 "-storepass:env", "MOVIL_KS", "-keypass:env", "MOVIL_KS"], env_extra={"MOVIL_KS": clave}, timeout=120)
    if r.returncode != 0 or not temporal.exists():
        raise Error("keytool no creó la clave: " + _tapar(r.stdout + r.stderr, clave)[-400:])
    try:
        bov.escribir(serv, clave, f"clave de subida de {app} (solo este PC)")
        if bov.leer(serv) != clave:
            raise Error("La contraseña leída de la bóveda no coincide con la escrita.")
    except Exception:
        temporal.unlink(missing_ok=True)
        bov.borrar(serv)
        raise
    temporal.replace(rutas["almacen"])
    cert = _correr([KEYTOOL, "-exportcert", "-rfc", "-keystore", rutas["almacen"], "-storetype", "PKCS12",
                    "-alias", ALIAS, "-storepass:env", "MOVIL_KS", "-file", rutas["certificado"]],
                   env_extra={"MOVIL_KS": clave})
    huella, caduca = _huella_almacen(rutas["almacen"], clave)
    return {"app": app, "almacen": str(rutas["almacen"]), "alias": ALIAS, "boveda": serv, "sha256": huella,
            "caduca": caduca, "certificado_publico": str(rutas["certificado"]) if cert.returncode == 0 else None,
            "siguiente": "Haz una copia de la carpeta de la firma y de la contraseña fuera de este PC "
                         "(docs/firma-y-claves.md, «Copia de seguridad»)."}


def firma_comprobar(app: str) -> dict:
    rutas = _rutas_firma(app)
    serv = servicio_firma(app)
    bov = Boveda()
    if not rutas["almacen"].exists():
        raise Error(f"No existe {rutas['almacen']}: crea la clave con `movil.bat firma crear {app}`.")
    if not bov.existe(serv):
        raise Error(f"Falta la contraseña {serv} en el Administrador de credenciales de este PC.")
    huella, caduca = _huella_almacen(rutas["almacen"], bov.leer(serv))
    return {"app": app, "almacen": str(rutas["almacen"]), "boveda": serv, "sha256": huella, "caduca": caduca,
            "ok": huella != "?"}


def _huella_firmante(archivo: Path) -> str | None:
    r = _correr([KEYTOOL, "-printcert", "-jarfile", archivo], timeout=60)
    return huella_sha256(r.stdout + r.stderr)


def _firmado(archivo: Path) -> bool:
    r = _correr([JARSIGNER, "-verify", archivo], timeout=120)
    return "jar verified" in r.stdout


def firmar(app: str, aab: str, salida: str | None = None) -> dict:
    origen = Path(aab)
    if origen.suffix.lower() != ".aab" or not origen.exists():
        raise Error(f"No existe el .aab {origen}.")
    man = manifiesto_aab(origen)
    if man["depurable"]:
        raise Error("El bundle es depurable: firma solo el de `bundleRelease`.")
    esperado = ficha_app(app).get("paquete")
    if esperado and man["paquete"] != esperado:
        raise Error(f"El bundle es de {man['paquete']}, pero {app} es {esperado} en el registro.")
    if _firmado(origen):
        raise Error("El bundle ya viene firmado (¿con la clave debug?). La app debe entregar el AAB de release SIN "
                    "firmar: quita el signingConfig de release de su Gradle.")
    rutas = _rutas_firma(app)
    serv = servicio_firma(app)
    clave = Boveda().leer(serv)
    destino = Path(salida) if salida else origen.with_name(f"{origen.stem}-firmado.aab")
    r = _correr([JARSIGNER, "-keystore", rutas["almacen"], "-storetype", "PKCS12", "-storepass:env", "MOVIL_KS",
                 "-sigalg", "SHA256withRSA", "-digestalg", "SHA-256", "-signedjar", destino, origen, ALIAS],
                env_extra={"MOVIL_KS": clave}, timeout=300)
    if r.returncode != 0 or not destino.exists():
        raise Error("jarsigner falló: " + _tapar(r.stdout + r.stderr, clave)[-400:])
    huella_esperada, _ = _huella_almacen(rutas["almacen"], clave)
    huella = _huella_firmante(destino)
    if not _firmado(destino) or huella != huella_esperada:
        raise Error(f"La firma no se verifica o no es la clave de subida de {app} (huella {huella}).")
    return {"app": app, "paquete": man["paquete"], "version_code": man["version_code"], "firmado": str(destino),
            "sha256_firmante": huella, "bytes": destino.stat().st_size}


def apk_universal(app: str, aab: str, salida: str | None = None) -> dict:
    """APK único para pasar a amigos fuera de Play, firmado con la clave de subida (ver TRAMPA en AGENTS.md)."""
    origen = Path(aab)
    rutas = _rutas_firma(app)
    clave = Boveda().leer(servicio_firma(app))
    carpeta = Path(tempfile.mkdtemp(prefix="movil-apk-"))
    try:
        fichero_clave = carpeta / "ks.txt"
        fichero_clave.write_text(clave, encoding="utf-8")
        apks = carpeta / "universal.apks"
        r = _bundletool("build-apks", f"--bundle={origen}", f"--output={apks}", "--mode=universal",
                        f"--ks={rutas['almacen']}", f"--ks-pass=file:{fichero_clave}", f"--ks-key-alias={ALIAS}",
                        f"--key-pass=file:{fichero_clave}")
        fichero_clave.unlink()
        if r.returncode != 0:
            raise Error("bundletool build-apks falló: " + _tapar(r.stdout + r.stderr, clave)[-500:])
        destino = Path(salida) if salida else origen.with_name(f"{origen.stem.replace('-firmado', '')}-universal.apk")
        with zipfile.ZipFile(apks) as z:
            destino.write_bytes(z.read("universal.apk"))
    finally:
        shutil.rmtree(carpeta, ignore_errors=True)
    v = _correr([BUILD_TOOLS / "apksigner.bat", "verify", "--print-certs", destino], timeout=120)
    huella_apk = re.search(r"SHA-256 digest: ([0-9a-f]{64})", v.stdout)
    return {"app": app, "apk": str(destino), "bytes": destino.stat().st_size, "verificado": v.returncode == 0,
            "sha256_firmante": huella_apk.group(1) if huella_apk else None}


# ======================================================================== órdenes: revisar y probar
def manifiesto_aab(aab: Path) -> dict:
    r = _bundletool("dump", "manifest", f"--bundle={aab}", timeout=120)
    if r.returncode != 0:
        raise Error(f"bundletool no pudo leer el manifiesto de {aab}: {(r.stdout + r.stderr)[-300:]}")
    inicio = r.stdout.find("<manifest")
    return leer_manifiesto(r.stdout[inicio:])


def revisar(aab: str) -> dict:
    """Lo que se puede medir del artefacto contra los requisitos de Play de hoy. No sustituye a Play Console."""
    origen = Path(aab)
    if origen.suffix.lower() != ".aab" or not origen.exists():
        raise Error(f"No existe el .aab {origen}: Play solo acepta App Bundles para apps nuevas.")
    valida = _bundletool("validate", f"--bundle={origen}", timeout=300)
    man = manifiesto_aab(origen)
    r16k = revisar_16k(origen)
    bloqueos = veredicto(man, r16k)
    if valida.returncode != 0:
        bloqueos.insert(0, "bundletool validate falló: " + (valida.stdout + valida.stderr).strip()[-300:])
    return {"aab": str(origen), "bytes": origen.stat().st_size, "firmado": _firmado(origen),
            "sha256_firmante": _huella_firmante(origen), "manifiesto": {k: v for k, v in man.items() if k != "permisos"},
            "permisos": [p["nombre"] for p in man["permisos"]], "declaraciones_play": declaraciones(man),
            "16k": r16k, "bloqueos": bloqueos, "ok": not bloqueos}


def _lab():
    sys.path.insert(0, str(LAB_DIR))
    import lab  # noqa: PLC0415
    return lab


def probar(archivo: str, instancia: int = 0, guion: str | None = None, espera: float = 4.0) -> dict:
    """Prueba de humo en el laboratorio: instalación limpia, arranque, sin cierres, captura y (opcional) un guion."""
    lab = _lab()
    origen = Path(archivo)
    if origen.suffix.lower() == ".aab":
        paquete = manifiesto_aab(origen)["paquete"]
    else:
        r = _correr([BUILD_TOOLS / "aapt2.exe", "dump", "badging", origen], timeout=60)
        m = re.search(r"package: name='([^']+)'", r.stdout)
        if not m:
            raise Error(f"No pude leer el paquete de {origen}.")
        paquete = m.group(1)
    serial = lab.serial_de(instancia)
    pasos = {}
    if not any(d["serial"] == serial for d in lab.dispositivos()):
        pasos["arrancar"] = lab.arrancar(instancia)
    lab.desinstalar(paquete, instancia)
    lab.logcat(instancia, limpiar=True)
    pasos["instalar"] = lab.instalar(str(origen), instancia)
    pasos["abrir"] = lab.abrir(paquete, instancia)
    time.sleep(espera)
    pasos["fallos"] = lab.fallos(paquete, instancia)
    pasos["captura"] = lab.captura(instancia)
    if guion:
        pasos["guion"] = lab.guion(guion, instancia)
    ok = pasos["fallos"]["limpio"] and (not guion or pasos["guion"]["ok"])
    return {"paquete": paquete, "serial": serial, "ok": ok, "pasos": pasos}


# ======================================================================== órdenes: API de Play
def credencial_guardar(ruta_json: str, reemplazar: bool = False) -> dict:
    origen = Path(ruta_json)
    if not origen.exists():
        raise Error(f"No existe {origen}.")
    try:
        info = json.loads(origen.read_text(encoding="utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError) as e:
        raise Error("El archivo no es el JSON de una cuenta de servicio de Google Cloud.") from e
    faltan = [k for k in ("type", "client_email", "private_key", "project_id") if not info.get(k)]
    if faltan or info.get("type") != "service_account":
        raise Error(f"No es una clave de cuenta de servicio (type={info.get('type')!r}, faltan {faltan}).")
    if CRED_PLAY.exists() and not reemplazar:
        raise Error(f"Ya hay una credencial en {CRED_PLAY}: usa --reemplazar si Steven lo pidió.")
    SECRETOS.mkdir(parents=True, exist_ok=True)
    cifrado = dpapi_cifrar(json.dumps(info).encode("utf-8"))
    temporal = CRED_PLAY.with_suffix(".nuevo")
    temporal.write_bytes(cifrado)
    if json.loads(dpapi_descifrar(temporal.read_bytes())) != info:
        temporal.unlink()
        raise Error("La credencial cifrada no se pudo leer de vuelta: no se guardó nada.")
    temporal.replace(CRED_PLAY)
    return {"guardada": str(CRED_PLAY), "cuenta_de_servicio": info["client_email"], "proyecto": info["project_id"],
            "siguiente": f"Borra el original con Mayús+Supr: {origen}. Luego `movil.bat play credencial comprobar`."}


def _credenciales():
    if not CRED_PLAY.exists():
        raise Error("No hay credencial de la API de Play en este PC: docs/api-play.md, «Dar acceso a la API».")
    from google.oauth2 import service_account  # noqa: PLC0415
    info = json.loads(dpapi_descifrar(CRED_PLAY.read_bytes()))
    return service_account.Credentials.from_service_account_info(
        info, scopes=["https://www.googleapis.com/auth/androidpublisher"])


def _servicio_play():
    from googleapiclient.discovery import build  # noqa: PLC0415
    return build("androidpublisher", "v3", credentials=_credenciales(), cache_discovery=False)


def credencial_comprobar() -> dict:
    from google.auth.transport.requests import Request  # noqa: PLC0415
    cred = _credenciales()
    try:
        cred.refresh(Request())
    except Exception as e:  # noqa: BLE001
        raise Error(f"Google rechazó la credencial: {type(e).__name__}: {str(e)[:300]}") from e
    return {"cuenta_de_servicio": cred.service_account_email, "token": "obtenido (no se muestra)", "ok": True}


def _error_google(e: Exception) -> Error:
    texto = getattr(e, "content", b"")
    texto = texto.decode("utf-8", errors="replace") if isinstance(texto, bytes) else str(texto)
    return Error(f"La API de Play respondió {getattr(getattr(e, 'resp', None), 'status', '?')}: "
                 f"{(texto or str(e))[:600]}")


def play_estado(paquete: str, servicio=None) -> dict:
    validar_paquete(paquete)
    s = servicio or _servicio_play()
    edits = s.edits()
    try:
        edit = edits.insert(packageName=paquete, body={}).execute()
        pistas = edits.tracks().list(packageName=paquete, editId=edit["id"]).execute().get("tracks", [])
        edits.delete(packageName=paquete, editId=edit["id"]).execute()
    except Exception as e:  # noqa: BLE001
        if type(e).__name__ == "HttpError":
            raise _error_google(e) from e
        raise
    return {"paquete": paquete, "pistas": pistas}


def play_subir(app: str, aab: str, pista: str = "internal", estado: str = "completed",
               notas: dict[str, str] | None = None, nombre: str | None = None, fraccion: float | None = None,
               sin_revision: bool = False, confirmo: bool = False, confirmo_produccion: bool = False,
               servicio=None) -> dict:
    exigir_permiso_pista(pista, confirmo, confirmo_produccion)
    origen = Path(aab)
    ficha = ficha_app(app)
    rev = revisar(str(origen))
    if not rev["ok"]:
        raise Error("El bundle no pasa la revisión: " + " | ".join(rev["bloqueos"]))
    huella_esperada = firma_comprobar(app)["sha256"]
    if rev["sha256_firmante"] != huella_esperada:
        raise Error(f"El bundle no está firmado con la clave de subida de {app}: usa `movil.bat firmar {app} …`.")
    paquete = rev["manifiesto"]["paquete"]
    if ficha.get("paquete") != paquete:
        raise Error(f"El bundle es de {paquete} y el registro dice {ficha.get('paquete')}.")
    cuerpo = cuerpo_pista(pista, rev["manifiesto"]["version_code"], estado, notas, nombre, fraccion)
    s = servicio or _servicio_play()
    edits = s.edits()
    edit_id = None
    try:
        from googleapiclient.http import MediaFileUpload  # noqa: PLC0415
        edit_id = edits.insert(packageName=paquete, body={}).execute()["id"]
        subida = edits.bundles().upload(packageName=paquete, editId=edit_id,
                                        media_body=MediaFileUpload(str(origen), mimetype="application/octet-stream",
                                                                   resumable=True)).execute()
        edits.tracks().update(packageName=paquete, editId=edit_id, track=pista, body=cuerpo).execute()
        hecho = edits.commit(packageName=paquete, editId=edit_id,
                             changesNotSentForReview=sin_revision or None).execute()
    except Exception as e:  # noqa: BLE001
        if edit_id:
            try:
                edits.delete(packageName=paquete, editId=edit_id).execute()
            except Exception:  # noqa: BLE001
                pass
        if type(e).__name__ == "HttpError":
            raise _error_google(e) from e
        raise
    return {"app": app, "paquete": paquete, "pista": pista, "estado": estado,
            "version_code": subida.get("versionCode"), "sha256_subido": subida.get("sha256"),
            "edit": hecho.get("id"), "enviado_a_revision": not sin_revision}


# ======================================================================== órdenes: protocolo con las apps
def solicitudes() -> dict:
    """Estado de las solicitudes de publicación que dejan las conversaciones de cada app."""
    filas = []
    for app, f in sorted(registro().items()):
        carpeta = Path(f.get("carpeta", ""))
        sol = carpeta / "publicacion" / "SOLICITUD.md"
        resp = carpeta / "publicacion" / "RESPUESTA.md"
        fila = {"app": app, "carpeta": str(carpeta), "estado_registro": f.get("estado")}
        if sol.exists():
            fila["solicitud"] = leer_solicitud(sol.read_text(encoding="utf-8", errors="replace"))
            fila["solicitud_modificada"] = _dt.datetime.fromtimestamp(sol.stat().st_mtime).isoformat(timespec="minutes")
            fila["pendiente"] = not resp.exists() or resp.stat().st_mtime < sol.stat().st_mtime
        else:
            fila["pendiente"] = False
        filas.append(fila)
    return {"apps": filas, "pendientes": [f["app"] for f in filas if f.get("pendiente")]}


def doctor() -> dict:
    def ok(c):
        return "OK" if c else "FALTA"
    lab_ok = (LAB_DIR / "lab.py").exists()
    filas = {
        "jdk17 (keytool/jarsigner)": ok(KEYTOOL.exists() and JARSIGNER.exists()),
        "sdk": ok(SDK.exists()),
        "build-tools 36.0.0": ok((BUILD_TOOLS / "aapt2.exe").exists()),
        "platform android-36": ok((SDK / "platforms" / "android-36" / "android.jar").exists()),
        "cmdline-tools": ok((SDK / "cmdline-tools" / "latest" / "bin" / "android.exe").exists()),
        "bundletool": ok(BUNDLETOOL.exists()),
        "laboratorio": ok(lab_ok),
        "credencial Play (DPAPI)": "OK" if CRED_PLAY.exists() else "FALTA (Steven: docs/api-play.md)",
    }
    try:
        import googleapiclient  # noqa: F401,PLC0415
        import google.auth  # noqa: F401,PLC0415
        filas["librerías API Play"] = "OK"
    except ImportError:
        filas["librerías API Play"] = "FALTA (.venv)"
    bov = Boveda()
    for app in registro():
        filas[f"firma {app}"] = ok(_rutas_firma(app)["almacen"].exists() and bov.existe(servicio_firma(app)))
    return {"comprobaciones": filas, "ok": all(v == "OK" for k, v in filas.items() if not k.startswith(("firma", "credencial")))}


# ======================================================================== línea de órdenes
def _notas(args) -> dict | None:
    notas = {}
    if args.notas_es:
        notas["es-419"] = args.notas_es
    if args.notas_en:
        notas["en-US"] = args.notas_en
    return notas or None


def _parser() -> argparse.ArgumentParser:
    ap = argparse.ArgumentParser(prog="movil.bat", description="Administrador Móvil (ver AGENTS.md)")
    sub = ap.add_subparsers(dest="orden", required=True)
    sub.add_parser("doctor")
    sub.add_parser("solicitudes")
    p = sub.add_parser("firma"); s = p.add_subparsers(dest="sub", required=True)
    q = s.add_parser("crear"); q.add_argument("app"); q.add_argument("--nombre-comun")
    q = s.add_parser("comprobar"); q.add_argument("app")
    p = sub.add_parser("firmar"); p.add_argument("app"); p.add_argument("aab"); p.add_argument("--salida")
    p = sub.add_parser("apk-universal"); p.add_argument("app"); p.add_argument("aab"); p.add_argument("--salida")
    p = sub.add_parser("revisar"); p.add_argument("aab")
    p = sub.add_parser("probar"); p.add_argument("archivo"); p.add_argument("--instancia", type=int, default=0)
    p.add_argument("--guion"); p.add_argument("--espera", type=float, default=4.0)
    p = sub.add_parser("play"); s = p.add_subparsers(dest="sub", required=True)
    q = s.add_parser("credencial"); q.add_argument("accion", choices=["guardar", "comprobar"])
    q.add_argument("ruta", nargs="?"); q.add_argument("--reemplazar", action="store_true")
    q = s.add_parser("estado"); q.add_argument("paquete")
    q = s.add_parser("subir"); q.add_argument("app"); q.add_argument("aab"); q.add_argument("--pista", default="internal")
    q.add_argument("--estado", default="completed"); q.add_argument("--notas-es"); q.add_argument("--notas-en")
    q.add_argument("--nombre"); q.add_argument("--fraccion", type=float); q.add_argument("--sin-revision", action="store_true")
    q.add_argument("--confirmo", action="store_true"); q.add_argument("--confirmo-produccion", action="store_true")
    return ap


def ejecutar(argv: list[str]) -> tuple[dict, bool]:
    a = _parser().parse_args(argv)
    if a.orden == "doctor":
        r = doctor()
        return r, r["ok"]
    if a.orden == "solicitudes":
        return solicitudes(), True
    if a.orden == "firma":
        return (firma_crear(a.app, a.nombre_comun) if a.sub == "crear" else firma_comprobar(a.app)), True
    if a.orden == "firmar":
        return firmar(a.app, a.aab, a.salida), True
    if a.orden == "apk-universal":
        r = apk_universal(a.app, a.aab, a.salida)
        return r, r["verificado"]
    if a.orden == "revisar":
        r = revisar(a.aab)
        return r, r["ok"]
    if a.orden == "probar":
        r = probar(a.archivo, a.instancia, a.guion, a.espera)
        return r, r["ok"]
    if a.orden == "play":
        if a.sub == "credencial":
            if a.accion == "guardar":
                if not a.ruta:
                    raise Error("Falta la ruta del JSON de la cuenta de servicio.")
                return credencial_guardar(a.ruta, a.reemplazar), True
            return credencial_comprobar(), True
        if a.sub == "estado":
            return play_estado(a.paquete), True
        if a.sub == "subir":
            return play_subir(a.app, a.aab, a.pista, a.estado, _notas(a), a.nombre, a.fraccion, a.sin_revision,
                              a.confirmo, a.confirmo_produccion), True
    raise Error(f"Orden sin implementar: {argv}")


def main(argv: list[str] | None = None) -> int:
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    except AttributeError:
        pass
    try:
        resultado, ok = ejecutar(sys.argv[1:] if argv is None else argv)
    except Error as e:
        resultado, ok = {"error": str(e)}, False
    except Exception as e:  # noqa: BLE001
        if type(e).__name__ != "ErrorLab":      # los errores explicados del laboratorio se muestran igual
            raise
        resultado, ok = {"error": f"Laboratorio: {e}"}, False
    print(json.dumps(resultado, ensure_ascii=False, indent=1, default=str))
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
