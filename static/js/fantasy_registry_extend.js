/**
 * Fantasy Registry — Europe, Americas, Asia, International
 * 2026/27 verified club lists.
 * Load AFTER fantasy_registry.js (Africa base).
 */
(function () {
    if (!window.OpenBox?.FantasyRegistry?.tournaments) {
        console.error('[registry-extend] base registry not loaded');
        return;
    }
    var R = OpenBox.FantasyRegistry.tournaments;

    /* ═══════════════════════════════════════════════
       PREMIER LEAGUE 2026/27 — 20 clubs
       Verified: premierleague.com, NBC Sports (Aug 2026)
       Promoted: Coventry, Hull, Ipswich
       Relegated: West Ham, Burnley, Wolves
       ═══════════════════════════════════════════════ */
    R.epl = { id:"epl", name:"English Premier League", region:"Europe", type:"domestic", cols:30, rows:100, clubs:[
        {id:"ars",name:"Arsenal"},
        {id:"avl",name:"Aston Villa"},
        {id:"bou",name:"AFC Bournemouth"},
        {id:"bre",name:"Brentford"},
        {id:"bha",name:"Brighton & Hove Albion"},
        {id:"che",name:"Chelsea"},
        {id:"cov",name:"Coventry City"},
        {id:"cry",name:"Crystal Palace"},
        {id:"eve",name:"Everton"},
        {id:"ful",name:"Fulham"},
        {id:"hul",name:"Hull City"},
        {id:"ips",name:"Ipswich Town"},
        {id:"lee",name:"Leeds United"},
        {id:"liv",name:"Liverpool"},
        {id:"mci",name:"Manchester City"},
        {id:"mun",name:"Manchester United"},
        {id:"new",name:"Newcastle United"},
        {id:"nfo",name:"Nottingham Forest"},
        {id:"sun",name:"Sunderland"},
        {id:"tot",name:"Tottenham Hotspur"}
    ]};

    /* ═══════════════════════════════════════════════
       LA LIGA 2026/27 — 20 clubs
       Verified: Wikipedia, eldesmarque.com (Jun 2026)
       Promoted: Racing Santander, Deportivo, Málaga
       Relegated: Oviedo, Girona, Mallorca
       ═══════════════════════════════════════════════ */
    R.laliga = { id:"laliga", name:"La Liga", region:"Europe", type:"domestic", cols:30, rows:100, clubs:[
        {id:"ala",name:"Deportivo Alavés"},
        {id:"ath",name:"Athletic Club"},
        {id:"atm",name:"Atlético Madrid"},
        {id:"fcb",name:"FC Barcelona"},
        {id:"cel",name:"Celta de Vigo"},
        {id:"elc",name:"Elche"},
        {id:"esp",name:"Espanyol"},
        {id:"get",name:"Getafe"},
        {id:"lev",name:"Levante"},
        {id:"mal",name:"Málaga"},
        {id:"osa",name:"Osasuna"},
        {id:"rac",name:"Racing Santander"},
        {id:"ray",name:"Rayo Vallecano"},
        {id:"bet",name:"Real Betis"},
        {id:"dep",name:"Deportivo La Coruña"},
        {id:"rma",name:"Real Madrid"},
        {id:"rso",name:"Real Sociedad"},
        {id:"sev",name:"Sevilla"},
        {id:"val",name:"Valencia"},
        {id:"vil",name:"Villarreal"}
    ]};

    /* ═══════════════════════════════════════════════
       SERIE A 2026/27 — 20 clubs
       Verified: sportsbrackets.net, Lega Serie A (May 2026)
       Promoted: Venezia, Frosinone, Monza
       Relegated: Pisa, Verona, Cremonese
       ═══════════════════════════════════════════════ */
    R.seriea = { id:"seriea", name:"Serie A", region:"Europe", type:"domestic", cols:30, rows:100, clubs:[
        {id:"acm",name:"AC Milan"},
        {id:"rom",name:"AS Roma"},
        {id:"ata",name:"Atalanta"},
        {id:"bol",name:"Bologna"},
        {id:"cag",name:"Cagliari"},
        {id:"com",name:"Como"},
        {id:"fio",name:"Fiorentina"},
        {id:"fro",name:"Frosinone"},
        {id:"gen",name:"Genoa"},
        {id:"int",name:"Inter Milan"},
        {id:"juv",name:"Juventus"},
        {id:"laz",name:"Lazio"},
        {id:"lec",name:"Lecce"},
        {id:"mon",name:"Monza"},
        {id:"nap",name:"Napoli"},
        {id:"par",name:"Parma"},
        {id:"sas",name:"Sassuolo"},
        {id:"tor",name:"Torino"},
        {id:"udi",name:"Udinese"},
        {id:"ven",name:"Venezia"}
    ]};

    /* ═══════════════════════════════════════════════
       BUNDESLIGA 2026/27 — 18 clubs
       Verified: beIN Sports, Flashscore (Aug 2026)
       Promoted: Schalke, Elversberg, Paderborn
       Relegated: Wolfsburg, Heidenheim, St. Pauli
       ═══════════════════════════════════════════════ */
    R.bundes = { id:"bundes", name:"Bundesliga", region:"Europe", type:"domestic", cols:30, rows:100, clubs:[
        {id:"aug",name:"FC Augsburg"},
        {id:"b04",name:"Bayer Leverkusen"},
        {id:"bay",name:"Bayern Munich"},
        {id:"bvb",name:"Borussia Dortmund"},
        {id:"bmg",name:"Borussia Mönchengladbach"},
        {id:"sge",name:"Eintracht Frankfurt"},
        {id:"elv",name:"SV Elversberg"},
        {id:"scf",name:"SC Freiburg"},
        {id:"hsv",name:"Hamburger SV"},
        {id:"hof",name:"TSG Hoffenheim"},
        {id:"koln",name:"FC Cologne"},
        {id:"m05",name:"Mainz 05"},
        {id:"pad",name:"SC Paderborn"},
        {id:"rbl",name:"RB Leipzig"},
        {id:"sch",name:"Schalke 04"},
        {id:"vfb",name:"VfB Stuttgart"},
        {id:"fcu",name:"Union Berlin"},
        {id:"svw",name:"Werder Bremen"}
    ]};

    /* ═══════════════════════════════════════════════
       LIGUE 1 2026/27 — 18 clubs
       Verified: Ligue 1, Wikipedia (Aug 2026)
       Promoted: Troyes, Le Mans, Paris FC
       Relegated: Nantes, Metz
       ═══════════════════════════════════════════════ */
    R.ligue1 = { id:"ligue1", name:"Ligue 1", region:"Europe", type:"domestic", cols:30, rows:100, clubs:[
        {id:"ang",name:"Angers"},
        {id:"aux",name:"Auxerre"},
        {id:"bre",name:"Brest"},
        {id:"hac",name:"Le Havre"},
        {id:"lem",name:"Le Mans"},
        {id:"rcl",name:"Lens"},
        {id:"lil",name:"Lille"},
        {id:"lor",name:"Lorient"},
        {id:"lyo",name:"Lyon"},
        {id:"mar",name:"Marseille"},
        {id:"asm",name:"Monaco"},
        {id:"nic",name:"Nice"},
        {id:"pfc",name:"Paris FC"},
        {id:"psg",name:"Paris Saint-Germain"},
        {id:"ren",name:"Rennes"},
        {id:"str",name:"Strasbourg"},
        {id:"tou",name:"Toulouse"},
        {id:"tro",name:"Troyes"}
    ]};

    /* ═══════════════════════════════════════════════
       NPFL 2026/27 — 20 clubs
       Verified: Guardian Nigeria (Aug 2026)
       ═══════════════════════════════════════════════ */
    R.npfl = { id:"npfl", name:"Nigeria Premier Football League", region:"Africa", type:"domestic", cols:30, rows:100, clubs:[
        {id:"3sc",name:"Shooting Stars"},
        {id:"int_lag",name:"Inter Lagos"},
        {id:"ran",name:"Rangers International"},
        {id:"kat",name:"Katsina United"},
        {id:"kan",name:"Kano Pillars"},
        {id:"kwa",name:"Kwara United"},
        {id:"riv",name:"Rivers United"},
        {id:"ben",name:"Bendel Insurance"},
        {id:"dom",name:"Doma United"},
        {id:"eny",name:"Enyimba"},
        {id:"iko",name:"Ikorodu City"},
        {id:"nas",name:"Nasarawa United"},
        {id:"nig",name:"Niger Tornadoes"},
        {id:"akw",name:"Akwa United"},
        {id:"spo",name:"Sporting Lagos"},
        {id:"bay",name:"Bayelsa United"},
        {id:"barau",name:"Barau FC"},
        {id:"gom",name:"Gombe United"},
        {id:"sun",name:"Sunshine Stars"},
        {id:"hea",name:"Heartland FC"}
    ]};

    /* ═══════════════════════════════════════════════
       CAF CHAMPIONS LEAGUE 2026/27 — 48+ clubs
       Verified: foot-africa.com (Jul 2026)
       Note: preliminary rounds in progress; group stage Nov 2026
       ═══════════════════════════════════════════════ */
    R.cafcl = { id:"cafcl", name:"CAF Champions League", region:"Africa", type:"continental", cols:48, rows:100, clubs:[
        {id:"mca",name:"MC Alger"},
        {id:"jss",name:"JS Saoura"},
        {id:"petro",name:"Petro de Luanda"},
        {id:"wiliete",name:"Wiliete SC"},
        {id:"orl",name:"Orlando Pirates"},
        {id:"msu",name:"Mamelodi Sundowns"},
        {id:"ase",name:"ASEC Mimosas"},
        {id:"san_pedro",name:"FC San Pedro"},
        {id:"zam",name:"Zamalek"},
        {id:"pyr",name:"Pyramids FC"},
        {id:"djoliba",name:"Djoliba AC"},
        {id:"stade_malien",name:"Stade Malien"},
        {id:"mas_fes",name:"MAS Fès"},
        {id:"rsb",name:"RS Berkane"},
        {id:"ran",name:"Enugu Rangers"},
        {id:"riv",name:"Rivers United"},
        {id:"tpm",name:"TP Mazembe"},
        {id:"aigles",name:"Aigles du Congo"},
        {id:"hilal_omd",name:"Al Hilal Omdurman"},
        {id:"merrikh",name:"Al Merrikh"},
        {id:"yang",name:"Young Africans"},
        {id:"simba",name:"Simba SC"},
        {id:"caf",name:"Club Africain"},
        {id:"est",name:"Espérance de Tunis"},
        {id:"sobemap",name:"AS SOBEMAP"},
        {id:"gaborone",name:"Gaborone United"},
        {id:"rahimo",name:"Rahimo FC"},
        {id:"aigle_noir",name:"Aigle Noir"},
        {id:"colombe",name:"Colombe Sportive"},
        {id:"palmeira",name:"GD Palmeira"},
        {id:"fomboni",name:"Fomboni FC"},
        {id:"port",name:"AS Port"},
        {id:"nsingizini",name:"Nsingizini Hotspurs"},
        {id:"sidama",name:"Sidama Bunna"},
        {id:"medeama",name:"Medeama SC"},
        {id:"horoya",name:"Horoya AC"},
        {id:"gor_mahia",name:"Gor Mahia"},
        {id:"lijabatho",name:"Lijabatho FC"},
        {id:"watanga",name:"Watanga FC"},
        {id:"al_swehly",name:"Al-Swehly"},
        {id:"wanderers",name:"Mighty Wanderers"},
        {id:"cure_waves",name:"La Cure Waves"},
        {id:"nouadhibou",name:"FC Nouadhibou"},
        {id:"songo",name:"UD Songo"},
        {id:"african_stars",name:"African Stars"},
        {id:"nigelec",name:"ASN Nigelec"},
        {id:"vipers",name:"Vipers SC"},
        {id:"apr",name:"APR FC"}
    ]};

    /* ═══════════════════════════════════════════════
       BRASILEIRÃO SÉRIE A 2026 — 20 clubs
       Verified: jc.uol.com.br (Dec 2025)
       ═══════════════════════════════════════════════ */
    R.brasileirao_a = { id:"brasileirao_a", name:"Brasileirão Série A", region:"South America", type:"domestic", cols:30, rows:100, clubs:[
        {id:"fla",name:"Flamengo"},
        {id:"pal",name:"Palmeiras"},
        {id:"cru",name:"Cruzeiro"},
        {id:"mir",name:"Mirassol"},
        {id:"flu",name:"Fluminense"},
        {id:"bah",name:"Bahia"},
        {id:"bot",name:"Botafogo"},
        {id:"sao",name:"São Paulo"},
        {id:"bgt",name:"Red Bull Bragantino"},
        {id:"cor",name:"Corinthians"},
        {id:"gre",name:"Grêmio"},
        {id:"vas",name:"Vasco da Gama"},
        {id:"cam",name:"Atlético Mineiro"},
        {id:"san",name:"Santos"},
        {id:"vit",name:"Vitória"},
        {id:"int",name:"Internacional"},
        {id:"coritiba",name:"Coritiba"},
        {id:"ath_p",name:"Athletico Paranaense"},
        {id:"cha",name:"Chapecoense"},
        {id:"remo",name:"Remo"}
    ]};

    /* ═══════════════════════════════════════════════
       MLS 2026 — 30 clubs (East + West)
       Verified: MLSsoccer.com, ESPN (Feb 2026)
       ═══════════════════════════════════════════════ */
    R.mls = { id:"mls", name:"Major League Soccer", region:"North America", type:"domestic", cols:30, rows:100, clubs:[
        // Eastern Conference
        {id:"mia",name:"Inter Miami CF"},
        {id:"cin",name:"FC Cincinnati"},
        {id:"nsh",name:"Nashville SC"},
        {id:"phi",name:"Philadelphia Union"},
        {id:"chi",name:"Chicago Fire FC"},
        {id:"clt",name:"Charlotte FC"},
        {id:"clb",name:"Columbus Crew"},
        {id:"nyc",name:"New York City FC"},
        {id:"orl",name:"Orlando City"},
        {id:"nyrb",name:"Red Bull New York"},
        {id:"atl",name:"Atlanta United"},
        {id:"ner",name:"New England Revolution"},
        {id:"tor",name:"Toronto FC"},
        {id:"dcu",name:"D.C. United"},
        {id:"mtl",name:"CF Montréal"},
        // Western Conference
        {id:"lafc",name:"LAFC"},
        {id:"van",name:"Vancouver Whitecaps"},
        {id:"sd",name:"San Diego FC"},
        {id:"sea",name:"Seattle Sounders"},
        {id:"lag",name:"LA Galaxy"},
        {id:"atx",name:"Austin FC"},
        {id:"min",name:"Minnesota United"},
        {id:"por",name:"Portland Timbers"},
        {id:"hou",name:"Houston Dynamo"},
        {id:"dal",name:"FC Dallas"},
        {id:"rsl",name:"Real Salt Lake"},
        {id:"sj",name:"San Jose Earthquakes"},
        {id:"stl",name:"St. Louis CITY SC"},
        {id:"col",name:"Colorado Rapids"},
        {id:"skc",name:"Sporting Kansas City"}
    ]};

    /* ═══════════════════════════════════════════════
       SAUDI PRO LEAGUE 2026/27 — 18 clubs
       Verified: SPL, Khel Now (Sep 2026)
       ═══════════════════════════════════════════════ */
    R.saudi_pl = { id:"saudi_pl", name:"Saudi Pro League", region:"Asia", type:"domestic", cols:30, rows:100, clubs:[
        {id:"hilal",name:"Al Hilal"},
        {id:"nassr",name:"Al Nassr"},
        {id:"ittihad",name:"Al Ittihad"},
        {id:"ahli",name:"Al Ahli"},
        {id:"qadsiah",name:"Al Qadsiah"},
        {id:"shabab",name:"Al Shabab"},
        {id:"ettifaq",name:"Al Ettifaq"},
        {id:"taawoun",name:"Al Taawoun"},
        {id:"fateh",name:"Al Fateh"},
        {id:"khaleej",name:"Al Khaleej"},
        {id:"kholood",name:"Al Kholood"},
        {id:"riyadh",name:"Al Riyadh"},
        {id:"fayha",name:"Al Fayha"},
        {id:"hazem",name:"Al Hazem"},
        {id:"abha",name:"Abha"},
        {id:"faisaly",name:"Al Faisaly"},
        {id:"diriyah",name:"Diriyah Club"},
        {id:"neom",name:"NEOM SC"}
    ]};

    /* ═══════════════════════════════════════════════
       UEFA CHAMPIONS LEAGUE 2026/27 — 36 teams
       Verified: UEFA.com (Sep 2026)
       ═══════════════════════════════════════════════ */
    R.ucl = { id:"ucl", name:"UEFA Champions League", region:"Europe", type:"continental", cols:48, rows:100, clubs:[
        {id:"ars",name:"Arsenal"},
        {id:"avl",name:"Aston Villa"},
        {id:"liv",name:"Liverpool"},
        {id:"mci",name:"Manchester City"},
        {id:"mun",name:"Manchester United"},
        {id:"atm",name:"Atlético Madrid"},
        {id:"fcb",name:"Barcelona"},
        {id:"bet",name:"Real Betis"},
        {id:"rma",name:"Real Madrid"},
        {id:"vil",name:"Villarreal"},
        {id:"bay",name:"Bayern München"},
        {id:"bvb",name:"Borussia Dortmund"},
        {id:"rbl",name:"RB Leipzig"},
        {id:"vfb",name:"VfB Stuttgart"},
        {id:"int",name:"Inter"},
        {id:"nap",name:"Napoli"},
        {id:"rom",name:"Roma"},
        {id:"com",name:"Como"},
        {id:"lil",name:"Lille"},
        {id:"rcl",name:"Lens"},
        {id:"psg",name:"Paris Saint-Germain"},
        {id:"bru",name:"Club Brugge"},
        {id:"fey",name:"Feyenoord"},
        {id:"psv",name:"PSV"},
        {id:"por",name:"Porto"},
        {id:"spo",name:"Sporting CP"},
        {id:"ben",name:"Benfica"},
        {id:"cel",name:"Celtic"},
        {id:"rsc",name:"RSC Anderlecht"},
        {id:"sal",name:"Red Bull Salzburg"},
        {id:"shk",name:"Shakhtar Donetsk"},
        {id:"spa",name:"Sparta Prague"},
        {id:"slo",name:"Slovan Bratislava"},
        {id:"crv",name:"Crvena Zvezda"},
        {id:"stu",name:"Sturm Graz"},
        {id:"yng",name:"Young Boys"}
    ]};

    /* ═══════════════════════════════════════════════
       FIFA WORLD CUP 2026 — 48 qualified teams
       Verified: FIFA.com (Apr 2026)
       ═══════════════════════════════════════════════ */
    R.worldcup = { id:"worldcup", name:"FIFA World Cup 2026", region:"International", type:"international", cols:48, rows:100, clubs:[
        // Hosts
        {id:"can",name:"Canada"},
        {id:"mex",name:"Mexico"},
        {id:"usa",name:"USA"},
        // AFC
        {id:"aus",name:"Australia"},
        {id:"irq",name:"Iraq"},
        {id:"irn",name:"IR Iran"},
        {id:"jpn",name:"Japan"},
        {id:"jor",name:"Jordan"},
        {id:"kor",name:"Korea Republic"},
        {id:"qat",name:"Qatar"},
        {id:"sau",name:"Saudi Arabia"},
        {id:"uzb",name:"Uzbekistan"},
        // CAF
        {id:"alg",name:"Algeria"},
        {id:"cpv",name:"Cabo Verde"},
        {id:"cod",name:"Congo DR"},
        {id:"civ",name:"Côte d'Ivoire"},
        {id:"egy",name:"Egypt"},
        {id:"gha",name:"Ghana"},
        {id:"mar",name:"Morocco"},
        {id:"sen",name:"Senegal"},
        {id:"rsa",name:"South Africa"},
        {id:"tun",name:"Tunisia"},
        // Concacaf
        {id:"cur",name:"Curaçao"},
        {id:"hai",name:"Haiti"},
        {id:"pan",name:"Panama"},
        // CONMEBOL
        {id:"arg",name:"Argentina"},
        {id:"bra",name:"Brazil"},
        {id:"col",name:"Colombia"},
        {id:"ecu",name:"Ecuador"},
        {id:"par",name:"Paraguay"},
        {id:"uru",name:"Uruguay"},
        // OFC
        {id:"nzl",name:"New Zealand"},
        // UEFA
        {id:"aut",name:"Austria"},
        {id:"bel",name:"Belgium"},
        {id:"bih",name:"Bosnia and Herzegovina"},
        {id:"cro",name:"Croatia"},
        {id:"cze",name:"Czechia"},
        {id:"eng",name:"England"},
        {id:"fra",name:"France"},
        {id:"ger",name:"Germany"},
        {id:"ned",name:"Netherlands"},
        {id:"nor",name:"Norway"},
        {id:"por",name:"Portugal"},
        {id:"sco",name:"Scotland"},
        {id:"esp",name:"Spain"},
        {id:"swe",name:"Sweden"},
        {id:"sui",name:"Switzerland"},
        {id:"tur",name:"Türkiye"}
    ]};

})();