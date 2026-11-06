# shellcheck shell=bash disable=SC2034
# Funções usadas pelos scripts desta receita.

# O Firefox lê as políticas daqui em qualquer distro, inclusive o Snap do Ubuntu.
POLITICAS=/etc/firefox/policies/policies.json
UBLOCK=uBlock0@raymondhill.net
UBLOCK_URL=https://addons.mozilla.org/firefox/downloads/latest/ublock-origin/latest.xpi

firefox_instalado() {
    command -v firefox >/dev/null || command -v firefox-esr >/dev/null || [ -x /snap/bin/firefox ]
}

# As políticas que esta receita quer, em JSON. Cada preferência vai com
# "Status": "default", então a pessoa ainda pode mudar no about:config.
politicas_da_receita() {
    python3 - "${BORA_BLOQUEAR_ANUNCIOS:-sim}" "$UBLOCK" "$UBLOCK_URL" <<'PY'
import json, sys
bloquear, ublock, url = sys.argv[1] == "sim", sys.argv[2], sys.argv[3]
def pref(v):
    return {"Value": v, "Status": "default"}
p = {
    "DisableTelemetry": True,
    "DisableFirefoxStudies": True,
    "FirefoxHome": {"SponsoredTopSites": False},
    "Preferences": {
        # Tira da memória as abas que você não está usando quando a memória acaba.
        "browser.tabs.unloadOnLowMemory": pref(True),
        # Ao abrir, só carrega as abas antigas quando você clicar nelas.
        "browser.sessionstore.restore_on_demand": pref(True),
        # Grava a sessão a cada minuto, e não a cada 15 segundos: menos disco.
        "browser.sessionstore.interval": pref(60000),
    },
}
if bloquear:
    p["ExtensionSettings"] = {ublock: {"installation_mode": "normal_installed", "install_url": url}}
print(json.dumps(p, indent=2, sort_keys=True))
PY
}

# Junta as políticas da receita ao arquivo que já existir, sem tirar nada dele.
# Lê o arquivo atual pela entrada padrão e escreve o resultado na saída.
juntar_politicas() {
    python3 -c '
import json, sys
atual = sys.stdin.read().strip()
atual = json.loads(atual) if atual else {}
novo = json.loads(sys.argv[1])
pol = atual.setdefault("policies", {})
for k, v in novo.items():
    if isinstance(v, dict) and isinstance(pol.get(k), dict):
        pol[k].update(v)
    else:
        pol[k] = v
print(json.dumps(atual, indent=2, ensure_ascii=False, sort_keys=True))
' "$(politicas_da_receita)"
}

# O arquivo já tem tudo o que a receita pede?
politicas_aplicadas() {
    [ -f "$POLITICAS" ] || return 1
    python3 -c '
import json, sys
pol = json.load(open(sys.argv[1])).get("policies", {})
novo = json.loads(sys.argv[2])
for k, v in novo.items():
    if isinstance(v, dict):
        atual = pol.get(k)
        if not isinstance(atual, dict) or any(atual.get(a) != b for a, b in v.items()):
            sys.exit(1)
    elif pol.get(k) != v:
        sys.exit(1)
' "$POLITICAS" "$(politicas_da_receita)" 2>/dev/null
}
