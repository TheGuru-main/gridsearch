i/**
 * Fantasy Registry — tournaments as grids, clubs as columns.
 */

window.OpenBox = window.OpenBox || {};

OpenBox.FantasyRegistry = {

  tournaments: {

    // ═══════════════════════════════════════════════════════
    //  AFRICA
    // ═══════════════════════════════════════════════════════
    npfl: {
      id: "npfl", name: "Nigeria Premier League", region: "Africa", type: "domestic", cols: 30, rows: 100,
      clubs: [
        { id: "3sc", name: "Shooting Stars", players: [
          { name: "Mustapha Lawal", pos: "GK" }, { name: "Saheed Lawal", pos: "GK" },
          { name: "Gafar Ojo", pos: "DEF" }, { name: "Dimeji Lawal", pos: "DEF" },
          { name: "Taiwo Adeyemi", pos: "DEF" }, { name: "Ayodeji Adebayo", pos: "DEF" },
          { name: "Malomo Taofeek", pos: "MID" }, { name: "Ayobami Ayoola", pos: "MID" },
          { name: "Rafiu Salami", pos: "MID" }, { name: "Wasiu Alalade", pos: "MID" },
          { name: "Junior Lokosa", pos: "FWD" }, { name: "Tunde Adeniji", pos: "FWD" },
          { name: "Chinedu Nwosu", pos: "FWD" }, { name: "Yemi Adeyemi", pos: "FWD" },
        ]},
        { id: "int_lag", name: "Inter Lagos", players: [
          { name: "Emminence Naingba", pos: "GK" }, { name: "Monsoor", pos: "GK" },
          { name: "Godgift", pos: "DEF" }, { name: "Azeez", pos: "DEF" },
          { name: "Lucky", pos: "DEF" }, { name: "Mustapha", pos: "DEF" },
          { name: "Taheer", pos: "MID" }, { name: "Raheem", pos: "MID" },
          { name: "Promise", pos: "MID" }, { name: "Dawari", pos: "MID" },
          { name: "T. Azeez", pos: "FWD" }, { name: "Amadou", pos: "FWD" },
          { name: "Damilare", pos: "FWD" }, { name: "Adams", pos: "FWD" },
          { name: "Sochima", pos: "FWD" },
        ]},
        { id: "ran", name: "Rangers International", players: [
          { name: "Detan Ogundare", pos: "GK" }, { name: "Ifeanyi Nweke", pos: "GK" },
          { name: "Chidiebere Okolie", pos: "DEF" }, { name: "Kalu Orji", pos: "DEF" },
          { name: "Uche John", pos: "DEF" }, { name: "Tope Olusesi", pos: "DEF" },
          { name: "Kenechukwu Agu", pos: "MID" }, { name: "Chukwudi Nwafor", pos: "MID" },
          { name: "Onyeka Eze", pos: "MID" }, { name: "Ugochukwu Obi", pos: "MID" },
          { name: "Chidera Ezeh", pos: "FWD" }, { name: "Godwin Obaje", pos: "FWD" },
          { name: "Ifeanyi George", pos: "FWD" }, { name: "Emmanuel Daniel", pos: "FWD" },
        ]},
        { id: "kat", name: "Katsina United", players: [
          { name: "Yusuf Mohammed", pos: "GK" }, { name: "Bashir Sani", pos: "GK" },
          { name: "Tasiu Lawal", pos: "DEF" }, { name: "Ibrahim Sule", pos: "DEF" },
          { name: "Abdullahi Musa", pos: "DEF" }, { name: "Haruna Aliyu", pos: "DEF" },
          { name: "Sani Faisal", pos: "MID" }, { name: "Nura Aminu", pos: "MID" },
          { name: "Usman Barau", pos: "MID" }, { name: "Kabiru Dogo", pos: "MID" },
          { name: "Mubarak Said", pos: "FWD" }, { name: "Aliyu Kano", pos: "FWD" },
          { name: "Garba Bello", pos: "FWD" }, { name: "Suleiman Abdullahi", pos: "FWD" },
        ]},
        { id: "kan", name: "Kano Pillars", players: [
          { name: "Ibrahim Danjuma", pos: "GK" }, { name: "Sani Yusuf", pos: "GK" },
          { name: "Musa Abdullahi", pos: "DEF" }, { name: "Bello Garba", pos: "DEF" },
          { name: "Yakubu Sule", pos: "DEF" }, { name: "Usman Mohammed", pos: "DEF" },
          { name: "Ahmed Musa", pos: "MID" }, { name: "Shehu Abdullahi", pos: "MID" },
          { name: "Nura Mohammed", pos: "MID" }, { name: "Abubakar Lawal", pos: "MID" },
          { name: "Rabiu Ali", pos: "FWD" }, { name: "Nyima Nwagua", pos: "FWD" },
          { name: "Adamu Hassan", pos: "FWD" }, { name: "Mustapha Salisu", pos: "FWD" },
        ]},
        { id: "kwa", name: "Kwara United", players: [
          { name: "Adewale Adeyinka", pos: "GK" }, { name: "Nurudeen Mudathir", pos: "GK" },
          { name: "Isaiah Ejeh", pos: "DEF" }, { name: "Abubakar Garba", pos: "DEF" },
          { name: "Ezekiel Bassey", pos: "DEF" }, { name: "Samuel Ganda", pos: "DEF" },
          { name: "Jide Fatokun", pos: "MID" }, { name: "Ibrahim Ayinla", pos: "MID" },
          { name: "Kabir Balogun", pos: "MID" }, { name: "Samad Kadiri", pos: "MID" },
          { name: "Michael Ohanu", pos: "FWD" }, { name: "Wasiu Alalade", pos: "FWD" },
          { name: "Junior Lokosa", pos: "FWD" }, { name: "Stephen Jude", pos: "FWD" },
        ]},
        { id: "riv", name: "Rivers United", players: [
          { name: "Tamuno George", pos: "GK" }, { name: "Ebiye Precious", pos: "GK" },
          { name: "Sokari Davies", pos: "DEF" }, { name: "Ayo Briggs", pos: "DEF" },
          { name: "Tonye Hart", pos: "DEF" }, { name: "Boma George", pos: "DEF" },
          { name: "Nelson Esor", pos: "MID" }, { name: "Chijioke Akuneto", pos: "MID" },
          { name: "Moses Omoduemuke", pos: "MID" }, { name: "Joseph Onoja", pos: "MID" },
          { name: "Alex Oyowah", pos: "FWD" }, { name: "Bernard Ovoke", pos: "FWD" },
          { name: "Malachi Ohawume", pos: "FWD" }, { name: "Godwin Aguda", pos: "FWD" },
        ]},
        { id: "ben", name: "Bendel Insurance", players: [
          { name: "Amas Obasogie", pos: "GK" }, { name: "Joshua Ejeh", pos: "GK" },
          { name: "Efe Enabulele", pos: "DEF" }, { name: "Sunday Anyanwu", pos: "DEF" },
          { name: "Osaro Aghayere", pos: "DEF" }, { name: "Benjamin Tanimu", pos: "DEF" },
          { name: "Divine Nwachukwu", pos: "MID" }, { name: "Edo Moses", pos: "MID" },
          { name: "Ismael Seriki", pos: "MID" }, { name: "Depo Adedipe", pos: "MID" },
          { name: "Sarkin Abdallah", pos: "FWD" }, { name: "Junior Osaghae", pos: "FWD" },
          { name: "Austine Ogunye", pos: "FWD" }, { name: "Efe Igbinoba", pos: "FWD" },
        ]},
        { id: "warri", name: "Warri Wolves", players: [
          { name: "Chinedu Sunday", pos: "GK" }, { name: "Usman Mohammed", pos: "GK" },
          { name: "Tamuno Kalio", pos: "DEF" }, { name: "Efe Enabulele", pos: "DEF" },
          { name: "Kalu Orji", pos: "DEF" }, { name: "Uche John", pos: "DEF" },
          { name: "Kenechukwu Agu", pos: "MID" }, { name: "Onyeka Eze", pos: "MID" },
          { name: "Chukwudi Nwafor", pos: "MID" }, { name: "Ugochukwu Obi", pos: "MID" },
          { name: "Chidera Ezeh", pos: "FWD" }, { name: "Godwin Obaje", pos: "FWD" },
          { name: "Ifeanyi George", pos: "FWD" }, { name: "Emmanuel Daniel", pos: "FWD" },
        ]},
        { id: "dom", name: "Doma United", players: [
          { name: "Suleiman Adamu", pos: "GK" }, { name: "Bala Bello", pos: "GK" },
          { name: "Musa Ibrahim", pos: "DEF" }, { name: "Abubakar Sadiq", pos: "DEF" },
          { name: "Haruna Usman", pos: "DEF" }, { name: "Isaac Danjuma", pos: "DEF" },
          { name: "Mohammed Bello", pos: "MID" }, { name: "Abdulazeez Isah", pos: "MID" },
          { name: "Yakubu Sule", pos: "MID" }, { name: "Nnamdi Emmanuel", pos: "MID" },
          { name: "Chibuike Ohizu", pos: "FWD" }, { name: "Mubarak Said", pos: "FWD" },
          { name: "Sadiq Suleiman", pos: "FWD" }, { name: "Umar Abubakar", pos: "FWD" },
        ]},
        { id: "eny", name: "Enyimba", players: [
          { name: "Nathaniel Asibe", pos: "GK" }, { name: "Dare Dede", pos: "GK" },
          { name: "John Uche Akubueze", pos: "DEF" }, { name: "Pascal Eze", pos: "DEF" },
          { name: "Wisdom Obichere", pos: "DEF" }, { name: "Emeka Onyema", pos: "DEF" },
          { name: "Bonni Abubakar", pos: "MID" }, { name: "Umoh Hogan Ukpa", pos: "MID" },
          { name: "Bright Ihionu", pos: "MID" }, { name: "Daniel Simon", pos: "MID" },
          { name: "Samuel Okechukwu", pos: "FWD" }, { name: "Kingsley Maduforo", pos: "FWD" },
          { name: "Stanley Dimgba", pos: "FWD" }, { name: "Chidiebere Nnachi", pos: "FWD" },
        ]},
        { id: "iko", name: "Ikorodu City", players: [
          { name: "Chikamso Amaefula", pos: "GK" }, { name: "James Ekebuike", pos: "GK" },
          { name: "Alex Oyowah", pos: "DEF" }, { name: "Ubong Williams", pos: "DEF" },
          { name: "Sokari Davies", pos: "DEF" }, { name: "Ayo Briggs", pos: "DEF" },
          { name: "Nelson Esor", pos: "MID" }, { name: "Chijioke Akuneto", pos: "MID" },
          { name: "Moses Omoduemuke", pos: "MID" }, { name: "Joseph Onoja", pos: "MID" },
          { name: "Alex Oyowah", pos: "FWD" }, { name: "Bernard Ovoke", pos: "FWD" },
          { name: "Malachi Ohawume", pos: "FWD" }, { name: "Godwin Aguda", pos: "FWD" },
        ]},
        { id: "nas", name: "Nasarawa United", players: [
          { name: "Ishola Saheed", pos: "GK" }, { name: "Musa Aliyu", pos: "GK" },
          { name: "Bala Mohammed", pos: "DEF" }, { name: "Abbas Adamu", pos: "DEF" },
          { name: "Idris Aliyu", pos: "DEF" }, { name: "Sunday Akinmoladun", pos: "DEF" },
          { name: "Umar Idris", pos: "MID" }, { name: "Alhassan Ibrahim", pos: "MID" },
          { name: "Najeeb Yakubu", pos: "MID" }, { name: "Jonas Emmanuel", pos: "MID" },
          { name: "Shamsudeen Hashim", pos: "FWD" }, { name: "Abba Umar", pos: "FWD" },
          { name: "Ezekiel Onah", pos: "FWD" }, { name: "Ibrahim Adamu", pos: "FWD" },
        ]},
        { id: "nig", name: "Niger Tornadoes", players: [
          { name: "Ishola Saheed", pos: "GK" }, { name: "Musa Aliyu", pos: "GK" },
          { name: "Bala Mohammed", pos: "DEF" }, { name: "Abbas Adamu", pos: "DEF" },
          { name: "Idris Aliyu", pos: "DEF" }, { name: "Sunday Akinmoladun", pos: "DEF" },
          { name: "Umar Idris", pos: "MID" }, { name: "Alhassan Ibrahim", pos: "MID" },
          { name: "Najeeb Yakubu", pos: "MID" }, { name: "Jonas Emmanuel", pos: "MID" },
          { name: "Shamsudeen Hashim", pos: "FWD" }, { name: "Abba Umar", pos: "FWD" },
          { name: "Ezekiel Onah", pos: "FWD" }, { name: "Ibrahim Adamu", pos: "FWD" },
        ]},
        { id: "akw", name: "Akwa United", players: [
          { name: "Adebayo Ojo", pos: "GK" }, { name: "Emmanuel Iwu", pos: "GK" },
          { name: "James Daniel", pos: "DEF" }, { name: "Etim Essien", pos: "DEF" },
          { name: "Uche Okafor", pos: "DEF" }, { name: "Friday Ubong", pos: "DEF" },
          { name: "Aniefiok Godwin", pos: "MID" }, { name: "Mfon Udoh", pos: "MID" },
          { name: "Cyril Olisema", pos: "MID" }, { name: "Samuel Mathias", pos: "MID" },
          { name: "Akpan Bassey", pos: "FWD" }, { name: "Ubong Friday", pos: "FWD" },
          { name: "Ndifreke Effiong", pos: "FWD" }, { name: "Emmanuel Ayaosi", pos: "FWD" },
        ]},
        { id: "spo", name: "Sporting Lagos", players: [
          { name: "Obike Opara", pos: "GK" }, { name: "Chibueze Osuchukwu", pos: "GK" },
          { name: "Olawale Ojo", pos: "DEF" }, { name: "Tobi Adebayo", pos: "DEF" },
          { name: "Chukwuemeka Nwosu", pos: "DEF" }, { name: "Ahmed Ibrahim", pos: "DEF" },
          { name: "Kehinde Adeyemi", pos: "MID" }, { name: "Onyeka Okonkwo", pos: "MID" },
          { name: "Damilare Ogunleye", pos: "MID" }, { name: "Samuel Odukoya", pos: "MID" },
          { name: "Promise Awosanmi", pos: "FWD" }, { name: "Adebayo Adewale", pos: "FWD" },
          { name: "Chidera Ezeh", pos: "FWD" }, { name: "Ifeanyi Ubah", pos: "FWD" },
        ]},
        { id: "bay", name: "Bayelsa United", players: [
          { name: "Edwin Okon", pos: "GK" }, { name: "Peremobowei Soun", pos: "GK" },
          { name: "Tombiri Ateke", pos: "DEF" }, { name: "Iniobong Umana", pos: "DEF" },
          { name: "Tarila Okon", pos: "DEF" }, { name: "Boma Amgbare", pos: "DEF" },
          { name: "Ebiye Ogoli", pos: "MID" }, { name: "Timi Ozornwafor", pos: "MID" },
          { name: "Preye Sele", pos: "MID" }, { name: "Samuel Oyedeji", pos: "MID" },
          { name: "Robert Mizo", pos: "FWD" }, { name: "Eletu Oguntuase", pos: "FWD" },
          { name: "Ernest Governor", pos: "FWD" }, { name: "Ikechukwu Nwannukwu", pos: "FWD" },
        ]},
        { id: "barau", name: "Barau FC", players: [
          { name: "Suleiman Adamu", pos: "GK" }, { name: "Bala Bello", pos: "GK" },
          { name: "Musa Ibrahim", pos: "DEF" }, { name: "Abubakar Sadiq", pos: "DEF" },
          { name: "Haruna Usman", pos: "DEF" }, { name: "Isaac Danjuma", pos: "DEF" },
          { name: "Mohammed Bello", pos: "MID" }, { name: "Abdulazeez Isah", pos: "MID" },
          { name: "Yakubu Sule", pos: "MID" }, { name: "Nnamdi Emmanuel", pos: "MID" },
          { name: "Chibuike Ohizu", pos: "FWD" }, { name: "Mubarak Said", pos: "FWD" },
          { name: "Sadiq Suleiman", pos: "FWD" }, { name: "Umar Abubakar", pos: "FWD" },
        ]},
        { id: "gom", name: "Gombe United", players: [
          { name: "Bello Jibril", pos: "GK" }, { name: "Sani Garba", pos: "GK" },
          { name: "Ahmed Abdul", pos: "DEF" }, { name: "Musa Adamu", pos: "DEF" },
          { name: "Ibrahim Hassan", pos: "DEF" }, { name: "Yusuf Bello", pos: "DEF" },
          { name: "Sule Mohammed", pos: "MID" }, { name: "Danjuma Aliyu", pos: "MID" },
          { name: "Umar Farouk", pos: "MID" }, { name: "Isah Adamu", pos: "MID" },
          { name: "Rabiu Sani", pos: "FWD" }, { name: "Abba Umar", pos: "FWD" },
          { name: "Garba Yakubu", pos: "FWD" }, { name: "Suleiman Usman", pos: "FWD" },
        ]},
        { id: "sun", name: "Sunshine Stars", players: [
          { name: "Mustapha Lawal", pos: "GK" }, { name: "David Ariyo", pos: "GK" },
          { name: "Waheed Adebayo", pos: "DEF" }, { name: "Seun Olulayo", pos: "DEF" },
          { name: "Anthony Omaka", pos: "DEF" }, { name: "Uche Oduah", pos: "DEF" },
          { name: "Fuad Ekelojuoti", pos: "MID" }, { name: "Ola Adeyemo", pos: "MID" },
          { name: "Tunde Adeniji", pos: "MID" }, { name: "Ezekiel Thompson", pos: "MID" },
          { name: "Sadeeq Yusuf", pos: "FWD" }, { name: "Chinedu Nwosu", pos: "FWD" },
          { name: "Emeka Obioma", pos: "FWD" }, { name: "Promise Awosanmi", pos: "FWD" },
        ]},
        { id: "hea", name: "Heartland FC", players: [
          { name: "Chisom Chikatara", pos: "GK" }, { name: "Ebele Obi", pos: "GK" },
          { name: "Chinedu Efugh", pos: "DEF" }, { name: "Nnamdi Nwabuike", pos: "DEF" },
          { name: "Kingsley Ozioma", pos: "DEF" }, { name: "Emeka Onyekachi", pos: "DEF" },
          { name: "Chukwudi Nwafor", pos: "MID" }, { name: "Onyekachi Nwafor", pos: "MID" },
          { name: "Cletus Emeka", pos: "MID" }, { name: "Ifeanyi Matthew", pos: "MID" },
          { name: "Chidi Nwaneri", pos: "FWD" }, { name: "Emeka Ogbugh", pos: "FWD" },
          { name: "Nnamdi Ohanu", pos: "FWD" }, { name: "Uche Nwofor", pos: "FWD" },
        ]},
        { id: "abi", name: "Abia Warriors", players: [
          { name: "Uche Okafor", pos: "GK" }, { name: "Chinedu Anozie", pos: "GK" },
          { name: "Kalu Nweke", pos: "DEF" }, { name: "Chinedu Efugh", pos: "DEF" },
          { name: "Emeka Onyema", pos: "DEF" }, { name: "Nnamdi Nwabuike", pos: "DEF" },
          { name: "Daniel Simon", pos: "MID" }, { name: "Ifeanyi Ihemekwele", pos: "MID" },
          { name: "Chukwudi Nwafor", pos: "MID" }, { name: "Onyeka Eze", pos: "MID" },
          { name: "Chinedu Nwosu", pos: "FWD" }, { name: "Kingsley Maduforo", pos: "FWD" },
          { name: "Stanley Dimgba", pos: "FWD" }, { name: "Chidiebere Nnachi", pos: "FWD" },
        ]},
      ],
    },

    cafcl: {
      id: "cafcl", name: "CAF Champions League", region: "Africa", type: "continental", cols: 48, rows: 100,
      clubs: [
        { id: "msu", name: "Mamelodi Sundowns", players: [
          { name: "Ronwen Williams", pos: "GK" }, { name: "Denis Onyango", pos: "GK" },
          { name: "Khuliso Mudau", pos: "DEF" }, { name: "Mothobi Mvala", pos: "DEF" },
          { name: "Grant Kekana", pos: "DEF" }, { name: "Aubrey Modiba", pos: "DEF" },
          { name: "Teboho Mokoena", pos: "MID" }, { name: "Themba Zwane", pos: "MID" },
          { name: "Marcelo Allende", pos: "MID" }, { name: "Neo Maema", pos: "MID" },
          { name: "Peter Shalulile", pos: "FWD" }, { name: "Lucas Ribeiro", pos: "FWD" },
          { name: "Iqraam Rayners", pos: "FWD" }, { name: "Rivaldo Coetzee", pos: "FWD" },
        ]},
        { id: "orl", name: "Orlando Pirates", players: [
          { name: "Sipho Chaine", pos: "GK" }, { name: "Melusi Buthelezi", pos: "GK" },
          { name: "Innocent Maela", pos: "DEF" }, { name: "Tapelo Xoki", pos: "DEF" },
          { name: "Nkosinathi Sibisi", pos: "DEF" }, { name: "Thabiso Monyane", pos: "DEF" },
          { name: "Makhehlene Makhaula", pos: "MID" }, { name: "Patrick Maswanganyi", pos: "MID" },
          { name: "Themba Zwane", pos: "MID" }, { name: "Relebohile Mofokeng", pos: "MID" },
          { name: "Tshegofatso Mabasa", pos: "FWD" }, { name: "Evidence Makgopa", pos: "FWD" },
          { name: "Iqraam Rayners", pos: "FWD" }, { name: "Zakhele Lepasa", pos: "FWD" },
        ]},
        { id: "zam", name: "Zamalek", players: [
          { name: "Mohamed Awad", pos: "GK" }, { name: "Mahmoud El Zanfaly", pos: "GK" },
          { name: "Omar Gaber", pos: "DEF" }, { name: "Mahmoud Hamdy El Wensh", pos: "DEF" },
          { name: "Hussein El Sayed", pos: "DEF" }, { name: "Ahmed Fatouh", pos: "DEF" },
          { name: "Nabil Emad Donga", pos: "MID" }, { name: "Mohamed Shehata", pos: "MID" },
          { name: "Youssef Obama", pos: "MID" }, { name: "Ahmed Sayed Zizo", pos: "MID" },
          { name: "Mostafa Shalaby", pos: "FWD" }, { name: "Nasser Mansi", pos: "FWD" },
          { name: "Seif El Jaziri", pos: "FWD" }, { name: "Shikabala", pos: "FWD" },
        ]},
        { id: "pyr", name: "Pyramids FC", players: [
          { name: "Ahmed El Shenawy", pos: "GK" }, { name: "Sherif Ekramy", pos: "GK" },
          { name: "Ali Gabr", pos: "DEF" }, { name: "Ahmed Samy", pos: "DEF" },
          { name: "Mohamed Hamdy", pos: "DEF" }, { name: "Osama Galal", pos: "DEF" },
          { name: "Mohamed El Chibi", pos: "MID" }, { name: "Walid El Karti", pos: "MID" },
          { name: "Mostafa Fathi", pos: "MID" }, { name: "Ibrahim Adel", pos: "MID" },
          { name: "Fiston Mayele", pos: "FWD" }, { name: "Marwan Hamdy", pos: "FWD" },
          { name: "Dodo", pos: "FWD" }, { name: "Youssef Obama", pos: "FWD" },
        ]},
        { id: "est", name: "Espérance de Tunis", players: [
          { name: "Moez Ben Cherifia", pos: "GK" }, { name: "Amen Allah Memmiche", pos: "GK" },
          { name: "Mohamed Amine Tougai", pos: "DEF" }, { name: "Yassine Meriah", pos: "DEF" },
          { name: "Ali Abdi", pos: "DEF" }, { name: "Hamdi Nagguez", pos: "DEF" },
          { name: "Ghaylene Chaalali", pos: "MID" }, { name: "Fousseyni Coulibaly", pos: "MID" },
          { name: "Mohamed Ali Ben Romdhane", pos: "MID" }, { name: "Anayo Iwuala", pos: "MID" },
          { name: "Youssef Msakni", pos: "FWD" }, { name: "Rodrigo Rodrigues", pos: "FWD" },
          { name: "Kingsley Eduwo", pos: "FWD" }, { name: "Bilel Mejri", pos: "FWD" },
        ]},
        { id: "crb", name: "CR Belouizdad", players: [
          { name: "Alexis Guendouz", pos: "GK" }, { name: "Toufik Moussaoui", pos: "GK" },
          { name: "Mokhtar Belkhiter", pos: "DEF" }, { name: "Chouaib Keddad", pos: "DEF" },
          { name: "Zineddine Belaid", pos: "DEF" }, { name: "Hocine Benayad", pos: "DEF" },
          { name: "Zakaria Draoui", pos: "MID" }, { name: "Adel Bouguerra", pos: "MID" },
          { name: "Hicham Boudaoui", pos: "MID" }, { name: "Abderrahmane Meziane", pos: "MID" },
          { name: "Karim Aribi", pos: "FWD" }, { name: "Lamine Abid", pos: "FWD" },
          { name: "Bouly Junior Sambou", pos: "FWD" }, { name: "Ahmed Kendouci", pos: "FWD" },
        ]},
         { id: "mca", name: "MC Alger", players: [
          { name: "Oussama Benbot", pos: "GK" }, { name: "Farid Chaal", pos: "GK" },
          { name: "Ayoub Abdellaoui", pos: "DEF" }, { name: "Mohamed Azzi", pos: "DEF" },
          { name: "Réda Halaïmia", pos: "DEF" }, { name: "Miloud Rebiai", pos: "DEF" },
          { name: "Sofiane Bendebka", pos: "MID" }, { name: "Zakaria Draoui", pos: "MID" },
          { name: "Ali Haroun", pos: "MID" }, { name: "Youcef Belaili", pos: "MID" },
          { name: "Andy Delort", pos: "FWD" }, { name: "Bilal Brahimi", pos: "FWD" },
          { name: "Mohamed Bangoura", pos: "FWD" }, { name: "Zakaria Naidji", pos: "FWD" },
        ]},
      ],
    },

    cafcc: {
      id: "cafcc", name: "CAF Confederation Cup", region: "Africa", type: "continental", cols: 48, rows: 100,
      clubs: [
        { id: "ahl", name: "Al Ahly", players: [
          { name: "Mohamed El Shenawy", pos: "GK" }, { name: "Mohamed Seha", pos: "GK" },
          { name: "Karim Fouad", pos: "DEF" }, { name: "Yasser Ibrahim", pos: "DEF" },
          { name: "Achraf Dari", pos: "DEF" }, { name: "Yassin Marei", pos: "DEF" },
          { name: "Akram Tawfik", pos: "MID" }, { name: "Ahmed Eid", pos: "MID" },
          { name: "Emam Ashour", pos: "MID" }, { name: "Mohamed Magdy Afsha", pos: "MID" },
          { name: "Hussein El Shahat", pos: "FWD" }, { name: "Marwan Otaka", pos: "FWD" },
          { name: "Taher Mohamed Taher", pos: "FWD" }, { name: "Ahmed Abdel Kader", pos: "FWD" },
        ]},
        { id: "zed", name: "ZED FC", players: [
          { name: "Mohamed Sobhi", pos: "GK" }, { name: "Ali Lotfi", pos: "GK" },
          { name: "Mohamed Ismail", pos: "DEF" }, { name: "Ahmed Ayman", pos: "DEF" },
          { name: "Mostafa El Aash", pos: "DEF" }, { name: "Ali Elfil", pos: "DEF" },
          { name: "Ahmed Adel", pos: "MID" }, { name: "Mostafa Saad", pos: "MID" },
          { name: "Mahmoud Bolbol", pos: "MID" }, { name: "Rasheed Ahmed", pos: "MID" },
          { name: "Shady Hussein", pos: "FWD" }, { name: "Dilson", pos: "FWD" },
          { name: "Moustafa Ziko", pos: "FWD" }, { name: "Amr El Sisi", pos: "FWD" },
        ]},
        { id: "rsb", name: "Renaissance Berkane", players: [
          { name: "Hamza Hamiani", pos: "GK" }, { name: "Amine El Ouaad", pos: "GK" },
          { name: "Issoufou Dayo", pos: "DEF" }, { name: "Adil Tahif", pos: "DEF" },
          { name: "Hamza Regragui", pos: "DEF" }, { name: "Yassine Labhiri", pos: "DEF" },
          { name: "Larbi Naji", pos: "MID" }, { name: "Mohamed El Mourabit", pos: "MID" },
          { name: "Bilal El Ouadghiri", pos: "MID" }, { name: "Mateus Criciúma", pos: "MID" },
          { name: "Youssef Zghoudi", pos: "FWD" }, { name: "Chadrack Lukombe", pos: "FWD" },
          { name: "Ayoub Khairi", pos: "FWD" }, { name: "Paul Bassène", pos: "FWD" },
        ]},
      ],
    },

    egypt_pl: {
      id: "egypt_pl", name: "Egyptian Premier League", region: "Africa", type: "domestic", cols: 30, rows: 100,
      clubs: [
        { id: "zam", name: "Zamalek", players: [
          { name: "Mohamed Awad", pos: "GK" }, { name: "Mahmoud El Zanfaly", pos: "GK" },
          { name: "Omar Gaber", pos: "DEF" }, { name: "Mahmoud Hamdy El Wensh", pos: "DEF" },
          { name: "Hussein El Sayed", pos: "DEF" }, { name: "Ahmed Fatouh", pos: "DEF" },
          { name: "Nabil Emad Donga", pos: "MID" }, { name: "Mohamed Shehata", pos: "MID" },
          { name: "Youssef Obama", pos: "MID" }, { name: "Ahmed Sayed Zizo", pos: "MID" },
          { name: "Mostafa Shalaby", pos: "FWD" }, { name: "Nasser Mansi", pos: "FWD" },
          { name: "Seif El Jaziri", pos: "FWD" }, { name: "Shikabala", pos: "FWD" },
        ]},
        { id: "pyr", name: "Pyramids FC", players: [
          { name: "Ahmed El Shenawy", pos: "GK" }, { name: "Sherif Ekramy", pos: "GK" },
          { name: "Ali Gabr", pos: "DEF" }, { name: "Ahmed Samy", pos: "DEF" },
          { name: "Mohamed Hamdy", pos: "DEF" }, { name: "Osama Galal", pos: "DEF" },
          { name: "Mohamed El Chibi", pos: "MID" }, { name: "Walid El Karti", pos: "MID" },
          { name: "Mostafa Fathi", pos: "MID" }, { name: "Ibrahim Adel", pos: "MID" },
          { name: "Fiston Mayele", pos: "FWD" }, { name: "Marwan Hamdy", pos: "FWD" },
          { name: "Dodo", pos: "FWD" }, { name: "Youssef Obama", pos: "FWD" },
        ]},
        { id: "ahl", name: "Al Ahly", players: [
          { name: "Mohamed El Shenawy", pos: "GK" }, { name: "Mohamed Seha", pos: "GK" },
          { name: "Karim Fouad", pos: "DEF" }, { name: "Yasser Ibrahim", pos: "DEF" },
          { name: "Achraf Dari", pos: "DEF" }, { name: "Yassin Marei", pos: "DEF" },
          { name: "Akram Tawfik", pos: "MID" }, { name: "Ahmed Eid", pos: "MID" },
          { name: "Emam Ashour", pos: "MID" }, { name: "Mohamed Magdy Afsha", pos: "MID" },
          { name: "Hussein El Shahat", pos: "FWD" }, { name: "Marwan Otaka", pos: "FWD" },
          { name: "Taher Mohamed Taher", pos: "FWD" }, { name: "Ahmed Abdel Kader", pos: "FWD" },
        ]},
        { id: "masry", name: "Al Masry", players: [
          { name: "Essam Tharwat", pos: "GK" }, { name: "Mahmoud Gad", pos: "GK" },
          { name: "Ahmed Alaa", pos: "DEF" }, { name: "Baher El Mohamady", pos: "DEF" },
          { name: "Amr Moussa", pos: "DEF" }, { name: "Karim El Eraki", pos: "DEF" },
          { name: "Mido Gaber", pos: "MID" }, { name: "Youssef El Gohary", pos: "MID" },
          { name: "Salah Mohsen", pos: "MID" }, { name: "Ahmed Refaat", pos: "MID" },
          { name: "Fakhreddine Ben Youssef", pos: "FWD" }, { name: "Salah Ashour", pos: "FWD" },
          { name: "Karim Bambo", pos: "FWD" }, { name: "Hussein Ragab", pos: "FWD" },
        ]},
      ],
    },

    sa_psl: {
      id: "sa_psl", name: "South African Premier Division", region: "Africa", type: "domestic", cols: 30, rows: 100,
      clubs: [
        { id: "msu", name: "Mamelodi Sundowns", players: [
          { name: "Ronwen Williams", pos: "GK" }, { name: "Denis Onyango", pos: "GK" },
          { name: "Khuliso Mudau", pos: "DEF" }, { name: "Mothobi Mvala", pos: "DEF" },
          { name: "Grant Kekana", pos: "DEF" }, { name: "Aubrey Modiba", pos: "DEF" },
          { name: "Teboho Mokoena", pos: "MID" }, { name: "Themba Zwane", pos: "MID" },
          { name: "Marcelo Allende", pos: "MID" }, { name: "Neo Maema", pos: "MID" },
          { name: "Peter Shalulile", pos: "FWD" }, { name: "Lucas Ribeiro", pos: "FWD" },
          { name: "Iqraam Rayners", pos: "FWD" }, { name: "Rivaldo Coetzee", pos: "FWD" },
        ]},
        { id: "orl", name: "Orlando Pirates", players: [
          { name: "Sipho Chaine", pos: "GK" }, { name: "Melusi Buthelezi", pos: "GK" },
          { name: "Innocent Maela", pos: "DEF" }, { name: "Tapelo Xoki", pos: "DEF" },
          { name: "Nkosinathi Sibisi", pos: "DEF" }, { name: "Thabiso Monyane", pos: "DEF" },
          { name: "Makhehlene Makhaula", pos: "MID" }, { name: "Patrick Maswanganyi", pos: "MID" },
          { name: "Themba Zwane", pos: "MID" }, { name: "Relebohile Mofokeng", pos: "MID" },
          { name: "Tshegofatso Mabasa", pos: "FWD" }, { name: "Evidence Makgopa", pos: "FWD" },
          { name: "Iqraam Rayners", pos: "FWD" }, { name: "Zakhele Lepasa", pos: "FWD" },
        ]},
      ],
    },

    botola: {
      id: "botola", name: "Botola Pro", region: "Africa", type: "domestic", cols: 30, rows: 100,
      clubs: [
        { id: "wyd", name: "Wydad Casablanca", players: [
          { name: "Ahmed Reda Tagnaouti", pos: "GK" }, { name: "Youssef El Motie", pos: "GK" },
          { name: "Yahya Attiyat Allah", pos: "DEF" }, { name: "Amine Farhane", pos: "DEF" },
          { name: "Cheick Comara", pos: "DEF" }, { name: "Ayoub El Amloud", pos: "DEF" },
          { name: "Yahya Jabrane", pos: "MID" }, { name: "Ismail Haddad", pos: "MID" },
          { name: "Oussama Falouh", pos: "MID" }, { name: "Zakaria Draoui", pos: "MID" },
          { name: "Ayoub El Kaabi", pos: "FWD" }, { name: "Badie Aouk", pos: "FWD" },
          { name: "Mounir El Haddadi", pos: "FWD" }, { name: "Zouhair El Moutaraji", pos: "FWD" },
        ]},
        { id: "raja", name: "Raja Casablanca", players: [
          { name: "Anas Zniti", pos: "GK" }, { name: "Marouane Fakhr", pos: "GK" },
          { name: "Abdellah Khafifi", pos: "DEF" }, { name: "Marouane Hadhoudi", pos: "DEF" },
          { name: "Omar Boutayeb", pos: "DEF" }, { name: "Abdeljalil Jbira", pos: "DEF" },
          { name: "Mohamed Zrida", pos: "MID" }, { name: "Zakaria El Wardi", pos: "MID" },
          { name: "Mohamed Azrida", pos: "MID" }, { name: "Yousri Bouzok", pos: "MID" },
          { name: "Yousra Ben Guitoun", pos: "FWD" }, { name: "Hamza Khabba", pos: "FWD" },
          { name: "Adam Ennafati", pos: "FWD" }, { name: "Nahiri", pos: "FWD" },
        ]},
      ],
    },
  },
};

// ═══════════════════════════════════════════════════════
//  HELPERS
// ═══════════════════════════════════════════════════════
OpenBox.FantasyRegistry.listTournaments = function () {
  return Object.values(OpenBox.FantasyRegistry.tournaments).map(t => ({
    id: t.id, name: t.name, region: t.region, type: t.type,
    club_count: t.clubs.length, cols: t.cols, rows: t.rows,
  }));
};

OpenBox.FantasyRegistry.getTournament = function (id) {
  const t = OpenBox.FantasyRegistry.tournaments[id];
  if (!t) return null;
  return { ...t, clubs: t.clubs.map((c, col) => ({ ...c, col })) };
};

OpenBox.FantasyRegistry.playersForClub = function (tournamentId, clubId) {
  const t = OpenBox.FantasyRegistry.tournaments[tournamentId];
  if (!t) return [];
  const club = t.clubs.find(c => c.id === clubId);
  if (!club) return [];
  return club.players.map((p, i) => ({
    id: `${tournamentId}:${clubId}:${i}`,
    name: p.name,
    position: p.pos,
    club_id: clubId,
    tournament_id: tournamentId,
    price: priceFor(p),
  }));
};

function priceFor(p) {
  const base = { GK: 50, DEF: 70, MID: 90, FWD: 110 }[p.pos] || 50;
  const hash = (p.name || "").split("").reduce((s, c) => s + c.charCodeAt(0), 0);
  return Math.min(500, base + (hash % 80));
} 