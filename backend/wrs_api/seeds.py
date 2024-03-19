import requests
import pprint

seasons = {
    14: 1,
    14: 2
}

game_modes = {
    420: "Solo Ranked",
    400: "Normal",
    490: "Quick Play",
    450: "ARAM",
    1300: "Nexus Blitz",
    1700: "Arena",
    440: "Flex",
    700: "Clash",
    900: "ARUF",
    1900: "Pick URF",
    1020: "One For All",
    470: "(N) Twisted Treeline",
    720: "ARAM Clash"
}


# 106 ITEMS
legendary_items = {
  8020: "Abyssal Mask", 8001: "Anathema's Chains", 3003: "Archangel's Staff", 
  3504: "Ardent Censer", 6696: "Axiom Arc", 3102: "Banshee's Veil", 
  3071: "Black Cleaver", 3153: "Blade of The Ruined King", 3877: "Bloodsong", 
  3072: "Bloodthirster", 3867: "Bounty of Worlds", 3869: "Celestial Opposition", 
  6609: "Chempunk Chainsword", 4629: "Cosmic Drive", 3137: "Cryptbloom", 
  6621: "Dawncore", 3742: "Dead Man's Plate", 6333: "Death's Dance", 
  3870: "Dream Maker", 6620: "Echoes of Helia", 6692: "Eclipse", 
  3814: "Edge of Night", 3508: "Essence Reaver", 3073: "Experimental Hexplate", 
  3121: "Fimbulwinter", 4401: "Force of Nature", 3110: "Frozen Heart", 
  3026: "Guardian Angel", 3124: "Guinsoo's Rageblade", 3084: "Heartsteel", 
  3152: "Hextech Rocketbelt", 6664: "Hollow Radiance", 4628: "Horizon Focus", 
  6697: "Hubris", 3181: "Hullbreaker", 6662: "Iceborn Gauntlet", 
  6673: "Immortal Shieldbow", 4005: "Imperial Mandate", 3031: "Infinity Edge", 
  6665: "Jak'Sho, The Protean", 2504: "Kaenic Rookern", 3109: "Knight's Vow", 
  6672: "Kraken Slayer", 6653: "Liandry's Torment", 3100: "Lich Bane", 
  3190: "Locket of the Iron Solari", 3036: "Lord Dominik's Regards", 
  6655: "Luden's Companion", 3118: "Malignance", 3004: "Manamune", 
  3156: "Maw of Malmortius", 3041: "Mejai's Soulstealer", 3139: "Mercurial Scimitar", 
  3222: "Mikael's Blessing", 6617: "Moonstone Renewer", 3165: "Morellonomicon", 
  3033: "Mortal Reminder", 3042: "Muramana", 3115: "Nashor's Tooth", 
  6675: "Navori Quickblades", 6701: "Opportunity", 3046: "Phantom Dancer", 
  6698: "Profane Hydra", 3089: "Rabadon's Deathcap", 3143: "Randuin's Omen", 
  3094: "Rapid Firecannon", 3074: "Ravenous Hydra", 3107: "Redemption", 
  4633: "Riftmaker", 6657: "Rod of Ages", 3085: "Runaan's Hurricane", 
  3116: "Rylai's Crystal Scepter", 3040: "Seraph's Embrace", 
  6695: "Serpent's Fang", 6694: "Serylda's Grudge", 4645: "Shadowflame", 
  222065: "Shurelya's Battlesong", 3876: "Solstice Sleigh", 
  3161: "Spear of Shojin", 3065: "Spirit Visage", 6616: "Staff of Flowing Water", 
  3087: "Statikk Shiv", 3053: "Sterak's Gage", 3095: "Stormrazor", 
  4646: "Stormsurge", 6631: "Stridebreaker", 6610: "Sundered Sky", 
  3068: "Sunfire Aegis", 3302: "Terminus", 6676: "The Collector", 
  3075: "Thornmail", 3748: "Titanic Hydra", 3002: "Trailblazer", 
  3078: "Trinity Force", 3179: "Umbral Glaive", 2502: "Unending Despair", 
  4643: "Vigilant Wardstone", 3135: "Void Staff", 6699: "Voltaic Cyclosword", 
  3083: "Warmog's Armor", 3119: "Winter's Approach", 3091: "Wit's End", 
  3142: "Youmuu's Ghostblade", 3871: "Zaz'Zak's Realmspike", 
  3050: "Zeke's Convergence", 3157: "Zhonya's Hourglass"
}

# 167 CHAMPIONS
all_champions = {
  1: "Annie", 2: "Olaf", 3: "Galio", 4: "Twisted Fate", 5: "Xin Zhao",
  6: "Urgot", 7: "LeBlanc", 8: "Vladimir", 9: "Fiddlesticks", 10: "Kayle",
  11: "Master Yi", 12: "Alistar", 13: "Ryze", 14: "Sion", 15: "Sivir",
  16: "Soraka", 17: "Teemo", 18: "Tristana", 19: "Warwick", 20: "Nunu & Willump",
  21: "Miss Fortune", 22: "Ashe", 23: "Tryndamere", 24: "Jax", 25: "Morgana",
  26: "Zilean", 27: "Singed", 28: "Evelynn", 29: "Twitch", 30: "Karthus",
  31: "Cho'Gath", 32: "Amumu", 33: "Rammus", 34: "Anivia", 35: "Shaco",
  36: "Dr. Mundo", 37: "Sona", 38: "Kassadin", 39: "Irelia", 40: "Janna",
  41: "Gangplank", 42: "Corki", 43: "Karma", 44: "Taric", 45: "Veigar",
  48: "Trundle", 50: "Swain", 51: "Caitlyn", 53: "Blitzcrank", 54: "Malphite",
  55: "Katarina", 56: "Nocturne", 57: "Maokai", 58: "Renekton", 59: "Jarvan IV",
  60: "Elise", 61: "Orianna", 62: "Wukong", 63: "Brand", 64: "Lee Sin",
  67: "Vayne", 68: "Rumble", 69: "Cassiopeia", 72: "Skarner", 74: "Heimerdinger",
  75: "Nasus", 76: "Nidalee", 77: "Udyr", 78: "Poppy", 79: "Gragas",
  80: "Pantheon", 81: "Ezreal", 82: "Mordekaiser", 83: "Yorick", 84: "Akali",
  85: "Kennen", 86: "Garen", 89: "Leona", 90: "Malzahar", 91: "Talon",
  92: "Riven", 96: "Kog'Maw", 98: "Shen", 99: "Lux", 101: "Xerath",
  102: "Shyvana", 103: "Ahri", 104: "Graves", 105: "Fizz", 106: "Volibear",
  107: "Rengar", 110: "Varus", 111: "Nautilus", 112: "Viktor", 113: "Sejuani",
  114: "Fiora", 115: "Ziggs", 117: "Lulu", 119: "Draven", 120: "Hecarim",
  121: "Kha'Zix", 122: "Darius", 126: "Jayce", 127: "Lissandra", 131: "Diana",
  133: "Quinn", 134: "Syndra", 136: "Aurelion Sol", 141: "Kayn", 142: "Zoe",
  143: "Zyra", 145: "Kai'Sa", 147: "Seraphine", 150: "Gnar", 154: "Zac",
  157: "Yasuo", 161: "Vel'Koz", 163: "Taliyah", 164: "Camille", 166: "Akshan",
  200: "Bel'Veth", 201: "Braum", 202: "Jhin", 203: "Kindred", 221: "Zeri",
  222: "Jinx", 223: "Tahm Kench", 233: "Briar", 234: "Viego", 235: "Senna",
  236: "Lucian", 238: "Zed", 240: "Kled", 245: "Ekko", 246: "Qiyana",
  254: "Vi", 266: "Aatrox", 267: "Nami", 268: "Azir", 350: "Yuumi",
  360: "Samira", 412: "Thresh", 420: "Illaoi", 421: "Rek'Sai", 427: "Ivern",
  429: "Kalista", 432: "Bard", 497: "Rakan", 498: "Xayah", 516: "Ornn",
  517: "Sylas", 518: "Neeko", 523: "Aphelios", 526: "Rell", 555: "Pyke",
  711: "Vex", 777: "Yone", 875: "Sett", 876: "Lillia", 887: "Gwen",
  888: "Renata Glasc", 895: "Nilah", 897: "K'Sante", 901: "Smolder",
  902: "Milio", 910: "Hwei", 950: "Naafiri"
}


regions = ["americas", "asia", "europe", "sea", "esports"]


# AMERICAS = na1, br1, la1, la2
# ASIA = jp1, kr
# EUROPE = euw1, eun1, tr1, ru
# SEA = oc1, ph2, sg2, th2, tw2, vn2 ..... oc1 is ASIA when SEA is not an option
platforms = ['tr1', 'ph2', 'la1', 'tw2', 'la2', 'eun1', 'vn2',
'kr', 'oc1', 'na1', 'jp1', 'euw1', 'sg2', 'ru', 'th2', 'br1']


tier_two_boots = {
    3006: "Berserker's Greaves",
    3009: 'Boots of Swiftness',
    3111: "Mercury's Treads",
    3117: 'Mobility Boots',
    3047: 'Plated Steelcaps'
}





## NEXT: WRITE MODELS TO REFLECT REQUIREMENTS IN ERD, MAKE SURE MIGRATIONS GENERATE CORRECTLY (ID COLUMN, PARTITION ORDER OF OPERATIONS ISSUE)
## THEN SEED AND START REFACTOR OF "OLD" FOLDER, MAKE SURE TIMELINE IS INTEGRATE INTO MATCH, REDUCE JSON








### GET ALL CHAMPIONS FROM A DICT OF "NAME": NONE"
# url = "https://ddragon.leagueoflegends.com/cdn/14.5.1/data/en_US/champion.json"
# response = requests.get(url)
# if response.status_code == 200:
#     riotChamps = response.json()["data"]
# else:
#     print(response.status_code)

# fixed_champs = {}
# for oldchamp in all_champions:
#     for riot_champ in riotChamps:
#         if riotChamps[riot_champ]["name"] == oldchamp:
#             fixed_champs[int(riotChamps[riot_champ]["key"])] = oldchamp