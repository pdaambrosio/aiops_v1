import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from core import ValidadorComando


def test_comando_valido_passa():
    v = ValidadorComando()
    r = v.validar("status_nginx")
    assert r.valido is True
    assert r.config is not None


def test_comando_fora_da_whitelist_falha():
    v = ValidadorComando()
    r = v.validar("rm_rf_tudo")
    assert r.valido is False
    assert "whitelist" in r.erro.lower()


def test_parametro_obrigatorio_ausente_falha():
    v = ValidadorComando()
    r = v.validar("ping")  # ping exige 'host'
    assert r.valido is False
    assert "host" in r.erro


def test_parametro_com_injecao_e_bloqueado():
    v = ValidadorComando()
    r = v.validar("ping", {"host": "google.com; rm -rf /"})
    assert r.valido is False
    assert "proibido" in r.erro.lower()


def test_parametro_valido_passa():
    v = ValidadorComando()
    r = v.validar("ping", {"host": "google.com"})
    assert r.valido is True


def test_bool_do_resultado():
    v = ValidadorComando()
    assert bool(v.validar("uptime")) is True
    assert bool(v.validar("inexistente")) is False


if __name__ == "__main__":
    # executa sem pytest
    import traceback

    testes = [obj for nome, obj in globals().items() if nome.startswith("test_")]
    falhas = 0
    for t in testes:
        try:
            t()
            print(f"{t.__name__}")
        except AssertionError:
            falhas += 1
            print(f"{t.__name__}")
            traceback.print_exc()
    print(f"\n{len(testes) - falhas}/{len(testes)} passaram.")
    sys.exit(1 if falhas else 0)
