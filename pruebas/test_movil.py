"""Pruebas de movil.py. Sin red y sin tocar las firmas reales:
    .venv\\Scripts\\python.exe -I -m pytest -q pruebas
Las marcadas `herramientas` usan keytool/jarsigner/bundletool y el Administrador de credenciales con nombres
`android-firma-prueba-<pid>` que se borran al acabar (`-m herramientas`).
"""
import json
import os
import struct
import subprocess
import sys
import zipfile
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import movil  # noqa: E402

A = "{http://schemas.android.com/apk/res/android}"
MANIFIESTO = """<manifest xmlns:android="http://schemas.android.com/apk/res/android" package="com.steven.buscadorble"
  android:versionCode="4" android:versionName="4.0">
  <uses-sdk android:minSdkVersion="26" android:targetSdkVersion="35"/>
  <uses-permission android:name="android.permission.BLUETOOTH" android:maxSdkVersion="30"/>
  <uses-permission android:name="android.permission.BLUETOOTH_SCAN" android:usesPermissionFlags="neverForLocation"/>
  <uses-permission android:name="android.permission.ACCESS_FINE_LOCATION"/>
  <uses-permission android:name="android.permission.FOREGROUND_SERVICE_CONNECTED_DEVICE"/>
  <application android:debuggable="true">
    <service android:name=".Escaner" android:foregroundServiceType="connectedDevice"/>
  </application>
</manifest>"""


def elf64(alineaciones):
    """ELF64 mínimo con un PT_LOAD por alineación."""
    phoff, phentsize = 64, 56
    cab = bytearray(64)
    cab[:6] = b"\x7fELF\x02\x01"
    struct.pack_into("<Q", cab, 0x20, phoff)
    struct.pack_into("<HH", cab, 0x36, phentsize, len(alineaciones))
    cuerpo = bytearray()
    for al in alineaciones:
        ph = bytearray(56)
        struct.pack_into("<I", ph, 0, 1)
        struct.pack_into("<Q", ph, 0x30, al)
        cuerpo += ph
    return bytes(cab + cuerpo)


# ------------------------------------------------------------------ nombres
def test_nombres_validos_e_invalidos():
    assert movil.validar_app("buscador-geiger") == "buscador-geiger"
    for malo in ("", "A", "Mayus", "con espacio", "x" * 41, "-empieza"):
        with pytest.raises(movil.Error):
            movil.validar_app(malo)
    assert movil.servicio_firma("canario") == "android-firma-canario"
    movil.validar_paquete("com.steven.canario")
    for malo in ("canario", "com..x", "1com.x"):
        with pytest.raises(movil.Error):
            movil.validar_paquete(malo)


# ------------------------------------------------------------------ 16 KB
def test_elf_alineaciones():
    assert movil.alineaciones_elf(elf64([16384, 65536])) == [16384, 65536]
    assert movil.alineaciones_elf(b"no es elf") == []
    elf32 = bytearray(elf64([4096])); elf32[4] = 1
    assert movil.alineaciones_elf(bytes(elf32)) == []


def test_revisar_16k_solo_64_bits(tmp_path):
    aab = tmp_path / "x.aab"
    with zipfile.ZipFile(aab, "w") as z:
        z.writestr("base/lib/arm64-v8a/libbien.so", elf64([16384]))
        z.writestr("base/lib/x86_64/libmal.so", elf64([4096, 16384]))
        z.writestr("base/lib/armeabi-v7a/libviejo.so", elf64([4096]))      # 32 bits: no cuenta
        z.writestr("base/dex/classes.dex", b"dex")
    r = movil.revisar_16k(aab)
    assert r["nativas_64"] == 2
    assert [m["so"] for m in r["sin_16k"]] == ["base/lib/x86_64/libmal.so"]
    assert r["ok"] is False


def test_sin_nativas_cumple(tmp_path):
    aab = tmp_path / "x.aab"
    with zipfile.ZipFile(aab, "w") as z:
        z.writestr("base/dex/classes.dex", b"dex")
    assert movil.revisar_16k(aab) == {"nativas_64": 0, "sin_16k": [], "ok": True}


# ------------------------------------------------------------------ manifiesto y veredicto
def test_manifiesto_y_bloqueos():
    m = movil.leer_manifiesto(MANIFIESTO)
    assert (m["paquete"], m["version_code"], m["target_sdk"], m["min_sdk"]) == ("com.steven.buscadorble", 4, 35, 26)
    assert m["depurable"] is True
    bloqueos = movil.veredicto(m, {"ok": True, "sin_16k": []})
    assert any("targetSdk 35 < 36" in b for b in bloqueos)
    assert any("debuggable" in b for b in bloqueos)


def test_declaraciones_bluetooth_y_fgs():
    d = movil.declaraciones(movil.leer_manifiesto(MANIFIESTO))
    texto = " | ".join(d)
    assert "neverForLocation" in texto                     # BLUETOOTH_SCAN con la bandera buena
    assert "ACCESS_FINE_LOCATION" in texto
    assert "FOREGROUND_SERVICE_CONNECTED_DEVICE" in texto
    assert "connectedDevice" in texto
    assert not any(x.startswith("BLUETOOTH:") for x in d)  # el de maxSdkVersion=30 no se declara


def test_veredicto_limpio_y_version_code():
    m = {"target_sdk": 36, "depurable": False, "version_code": 1}
    assert movil.veredicto(m, {"ok": True, "sin_16k": []}) == []
    m["version_code"] = 2_100_000_001
    assert movil.veredicto(m, {"ok": True, "sin_16k": []})


# ------------------------------------------------------------------ pistas y permisos
def test_cuerpo_pista():
    c = movil.cuerpo_pista("internal", 7, "completed", {"es-419": "Arreglos"}, "1.0.7", None)
    assert c == {"track": "internal", "releases": [{"versionCodes": ["7"], "status": "completed", "name": "1.0.7",
                                                   "releaseNotes": [{"language": "es-419", "text": "Arreglos"}]}]}
    with pytest.raises(movil.Error):
        movil.cuerpo_pista("internal", 7, "inProgress", None, None, None)      # falta fracción
    with pytest.raises(movil.Error):
        movil.cuerpo_pista("internal", 7, "inProgress", None, None, 1.0)       # fracción no admitida
    with pytest.raises(movil.Error):
        movil.cuerpo_pista("internal", 7, "completed", None, None, 0.5)        # fracción sin rollout
    with pytest.raises(movil.Error):
        movil.cuerpo_pista("internal", 7, "publicada", None, None, None)


def test_permiso_por_pista():
    movil.exigir_permiso_pista("internal", False, False)
    with pytest.raises(movil.Error, match="--confirmo"):
        movil.exigir_permiso_pista("alpha", False, False)
    movil.exigir_permiso_pista("alpha", True, False)
    with pytest.raises(movil.Error, match="producción"):
        movil.exigir_permiso_pista("production", True, False)
    movil.exigir_permiso_pista("production", False, True)


def test_huella_y_solicitud():
    texto = "Certificate fingerprints:\n\t SHA1: AA\n\t SHA256: " + ":".join(["AB"] * 32) + "\nSignature algorithm"
    assert movil.huella_sha256(texto) == ":".join(["AB"] * 32)
    assert movil.huella_sha256("nada") is None
    sol = "# Solicitud de publicación\n**Estado:** PENDIENTE\nApp: buscador-geiger\nVersión: 5 (5.0)\n\nresto"
    d = movil.leer_solicitud(sol)
    assert d["estado"] == "PENDIENTE" and d["app"] == "buscador-geiger" and d["versión"] == "5 (5.0)"


# ------------------------------------------------------------------ subir con un servicio falso (orden de llamadas)
class Llamada:
    def __init__(self, registro, nombre, resultado):
        self.registro, self.nombre, self.resultado = registro, nombre, resultado

    def execute(self):
        self.registro.append(self.nombre)
        if isinstance(self.resultado, BaseException):        # también KeyboardInterrupt (Ctrl+C)
            raise self.resultado
        return self.resultado


class ServicioFalso:
    def __init__(self, falla_en=None):
        self.llamadas, self.args, self.falla_en = [], {}, falla_en

    def edits(self):
        return self

    def _r(self, nombre, resultado, **kw):
        self.args[nombre] = kw
        return Llamada(self.llamadas, nombre, RuntimeError("falla") if nombre == self.falla_en else resultado)

    def insert(self, **kw): return self._r("insert", {"id": "E1"}, **kw)
    def delete(self, **kw): return self._r("delete", {}, **kw)
    def commit(self, **kw): return self._r("commit", {"id": "E1"}, **kw)
    def bundles(self): return self
    def upload(self, **kw): return self._r("upload", {"versionCode": 3, "sha256": "x"}, **kw)
    def tracks(self): return self
    def update(self, **kw): return self._r("update", {}, **kw)
    def list(self, **kw): return self._r("list", {"tracks": [{"track": "internal"}]}, **kw)


@pytest.fixture
def subida_preparada(monkeypatch, tmp_path):
    aab = tmp_path / "a.aab"
    aab.write_bytes(b"PK")
    monkeypatch.setattr(movil, "ficha_app", lambda app: {"paquete": "com.steven.canario", "publicable": True})
    monkeypatch.setattr(movil, "revisar", lambda a: {"ok": True, "bloqueos": [], "firmado": True,
                                                    "sha256_firmante": "H", "sha256_firmantes": ["H"],
                                                    "manifiesto": {"paquete": "com.steven.canario", "version_code": 3}})
    monkeypatch.setattr(movil, "firma_comprobar", lambda app: {"sha256": "H"})
    return aab


def test_subir_orden_de_llamadas(subida_preparada):
    s = ServicioFalso()
    r = movil.play_subir("canario", str(subida_preparada), servicio=s, notas={"es-419": "x"})
    assert s.llamadas == ["insert", "upload", "update", "commit"]
    assert s.args["update"]["body"]["releases"][0]["versionCodes"] == ["3"]
    assert s.args["commit"]["changesNotSentForReview"] is None
    assert r["version_code"] == 3 and r["pista"] == "internal"


def test_subir_borra_el_edit_si_falla(subida_preparada):
    s = ServicioFalso(falla_en="update")
    with pytest.raises(RuntimeError):
        movil.play_subir("canario", str(subida_preparada), servicio=s)
    assert s.llamadas == ["insert", "upload", "update", "delete"]


def test_subir_rechaza_firma_ajena(subida_preparada, monkeypatch):
    monkeypatch.setattr(movil, "firma_comprobar", lambda app: {"sha256": "OTRA"})
    with pytest.raises(movil.Error, match="no está firmado con la clave de subida"):
        movil.play_subir("canario", str(subida_preparada), servicio=ServicioFalso())


def test_subir_a_testers_sin_confirmar_no_llama(subida_preparada):
    s = ServicioFalso()
    with pytest.raises(movil.Error):
        movil.play_subir("canario", str(subida_preparada), pista="alpha", servicio=s)
    assert s.llamadas == []


def test_estado(monkeypatch):
    s = ServicioFalso()
    r = movil.play_estado("com.steven.canario", servicio=s)
    assert s.llamadas == ["insert", "list", "delete"] and r["pistas"] == [{"track": "internal"}]


# ------------------------------------------------------------------ auditoría del 20-oct-2026 (PUE, FIR, SOL)
def test_pistas_de_produccion_por_dispositivo_exigen_su_confirmacion():           # PUE-01
    for pista in ("wear:production", "automotive:production", "tv:production", "Production", " production "):
        with pytest.raises(movil.Error, match="producción"):
            movil.exigir_permiso_pista(pista, True, False)
        movil.exigir_permiso_pista(pista, False, True)
    with pytest.raises(movil.Error, match="--confirmo"):
        movil.exigir_permiso_pista("cerrada-amigos", False, False)          # pista cerrada con nombre propio
    movil.exigir_permiso_pista("cerrada-amigos", True, False)
    movil.exigir_permiso_pista("Internal", False, False)


def test_huellas_de_todos_los_firmantes():                                         # FIR-01
    bloque = "Signer #{n}:\n\nCertificate fingerprints:\n\t SHA1: AA\n\t SHA256: {h}\n"
    texto = bloque.format(n=1, h=":".join(["AB"] * 32)) + bloque.format(n=2, h=":".join(["CD"] * 32))
    assert movil.huellas_sha256(texto) == [":".join(["AB"] * 32), ":".join(["CD"] * 32)]


def test_firmado_rechaza_entradas_sin_firmar(monkeypatch):                         # FIR-01
    def jarsigner(salida, codigo=0):
        return lambda cmd, timeout=120, env_extra=None: subprocess.CompletedProcess(cmd, codigo, salida, "")
    bueno = "jar verified.\n\nWarning:\nThis jar contains entries whose signer certificate is self-signed.\n"
    monkeypatch.setattr(movil, "_correr", jarsigner(bueno))
    assert movil._firmado(Path("x.aab")) is True                    # MEDIDO: así sale un AAB bien firmado
    monkeypatch.setattr(movil, "_correr", jarsigner(bueno + "This jar contains unsigned entries which have not "
                                                            "been integrity-checked.\n"))
    assert movil._firmado(Path("x.aab")) is False
    monkeypatch.setattr(movil, "_correr", jarsigner("jar is unsigned.\n"))
    assert movil._firmado(Path("x.aab")) is False
    monkeypatch.setattr(movil, "_correr", jarsigner(bueno, codigo=1))
    assert movil._firmado(Path("x.aab")) is False


def test_subir_rechaza_varios_firmantes(subida_preparada, monkeypatch):           # FIR-01
    monkeypatch.setattr(movil, "revisar", lambda a: {"ok": True, "bloqueos": [], "firmado": True,
                                                    "sha256_firmante": "H", "sha256_firmantes": ["H", "OTRA"],
                                                    "manifiesto": {"paquete": "com.steven.canario", "version_code": 3}})
    s = ServicioFalso()
    with pytest.raises(movil.Error, match="firm"):
        movil.play_subir("canario", str(subida_preparada), servicio=s)
    assert s.llamadas == []


def test_subir_rechaza_firma_no_verificada(subida_preparada, monkeypatch):         # FIR-01
    monkeypatch.setattr(movil, "revisar", lambda a: {"ok": True, "bloqueos": [], "firmado": False,
                                                    "sha256_firmante": "H", "sha256_firmantes": ["H"],
                                                    "manifiesto": {"paquete": "com.steven.canario", "version_code": 3}})
    with pytest.raises(movil.Error, match="firm"):
        movil.play_subir("canario", str(subida_preparada), servicio=ServicioFalso())


def test_subir_rechaza_app_no_publicable(subida_preparada, monkeypatch):           # PUE-02
    monkeypatch.setattr(movil, "ficha_app", lambda app: {"paquete": "com.steven.canario", "publicable": False})
    s = ServicioFalso()
    with pytest.raises(movil.Error, match="publicable"):
        movil.play_subir("canario", str(subida_preparada), servicio=s)
    assert s.llamadas == []


def test_estado_borra_el_edit_si_falla():                                          # PUE-03
    s = ServicioFalso(falla_en="list")
    with pytest.raises(RuntimeError):
        movil.play_estado("com.steven.canario", servicio=s)
    assert s.llamadas == ["insert", "list", "delete"]


def test_subir_borra_el_edit_con_ctrl_c(subida_preparada):                         # PUE-03
    class Interrumpido(ServicioFalso):
        def upload(self, **kw):
            self.args["upload"] = kw
            return Llamada(self.llamadas, "upload", KeyboardInterrupt())
    s = Interrumpido()
    with pytest.raises(KeyboardInterrupt):
        movil.play_subir("canario", str(subida_preparada), servicio=s)
    assert s.llamadas == ["insert", "upload", "delete"]


def test_solicitud_no_pisa_la_cabecera():                                          # SOL-01
    plantilla = (movil.HUB / "plantillas" / "SOLICITUD.md").read_text(encoding="utf-8")
    texto = plantilla.replace("<texto>", "Novedades: escaneo más rápido.\nEstado: sin cambios en la batería.")
    d = movil.leer_solicitud(texto)
    assert d["estado"] == "PENDIENTE"
    assert "novedades" not in d


def test_solicitud_clave_repetida_en_la_cabecera_no_pisa():                        # SOL-01
    d = movil.leer_solicitud("# Solicitud de publicación\n**Estado:** PENDIENTE\n**App:** x\nEstado: OTRO\n")
    assert d["estado"] == "PENDIENTE"


def test_solicitudes_salta_apps_sin_carpeta(monkeypatch):                          # SOL-01
    monkeypatch.setattr(movil, "registro", lambda: {"sin-carpeta": {"paquete": "com.x.y"}})
    r = movil.solicitudes()
    assert r["pendientes"] == [] and r["apps"][0].get("aviso")


def test_apk_universal_rechaza_aab_de_otra_app_sin_leer_la_clave(monkeypatch, tmp_path):   # FIR-02
    aab = tmp_path / "otra.aab"
    aab.write_bytes(b"PK")
    monkeypatch.setattr(movil, "ficha_app", lambda app: {"paquete": "com.steven.canario"})
    monkeypatch.setattr(movil, "manifiesto_aab", lambda a: {"paquete": "com.steven.buscadorble"})

    class BovedaQueNoSeDebeLeer:
        def leer(self, serv):
            raise AssertionError("se leyó la clave antes de validar el AAB")
    monkeypatch.setattr(movil, "Boveda", BovedaQueNoSeDebeLeer)
    with pytest.raises(movil.Error, match="buscadorble"):
        movil.apk_universal("canario", str(aab))
    with pytest.raises(movil.Error):
        movil.apk_universal("canario", str(tmp_path / "no-existe.aab"))


def test_firmar_borra_el_resultado_si_no_verifica(monkeypatch, tmp_path):          # FIR-02
    aab = tmp_path / "app-release.aab"
    aab.write_bytes(b"PK")
    monkeypatch.setattr(movil, "ficha_app", lambda app: {"paquete": "com.steven.canario"})
    monkeypatch.setattr(movil, "manifiesto_aab", lambda a: {"paquete": "com.steven.canario", "depurable": False,
                                                            "version_code": 1})
    monkeypatch.setattr(movil, "_firmado", lambda a: False)
    monkeypatch.setattr(movil, "_huellas_firmantes", lambda a: ["OTRA"])
    monkeypatch.setattr(movil, "_huella_almacen", lambda almacen, clave: ("H", "?"))

    class BovedaFalsa:
        def leer(self, serv):
            return "contrasena-de-prueba"
    monkeypatch.setattr(movil, "Boveda", BovedaFalsa)

    def jarsigner_falso(cmd, timeout=300, env_extra=None):
        Path(str(cmd[cmd.index("-signedjar") + 1])).write_bytes(b"PK firmado")
        return subprocess.CompletedProcess(cmd, 0, "", "")
    monkeypatch.setattr(movil, "_correr", jarsigner_falso)
    with pytest.raises(movil.Error):
        movil.firmar("canario", str(aab))
    assert not (tmp_path / "app-release-firmado.aab").exists()


def test_temporales_fuera_de_temp_y_se_limpian(monkeypatch, tmp_path):             # FIR-03
    monkeypatch.setattr(movil, "SECRETOS", tmp_path / "s")
    resto = tmp_path / "s" / "tmp" / "movil-apk-viejo"
    resto.mkdir(parents=True)
    (resto / "ks.txt").write_text("restos", encoding="utf-8")
    carpeta = movil.carpeta_temporal()
    assert carpeta.parent == tmp_path / "s" / "tmp"
    assert not resto.exists()


# ------------------------------------------------------------------ DPAPI y credencial (sin red)
def test_dpapi_ida_y_vuelta():
    datos = "credencial de prueba ñ 🔑".encode("utf-8")
    cifrado = movil.dpapi_cifrar(datos)
    assert cifrado != datos and datos not in cifrado
    assert movil.dpapi_descifrar(cifrado) == datos


def test_credencial_guardar(tmp_path, monkeypatch):
    monkeypatch.setattr(movil, "SECRETOS", tmp_path / "s")
    monkeypatch.setattr(movil, "CRED_PLAY", tmp_path / "s" / "play-api.dpapi")
    falsa = {"type": "service_account", "client_email": "x@y.iam.gserviceaccount.com", "private_key": "FALSA",
             "project_id": "p"}
    f = tmp_path / "sa.json"
    f.write_text(json.dumps(falsa), encoding="utf-8")
    r = movil.credencial_guardar(str(f))
    assert r["cuenta_de_servicio"] == "x@y.iam.gserviceaccount.com"
    assert b"FALSA" not in movil.CRED_PLAY.read_bytes()
    assert "FALSA" not in json.dumps(r)
    assert json.loads(movil.dpapi_descifrar(movil.CRED_PLAY.read_bytes())) == falsa
    with pytest.raises(movil.Error, match="--reemplazar"):
        movil.credencial_guardar(str(f))
    mala = tmp_path / "otra.json"
    mala.write_text(json.dumps({"type": "authorized_user"}), encoding="utf-8")
    with pytest.raises(movil.Error):
        movil.credencial_guardar(str(mala), reemplazar=True)


# ------------------------------------------------------------------ con herramientas reales (keytool, jarsigner)
@pytest.fixture
def firmas_de_prueba(tmp_path, monkeypatch):
    app = f"prueba-{os.getpid()}"
    monkeypatch.setattr(movil, "FIRMAS", tmp_path / "firmas")
    monkeypatch.setattr(movil, "ficha_app", lambda a: {"paquete": "com.steven.canario"})
    yield app
    movil.Boveda().borrar(movil.servicio_firma(app))


@pytest.mark.herramientas
def test_firma_crear_comprobar_y_no_pisar(firmas_de_prueba):
    app = firmas_de_prueba
    r = movil.firma_crear(app)
    assert Path(r["almacen"]).exists() and r["sha256"] and r["sha256"] != "?"
    clave = movil.Boveda().leer(movil.servicio_firma(app))
    assert clave not in json.dumps(r)
    assert movil.firma_comprobar(app)["sha256"] == r["sha256"]
    with pytest.raises(movil.Error, match="No se pisa"):
        movil.firma_crear(app)


@pytest.mark.herramientas
def test_firmar_un_aab_real(firmas_de_prueba, tmp_path):
    aab = Path(os.environ.get("MOVIL_AAB_PRUEBA", str(movil.HUB.parent / "Android Laboratorio" / "canario" / "app" /
                                                       "build" / "outputs" / "bundle" / "release" / "app-release.aab")))
    if not aab.exists():
        pytest.skip(f"no hay AAB de prueba en {aab}")
    app = firmas_de_prueba
    creada = movil.firma_crear(app)
    copia = tmp_path / "app-release.aab"
    copia.write_bytes(aab.read_bytes())
    r = movil.firmar(app, str(copia))
    assert r["sha256_firmante"] == creada["sha256"]
    with pytest.raises(movil.Error, match="ya viene firmado"):
        movil.firmar(app, r["firmado"])
