"""
Mapping between external sources (Bzzoiro, Transfermarkt) and our registry IDs.
Fuzzy match on club name. Registry is source of truth.
"""

REGISTRY = {
    "epl": {
        "name": "English Premier League",
        "aliases": ["premier league", "english premier league", "epl"],
        "clubs": {
            "ars": ["arsenal"], "avl": ["aston villa"],
            "bou": ["bournemouth", "afc bournemouth"], "bre": ["brentford"],
            "bha": ["brighton", "brighton & hove albion", "brighton and hove albion"],
            "che": ["chelsea"], "cov": ["coventry", "coventry city"],
            "cry": ["crystal palace"], "eve": ["everton"],
            "ful": ["fulham"], "hul": ["hull", "hull city"],
            "ips": ["ipswich", "ipswich town"], "lee": ["leeds", "leeds united"],
            "liv": ["liverpool"], "mci": ["manchester city", "man city"],
            "mun": ["manchester united", "man united", "man utd"],
            "new": ["newcastle", "newcastle united"],
            "nfo": ["nottingham forest", "nott'm forest"],
            "sun": ["sunderland"], "tot": ["tottenham", "tottenham hotspur", "spurs"],
        },
    },
    "laliga": {
        "name": "La Liga",
        "aliases": ["la liga", "laliga", "primera division"],
        "clubs": {
            "ala": ["alaves", "deportivo alaves"],
            "ath": ["athletic", "athletic bilbao", "athletic club"],
            "atm": ["atletico madrid", "atletico de madrid"],
            "fcb": ["barcelona", "fc barcelona", "barca"],
            "cel": ["celta", "celta vigo"], "elc": ["elche"],
            "esp": ["espanyol"], "get": ["getafe"],
            "lev": ["levante"], "mal": ["malaga"],
            "osa": ["osasuna"], "rac": ["racing santander"],
            "ray": ["rayo vallecano", "rayo"],
            "bet": ["real betis", "betis"],
            "dep": ["deportivo la coruna", "deportivo"],
            "rma": ["real madrid"], "rso": ["real sociedad"],
            "sev": ["sevilla"], "val": ["valencia"], "vil": ["villarreal"],
        },
    },
    "seriea": {
        "name": "Serie A",
        "aliases": ["serie a", "italian serie a"],
        "clubs": {
            "acm": ["ac milan", "milan"], "rom": ["roma", "as roma"],
            "ata": ["atalanta"], "bol": ["bologna"],
            "cag": ["cagliari"], "com": ["como"],
            "fio": ["fiorentina"], "fro": ["frosinone"],
            "gen": ["genoa"], "int": ["inter", "inter milan"],
            "juv": ["juventus", "juve"], "laz": ["lazio"],
            "lec": ["lecce"], "mon": ["monza"],
            "nap": ["napoli"], "par": ["parma"],
            "sas": ["sassuolo"], "tor": ["torino"],
            "udi": ["udinese"], "ven": ["venezia"],
        },
    },
    "bundes": {
        "name": "Bundesliga",
        "aliases": ["bundesliga", "german bundesliga"],
        "clubs": {
            "aug": ["augsburg"], "b04": ["bayer leverkusen", "leverkusen"],
            "bay": ["bayern munich", "bayern", "bayern munchen"],
            "bvb": ["borussia dortmund", "dortmund"],
            "bmg": ["borussia monchengladbach", "gladbach"],
            "sge": ["eintracht frankfurt", "frankfurt"],
            "elv": ["elversberg"], "scf": ["freiburg", "sc freiburg"],
            "hsv": ["hamburger sv", "hamburg"],
            "hof": ["hoffenheim"], "koln": ["cologne", "koln", "fc koln"],
            "m05": ["mainz"], "pad": ["paderborn"],
            "rbl": ["rb leipzig", "leipzig"],
            "sch": ["schalke"], "vfb": ["stuttgart", "vfb stuttgart"],
            "fcu": ["union berlin"], "svw": ["werder bremen", "werder"],
        },
    },
    "ligue1": {
        "name": "Ligue 1",
        "aliases": ["ligue 1", "french ligue 1"],
        "clubs": {
            "ang": ["angers"], "aux": ["auxerre"], "bre": ["brest"],
            "hac": ["le havre"], "lem": ["le mans"], "rcl": ["lens"],
            "lil": ["lille"], "lor": ["lorient"], "lyo": ["lyon"],
            "mar": ["marseille"], "asm": ["monaco"],
            "nic": ["nice"], "pfc": ["paris fc"],
            "psg": ["paris saint-germain", "psg", "paris sg"],
            "ren": ["rennes"], "str": ["strasbourg"],
            "tou": ["toulouse"], "tro": ["troyes"],
        },
    },
    "eredivisie": {
        "name": "Eredivisie",
        "aliases": ["eredivisie", "dutch eredivisie"],
        "clubs": {
            "aja": ["ajax"], "psv": ["psv", "psv eindhoven"],
            "fey": ["feyenoord"], "az": ["az", "az alkmaar"],
            "twe": ["twente", "fc twente"], "utr": ["utrecht"],
            "gae": ["go ahead eagles"], "nec": ["nec", "nec nijmegen"],
            "hee": ["heerenveen"], "spa": ["sparta rotterdam"],
            "for": ["fortuna sittard"], "gro": ["groningen"],
            "pec": ["pec zwolle"], "her": ["heracles"],
            "alm": ["almere"], "wil": ["willem ii"],
            "nac": ["nac breda"], "rkc": ["rkc waalwijk"],
        },
    },
    "portugal": {
        "name": "Primeira Liga",
        "aliases": ["primeira liga", "liga portugal"],
        "clubs": {
            "ben": ["benfica"], "por": ["porto", "fc porto"],
            "spo": ["sporting", "sporting cp", "sporting lisbon"],
            "bra": ["braga", "sc braga"], "vsc": ["vitoria", "vitoria sc"],
            "mor": ["moreirense"], "fam": ["famalicao"],
            "san": ["santa clara"], "est": ["estoril"],
            "rio": ["rio ave"], "aro": ["arouca"],
            "gil": ["gil vicente"], "nac": ["nacional"],
            "eam": ["estrela amadora"], "avs": ["avs"],
            "ton": ["tondela"], "alv": ["alverca"],
        },
    },
    "turkey": {
        "name": "Süper Lig",
        "aliases": ["super lig", "süper lig", "turkish super lig"],
        "clubs": {
            "gal": ["galatasaray"], "fen": ["fenerbahce", "fenerbahçe"],
            "bes": ["besiktas", "beşiktaş"], "ts": ["trabzonspor"],
            "bas": ["basaksehir", "istanbul basaksehir"],
            "sam": ["samsunspor"], "kon": ["konyaspor"],
            "gaz": ["gaziantep"], "ala": ["alanyaspor"],
            "riz": ["rizespor"], "ant": ["antalyaspor"],
            "kas": ["kasimpasa", "kasımpaşa"], "goz": ["goztepe", "göztepe"],
            "kay": ["kayserispor"], "eyu": ["eyupspor"],
            "koc": ["kocaelispor"],
            "gen": ["genclerbirligi"], "kar": ["karagumruk"],
        },
    },
    "brasileirao_a": {
        "name": "Brasileirão Série A",
        "aliases": ["brasileirao serie a", "brasileirão serie a", "brasileirao"],
        "clubs": {
            "fla": ["flamengo"], "pal": ["palmeiras"],
            "cru": ["cruzeiro"], "mir": ["mirassol"],
            "flu": ["fluminense"], "bah": ["bahia"],
            "bot": ["botafogo"], "sao": ["sao paulo", "são paulo"],
            "bgt": ["bragantino", "red bull bragantino"],
            "cor": ["corinthians"], "gre": ["gremio", "grêmio"],
            "vas": ["vasco", "vasco da gama"],
            "cam": ["atletico mineiro", "atlético mineiro"],
            "san": ["santos"], "vit": ["vitoria", "vitória"],
            "int": ["internacional"], "coritiba": ["coritiba"],
            "ath_p": ["athletico paranaense", "athletico-pr"],
            "cha": ["chapecoense"], "remo": ["remo"],
        },
    },
    "brasileirao_b": {
        "name": "Brasileirão Série B",
        "aliases": ["brasileirao serie b", "brasileirão serie b"],
        "clubs": {},
    },
    "argentina_primera": {
        "name": "Liga Profesional Argentina",
        "aliases": ["liga profesional", "primera division argentina", "argentina primera"],
        "clubs": {
            "riv": ["river plate"], "boc": ["boca juniors"],
            "rac": ["racing club", "racing"],
            "ind": ["independiente"], "san_l": ["san lorenzo"],
            "vel": ["velez", "velez sarsfield"],
            "est": ["estudiantes"], "gim": ["gimnasia"],
            "ros": ["rosario central"], "new": ["newell's"],
            "tall": ["talleres"], "bel": ["belgrano"],
            "lan": ["lanus", "lanús"], "ban": ["banfield"],
            "def": ["defensa y justicia"], "arg": ["argentinos juniors"],
        },
    },
    "mls": {
        "name": "Major League Soccer",
        "aliases": ["major league soccer", "mls"],
        "clubs": {
            "mia": ["inter miami", "miami"], "cin": ["fc cincinnati", "cincinnati"],
            "nsh": ["nashville"], "phi": ["philadelphia union", "philadelphia"],
            "chi": ["chicago fire", "chicago"], "clt": ["charlotte"],
            "clb": ["columbus crew", "columbus"],
            "nyc": ["new york city", "nycfc"],
            "orl": ["orlando city", "orlando"],
            "nyrb": ["new york red bulls", "red bull new york"],
            "atl": ["atlanta united", "atlanta"],
            "ner": ["new england revolution", "new england"],
            "tor": ["toronto"], "dcu": ["dc united"],
            "mtl": ["cf montreal", "montreal", "montréal"],
            "lafc": ["lafc"], "van": ["vancouver"],
            "sd": ["san diego"], "sea": ["seattle sounders", "seattle"],
            "lag": ["la galaxy", "los angeles galaxy"],
            "atx": ["austin"], "min": ["minnesota"],
            "por": ["portland"], "hou": ["houston"],
            "dal": ["fc dallas", "dallas"],
            "rsl": ["real salt lake"], "sj": ["san jose"],
            "stl": ["st louis"], "col": ["colorado"],
            "skc": ["sporting kansas city", "kansas city"],
        },
    },
    "ligamx": {
        "name": "Liga MX",
        "aliases": ["liga mx", "mexican liga mx"],
        "clubs": {
            "ame": ["america", "club america"],
            "cruz": ["cruz azul"], "chi": ["guadalajara", "chivas"],
            "tig": ["tigres", "tigres uanl"], "mty": ["monterrey"],
            "pum": ["pumas", "pumas unam"],
            "tol": ["toluca", "deportivo toluca"], "leo": ["leon", "león"],
            "pac": ["pachuca"], "atlas": ["atlas"],
            "nec": ["necaxa"], "pue": ["puebla"],
            "que": ["queretaro", "querétaro"],
            "san": ["santos laguna"], "tij": ["tijuana"],
            "jua": ["juarez", "juárez"], "asl": ["atletico san luis"],
            "maz": ["mazatlan", "mazatlán"],
        },
    },
    "saudi_pl": {
        "name": "Saudi Pro League",
        "aliases": ["saudi pro league", "saudi league"],
        "clubs": {
            "hilal": ["al hilal"], "nassr": ["al nassr"],
            "ittihad": ["al ittihad"], "ahli": ["al ahli"],
            "qadsiah": ["al qadsiah"], "shabab": ["al shabab"],
            "ettifaq": ["al ettifaq"], "taawoun": ["al taawoun"],
            "fateh": ["al fateh"], "khaleej": ["al khaleej"],
            "kholood": ["al kholood"], "riyadh": ["al riyadh"],
            "fayha": ["al fayha"], "hazem": ["al hazem"],
            "abha": ["abha"], "faisaly": ["al faisaly"],
            "diriyah": ["diriyah"], "neom": ["neom"],
        },
    },
    "j1": {
        "name": "J1 League",
        "aliases": ["j1 league", "j league"],
        "clubs": {
            "kawasaki": ["kawasaki frontale"], "yokohama_fm": ["yokohama f marinos"],
            "kashima": ["kashima antlers"], "urawa": ["urawa reds"],
            "kobe": ["vissel kobe"], "gamba": ["gamba osaka"],
            "hiroshima": ["sanfrecce hiroshima"], "fc_tokyo": ["fc tokyo"],
            "cerezo": ["cerezo osaka"], "nagoya": ["nagoya grampus"],
            "kashiwa": ["kashiwa reysol"], "shimizu": ["shimizu s-pulse"],
            "kyoto": ["kyoto sanga"], "avispa": ["avispa fukuoka"],
            "machida": ["machida zelvia"], "shonan": ["shonan bellmare"],
            "niigata": ["albirex niigata"], "yokohama_fc": ["yokohama fc"],
            "okayama": ["fagiano okayama"], "tokyo_v": ["tokyo verdy"],
        },
    },
    "npfl": {
        "name": "Nigeria Premier Football League",
        "aliases": ["nigeria premier", "npfl"],
        "clubs": {
            "3sc": ["shooting stars"], "int_lag": ["inter lagos"],
            "ran": ["rangers international", "rangers"],
            "kat": ["katsina united"], "kan": ["kano pillars"],
            "kwa": ["kwara united"], "riv": ["rivers united"],
            "ben": ["bendel insurance"], "dom": ["doma united"],
            "eny": ["enyimba"], "iko": ["ikorodu city"],
            "nas": ["nasarawa united"], "nig": ["niger tornadoes"],
            "akw": ["akwa united"], "spo": ["sporting lagos"],
            "bay": ["bayelsa united"], "barau": ["barau"],
            "gom": ["gombe united"], "sun": ["sunshine stars"],
            "hea": ["heartland"],
        },
    },
    "cafcl": {
        "name": "CAF Champions League",
        "aliases": ["caf champions league", "caf cl"],
        "clubs": {},  # populated dynamically as Bzzoiro returns teams
    },
    "egypt_pl": {
        "name": "Egyptian Premier League",
        "aliases": ["egyptian premier league", "egypt premier"],
        "clubs": {
            "ahl": ["al ahly"], "zam": ["zamalek"],
            "pyr": ["pyramids"], "masry": ["al masry", "masry"],
            "ismaily": ["ismaily"], "ittihad": ["ittihad alexandria"],
            "smouha": ["smouha"], "enppi": ["enppi"],
            "ceramica": ["ceramica cleopatra"],
            "future": ["modern future", "future fc"],
            "bank": ["national bank"], "zed": ["zed fc"],
            "gouna": ["el gouna"], "petrojet": ["petrojet"],
            "mahalla": ["ghazl el mahalla"],
        },
    },
    "sa_psl": {
        "name": "South African Premier Division",
        "aliases": ["south african premier", "betway premiership", "sa psl"],
        "clubs": {
            "msu": ["mamelodi sundowns", "sundowns"],
            "orl": ["orlando pirates", "pirates"],
            "kaizer": ["kaizer chiefs"], "supersport": ["supersport united"],
            "stellenbosch": ["stellenbosch"], "sek": ["sekhukhune united"],
            "tsg": ["ts galaxy"], "ctc": ["cape town city"],
        },
    },
    "botola": {
        "name": "Botola Pro",
        "aliases": ["botola pro", "botola"],
        "clubs": {
            "wyd": ["wydad"], "raja": ["raja"],
            "asfar": ["as far"], "rsb": ["renaissance berkane", "berkane"],
            "maghreb": ["maghreb fes"], "hassania": ["hassania agadir"],
        },
    },
}


def _norm(s: str) -> str:
    """Normalize a name for fuzzy matching."""
    if not s:
        return ""
    s = s.lower()
    for tok in [" fc", " cf", " sc", " ac", " afc", " cd", " ca",
                " club", " football club", " calcio", " de futbol",
                " fútbol", " sporting", "'s", "&", " and ", "."]:
        s = s.replace(tok, " ")
    s = "".join(c if c.isalnum() or c == " " else " " for c in s)
    return " ".join(s.split())


def match_tournament(source_name: str):
    """Match source league name to registry tournament key."""
    if not source_name:
        return None
    n = _norm(source_name)
    # exact alias match first
    for tid, t in REGISTRY.items():
        for a in t.get("aliases", []):
            if _norm(a) == n:
                return tid
    # substring fallback
    for tid, t in REGISTRY.items():
        for a in t.get("aliases", []):
            na = _norm(a)
            if na and (na in n or n in na):
                return tid
    return None


def match_club(tournament_id: str, source_club_name: str):
    """Match source club name to registry club key for a given tournament."""
    if not tournament_id or tournament_id not in REGISTRY or not source_club_name:
        return None
    clubs = REGISTRY[tournament_id].get("clubs", {})
    n = _norm(source_club_name)
    if not n:
        return None
    # exact
    for cid, aliases in clubs.items():
        for a in aliases:
            if _norm(a) == n:
                return cid
    # substring
    for cid, aliases in clubs.items():
        for a in aliases:
            na = _norm(a)
            if na and (na in n or n in na):
                return cid
    return None


def canonical_club_id(tournament_id: str, source_club_name: str,
                      source_key: str, source_club_id) -> str:
    """
    Return the ID to write in the DB.
    If a registry match is found: 'epl:ars'
    Otherwise: 'source:source_id' (e.g. 'bzz_9:755')
    """
    if tournament_id:
        cid = match_club(tournament_id, source_club_name)
        if cid:
            return f"{tournament_id}:{cid}"
    return f"{source_key}:{source_club_id}"