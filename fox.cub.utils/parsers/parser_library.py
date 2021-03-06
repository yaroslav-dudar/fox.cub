
class SoccerPunterLib:
    championship = [
        "/season/16211/England-Championship-2019-2020"
    ]

    epl = [
        "/season/16036/England-Premier-League-2019-2020"
    ]

    bundesliga = ["/season/16264/Germany-Bundesliga-2019-2020"]

    bundesliga2 = ["/season/16263/Germany-2-Bundesliga-2019-2020"]

    bundesliga3 = ["/season/16304/Germany-3-Liga-2019-2020"]

    efl_league1 = [
        "/season/16210/England-League-One-2019-2020"
    ]

    efl_league2 = [
        "/season/16212/England-League-Two-2019-2020"
    ]

    laliga = [
        "/season/16326/Spain-La-Liga-2019-2020"
    ]

    segunda = ["/Spain/Segunda-División-{0}-{1}".format(year, year+1)
        for year in range(1996, 2020)]

    serie_a = ["/season/16415/Italy-Serie-A-2019-2020"]

    serie_b = ["/Italy/Serie-B-{0}-{1}".format(year, year+1)
        for year in range(1993, 2020)]

    serie_c = ["/Italy/Serie-C-{0}-{1}".format(year, year+1)
        for year in range(1999, 2020)]

    france_ligue1 = ["/France/Ligue-1-{0}-{1}".format(year, year+1)
        for year in range(1994, 2019)]

    france_ligue2 = ["/France/Ligue-2-{0}-{1}".format(year, year+1)
        for year in range(1994, 2020)]

    belgium_div1 = ["/Belgium/First-Division-A-{0}-{1}".format(year, year+1)
        for year in range(1995, 2019)]

    eradivisie = ["/Netherlands/Eredivisie-{0}-{1}".format(year, year+1)
        for year in range(1993, 2020)]

    eereste_divicie = ["/Netherlands/Eerste-Divisie-{0}-{1}".format(year, year+1)
        for year in range(1996, 2020)]

    swiss_super_league = ["/Switzerland/Super-League-{0}-{1}".format(year, year+1)
        for year in range(1994, 2020)]

    swiss_chalange_league = ["/Switzerland/Challenge-League-{0}-{1}".format(year, year+1)
        for year in range(1999, 2020)]

    slovakia_super_liga = ["/Slovakia/Super-Liga-{0}-{1}".format(year, year+1)
        for year in range(2002, 2019)]

    norway_eliteserien = [
        "/season/15581/Norway-Eliteserien-2019",
        "/season/11983/Norway-Eliteserien-2018",
        "/season/804/Norway-Eliteserien-2017",
        "/season/1817/Norway-Eliteserien-2016",
        "/season/1816/Norway-Eliteserien-2015",
        "/season/1815/Norway-Eliteserien-2014",
        "/season/1814/Norway-Eliteserien-2013",
        "/season/3461/Norway-Eliteserien-2012",
        "/season/1813/Norway-Eliteserien-2011",
        "/season/1812/Norway-Eliteserien-2010",
        "/season/1811/Norway-Eliteserien-2009",
        "/season/1810/Norway-Eliteserien-2008",
        "/season/1809/Norway-Eliteserien-2007",
        "/season/1808/Norway-Eliteserien-2006",
        "/season/1807/Norway-Eliteserien-2005"
    ]

    denmark_division1 = ["/Denmark/1st-Division-{0}-{1}".format(year, year+1)
        for year in range(1997, 2019)]

    czech_liga = ["/Czech-Republic/Czech-Liga-{0}-{1}".format(year, year+1)
        for year in range(1994, 2020)]

    portugal_liga = ["/Portugal/Primeira-Liga-{0}-{1}".format(year, year+1)
        for year in range(1994, 2020)]

    mls = ["/USA/MLS-{0}".format(year)
        for year in range(2000, 2020)]

    austria_bundesliga = ["/Austria/Bundesliga-{0}-{1}".format(year, year+1)
        for year in range(1993, 2019)]

    scotland_premiership = ["/Scotland/Premiership-{0}-{1}".format(year, year+1)
        for year in range(1994, 2019)]

    turkey_1lig = ["/Turkey/1.-Lig-{0}-{1}".format(year, year+1)
        for year in range(2005, 2020)]

    denmark_superlig = [
        "/season/16020/Denmark-Superliga-2019-2020",
        "/season/12919/Denmark-Superliga-2018-2019",
        "/season/6361/Denmark-Superliga-2017-2018",
        "/season/759/Denmark-Superliga-2016-2017",
        "/season/1286/Denmark-Superliga-2015-2016",
        "/season/1282/Denmark-Superliga-2014-2015",
        "/season/1281/Denmark-Superliga-2013-2014",
        "/season/1280/Denmark-Superliga-2012-2013",
        "/season/1279/Denmark-Superliga-2011-2012",
        "/season/1278/Denmark-Superliga-2010-2011",
        "/season/1277/Denmark-Superliga-2009-2010",
        "/season/1276/Denmark-Superliga-2008-2009",
        "/season/1275/Denmark-Superliga-2007-2008",
        "/season/1274/Denmark-Superliga-2006-2007",
        "/season/1273/Denmark-Superliga-2005-2006"
    ]

    super_lig = [
        "/season/13056/Turkey-Super-Lig-2018-2019",
        "/season/8243/Turkey-Super-Lig-2017-2018",
        "/season/882/Turkey-Super-Lig-2016-2017",
        "/season/2160/Turkey-Super-Lig-2015-2016",
        "/season/2159/Turkey-Super-Lig-2014-2015",
        "/season/2158/Turkey-Super-Lig-2013-2014",
        "/season/2157/Turkey-Super-Lig-2012-2013",
        "/season/2156/Turkey-Super-Lig-2011-2012",
        "/season/2155/Turkey-Super-Lig-2010-2011",
        "/season/2154/Turkey-Super-Lig-2009-2010",
        "/season/2153/Turkey-Super-Lig-2008-2009",
        "/season/2152/Turkey-Super-Lig-2007-2008",
        "/season/2151/Turkey-Super-Lig-2006-2007",
        "/season/2150/Turkey-Super-Lig-2005-2006"
    ]

    j_league = [
        "/season/15675/Japan-J-League-2019",
        "/season/12144/Japan-J-League-2018",
        "/season/977/Japan-J-League-2017",
        "/season/3112/Japan-J-League-2016",
        "/season/3108/Japan-J-League-2015",
        "/season/3107/Japan-J-League-2014",
        "/season/3106/Japan-J-League-2013",
        "/season/3105/Japan-J-League-2012",
        "/season/3104/Japan-J-League-2011",
        "/season/3103/Japan-J-League-2010",
        "/season/3102/Japan-J-League-2009",
        "/season/3101/Japan-J-League-2008",
        "/season/3100/Japan-J-League-2007",
        "/season/3099/Japan-J-League-2006",
        "/season/3098/Japan-J-League-2005"
    ]

    eu_qualification = [
        "/Europe/EC-Qualification-2012-Poland-Ukraine/results",
        "/Europe/EC-Qualification-2016-France",
        "/Europe/EC-Qualification-2008-Austria-Switzerland",
        "/Europe/EC-Qualification-2004-Portugal",
        "/Europe/EC-Qualification-2000-Netherlands-Belgium",
        "/Europe/EC-Qualification-1996-England",
        "/Europe/EC-Qualification-1992-Sweden",
        "/Europe/EC-Qualification-1988-Germany",
        "/Europe/EC-Qualification-1984-France",

        "/Europe/WC-Qualification-Europe-2018-Russia",
        "/Europe/WC-Qualification-Europe-2014-Brazil",
        "/Europe/WC-Qualification-Europe-2010-South-Africa",
        "/Europe/WC-Qualification-Europe-2006-Germany",
        "/Europe/WC-Qualification-Europe-2002-Korea-Rep-Japan",
        "/Europe/WC-Qualification-Europe-1998-France",
        "/Europe/WC-Qualification-Europe-1994-USA"
    ]

    eu_championship = [
        "/Europe/European-Championship-2016-France",
        "/Europe/European-Championship-2012-Poland-Ukraine",
        "/Europe/European-Championship-2008-Austria-Switzerland",
        "/Europe/European-Championship-2004-Portugal",
        "/Europe/European-Championship-2000-Netherlands-Belgium",
        "/Europe/European-Championship-1996-England",
        "/Europe/European-Championship-1992-Sweden",
        "/Europe/European-Championship-1988-Germany",
        "/Europe/European-Championship-1984-France"
    ]

    sa_qualification = [
        "/South-America/WC-Qualification-South-America-2018-Russia",
        "/South-America/WC-Qualification-South-America-2014-Brazil",
        "/South-America/WC-Qualification-South-America-2010-South-Africa",
        "/South-America/WC-Qualification-South-America-2006-Germany",
        "/South-America/WC-Qualification-South-America-2002-Korea-Rep-Japan"
    ]

    copa_america = [
        "/South-America/Copa-America-2016-USA",
        "/South-America/Copa-America-2015-Chile",
        "/South-America/Copa-America-2011-Argentina",
        "/South-America/Copa-America-2007-Venezuela",
        "/South-America/Copa-America-2004-Peru",
        "/South-America/Copa-America-2001-Colombia",
        "/South-America/Copa-America-1999-Paraguay",
        "/South-America/Copa-America-1997-Bolivia",
        "/South-America/Copa-America-1995-Uruguay"
    ]

    africa_qualification = [
        "/Africa/WC-Qualification-Africa-2018-Russia",
        "/Africa/WC-Qualification-Africa-2014-Brazil",
        "/Africa/WC-Qualification-Africa-2010-South-Africa",
        "/Africa/WC-Qualification-Africa-2006-Germany",
        "/Africa/WC-Qualification-Africa-2002-Korea-Rep-Japan"
    ]

    africa_cup = [
        "/Africa/Africa-Cup-of-Nations-2017-Gabon",
        "/Africa/Africa-Cup-of-Nations-2015-Equatorial-Guinea",
        "/Africa/Africa-Cup-of-Nations-2013-South-Africa",
        "/Africa/Africa-Cup-of-Nations-2012-Equatorial-Guinea-Gabon",
        "/Africa/Africa-Cup-of-Nations-2010-Angola",
        "/Africa/Africa-Cup-of-Nations-2008-Ghana",
        "/Africa/Africa-Cup-of-Nations-2006-Egypt",
        "/Africa/Africa-Cup-of-Nations-2004-Tunisia",
        "/Africa/Africa-Cup-of-Nations-2002-Mali",
        "/Africa/Africa-Cup-of-Nations-2000-Ghana-Nigeria",
        "/Africa/Africa-Cup-of-Nations-1998-Burkina-Faso"
    ]

    asia_qualification = [
        "/Asia/Asian-Cup-Qualification-2019-UAE",
        "/Asia/Asian-Cup-Qualification-2015-Australia",

        "/Asia/WC-Qualification-Asia-2018-Russia",
        "/Asia/WC-Qualification-Asia-2014-Brazil",
        "/Asia/WC-Qualification-Asia-2010-South-Africa",
        "/Asia/WC-Qualification-Asia-2006-Germany",
        "/Asia/WC-Qualification-Asia-2002-Korea-Rep-Japan"
    ]

    asia_cup = [
        "/Asia/AFC-Asian-Cup-2019-UAE",
        "/Asia/AFC-Asian-Cup-2015-Australia",
        "/Asia/AFC-Asian-Cup-2011-Qatar",
        "/Asia/AFC-Asian-Cup-2007-Indonesia---Malaysia---Thailand---Vietnam",
        "/Asia/AFC-Asian-Cup-2004-China"
    ]

    gold_cup = [
        "/N-C-America/CONCACAF-Gold-Cup-2017-USA",
        "/N-C-America/CONCACAF-Gold-Cup-2015-USA-Canada",
        "/N-C-America/CONCACAF-Gold-Cup-2013-USA",
        "/N-C-America/CONCACAF-Gold-Cup-2011-USA",
        "/N-C-America/CONCACAF-Gold-Cup-2009-USA",
        "/N-C-America/CONCACAF-Gold-Cup-2007-USA",
        "/N-C-America/CONCACAF-Gold-Cup-2005-USA",
        "/N-C-America/CONCACAF-Gold-Cup-2003-USA-Mexico",
        "/N-C-America/CONCACAF-Gold-Cup-2002-USA",
        "/N-C-America/CONCACAF-Gold-Cup-2000-USA",
        "/N-C-America/CONCACAF-Gold-Cup-1998-USA",
        "/N-C-America/CONCACAF-Gold-Cup-1996-USA",
        "/N-C-America/CONCACAF-Gold-Cup-1993-USA-Mexico",
        "/N-C-America/CONCACAF-Gold-Cup-1991-USA"
    ]

    world_cup = [
        "/World/World-Cup-2018-Russia",
        "/World/World-Cup-2014-Brazil",
        "/World/World-Cup-2010-South-Africa",
        "/World/World-Cup-2006-Germany",
        "/World/World-Cup-2002-Korea-Rep-Japan",
        "/World/World-Cup-1998-France",
        "/World/World-Cup-1994-USA",
        "/World/World-Cup-1990-Italy",
        "/World/World-Cup-1986-Mexico",
        "/World/World-Cup-1982-Spain"
    ]

    world_cup_u20 = [
        "/World/U20-World-Cup-2019-Poland",
        "/World/U20-World-Cup-2017-Korea-Republic",
        "/World/U20-World-Cup-2015-New-Zealand",
        "/World/U20-World-Cup-2013-Turkey",
        "/World/U20-World-Cup-2011-Colombia",
        "/World/U20-World-Cup-2009-Egypt",
        "/World/U20-World-Cup-2007-Canada",
        "/World/U20-World-Cup-2005-Netherlands",
    ]

    uefa_u21 = [
        "/Europe/UEFA-U21-Championship-2019-Italy",
        "/Europe/UEFA-U21-Championship-2017-Poland",
        "/Europe/UEFA-U21-Championship-2015-Czech-Republic",
        "/Europe/UEFA-U21-Championship-2013-Israel",
        "/Europe/UEFA-U21-Championship-2011-Denmark",
        "/Europe/UEFA-U21-Championship-2009-Sweden",
        "/Europe/UEFA-U21-Championship-2007-Netherlands",
        "/Europe/UEFA-U21-Championship-2006-Portugal"
    ]

    uefa_u19 = [
        "/Europe/UEFA-U19-Championship-2019-Armenia",
        "/Europe/UEFA-U19-Championship-2018-Finland",
        "/Europe/UEFA-U19-Championship-2017-Georgia",
        "/Europe/UEFA-U19-Championship-2016-Germany",
        "/Europe/UEFA-U19-Championship-2015-Greece",
        "/Europe/UEFA-U19-Championship-2014-Hungary",
        "/Europe/UEFA-U19-Championship-2013-Lithuania",
        "/Europe/UEFA-U19-Championship-2012-Estonia",
        "/Europe/UEFA-U19-Championship-2011-Romania",
        "/Europe/UEFA-U19-Championship-2010-France",
    ]

    fa_cup = [
        "/season/16386/England-FA-Cup-2019-2020"
    ]

    dfb_pokal = ["/Germany/DFB-Pokal-{0}-{1}".format(year, year+1)
        for year in range(2004, 2020)]

    copa_del_rey = ["/Spain/Copa-del-Rey-{0}-{1}".format(year, year+1)
        for year in range(2004, 2020)]

    scotland_fa_cup = ["/Scotland/FA-Cup-{0}-{1}".format(year, year+1)
        for year in range(2004, 2020)]

    coupe_de_france = ["/France/Coupe-de-France-{0}-{1}".format(year, year+1)
        for year in range(2004, 2020)]

    copa_italia = ["/Italy/Coppa-Italia-{0}-{1}".format(year, year+1)
        for year in range(2004, 2020)]

    knvb_baker = ["/Netherlands/KNVB-Beker-{0}-{1}".format(year, year+1)
        for year in range(2004, 2020)]

    taga_de_portugal = ["/Portugal/Taça-de-Portugal-{0}-{1}".format(year, year+1)
        for year in range(2004, 2020)]

    austria_cup = ["/Austria/Cup-{0}-{1}".format(year, year+1)
        for year in range(2004, 2020)]

    swiss_pokal = ["/Switzerland/Schweizer-Pokal-{0}-{1}".format(year, year+1)
        for year in range(2004, 2020)]

    copa_de_ligue = ["/France/Coupe-de-la-Ligue-{0}-{1}".format(year, year+1)
        for year in range(2004, 2020)]

    league_cup = [
        "/season/16216/England-Carabao-Cup-2019-2020"
    ]

    open_cup = ["/USA/US-Open-Cup-{0}".format(year)
        for year in range(2007, 2020)]

    champions_league = [
        "/season/12950/Europe-Champions-League-2018-2019",
        "/season/7907/Europe-Champions-League-2017-2018",
        "/season/718/Europe-Champions-League-2016-2017",
        "/season/5321/Europe-Champions-League-2015-2016",
        "/season/5322/Europe-Champions-League-2014-2015",
        "/season/5315/Europe-Champions-League-2013-2014",
        "/season/5318/Europe-Champions-League-2012-2013",
        "/season/5313/Europe-Champions-League-2011-2012",
        "/season/5312/Europe-Champions-League-2010-2011",
        "/season/5311/Europe-Champions-League-2009-2010",
        "/season/5310/Europe-Champions-League-2008-2009",
        "/season/5309/Europe-Champions-League-2007-2008",
        "/season/5308/Europe-Champions-League-2006-2007",
        "/season/5307/Europe-Champions-League-2005-2006"
    ]

    europa_league = [
        "/season/12945/Europe-Europa-League-2018-2019",
        "/season/7908/Europe-Europa-League-2017-2018",
        "/season/719/Europe-Europa-League-2016-2017",
        "/season/5337/Europe-Europa-League-2015-2016",
        "/season/5335/Europe-Europa-League-2014-2015",
        "/season/5334/Europe-Europa-League-2013-2014",
        "/season/5333/Europe-Europa-League-2012-2013",
        "/season/5332/Europe-Europa-League-2011-2012",
        "/season/5331/Europe-Europa-League-2010-2011",
        "/season/5330/Europe-Europa-League-2009-2010",
        "/season/5329/Europe-Europa-League-2008-2009",
        "/season/5328/Europe-Europa-League-2007-2008",
        "/season/5327/Europe-Europa-League-2006-2007",
        "/season/5326/Europe-Europa-League-2005-2006"
    ]

    k_league2 = [
        "/season/15690/Korea-Republic-K-League-2-2019",
        "/season/12176/Korea-Republic-K-League-2-2018",
        "/season/6340/Korea-Republic-K-League-2-2017",
        "/season/6338/Korea-Republic-K-League-2-2016",
        "/season/6337/Korea-Republic-K-League-2-2015",
        "/season/6336/Korea-Republic-K-League-2-2014",
        "/season/6335/Korea-Republic-K-League-2-2013",
        "/season/6334/Korea-Republic-K-League-2-2012",
        "/season/6333/Korea-Republic-K-League-2-2011",
        "/season/6332/Korea-Republic-K-League-2-2010",
        "/season/6331/Korea-Republic-K-League-2-2009",
        "/season/6330/Korea-Republic-K-League-2-2008",
    ]

    allsvenskan = [
        "/season/15529/Sweden-Allsvenskan-2019",
        "/season/11759/Sweden-Allsvenskan-2018",
        "/season/848/Sweden-Allsvenskan-2017",
        "/season/2088/Sweden-Allsvenskan-2016",
        "/season/2087/Sweden-Allsvenskan-2015",
        "/season/2086/Sweden-Allsvenskan-2014",
        "/season/2085/Sweden-Allsvenskan-2013",
        "/season/2084/Sweden-Allsvenskan-2012",
        "/season/2083/Sweden-Allsvenskan-2011",
        "/season/2082/Sweden-Allsvenskan-2010",
        "/season/2081/Sweden-Allsvenskan-2009",
        "/season/2080/Sweden-Allsvenskan-2008",
        "/season/2079/Sweden-Allsvenskan-2007",
        "/season/2078/Sweden-Allsvenskan-2006",
        "/season/16515/Sweden-Allsvenskan-2005"
    ]

    china_super_league = [
        "/season/15715/China-PR-Super-League-2019",
        "/season/12250/China-PR-Super-League-2018",
        "/season/1003/China-PR-Super-League-2017",
        "/season/3174/China-PR-Super-League-2016",
        "/season/3173/China-PR-Super-League-2015",
        "/season/3172/China-PR-Super-League-2014",
        "/season/3171/China-PR-Super-League-2013",
        "/season/3170/China-PR-Super-League-2012",
        "/season/3169/China-PR-Super-League-2011",
        "/season/3168/China-PR-Super-League-2010",
        "/season/3167/China-PR-Super-League-2009",
        "/season/3166/China-PR-Super-League-2008",
        "/season/3165/China-PR-Super-League-2007",
        "/season/3164/China-PR-Super-League-2006",
        "/season/3163/China-PR-Super-League-2005"
    ]

    japan_cup = [
        "/season/15693/Japan-Ybc-Levain-Cup-2019",
        "/season/12161/Japan-Ybc-Levain-Cup-2018",
        "/season/992/Japan-Ybc-Levain-Cup-2017",
        "/season/3257/Japan-Ybc-Levain-Cup-2016",
        "/season/3256/Japan-Ybc-Levain-Cup-2015",
        "/season/3255/Japan-Ybc-Levain-Cup-2014",
        "/season/3254/Japan-Ybc-Levain-Cup-2013",
        "/season/3253/Japan-Ybc-Levain-Cup-2012",
        "/season/3252/Japan-Ybc-Levain-Cup-2011",
        "/season/3251/Japan-Ybc-Levain-Cup-2010",
        "/season/3250/Japan-Ybc-Levain-Cup-2009",
        "/season/3249/Japan-Ybc-Levain-Cup-2008",
        "/season/3248/Japan-Ybc-Levain-Cup-2007",
        "/season/3247/Japan-Ybc-Levain-Cup-2006",
        "/season/3246/Japan-Ybc-Levain-Cup-2005"
    ]

    eu_qual_2020 = [
        "/season/15474/Europe-Euro-Qualification-2020"
    ]


class BetStadtLib:
    pass