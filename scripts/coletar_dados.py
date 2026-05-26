#!/usr/bin/env python3
"""
coletar_dados.py — Coletor batch de dados do Alpha-Gen.

Fontes ESTRITAS (não buscar em mais nenhum lugar):
    Macro Brasil ......... bcb.gov.br (API SGS / Olinda)
    Macro Internacional .. finance.yahoo.com (via yfinance)
    Ações + FIIs ......... statusinvest.com.br
    Criptomoedas ......... coinmarketcap.com

Uso:
    python coletar_dados.py --macro
    python coletar_dados.py --ativos PETR4,HGLG11,VALE3
    python coletar_dados.py --cripto BTC,ETH
    python coletar_dados.py --macro --ativos PETR4 --cripto BTC
    python coletar_dados.py --ativos PETR4 --sem-cache

Saída: JSON único para stdout (logs em stderr).
Campos faltantes ficam null e listados em `_missing` da seção correspondente.

A skill que invoca este script deve:
  1. Olhar para `_missing` em cada bloco
  2. PERGUNTAR ao usuário pelos valores faltantes
  3. Nunca chutar / nunca buscar em outras fontes
"""

from __future__ import annotations

import argparse
import datetime as dt
import hashlib
import json
import os
import re
import sys
import time
from pathlib import Path
from typing import Any, Optional

import requests
from bs4 import BeautifulSoup

USER_AGENT = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
    "AppleWebKit/537.36 (KHTML, like Gecko) "
    "Chrome/124.0.0.0 Safari/537.36"
)
HTTP_TIMEOUT = 20
CACHE_TTL_SECONDS = 24 * 3600  # 24h


def log(msg: str) -> None:
    """Log em stderr para não poluir o JSON do stdout."""
    print(f"[coletar_dados] {msg}", file=sys.stderr)


# ---------------------------------------------------------------------------
# Cache em disco (24h TTL)
# ---------------------------------------------------------------------------

class Cache:
    def __init__(self, base_dir: Path, enabled: bool = True):
        self.base = base_dir
        self.enabled = enabled
        if enabled:
            self.base.mkdir(parents=True, exist_ok=True)

    def _key(self, name: str) -> Path:
        h = hashlib.sha1(name.encode("utf-8")).hexdigest()[:16]
        safe = re.sub(r"[^a-zA-Z0-9_-]", "_", name)[:60]
        return self.base / f"{safe}_{h}.json"

    def get(self, name: str) -> Optional[dict]:
        if not self.enabled:
            return None
        path = self._key(name)
        if not path.exists():
            return None
        age = time.time() - path.stat().st_mtime
        if age > CACHE_TTL_SECONDS:
            return None
        try:
            return json.loads(path.read_text(encoding="utf-8"))
        except Exception:
            return None

    def set(self, name: str, value: dict) -> None:
        if not self.enabled:
            return
        try:
            self._key(name).write_text(
                json.dumps(value, ensure_ascii=False), encoding="utf-8"
            )
        except Exception as e:
            log(f"cache.set falhou para {name}: {e}")


# ---------------------------------------------------------------------------
# HTTP helper
# ---------------------------------------------------------------------------

def http_get(url: str, headers: Optional[dict] = None) -> Optional[requests.Response]:
    h = {"User-Agent": USER_AGENT, "Accept-Language": "pt-BR,pt;q=0.9,en;q=0.8"}
    if headers:
        h.update(headers)
    try:
        r = requests.get(url, headers=h, timeout=HTTP_TIMEOUT)
        if r.status_code >= 400:
            log(f"HTTP {r.status_code} para {url}")
            return None
        return r
    except requests.RequestException as e:
        log(f"erro http {url}: {e}")
        return None


# ---------------------------------------------------------------------------
# BCB — API SGS e Olinda
# ---------------------------------------------------------------------------

def _bcb_sgs_ultimo(serie: int) -> Optional[float]:
    url = f"https://api.bcb.gov.br/dados/serie/bcdata.sgs.{serie}/dados/ultimos/1?formato=json"
    r = http_get(url)
    if not r:
        return None
    try:
        data = r.json()
        if not data:
            return None
        valor = data[-1].get("valor")
        return float(valor.replace(",", ".")) if isinstance(valor, str) else float(valor)
    except Exception as e:
        log(f"parse SGS {serie}: {e}")
        return None


def _bcb_sgs_ultimos_12(serie: int) -> Optional[list[float]]:
    url = f"https://api.bcb.gov.br/dados/serie/bcdata.sgs.{serie}/dados/ultimos/12?formato=json"
    r = http_get(url)
    if not r:
        return None
    try:
        data = r.json()
        out = []
        for d in data:
            v = d.get("valor")
            if isinstance(v, str):
                v = v.replace(",", ".")
            out.append(float(v))
        return out
    except Exception as e:
        log(f"parse SGS 12m {serie}: {e}")
        return None


def _bcb_focus_anual(ano: int) -> dict[str, Optional[float]]:
    """Busca medianas Focus para IPCA, PIB Total, Selic do ano."""
    indicadores = {"IPCA": "ipca_proj", "PIB Total": "pib_proj", "Selic": "selic_proj"}
    out: dict[str, Optional[float]] = {v: None for v in indicadores.values()}
    base = (
        "https://olinda.bcb.gov.br/olinda/servico/Expectativas/versao/v1/odata/"
        "ExpectativasMercadoAnuais"
    )
    for nome, chave in indicadores.items():
        params = (
            f"?$top=1&$filter=Indicador%20eq%20%27{nome.replace(' ', '%20')}%27"
            f"%20and%20DataReferencia%20eq%20%27{ano}%27"
            f"&$orderby=Data%20desc&$format=json"
        )
        r = http_get(base + params)
        if not r:
            continue
        try:
            vals = r.json().get("value", [])
            if vals:
                out[chave] = float(vals[0].get("Mediana"))
        except Exception as e:
            log(f"parse Focus {nome}: {e}")
    return out


def coletar_macro_brasil(cache: Cache) -> dict:
    cached = cache.get("macro_brasil")
    if cached:
        log("macro_brasil: cache hit")
        return cached

    selic = _bcb_sgs_ultimo(432)
    ipca_meses = _bcb_sgs_ultimos_12(433)
    usd_brl = _bcb_sgs_ultimo(1)
    focus = _bcb_focus_anual(dt.date.today().year)

    ipca_12m: Optional[float] = None
    if ipca_meses and len(ipca_meses) == 12:
        prod = 1.0
        for v in ipca_meses:
            prod *= (1 + v / 100)
        ipca_12m = round((prod - 1) * 100, 2)

    missing = []
    if selic is None: missing.append("selic_meta_pct")
    if ipca_12m is None: missing.append("ipca_12m_pct")
    if usd_brl is None: missing.append("usd_brl_ptax")
    for k, v in focus.items():
        if v is None: missing.append(f"focus.{k}")

    out = {
        "selic_meta_pct": selic,
        "ipca_12m_pct": ipca_12m,
        "usd_brl_ptax": usd_brl,
        "focus": focus,
        "_missing": missing,
    }
    cache.set("macro_brasil", out)
    return out


# ---------------------------------------------------------------------------
# Yahoo Finance — Macro internacional
# ---------------------------------------------------------------------------

def coletar_macro_internacional(cache: Cache) -> dict:
    cached = cache.get("macro_internacional")
    if cached:
        log("macro_internacional: cache hit")
        return cached

    tickers = {
        "treasury_10y": "^TNX",
        "vix": "^VIX",
        "wti": "CL=F",
        "brent": "BZ=F",
        "ouro": "GC=F",
        "dxy": "DX-Y.NYB",
        "usdbrl_yahoo": "USDBRL=X",
    }

    out: dict[str, Any] = {}
    missing: list[str] = []

    try:
        import yfinance as yf  # type: ignore
    except ImportError:
        log("yfinance não instalado — todos os dados internacionais ficam null")
        for k in tickers:
            out[k] = None
            missing.append(k)
        out["_missing"] = missing
        return out

    for chave, ticker_simbolo in tickers.items():
        try:
            t = yf.Ticker(ticker_simbolo)
            # tenta fast_info primeiro (mais leve)
            preco = None
            try:
                fi = t.fast_info
                preco = float(fi.last_price)
            except Exception:
                pass
            if preco is None or preco != preco:  # NaN check
                hist = t.history(period="5d")
                if hist is not None and not hist.empty:
                    preco = float(hist["Close"].iloc[-1])
            if preco is None or preco != preco:
                missing.append(chave)
                out[chave] = None
            else:
                out[chave] = round(preco, 4)
        except Exception as e:
            log(f"yfinance {ticker_simbolo}: {e}")
            out[chave] = None
            missing.append(chave)

    out["_missing"] = missing
    cache.set("macro_internacional", out)
    return out


# ---------------------------------------------------------------------------
# Status Invest — Ações e FIIs
# ---------------------------------------------------------------------------

_NUM_RE = re.compile(r"-?\d{1,3}(?:\.\d{3})+(?:,\d+)?|-?\d+(?:[.,]\d+)?")


def _parse_num_br(text: str) -> Optional[float]:
    """Converte '1.234,56' / '12,5%' / '565.330' / '-3,5' em float (heurística pt-BR)."""
    if text is None:
        return None
    t = text.strip().replace("\xa0", " ")
    if not t or t in {"-", "—", "N/A", "-%", "0,00%-"}:
        return None
    m = _NUM_RE.search(t)
    if not m:
        return None
    raw = m.group(0)
    has_comma = "," in raw
    if has_comma:
        # vírgula é decimal; pontos são milhar
        raw = raw.replace(".", "").replace(",", ".")
    else:
        # sem vírgula: se tem ponto seguido de exatamente 3 dígitos, é milhar
        if re.search(r"\.\d{3}(?:\.|$)", raw):
            raw = raw.replace(".", "")
        # caso "565.33" sem vírgula com 2 dígitos após o ponto: trata como decimal
    try:
        return float(raw)
    except ValueError:
        return None


def _is_value_class(c) -> bool:
    if not c:
        return False
    return "value" in (c if isinstance(c, str) else " ".join(c))


def _statusinvest_valor_apos_label(soup: BeautifulSoup, label: str) -> Optional[float]:
    """Encontra strong.value de um indicador no Status Invest.

    Tenta múltiplas estratégias porque o HTML mistura tooltips e nested spans:
      A) div[title="Label..."]  → strong.value dentro
      B) h3/h4/span cujo PRIMEIRO text node (antes do help_outline) == label
      C) h3/h4/span com texto exato == label
    """
    target = label.strip().lower()

    # A) match por atributo title (mais robusto, ignora tooltip-noise)
    for div in soup.find_all("div", attrs={"title": True}):
        title = (div.get("title") or "").strip().lower()
        if title == target or title.startswith(target + " ") or title.startswith(target + "("):
            strong = div.find("strong", class_=_is_value_class)
            if strong:
                num = _parse_num_br(strong.get_text())
                if num is not None:
                    return num

    # B) primeira sub-string textual do label dentro de h3/h4/span
    for tag in soup.find_all(["h3", "h4", "span", "div"]):
        # pega só o primeiro text node (ignora help_outline e tooltip)
        first = next((c for c in tag.children if isinstance(c, str) and c.strip()), None)
        if first and first.strip().lower() == target:
            # sobe procurando strong.value
            node = tag
            for _ in range(4):
                node = node.parent
                if node is None:
                    break
                strong = node.find("strong", class_=_is_value_class)
                if strong:
                    num = _parse_num_br(strong.get_text())
                    if num is not None:
                        return num

    # C) texto exato (caso simples sem nested)
    for tag in soup.find_all(["h3", "h4", "span", "div"], string=True):
        if tag.get_text(strip=True).lower() == target:
            nxt = tag.find_next("strong", class_=_is_value_class)
            if nxt:
                num = _parse_num_br(nxt.get_text())
                if num is not None:
                    return num
    return None


def _statusinvest_preco(html: str) -> Optional[float]:
    soup = BeautifulSoup(html, "lxml")
    # Status Invest: preço fica em div title="Valor atual do ativo" → strong.value
    for div in soup.find_all("div", attrs={"title": True}):
        title = div.get("title", "")
        if title.startswith("Valor atual"):
            strong = div.find("strong", class_=lambda c: c and "value" in (c if isinstance(c, str) else " ".join(c)))
            if strong:
                num = _parse_num_br(strong.get_text())
                if num is not None:
                    return num
    # Fallback: primeiro strong.value > 0.1 da página
    for strong in soup.find_all("strong", class_=lambda c: c and "value" in (c if isinstance(c, str) else " ".join(c))):
        num = _parse_num_br(strong.get_text())
        if num is not None and num > 0.1:
            return num
    return None


def coletar_ativo(ticker: str, cache: Cache) -> dict:
    ticker = ticker.upper().strip()
    cached = cache.get(f"ativo_{ticker}")
    if cached:
        log(f"{ticker}: cache hit")
        return cached

    # Tenta primeiro como ação; se HTTP 404, tenta FII
    base = "https://statusinvest.com.br"
    slug = ticker.lower()
    urls_tentativas = [
        ("acao", f"{base}/acoes/{slug}"),
        ("fii", f"{base}/fundos-imobiliarios/{slug}"),
    ]

    html: Optional[str] = None
    classe: Optional[str] = None
    for cls, url in urls_tentativas:
        r = http_get(url)
        if r and r.status_code == 200 and len(r.text) > 5000 and ticker in r.text.upper():
            html = r.text
            classe = cls
            break

    if html is None or classe is None:
        log(f"{ticker}: não encontrado no Status Invest")
        out = {
            "classe": None,
            "_missing": ["TODOS_OS_CAMPOS_NAO_ENCONTRADOS"],
            "_erro": f"Ticker {ticker} não encontrado em statusinvest.com.br",
        }
        cache.set(f"ativo_{ticker}", out)
        return out

    if classe == "acao":
        campos = {
            "preco": "__preco__",
            "p_l": "P/L",
            "p_vp": "P/VP",
            "dy_12m": "Dividend Yield",
            "roe": "ROE",
            "roic": "ROIC",
            "div_ebitda": "Dív. líquida/EBITDA",
            "margem_liquida": "M. Líquida",
            "lpa": "LPA",
            "vpa": "VPA",
            "liq_diaria": "Liquidez média diária",
        }
    else:  # fii
        campos = {
            "preco": "__preco__",
            "p_vp": "P/VP",
            "dy_12m": "Dividend Yield",
            "ult_rendimento": "Últ. Rendimento",
            "vacancia": "Vacância",
            "liq_diaria": "Liq. méd. diária",
            "vp_cota": "Val. patrim. p/cota",
            "n_cotistas": "Nº de Cotistas",
        }

    soup = BeautifulSoup(html, "lxml")
    out: dict[str, Any] = {"classe": classe}
    missing: list[str] = []
    for chave, label in campos.items():
        if label == "__preco__":
            valor = _statusinvest_preco(html)
        else:
            valor = _statusinvest_valor_apos_label(soup, label)
        out[chave] = valor
        if valor is None:
            missing.append(chave)

    # Sub-fatores granulares de FII que sabemos que Status Invest NÃO traz
    if classe == "fii":
        for campo_indispo in ("wault", "cap_rate", "rating_cris", "concentracao_inquilino", "indexacao_cris"):
            out[campo_indispo] = None
            missing.append(campo_indispo)

    out["_missing"] = missing
    cache.set(f"ativo_{ticker}", out)
    return out


# ---------------------------------------------------------------------------
# CoinMarketCap
# ---------------------------------------------------------------------------

_CMC_SLUG_MAP = {
    "BTC": "bitcoin",
    "ETH": "ethereum",
    "SOL": "solana",
    "BNB": "bnb",
    "XRP": "xrp",
    "ADA": "cardano",
    "DOGE": "dogecoin",
    "AVAX": "avalanche",
    "DOT": "polkadot",
    "MATIC": "polygon-ecosystem-token",
    "LINK": "chainlink",
    "LTC": "litecoin",
    "ATOM": "cosmos",
    "TRX": "tron",
    "USDT": "tether",
    "USDC": "usd-coin",
}


def _cmc_extrair_next_data(html: str) -> Optional[dict]:
    soup = BeautifulSoup(html, "lxml")
    tag = soup.find("script", id="__NEXT_DATA__")
    if not tag or not tag.string:
        return None
    try:
        return json.loads(tag.string)
    except Exception:
        return None


def coletar_cripto(symbol: str, cache: Cache) -> dict:
    sym = symbol.upper().strip()
    slug = _CMC_SLUG_MAP.get(sym, sym.lower())
    cached = cache.get(f"cripto_{sym}")
    if cached:
        log(f"{sym}: cache hit")
        return cached

    url = f"https://coinmarketcap.com/currencies/{slug}/"
    r = http_get(url)
    out: dict[str, Any] = {"slug": slug}
    missing: list[str] = []

    if not r or r.status_code != 200:
        log(f"{sym}: HTTP falhou ({r.status_code if r else 'sem resposta'})")
        for k in ("preco_usd", "var_24h", "var_7d", "var_30d", "market_cap", "volume_24h", "ath"):
            out[k] = None
            missing.append(k)
        out["_missing"] = missing
        out["_erro"] = f"Não foi possível carregar coinmarketcap.com/currencies/{slug}/"
        cache.set(f"cripto_{sym}", out)
        return out

    data = _cmc_extrair_next_data(r.text)
    detail = None
    try:
        # Caminho típico do payload do Next.js da CMC
        page_props = data["props"]["pageProps"]
        detail = page_props.get("detailRes", {}).get("detail") or page_props.get("info")
    except Exception:
        detail = None

    if detail:
        try:
            stats = detail.get("statistics") or {}
            out["preco_usd"] = stats.get("price")
            out["var_24h"] = stats.get("priceChangePercentage24h")
            out["var_7d"] = stats.get("priceChangePercentage7d")
            out["var_30d"] = stats.get("priceChangePercentage30d")
            out["market_cap"] = stats.get("marketCap")
            out["volume_24h"] = stats.get("volume24h")
            out["ath"] = stats.get("priceChangePercentageAllTime") or stats.get("high")
        except Exception as e:
            log(f"{sym}: parse __NEXT_DATA__ falhou: {e}")

    # Fallback: regex no HTML para preço (caso __NEXT_DATA__ mude estrutura)
    if out.get("preco_usd") is None:
        m = re.search(r'"price":\s*([\d.]+)', r.text)
        if m:
            try:
                out["preco_usd"] = float(m.group(1))
            except ValueError:
                pass

    for k in ("preco_usd", "var_24h", "var_7d", "var_30d", "market_cap", "volume_24h", "ath"):
        if out.get(k) is None:
            missing.append(k)
            out.setdefault(k, None)

    out["_missing"] = missing
    cache.set(f"cripto_{sym}", out)
    return out


def coletar_fear_greed_cripto(cache: Cache) -> dict:
    cached = cache.get("fear_greed_cripto")
    if cached:
        log("fear_greed_cripto: cache hit")
        return cached

    url = "https://coinmarketcap.com/charts/fear-and-greed-index/"
    r = http_get(url)
    out: dict[str, Any] = {"valor": None, "label": None}
    if not r:
        out["_missing"] = ["valor", "label"]
        cache.set("fear_greed_cripto", out)
        return out

    # Tenta extrair do __NEXT_DATA__
    try:
        data = _cmc_extrair_next_data(r.text)
        if data:
            # Estrutura aproximada; ajustar conforme CMC alterar
            page = data.get("props", {}).get("pageProps", {})
            fg = page.get("fearGreedData") or page.get("dehydratedState")
            txt = json.dumps(page)
            m = re.search(r'"value":\s*(\d+)[^}]*"name":\s*"([^"]+)"', txt)
            if m:
                out["valor"] = int(m.group(1))
                out["label"] = m.group(2)
    except Exception as e:
        log(f"fear_greed parse: {e}")

    # Fallback regex bruto
    if out["valor"] is None:
        m = re.search(r'fear[^A-Za-z0-9]*greed[^0-9]{0,40}(\d{1,3})', r.text, re.IGNORECASE)
        if m:
            try:
                v = int(m.group(1))
                if 0 <= v <= 100:
                    out["valor"] = v
                    out["label"] = (
                        "Medo Extremo" if v < 25
                        else "Medo" if v < 45
                        else "Neutro" if v < 55
                        else "Ganância" if v < 75
                        else "Ganância Extrema"
                    )
            except ValueError:
                pass

    if out["valor"] is None:
        out["_missing"] = ["valor", "label"]
    else:
        out["_missing"] = []

    cache.set("fear_greed_cripto", out)
    return out


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def main() -> int:
    ap = argparse.ArgumentParser(description="Coletor batch Alpha-Gen")
    ap.add_argument("--macro", action="store_true", help="Coleta dados macro (BR + internacional)")
    ap.add_argument("--ativos", type=str, default="", help="Tickers separados por vírgula, ex: PETR4,HGLG11")
    ap.add_argument("--cripto", type=str, default="", help="Símbolos cripto, ex: BTC,ETH")
    ap.add_argument("--sem-cache", action="store_true", help="Ignora cache e força refresh")
    ap.add_argument("--cache-dir", type=str, default=None, help="Pasta de cache (default: ../historico/cache_dados)")
    ap.add_argument("--saida", type=str, default=None, help="Escreve JSON em arquivo em vez de stdout")
    args = ap.parse_args()

    if not (args.macro or args.ativos or args.cripto):
        ap.print_help(sys.stderr)
        return 2

    script_dir = Path(__file__).resolve().parent
    if args.cache_dir:
        cache_dir = Path(args.cache_dir)
    else:
        cache_dir = script_dir.parent / "historico" / "cache_dados"

    cache = Cache(cache_dir, enabled=not args.sem_cache)

    resultado: dict[str, Any] = {
        "timestamp": dt.datetime.utcnow().isoformat() + "Z",
        "cache_dir": str(cache_dir),
        "cache_ativo": cache.enabled,
    }

    if args.macro:
        log("coletando macro...")
        resultado["macro"] = {
            "brasil": coletar_macro_brasil(cache),
            "internacional": coletar_macro_internacional(cache),
        }

    if args.ativos:
        log(f"coletando ativos: {args.ativos}")
        tickers = [t.strip() for t in args.ativos.split(",") if t.strip()]
        resultado["ativos"] = {t: coletar_ativo(t, cache) for t in tickers}

    if args.cripto:
        log(f"coletando cripto: {args.cripto}")
        simbolos = [s.strip() for s in args.cripto.split(",") if s.strip()]
        resultado["cripto"] = {s: coletar_cripto(s, cache) for s in simbolos}
        resultado["cripto"]["_fear_greed"] = coletar_fear_greed_cripto(cache)

    json_out = json.dumps(resultado, ensure_ascii=False, indent=2, default=str)

    if args.saida:
        Path(args.saida).write_text(json_out, encoding="utf-8")
        log(f"JSON salvo em {args.saida}")
    else:
        print(json_out)

    return 0


if __name__ == "__main__":
    sys.exit(main())
