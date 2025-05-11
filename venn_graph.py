import itertools
from venn import venn
import matplotlib.pyplot as plt

sets = {
    "Bar Graph": {
        "yellowbullheadbuccaneer968", "whitemarlinmasterfa1", "whitefishwrangler7df", "whitefishwhisperer6df",
        "wavewranglerc2", "wahoowrangler016", "wahoowarriord42", "turbottakerd86", "tunatrawlerafd",
        "swordfishsaboteur22f", "squidsquad7fd", "speckledtroutsaboteur509", "soleseeker47a", "snooksnatcherbdb",
        "skipjacktunatakerf85", "seasirenf43", "sardineseeker62e", "sailfishseeker8d5", "redfishraider677",
        "pompanoplunderere5d", "opheliacac", "musselmaraudere9b", "marlinmaster8ab", "mackerelmaster0a5",
        "longfintunalooterf32", "kingfisher87d", "huron1b3", "halibuthunterd84", "haddockhunter1a7",
        "europeanseabassbuccaneer777", "eelenthusiast8c6", "costasmeraldaac7", "cobiacapturere5e",
        "catfishcapturer7a8", "brownbullheadbriganded2", "brooktroutbuccaneerc0b", "bluemarlinbandit292",
        "bluegillbandita5f", "bluefintunabandit177", "bigeyetunabanditb73", "barracudabandit836",
        "baitedbreath538", "arcticgraylingangler094", "aquaticpursuitf31", "americaneelenthusiastcfa",
        "albacoreangler47d"
    },
    "Sunburst Chart": {
        "mrray9c4", "snappersnatcher7be", "brillbandit0a1", "sockeyesalmonseekerb95", "mackerelmaster0a5",
        "athenad34", "europeanseabassbuccaneer777", "oysteropener442", "browntroutbandite67",
        "redfinpickerelraider744", "brownbullheadbriganded2", "barracudabandit836", "goldentroutgrabber7f6",
        "sailfishseeker8d5", "redfishraider677", "whitemarlinmasterfa1", "tunatrawlerafd",
        "chainpickerelplunderer039"
    },
    "Path Map": {
        "snappersnatcher7be", "swordfishsaboteur22f", "channelcatfishcapturer175", "wahoowarriord42",
        "brillbandit0a1", "largemouthbasslooterf95", "redfinpickerelraider744", "seabassbandit9ad",
        "zanderzealotb23", "musselmaraudere9b", "bigeyetunabanditb73", "spanishmackerelmaster037",
        "haddockhawkb7c", "bigeyetunabuccaneera16", "whitemarlinwranglerbac", "whitesuckerwrangler0b3",
        "sockeyesalmonseekerb95", "malta8cc", "graylinggrabber802", "crabcatcher1aa"
    },
    "Parallel Coordinates": {
        "whitemarlinmasterfa1", "soleseeker47a", "tunatrawlerafd", "snooksnatcherbdb", "seasirenf43",
        "redfishraider677", "snappersnatcher7be", "sardineseeker62e", "sailfishseeker8d5", "marlinmaster8ab",
        "mackerelmaster0a5", "kingfisher87d", "haddockhunter1a7", "europeanseabassbuccaneer777",
        "catfishcapturer7a8"
    }
        
}

print("每个子集合的元素数量：")
for name, s in sets.items():
    print(f"{name} 的元素数量：{len(s)}")

# 打印所有任意3个集合交集不为空的组合
print("\n任意3个集合交集不为空的组合：")
for combo in itertools.combinations(sets.keys(), 3):
    intersection = sets[combo[0]] & sets[combo[1]] & sets[combo[2]]
    if intersection:
        print(f"{combo} 的交集（数量{len(intersection)}）：{intersection}")

print('--------------------------------')
# 画5集合韦恩图
venn(sets)
plt.show()

