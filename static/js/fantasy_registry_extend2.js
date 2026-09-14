/**
 * Fantasy Registry — remaining tournaments
 * Africa extras, Europe extras, South America extras, North America extras,
 * Asia, and International.
 * Load AFTER fantasy_registry.js and fantasy_registry_extend.js.
 */
(function () {
    if (!window.OpenBox?.FantasyRegistry?.tournaments) return;
    var R = OpenBox.FantasyRegistry.tournaments;

    /* ═══════════════════════════════════════════════
       EGYPTIAN PREMIER LEAGUE 2025/26 — 18 clubs
       ═══════════════════════════════════════════════ */
    R.egypt_pl = { id:"egypt_pl", name:"Egyptian Premier League", region:"Africa", type:"domestic", cols:30, rows:100, clubs:[
        {id:"ahl",name:"Al Ahly"},
        {id:"zam",name:"Zamalek"},
        {id:"pyr",name:"Pyramids FC"},
        {id:"masry",name:"Al Masry"},
        {id:"ismaily",name:"Ismaily"},
        {id:"ittihad",name:"Ittihad Alexandria"},
        {id:"smouha",name:"Smouha"},
        {id:"enppi",name:"ENPPI"},
        {id:"ceramica",name:"Ceramica Cleopatra"},
        {id:"future",name:"Modern Future"},
        {id:"bank",name:"National Bank of Egypt"},
        {id:"zed",name:"ZED FC"},
        {id:"gouna",name:"El Gouna"},
        {id:"petrojet",name:"Petrojet"},
        {id:"mahalla",name:"Ghazl El Mahalla"},
        {id:"baladiyat",name:"Baladiyat El Mahalla"},
        {id:"pharco",name:"Pharco FC"},
        {id:"wadi",name:"Wadi Degla"}
    ]};

    /* ═══════════════════════════════════════════════
       SOUTH AFRICAN PSL 2025/26 — 16 clubs
       ═══════════════════════════════════════════════ */
    R.sa_psl = { id:"sa_psl", name:"Betway Premiership", region:"Africa", type:"domestic", cols:30, rows:100, clubs:[
        {id:"msu",name:"Mamelodi Sundowns"},
        {id:"orl",name:"Orlando Pirates"},
        {id:"kaizer",name:"Kaizer Chiefs"},
        {id:"supersport",name:"SuperSport United"},
        {id:"stellenbosch",name:"Stellenbosch FC"},
        {id:"sek",name:"Sekhukhune United"},
        {id:"tsg",name:"TS Galaxy"},
        {id:"ctc",name:"Cape Town City"},
        {id:"arrows",name:"Golden Arrows"},
        {id:"chippa",name:"Chippa United"},
        {id:"polokwane",name:"Polokwane City"},
        {id:"marumo",name:"Marumo Gallants"},
        {id:"richards",name:"Richards Bay"},
        {id:"magesi",name:"Magesi FC"},
        {id:"durban",name:"Durban City"},
        {id:"siwelele",name:"Siwelele FC"}
    ]};

    /* ═══════════════════════════════════════════════
       BOTOLA PRO 2025/26 — 16 clubs
       ═══════════════════════════════════════════════ */
    R.botola = { id:"botola", name:"Botola Pro", region:"Africa", type:"domestic", cols:30, rows:100, clubs:[
        {id:"wyd",name:"Wydad Casablanca"},
        {id:"raja",name:"Raja Casablanca"},
        {id:"asfar",name:"AS FAR"},
        {id:"rsb",name:"Renaissance Berkane"},
        {id:"fus",name:"FUS Rabat"},
        {id:"maghreb",name:"Maghreb Fès"},
        {id:"hassania",name:"Hassania Agadir"},
        {id:"mco",name:"MC Oujda"},
        {id:"ocs",name:"Olympique Safi"},
        {id:"chabab",name:"Chabab Mohammédia"},
        {id:"irt",name:"Ittihad Tanger"},
        {id:"difa",name:"Difaâ El Jadida"},
        {id:"jss",name:"JS Soualem"},
        {id:"touarga",name:"Union Touarga"},
        {id:"codm",name:"COD Meknès"},
        {id:"rz",name:"Renaissance Zemamra"}
    ]};

    /* ═══════════════════════════════════════════════
       EREDIVISIE 2025/26 — 18 clubs
       ═══════════════════════════════════════════════ */
    R.eredivisie = { id:"eredivisie", name:"Eredivisie", region:"Europe", type:"domestic", cols:30, rows:100, clubs:[
        {id:"aja",name:"Ajax"},
        {id:"psv",name:"PSV"},
        {id:"fey",name:"Feyenoord"},
        {id:"az",name:"AZ Alkmaar"},
        {id:"twe",name:"FC Twente"},
        {id:"utr",name:"FC Utrecht"},
        {id:"gae",name:"Go Ahead Eagles"},
        {id:"nec",name:"NEC Nijmegen"},
        {id:"hee",name:"SC Heerenveen"},
        {id:"spa",name:"Sparta Rotterdam"},
        {id:"for",name:"Fortuna Sittard"},
        {id:"gro",name:"FC Groningen"},
        {id:"pec",name:"PEC Zwolle"},
        {id:"her",name:"Heracles Almelo"},
        {id:"alm",name:"Almere City"},
        {id:"wil",name:"Willem II"},
        {id:"nac",name:"NAC Breda"},
        {id:"rkc",name:"RKC Waalwijk"}
    ]};

    /* ═══════════════════════════════════════════════
       PRIMEIRA LIGA 2025/26 — 18 clubs
       ═══════════════════════════════════════════════ */
    R.portugal = { id:"portugal", name:"Liga Portugal Betclic", region:"Europe", type:"domestic", cols:30, rows:100, clubs:[
        {id:"ben",name:"Benfica"},
        {id:"por",name:"FC Porto"},
        {id:"spo",name:"Sporting CP"},
        {id:"bra",name:"SC Braga"},
        {id:"vsc",name:"Vitória SC"},
        {id:"mor",name:"Moreirense"},
        {id:"fam",name:"Famalicão"},
        {id:"san",name:"Santa Clara"},
        {id:"cp",name:"Casa Pia"},
        {id:"est",name:"Estoril Praia"},
        {id:"rio",name:"Rio Ave"},
        {id:"aro",name:"Arouca"},
        {id:"gil",name:"Gil Vicente"},
        {id:"nac",name:"Nacional"},
        {id:"eam",name:"Estrela Amadora"},
        {id:"avs",name:"AVS"},
        {id:"ton",name:"Tondela"},
        {id:"alv",name:"Alverca"}
    ]};

    /* ═══════════════════════════════════════════════
       SÜPER LIG 2025/26 — 18 clubs
       ═══════════════════════════════════════════════ */
    R.turkey = { id:"turkey", name:"Trendyol Süper Lig", region:"Europe", type:"domestic", cols:30, rows:100, clubs:[
        {id:"gal",name:"Galatasaray"},
        {id:"fen",name:"Fenerbahçe"},
        {id:"bes",name:"Beşiktaş"},
        {id:"ts",name:"Trabzonspor"},
        {id:"bas",name:"Başakşehir"},
        {id:"sam",name:"Samsunspor"},
        {id:"kon",name:"Konyaspor"},
        {id:"gaz",name:"Gaziantep FK"},
        {id:"ala",name:"Alanyaspor"},
        {id:"riz",name:"Çaykur Rizespor"},
        {id:"ant",name:"Antalyaspor"},
        {id:"kas",name:"Kasımpaşa"},
        {id:"goz",name:"Göztepe"},
        {id:"kay",name:"Kayserispor"},
        {id:"eyu",name:"Eyüpspor"},
        {id:"koc",name:"Kocaelispor"},
        {id:"gen",name:"Gençlerbirliği"},
        {id:"kar",name:"Fatih Karagümrük"}
    ]};

    /* ═══════════════════════════════════════════════
       UEFA EUROPA LEAGUE 2025/26 — 36 teams
       ═══════════════════════════════════════════════ */
    R.uel = { id:"uel", name:"UEFA Europa League", region:"Europe", type:"continental", cols:48, rows:100, clubs:[
        {id:"mun",name:"Manchester United"},
        {id:"tot",name:"Tottenham"},
        {id:"avl",name:"Aston Villa"},
        {id:"new",name:"Newcastle"},
        {id:"rom",name:"Roma"},
        {id:"laz",name:"Lazio"},
        {id:"juv",name:"Juventus"},
        {id:"nap",name:"Napoli"},
        {id:"rso",name:"Real Sociedad"},
        {id:"ath",name:"Athletic Bilbao"},
        {id:"sev",name:"Sevilla"},
        {id:"bet",name:"Real Betis"},
        {id:"ein",name:"Eintracht Frankfurt"},
        {id:"hof",name:"Hoffenheim"},
        {id:"vfb",name:"VfB Stuttgart"},
        {id:"aja",name:"Ajax"},
        {id:"az",name:"AZ Alkmaar"},
        {id:"fey",name:"Feyenoord"},
        {id:"por",name:"FC Porto"},
        {id:"bra",name:"SC Braga"},
        {id:"ben",name:"Benfica"},
        {id:"gal",name:"Galatasaray"},
        {id:"fen",name:"Fenerbahçe"},
        {id:"bes",name:"Beşiktaş"},
        {id:"oly",name:"Olympiacos"},
        {id:"pae",name:"PAOK"},
        {id:"pan",name:"Panathinaikos"},
        {id:"din",name:"Dinamo Zagreb"},
        {id:"rfs",name:"RFS"},
        {id:"mld",name:"Maccabi Tel Aviv"},
        {id:"cel",name:"Celtic"},
        {id:"ran",name:"Rangers"},
        {id:"fer",name:"Ferencváros"},
        {id:"plz",name:"Viktoria Plzeň"},
        {id:"mal",name:"Malmö FF"},
        {id:"bodo",name:"Bodø/Glimt"}
    ]};

    /* ═══════════════════════════════════════════════
       UEFA CONFERENCE LEAGUE 2025/26 — 36 teams
       ═══════════════════════════════════════════════ */
    R.uecl = { id:"uecl", name:"UEFA Conference League", region:"Europe", type:"continental", cols:48, rows:100, clubs:[
        {id:"che",name:"Chelsea"},
        {id:"cry",name:"Crystal Palace"},
        {id:"fio",name:"Fiorentina"},
        {id:"ata",name:"Atalanta"},
        {id:"bet",name:"Real Betis"},
        {id:"vil",name:"Villarreal"},
        {id:"cop",name:"FC Copenhagen"},
        {id:"gen",name:"KAA Gent"},
        {id:"leg",name:"Legia Warsaw"},
        {id:"jag",name:"Jagiellonia"},
        {id:"cel",name:"Cercle Brugge"},
        {id:"tse",name:"TSC Bačka Topola"},
        {id:"ray",name:"Rayo Vallecano"},
        {id:"siv",name:"Sivasspor"},
        {id:"shk",name:"Shkëndija"},
        {id:"bor",name:"Borac Banja Luka"},
        {id:"bre",name:"Breiðablik"},
        {id:"vll",name:"Vllaznia"},
        {id:"paf",name:"Pafos"},
        {id:"omonia",name:"Omonia"},
        {id:"apoel",name:"APOEL"},
        {id:"ast",name:"Astana"},
        {id:"kairat",name:"Kairat"},
        {id:"ararat",name:"Ararat-Armenia"},
        {id:"noah",name:"Noah"},
        {id:"sabah",name:"Sabah"},
        {id:"linc",name:"Lincoln Red Imps"},
        {id:"viking",name:"Víkingur"},
        {id:"sham",name:"Shamrock Rovers"},
        {id:"shel",name:"Shelbourne"},
        {id:"the_new",name:"The New Saints"},
        {id:"flo",name:"Floriana"},
        {id:"aberdeen",name:"Aberdeen"},
        {id:"hearts",name:"Hearts"},
        {id:"caernarfon",name:"Caernarfon Town"},
        {id:"cliftonville",name:"Cliftonville"}
    ]};

    /* ═══════════════════════════════════════════════
       COPA LIBERTADORES 2026 — 32 group stage clubs
       ═══════════════════════════════════════════════ */
    R.libertadores = { id:"libertadores", name:"Copa Libertadores", region:"South America", type:"continental", cols:48, rows:100, clubs:[
        // Brazil
        {id:"fla",name:"Flamengo"},
        {id:"pal",name:"Palmeiras"},
        {id:"bot",name:"Botafogo"},
        {id:"flu",name:"Fluminense"},
        {id:"cru",name:"Cruzeiro"},
        {id:"int",name:"Internacional"},
        {id:"sao",name:"São Paulo"},
        {id:"bah",name:"Bahia"},
        // Argentina
        {id:"riv",name:"River Plate"},
        {id:"boc",name:"Boca Juniors"},
        {id:"rac",name:"Racing Club"},
        {id:"est",name:"Estudiantes"},
        {id:"vel",name:"Vélez Sarsfield"},
        {id:"san_l",name:"San Lorenzo"},
        // Uruguay
        {id:"pen",name:"Peñarol"},
        {id:"nac",name:"Nacional"},
        // Chile
        {id:"col",name:"Colo-Colo"},
        {id:"uc",name:"Universidad Católica"},
        // Colombia
        {id:"atl_n",name:"Atlético Nacional"},
        {id:"mil",name:"Millonarios"},
        // Ecuador
        {id:"ldu",name:"LDU Quito"},
        {id:"bar",name:"Barcelona SC"},
        {id:"ind_v",name:"Independiente del Valle"},
        // Paraguay
        {id:"cer",name:"Cerro Porteño"},
        {id:"lib",name:"Libertad"},
        {id:"olimpia",name:"Olimpia"},
        // Bolivia
        {id:"bol",name:"Bolívar"},
        {id:"str",name:"The Strongest"},
        // Peru
        {id:"alp",name:"Alianza Lima"},
        {id:"uni",name:"Universitario"},
        // Venezuela
        {id:"car",name:"Caracas FC"},
        {id:"dep_t",name:"Deportivo Táchira"}
    ]};

    /* ═══════════════════════════════════════════════
       COPA SUDAMERICANA 2026 — 32 clubs
       ═══════════════════════════════════════════════ */
    R.sudamericana = { id:"sudamericana", name:"Copa Sudamericana", region:"South America", type:"continental", cols:48, rows:100, clubs:[
        {id:"cor",name:"Corinthians"},
        {id:"vas",name:"Vasco da Gama"},
        {id:"cam",name:"Atlético Mineiro"},
        {id:"bgt",name:"Red Bull Bragantino"},
        {id:"ath_p",name:"Athletico Paranaense"},
        {id:"gre",name:"Grêmio"},
        {id:"ind",name:"Independiente"},
        {id:"lan",name:"Lanús"},
        {id:"def",name:"Defensa y Justicia"},
        {id:"hur",name:"Huracán"},
        {id:"arg",name:"Argentinos Juniors"},
        {id:"tall",name:"Talleres"},
        {id:"dan",name:"Danubio"},
        {id:"liv",name:"Liverpool FC"},
        {id:"coh",name:"Coquimbo Unido"},
        {id:"pal",name:"Palestino"},
        {id:"jun",name:"Junior"},
        {id:"ind_m",name:"Independiente Medellín"},
        {id:"eme",name:"Emelec"},
        {id:"cat",name:"Universidad Católica (ECU)"},
        {id:"gua",name:"Guaraní"},
        {id:"nacio",name:"Nacional Potosí"},
        {id:"alw",name:"Always Ready"},
        {id:"mel",name:"Melgar"},
        {id:"sport",name:"Sporting Cristal"},
        {id:"cien",name:"Cienciano"},
        {id:"met",name:"Metropolitanos"},
        {id:"car",name:"Carabobo"},
        {id:"cerro_l",name:"Cerro Largo"},
        {id:"racing_m",name:"Racing Montevideo"},
        {id:"auc",name:"Aucas"},
        {id:"mushu",name:"Mushuc Runa"}
    ]};

    /* ═══════════════════════════════════════════════
       ARGENTINE PRIMERA 2026 — 28 clubs
       ═══════════════════════════════════════════════ */
    R.argentina_primera = { id:"argentina_primera", name:"Liga Profesional Argentina", region:"South America", type:"domestic", cols:30, rows:100, clubs:[
        {id:"riv",name:"River Plate"},
        {id:"boc",name:"Boca Juniors"},
        {id:"rac",name:"Racing Club"},
        {id:"ind",name:"Independiente"},
        {id:"san_l",name:"San Lorenzo"},
        {id:"vel",name:"Vélez Sarsfield"},
        {id:"est",name:"Estudiantes"},
        {id:"gim",name:"Gimnasia LP"},
        {id:"ros",name:"Rosario Central"},
        {id:"new",name:"Newell's Old Boys"},
        {id:"tall",name:"Talleres"},
        {id:"bel",name:"Belgrano"},
        {id:"lan",name:"Lanús"},
        {id:"ban",name:"Banfield"},
        {id:"def",name:"Defensa y Justicia"},
        {id:"arg",name:"Argentinos Juniors"},
        {id:"huracan",name:"Huracán"},
        {id:"god",name:"Godoy Cruz"},
        {id:"inst",name:"Instituto"},
        {id:"cen",name:"Central Córdoba"},
        {id:"bar",name:"Barracas Central"},
        {id:"pla",name:"Platense"},
        {id:"tig",name:"Tigre"},
        {id:"sarm",name:"Sarmiento"},
        {id:"union",name:"Unión Santa Fe"},
        {id:"ald",name:"Aldosivi"},
        {id:"san_m",name:"San Martín San Juan"},
        {id:"dep_r",name:"Deportivo Riestra"}
    ]};

    /* ═══════════════════════════════════════════════
       LIGA MX 2026 — 18 clubs
       ═══════════════════════════════════════════════ */
    R.ligamx = { id:"ligamx", name:"Liga MX", region:"North America", type:"domestic", cols:30, rows:100, clubs:[
        {id:"ame",name:"Club América"},
        {id:"cruz",name:"Cruz Azul"},
        {id:"chi",name:"Guadalajara"},
        {id:"tig",name:"Tigres UANL"},
        {id:"mty",name:"Monterrey"},
        {id:"pum",name:"Pumas UNAM"},
        {id:"tol",name:"Deportivo Toluca"},
        {id:"leo",name:"León"},
        {id:"pac",name:"Pachuca"},
        {id:"atlas",name:"Atlas"},
        {id:"nec",name:"Necaxa"},
        {id:"pue",name:"Puebla"},
        {id:"que",name:"Querétaro"},
        {id:"san",name:"Santos Laguna"},
        {id:"tij",name:"Tijuana"},
        {id:"jua",name:"FC Juárez"},
        {id:"asl",name:"Atlético San Luis"},
        {id:"maz",name:"Mazatlán"}
    ]};

    /* ═══════════════════════════════════════════════
       CONCACAF CHAMPIONS CUP 2026 — 27 clubs
       ═══════════════════════════════════════════════ */
    R.concacaf_cl = { id:"concacaf_cl", name:"CONCACAF Champions Cup", region:"North America", type:"continental", cols:48, rows:100, clubs:[
        // MLS
        {id:"mia",name:"Inter Miami"},
        {id:"lafc",name:"LAFC"},
        {id:"sea",name:"Seattle Sounders"},
        {id:"clb",name:"Columbus Crew"},
        {id:"cin",name:"FC Cincinnati"},
        {id:"phi",name:"Philadelphia Union"},
        {id:"van",name:"Vancouver Whitecaps"},
        {id:"sd",name:"San Diego FC"},
        // Liga MX
        {id:"ame",name:"América"},
        {id:"cruz",name:"Cruz Azul"},
        {id:"tig",name:"Tigres"},
        {id:"mty",name:"Monterrey"},
        {id:"tol",name:"Toluca"},
        {id:"pum",name:"Pumas"},
        {id:"leo",name:"León"},
        {id:"pac",name:"Pachuca"},
        // Central America & Caribbean
        {id:"sap",name:"Saprissa"},
        {id:"ald",name:"Alajuelense"},
        {id:"here",name:"Herediano"},
        {id:"oli",name:"Olimpia"},
        {id:"mot",name:"Motagua"},
        {id:"comu",name:"Comunicaciones"},
        {id:"ant",name:"Antigua"},
        {id:"cav",name:"Cavalier"},
        {id:"moun",name:"Mount Pleasant"},
        {id:"rob",name:"Robinhood"},
        {id:"cen",name:"Central FC"}
    ]};

    /* ═══════════════════════════════════════════════
       J1 LEAGUE 2026 — 20 clubs
       ═══════════════════════════════════════════════ */
    R.j1 = { id:"j1", name:"J1 League", region:"Asia", type:"domestic", cols:30, rows:100, clubs:[
        {id:"kawasaki",name:"Kawasaki Frontale"},
        {id:"yokohama_fm",name:"Yokohama F. Marinos"},
        {id:"kashima",name:"Kashima Antlers"},
        {id:"urawa",name:"Urawa Red Diamonds"},
        {id:"kobe",name:"Vissel Kobe"},
        {id:"gamba",name:"Gamba Osaka"},
        {id:"hiroshima",name:"Sanfrecce Hiroshima"},
        {id:"fc_tokyo",name:"FC Tokyo"},
        {id:"cerezo",name:"Cerezo Osaka"},
        {id:"nagoya",name:"Nagoya Grampus"},
        {id:"kashiwa",name:"Kashiwa Reysol"},
        {id:"shimizu",name:"Shimizu S-Pulse"},
        {id:"kyoto",name:"Kyoto Sanga"},
        {id:"avispa",name:"Avispa Fukuoka"},
        {id:"machida",name:"FC Machida Zelvia"},
        {id:"shonan",name:"Shonan Bellmare"},
        {id:"niigata",name:"Albirex Niigata"},
        {id:"yokohama_fc",name:"Yokohama FC"},
        {id:"okayama",name:"Fagiano Okayama"},
        {id:"tokyo_v",name:"Tokyo Verdy"}
    ]};

    /* ═══════════════════════════════════════════════
       AFC CHAMPIONS LEAGUE ELITE 2025/26 — 24 clubs
       ═══════════════════════════════════════════════ */
    R.afc_cl = { id:"afc_cl", name:"AFC Champions League Elite", region:"Asia", type:"continental", cols:48, rows:100, clubs:[
        // West Asia
        {id:"hilal",name:"Al Hilal"},
        {id:"nassr",name:"Al Nassr"},
        {id:"ittihad",name:"Al Ittihad"},
        {id:"ahli",name:"Al Ahli"},
        {id:"shabab",name:"Al Shabab"},
        {id:"qadsiah",name:"Al Qadsiah"},
        {id:"sadd",name:"Al Sadd"},
        {id:"rayyan",name:"Al Rayyan"},
        {id:"ain",name:"Al Ain"},
        {id:"sharjah",name:"Sharjah"},
        {id:"wasl",name:"Al Wasl"},
        {id:"pakhtakor",name:"Pakhtakor"},
        // East Asia
        {id:"vissel",name:"Vissel Kobe"},
        {id:"kawasaki",name:"Kawasaki Frontale"},
        {id:"yokohama",name:"Yokohama F. Marinos"},
        {id:"kashima",name:"Kashima Antlers"},
        {id:"ulsan",name:"Ulsan HD"},
        {id:"jeonbuk",name:"Jeonbuk Hyundai"},
        {id:"pohang",name:"Pohang Steelers"},
        {id:"gwangju",name:"Gwangju FC"},
        {id:"shanghai_p",name:"Shanghai Port"},
        {id:"shanghai_s",name:"Shanghai Shenhua"},
        {id:"buriram",name:"Buriram United"},
        {id:"bangkok",name:"BG Pathum United"}
    ]};

   /* ═══════════════════════════════════════════════
       AFRICA CUP OF NATIONS 2027 — 24 teams
       ═══════════════════════════════════════════════ */
    R.afcon = { id:"afcon", name:"Africa Cup of Nations 2027", region:"International", type:"international", cols:30, rows:100, clubs:[
        {id:"ken",name:"Kenya"},
        {id:"tza",name:"Tanzania"},
        {id:"uga",name:"Uganda"},
        {id:"mar",name:"Morocco"},
        {id:"alg",name:"Algeria"},
        {id:"tun",name:"Tunisia"},
        {id:"egy",name:"Egypt"},
        {id:"sen",name:"Senegal"},
        {id:"nga",name:"Nigeria"},
        {id:"civ",name:"Côte d'Ivoire"},
        {id:"cmr",name:"Cameroon"},
        {id:"gha",name:"Ghana"},
        {id:"rsa",name:"South Africa"},
        {id:"cod",name:"DR Congo"},
        {id:"bur",name:"Burkina Faso"},
        {id:"mli",name:"Mali"},
        {id:"gui",name:"Guinea"},
        {id:"cpv",name:"Cabo Verde"},
        {id:"ang",name:"Angola"},
        {id:"zam",name:"Zambia"},
        {id:"moz",name:"Mozambique"},
        {id:"eqg",name:"Equatorial Guinea"},
        {id:"gab",name:"Gabon"},
        {id:"sud",name:"Sudan"}
    ]};

})();
        