# backend/classifiers/ai_classifier.py

from typing import List, Dict, Any, Tuple, Optional
import re
import unicodedata
import torch

try:
    import spacy
    _SPACY_OK = True
except Exception:
    _SPACY_OK = False

# Optional zero-shot (kept OFF by default for Shorts)
try:
    from transformers import pipeline  # noqa
    _HF_OK = True
except Exception:
    _HF_OK = False


# =========================
# Utilities & Normalization
# =========================
def _norm(s: str) -> str:
    s = unicodedata.normalize("NFKC", s or "")
    s = re.sub(r"\s+", " ", s).strip()
    return s

def _alnum_key(s: str) -> str:
    s = _norm(s).lower()
    # strip leading determiners in EN/DE
    s = re.sub(r"^(the|a|an|der|die|das|den|dem|ein|eine)\s+", "", s)
    return re.sub(r"[^a-z0-9]+", "", s)

# Treat commemorative tails as variants of the same core place
_COMM_TAILS = {
    "memorial", "denkmal", "mahnmal", "gedenkstätte", "gedenkstatte", "monument"
}

def _core_key(s: str) -> str:
    """
    Canonical key that removes trailing commemorative descriptors so that
    'Berlin Wall Memorial' and 'Berlin Wall' share the same core.
    Does NOT strip structural POI words like 'Gate', 'Bridge', etc.
    """
    norm = _norm(s).lower()
    # strip leading determiners (mirror _alnum_key)
    norm = re.sub(r"^(the|a|an|der|die|das|den|dem|ein|eine)\s+", "", norm)
    toks = re.split(r"[^a-z0-9]+", norm)
    toks = [t for t in toks if t]

    if not toks:
        return ""

    # If last token is a commemorative tail, drop it
    if toks and toks[-1] in _COMM_TAILS:
        toks = toks[:-1]

    # Return compact alnum core
    return "".join(toks)

def _strip_leading_det_display(s: str) -> str:
    return re.sub(r"^(?:the|a|an|der|die|das|den|dem|ein|eine)\s+", "", s, flags=re.I)

def _is_mostly_letters(name: str) -> bool:
    return bool(re.fullmatch(r"[A-Za-zÀ-ÖØ-öø-ÿ0-9'’\-\s\.]+", name))

# ==================================
# Timestamp timeline (Shorts) parser
# ==================================
TS_LINE = re.compile(
    r"(?:^|\s)(?P<ts>\d{1,2}:\d{2})(?:\s*[-–—:]\s*|\s+)(?P<label>[A-ZÄÖÜ][^\n,.;:]+)",
    flags=re.UNICODE
)

# =======================================================
# Regex fallback for capitalized multiword POI candidates
#  - includes German preps/articles common in names
# =======================================================
# Capitalized multiword phrase matcher that does NOT cross sentence punctuation.
CAPITAL_PHRASE = re.compile(
    r"\b("                                  # begin capture of the full name
    r"[A-ZÄÖÜ][A-Za-zÀ-ÖØ-öø-ÿ0-9’'&\-]+"   # first TitleCase token (no dot)
    r"(?:\s+(?:of|de|di|la|le|the|and|&|y|am|im|an der|an dem|zu|vom|von der|bei|an|auf|in)\s+"
    r"[A-ZÄÖÜ][A-Za-zÀ-ÖØ-öø-ÿ0-9’'&\-]+)*" # optional connector + TitleCase token
    r"(?:\s+[A-ZÄÖÜ][A-Za-zÀ-ÖØ-öø-ÿ0-9’'&\-]+)*"  # more TitleCase tokens
    r")\b",
    flags=re.UNICODE
)

# ===============================
# Cleaning / de-noising
# ===============================
# Call-to-action / trailing verbs to trim off the end of matches
TRAILING_ACTION_RE = re.compile(
    r"\s*(?:[-–—]|\.|,|:)?\s*"
    r"(?:"
        r"visit|explore|learn|take|relax|enjoy|discover|check out|see|watch|go|head|walk|stroll|experience|"
        r"after|before|from|next|then|now|today|tomorrow|tonight|later|meanwhile"
    r")\b.*$",
    flags=re.IGNORECASE
)

# Trashy fillers / discourse markers that should not be POIs
BLOCK_SINGLE_WORDS = {
    "here","these","this","that","today","tomorrow","yesterday","intro","outro","chapter","section",
    "enjoy","visit","explore","learn","take","relax","discover","watch",
}

BLOCK_PREFIXES = [
    "speaking of", "fun facts", "introduction", "pro tip", "travel hack", "link in bio", "google maps list",
]
BLOCK_CONTAINS = [
    "thanks for watching", "subscribe", "like and", "in this video", "today we", "this video",
]

# Overly generic regions/countries — drop unless paired with a concrete POI keyword
COUNTRY_REGION_WORDS = {"germany", "deutschland", "europe"}

# Strong POI keywords (used for hinting and for allowing single-token names)
KEYWORD_HINT_RULES: List[Tuple[str, str]] = [
    # Water / coasts
    (r"\bsee\b|see$", "lake"),
    (r"\bmeer\b", "coast"),
    (r"\bfluss\b|\briver\b|rhein\b|elbe\b|donau\b|isar\b|main\b|neckar\b|oder\b", "river"),
    (r"\bufer\b|\bpromenade\b|\bkanal\b", "riverfront"),
    (r"\bstrand\b|\bbucht\b|\bbay\b", "beach"),

    # Nature
    (r"\balpen\b|\bberg(e)?\b|\bgipfel\b|\bspitze\b", "mountain"),
    (r"\btal\b|\bklamm\b|\bschlucht\b|\bgorge\b", "gorge"),
    (r"\bdüne?n?\b|\bdunes?\b", "dunes"),
    (r"\bwald\b|\bforst\b", "forest"),
    (r"\bhöhle\b|\bhoehle\b|\bcave\b", "cave"),
    (r"\bnationalpark\b|\bpark\b|\bgarten\b|\bschlosspark\b", "park"),

    # Architecture / heritage
    (r"\bburg\b|\bschloss\b|\bfestung\b|\bruine\b|castle|palace|citadel|fort", "castle"),
    (r"\bdom\b|\bkathedrale\b|\bkirche\b|\bmünster\b|\bmunster\b|\bbasilika\b|cathedral|church|basilica", "church"),
    (r"\btor\b|\bgate\b", "gate"),
    (r"\bbrücke\b|\bbrucke\b|\bbridge\b", "bridge"),
    (r"\baltstadt\b|old town|historic center", "old town"),
    (r"\bplatz\b|\bmarktplatz\b|\bmarkt\b|\bsquare\b", "square"),
    (r"\b(?:\w*turm|tower)\b", "tower"),
    (r"\bmarkt\b|\bmarket\b|\bbazaar\b|\bsouk\b", "market"),
    (r"\bkanal\b|\bcanal\b", "canal"),
    (r"\bgarten\b|\bgarden\b", "garden"),
    (r"\bwindm(ill|ills)\b|kinderdijk\b", "windmills"),

    # Historical landmarks
    (r"\bberlin wall\b|\bwall\b|\bmauer\b", "historic site"),
    (r"\bmemorial\b|\bdenkmal\b|\bmahnmal\b|\bgedenkst(ä|a)tte\b", "memorial"),
    (r"\bmonument\b|monumente?\b", "monument"),

    # Islands / harbors
    (r"\binsel\b|island\b", "island"),
    (r"\bhafen\b|harbou?r\b|marina\b", "harbor"),

    # Museums (keep separate so “Museum Island” maps to museum)
    (r"\bmuseum\b|\bmuseen\b|\bgalerie\b|\bgallery\b", "museum"),
]

ALLOWED_HINTS = {
    "gate","museum","park","square","bridge","castle","church","island","harbor",
    "river","lake","dunes","gorge","forest","cave","old town","tower","market",
    "canal","garden","windmills","riverfront","mountain","beach","coast","viewpoint",
    "historic site","memorial","monument",
}

def _contains_country_region(name: str) -> bool:
    low = name.lower()
    return any(w in low for w in COUNTRY_REGION_WORDS)

def _trim_trailing_actions(s: str) -> str:
    return TRAILING_ACTION_RE.sub("", s).strip()

def _clean_name(raw: str) -> Optional[str]:
    s = _norm(raw)
    s = re.sub(r'^[\'"“”„]+|[\'"“”„]+$', "", s).strip()
    s = re.sub(r"[\.…,:;!\?]+$", "", s).strip()
    s = _trim_trailing_actions(s)
    low = s.lower()

    # Early drops
    if low in BLOCK_SINGLE_WORDS:
        return None
    if any(low.startswith(p) for p in BLOCK_PREFIXES):
        return None
    if any(t in low for t in BLOCK_CONTAINS):
        return None

    # “East and West Germany”, “West Germany”, etc. → drop unless a POI keyword is present
    if _contains_country_region(s):
        if not _hint_from_rules(s):
            return None

    if len(s) < 3:
        return None
    return s

def _hint_from_rules(name: str) -> Optional[str]:
    low = name.lower()
    for pattern, hint in KEYWORD_HINT_RULES:
        if re.search(pattern, low):
            return hint
    return None

# ==========================================
# spaCy: load model or build a simple ruler
# ==========================================
def _load_spacy_or_ruler():
    try:
        import spacy  # noqa
    except Exception:
        return None

    # Prefer DE; then EN
    for m in ("de_core_news_sm", "de_core_news_md", "en_core_web_sm", "en_core_web_md"):
        try:
            return spacy.load(m)
        except Exception:
            pass

    # Programmatic download fallback
    try:
        from spacy.cli import download
        for m in ("de_core_news_sm", "en_core_web_sm"):
            try: download(m)
            except Exception: pass
        for m in ("de_core_news_sm", "en_core_web_sm"):
            try: return spacy.load(m)
            except Exception: pass
    except Exception:
        pass

    # Blank model + EntityRuler
    try:
        try:
            nlp = spacy.blank("de")
        except Exception:
            nlp = spacy.blank("en")
        ruler = nlp.add_pipe("entity_ruler", config={"phrase_matcher_attr": "LOWER"})
        patterns = []
        # Seed with common geo tokens to bias recognition
        tokens = [
            "see","meer","fluss","ufer","promenade","hafen","strand","bucht","kanal",
            "wasserfall","fälle","fall","klamm","schlucht","höhle","hoehle",
            "berg","berge","alpen","gipfel","spitze","tal","grat","wald","nationalpark",
            "park","garten","schlosspark","burg","schloss","festung","ruine","tor","dom",
            "kathedrale","kirche","münster","munster","basilika","platz","marktplatz",
            "markt","allee","straße","strasse","brücke","brucke","altstadt","museum","galerie",
            "lake","river","harbor","harbour","marina","bridge","cathedral","church",
            "castle","palace","ruins","square","market","garden","viewpoint", "Fernsehturm", "fernsehturm",
        ]
        for kw in tokens:
            patterns.append({"label": "LOC", "pattern": kw})
        title = {"IS_TITLE": True, "IS_ALPHA": True}
        for n in range(2, 6):
            patterns.append({"label": "LOC", "pattern": [title] * n})
        ruler.add_patterns(patterns)
        return nlp
    except Exception:
        return None

# =========================
# Core extractor (fast)
# =========================
class POIExtractor:
    """
    For Shorts: feed the merged transcript text (we join segments internally).
    Returns minimal list: [{"name": str, "hint": str}, ...] with strong noise suppression.
    """

    def __init__(
        self,
        use_zsl: bool = False,                 # OFF for speed
        zsl_model: str = "facebook/bart-large-mnli",
        zsl_min_score: float = 0.50,
        device: int = 0 if torch.cuda.is_available() else -1,
        max_results: int = 25,
    ):
        self.use_zsl = bool(use_zsl and _HF_OK)
        self.zsl_min_score = float(zsl_min_score)
        self.max_results = int(max_results)

        self._nlp = _load_spacy_or_ruler() if _SPACY_OK else None
        self._zsl = None
        if self.use_zsl:
            from transformers import pipeline as hfpipe  # type: ignore
            self._zsl = hfpipe("zero-shot-classification", model=zsl_model, device=device, truncation=True)

    # ---- candidate mining ----
    def _mine_from_timestamps(self, text: str) -> List[Tuple[str, int]]:
        out = []
        for m in TS_LINE.finditer(text):
            raw = _clean_name(m.group("label"))
            if not raw:
                continue
            if _is_mostly_letters(raw):
                out.append((raw, m.start("label")))
        return out

    def _mine_spacy(self, text: str) -> List[Tuple[str, int]]:
        out = []
        if not self._nlp:
            return out
        doc = self._nlp(text)
        for ent in doc.ents:
            if ent.label_ in {"GPE", "LOC", "FAC", "ORG", "WORK_OF_ART"}:
                raw = _clean_name(ent.text)
                if not raw:
                    continue
                if _is_mostly_letters(raw):
                    out.append((raw, ent.start_char))
        return out

    def _mine_regex_caps(self, text: str) -> List[Tuple[str, int]]:
        out = []
        for m in CAPITAL_PHRASE.finditer(text):
            raw = _clean_name(m.group(1))
            if not raw:
                continue
            # Single tokens allowed only if they contain a strong POI keyword (e.g., “Kinderdijk” via windmills rule)
            if len(raw.split()) <= 1 and not _hint_from_rules(raw):
                continue
            if _is_mostly_letters(raw):
                out.append((raw, m.start(1)))
        return out
    
    # ---- dedupe + keep first occurrence ----
    def _dedupe_keep_order(self, items: List[Tuple[str, int]]) -> List[str]:
        # Keep first occurrence order, but collapse 'core' variants and prefer the longer/more specific name.
        seen_alnum = {}   # alnum_key -> index in out
        seen_core  = {}   # core_key  -> index in out
        out: List[str] = []

        for name, _ in sorted(items, key=lambda x: x[1]):  # by first appearance
            k_alnum = _alnum_key(name)
            if not k_alnum:
                continue
            k_core  = _core_key(name)

            # Already seen exact (alnum) -> skip
            if k_alnum in seen_alnum:
                continue

            # If a core variant exists, decide whether to replace with the more specific (longer) one
            if k_core and k_core in seen_core:
                j = seen_core[k_core]
                cur = out[j]
                # prefer the longer string as "more specific"
                if len(name) > len(cur):
                    out[j] = name
                    # update alnum map for the replaced entry
                    seen_alnum[_alnum_key(cur)] = j  # keep old alnum occupied
                    seen_alnum[k_alnum] = j         # and map new alnum too
                # else: keep existing, drop this
                continue

            # New entry
            idx = len(out)
            out.append(name)
            seen_alnum[k_alnum] = idx
            if k_core:
                seen_core[k_core] = idx

            if len(out) >= self.max_results:
                break

        return out


    # ---- optional ZSL to refine; we will still filter generic labels ----
    _ZSL_LABEL_TO_HINT = {
        "Beach/Lake/Riverfront": "beach",
        "Park/Garden/Nature": "park",
        "Viewpoint/Scenic Spot": "viewpoint",
        "Museum/Gallery": "museum",
        "Religious Site": "religious site",
        "Historic Building/Site": "historic site",
        "Landmark/Monument": "landmark",
        "Neighborhood/District": "neighborhood",
        "Shopping/Market": "market",
        "Restaurant/Cafe/Bar": "restaurant",
        "Theatre/Venue/Attraction": "attraction",
    }
    _POI_LABEL_DEFS = {
        "Landmark/Monument": "A famous landmark or monument.",
        "Museum/Gallery": "A museum or gallery.",
        "Religious Site": "A church, mosque, temple, synagogue, shrine, or cathedral.",
        "Park/Garden/Nature": "A park, garden, national park, or natural viewpoint.",
        "Neighborhood/District": "A neighborhood or historic district.",
        "Viewpoint/Scenic Spot": "A viewpoint or scenic spot.",
        "Beach/Lake/Riverfront": "A beach, lakefront, or riverfront.",
        "Shopping/Market": "A shopping street or market.",
        "Restaurant/Cafe/Bar": "A restaurant, café, or bar.",
        "Theatre/Venue/Attraction": "A venue, theme park, stadium, or attraction.",
        "Historic Building/Site": "A palace, castle, ruins, citadel, fort.",
    }
    _POI_HYPOTHESES = [f"This place is: {definition}" for definition in _POI_LABEL_DEFS.values()]
    _HYP2LABEL = dict(zip(_POI_HYPOTHESES, list(_POI_LABEL_DEFS.keys())))

    def _zsl_label(self, names: List[str]) -> Dict[str, str]:
        if not (self._zsl and names):
            return {}
        res: Dict[str, str] = {}
        B = 16
        for i in range(0, len(names), B):
            chunk = names[i:i+B]
            out = self._zsl(chunk, candidate_labels=self._POI_HYPOTHESES, multi_label=True)
            if isinstance(out, dict):
                out = [out]
            for nm, r in zip(chunk, out):
                best_lab, best_sc = None, 0.0
                for hyp, sc in zip(r["labels"], r["scores"]):
                    lab = self._HYP2LABEL[hyp]
                    if sc > best_sc:
                        best_lab, best_sc = lab, float(sc)
                if best_lab and best_sc >= 0.50:
                    hint = self._ZSL_LABEL_TO_HINT.get(best_lab)
                    # keep only if the hint is in allowed (drop landmark/attraction/neighborhood)
                    if hint in ALLOWED_HINTS:
                        res[nm] = hint
        return res

    # ---- public API ----
    def extract_name_hint(self, segments: List[Dict[str, Any]]) -> List[Dict[str, str]]:
        # 1) merge full text
        full_text = " ".join(_norm(s.get("text", "")) for s in (segments or [])).strip()
        if not full_text:
            return []

        # 2) candidates
        cands: List[Tuple[str, int]] = []
        cands += self._mine_from_timestamps(full_text)
        cands += self._mine_spacy(full_text)
        cands += self._mine_regex_caps(full_text)
        if not cands:
            return []

        # 3) dedupe
        names = self._dedupe_keep_order(cands)

        # 4) infer hints via rules (no city/landmark/attraction)
        hints: Dict[str, str] = {}
        for nm in names:
            # require either 2+ tokens OR a strong keyword-derived hint
            tokens = nm.split()
            hint_rule = _hint_from_rules(nm)
            if len(tokens) <= 1 and not hint_rule:
                continue
            if hint_rule and hint_rule in ALLOWED_HINTS:
                hints[nm] = hint_rule

        # 5) optionally refine with ZSL for names missing hints
        if self.use_zsl:
            missing = [nm for nm in names if nm not in hints]
            hints.update(self._zsl_label(missing))

        # 6) final filtering: keep only names with allowed hints
        out, seen = [], set()
        for nm in names:
            h = hints.get(nm)
            if not h or h not in ALLOWED_HINTS:
                continue
            key = _alnum_key(nm)
            if key in seen:
                continue
            seen.add(key)
            out.append({"name": nm, "hint": h})
        
        return out
