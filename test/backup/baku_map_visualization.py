import json
import math

# Your actual API response data
response_text = '''[{"id":"vuwtttvvtwuw","base":[1370339328,809402368],"zrange":[12,12],"layer":"m@762526034","features":[{"id":"13681174912190645975","a":[0,0,1370339328,809402368,1370339328,809402368,1370339328,809402368],"bb":[-14,-29,13,2,-14,-29,13,2,-14,-29,13,2,-14,-29,13,2,-86,-29,-13,-11,-135,-15,-13,3],"c":"{\\"1\\":{\\"title\\":\\"AAAF Park Yaşayış Kompleksi\\"}}","io":[0,-13]},{"id":"166171470317410144","a":[32768,-131072,1370372096,809271296,1370372096,809271296,1370372096,809271296],"bb":[-14,-29,13,2,-14,-29,13,2,-14,-29,13,2,-14,-29,13,2,-48,-36,-12,-18,-91,-22,-12,-4,-78,-8,-12,10],"c":"{\\"1\\":{\\"title\\":\\"Baku Engineering University\\"}}","io":[0,-13]},{"id":"8225617313073113012","a":[268288,-210944],"bb":[-159,-22,-12,-4],"c":"{\\"1\\":{\\"title\\":\\"Bank Respublika Arena\\"}}"}]},{"id":"vuwtttvvtwwu","base":[1370607616,809191424],"zrange":[12,12],"layer":"m@762526034","features":[{"id":"8225617313073113012","a":[0,0,1370607616,809191424,1370607616,809191424,1370607616,809191424],"bb":[-14,-29,13,2,-14,-29,13,2,-14,-29,13,2,-14,-29,13,2,-159,-22,-12,-4],"c":"{\\"1\\":{\\"title\\":\\"Bank Respublika Arena\\"}}","io":[0,-13]},{"id":"0x40308f53afed4917:0x9445d051d3cee885","a":[147456,163840,1370755072,809355264,1370755072,809355264,1370755072,809355264],"bb":[-14,-29,13,2,-14,-29,13,2,-14,-29,13,2,-14,-29,13,2],"c":"{\\"1\\":{\\"title\\":\\"Mud Volcano\\"}}","io":[0,-13]},{"id":"0x403088cfcb3fadcb:0xd3f34a18daa7f997","a":[372736,180224],"bb":[-25,-11,26,2,-34,-2,34,11],"c":"{\\"1\\":{\\"title\\":\\"Binagadi Settlement\\"}}"},{"id":"0x4030861a586b2a6f:0xd3194acd21fc914b","a":[145408,286720],"bb":[-43,-11,43,2,-22,-2,23,11],"c":"{\\"1\\":{\\"title\\":\\"Nurlu Yaşayış Massivi\\"}}"}]},{"id":"vuwtttvvtwww","base":[1371658240,809535488],"zrange":[12,12],"layer":"m@762526034","features":[{"id":"12578913194700600236","a":[0,0],"bb":[-153,-22,-13,-4],"c":"{\\"1\\":{\\"title\\":\\"Sabunçu Xəstəxanası\\"}}"},{"id":"0x4030898dd6144c29:0x6fab276612ee2bb3","a":[-116736,-141312],"bb":[-30,-6,31,7],"c":"{\\"1\\":{\\"title\\":\\"Balakhani\\"}}"},{"id":"0x403088cfcb3fadcb:0xd3f34a18daa7f997","a":[-677888,-163840],"bb":[-25,-11,26,2,-34,-2,34,11],"c":"{\\"1\\":{\\"title\\":\\"Binagadi Settlement\\"}}"}]},{"id":"vuwtttvvuvtv","base":[1370396672,809635840],"zrange":[12,12],"layer":"m@762526034","features":[{"id":"0x4030869969eaa47b:0x836bcddab39159e9","a":[0,0],"bb":[-25,-6,25,7],"c":"{\\"1\\":{\\"title\\":\\"Hökməli\\"}}"}]},{"id":"vuwtttvvuvtw","zrange":[12,12],"layer":"m@762526034"},{"id":"vuwtttvvuvvt","base":[1370953728,809641984],"zrange":[12,12],"layer":"m@762526034","features":[{"id":"1554028385086618596","a":[0,0,1370953728,809641984,1370953728,809641984,1370953728,809641984],"bb":[-14,-29,13,2,-14,-29,13,2,-14,-29,13,2,-14,-29,13,2,-113,-22,-12,-4],"c":"{\\"1\\":{\\"title\\":\\"Heydər Məscidi\\"}}","io":[0,-13]},{"id":"11271902678587595986","a":[-118784,219136,1370834944,809861120,1370834944,809861120,1370834944,809861120],"bb":[-14,-29,13,2,-14,-29,13,2,-14,-29,13,2,-14,-29,13,2,13,-29,114,-11,13,-15,66,3],"c":"{\\"1\\":{\\"title\\":\\"Milli Onkologiya Mərkəzi\\"}}","io":[0,-13]},{"id":"0x4030864bb741c7fd:0x5cb163c86e320813","a":[-114688,-75776],"bb":[-23,-6,24,7],"c":"{\\"1\\":{\\"title\\":\\"Biləcəri\\"}}"},{"id":"0x4030865d830dc177:0x3836bc7a9b178356","a":[-307200,-8192],"bb":[-26,-6,27,7],"c":"{\\"1\\":{\\"title\\":\\"Sulutəpə\\"}}"},{"id":"0x403087b9c663cdbd:0x3f25195eefaed750","a":[-59392,30720],"bb":[-13,-11,14,2,-36,-2,37,11],"c":"{\\"1\\":{\\"title\\":\\"9-cu Mikrorayon\\"}}"},{"id":"0x4030871df800bf8f:0x3cddd691a76c0c2f","a":[-352256,151552],"bb":[-27,-6,27,7],"c":"{\\"1\\":{\\"title\\":\\"Xocəsən\\"}}"}]},{"id":"vuwtttvvuvvu","base":[1371068416,810113024],"zrange":[12,12],"layer":"m@762526034","features":[{"id":"17432410328216189643","a":[0,0],"bb":[-39,-6,39,12],"c":"{\\"1\\":{\\"title\\":\\"Bakı bulvarı\\"}}"},{"id":"12011582899010022726","a":[-88064,86016,1370980352,810199040,1370980352,810199040,1370980352,810199040],"bb":[-14,-29,13,2,-14,-29,13,2,-14,-29,13,2,-14,-29,13,2,13,-22,100,-4],"c":"{\\"1\\":{\\"title\\":\\"Dağüstü park\\"}}","io":[0,-13]},{"id":"4168587451644942235","a":[100352,-43008],"bb":[-102,-22,-12,-4],"c":"{\\"1\\":{\\"title\\":\\"Crescent Mall\\"}}"},{"id":"14393325598320405505","a":[-8192,243712],"bb":[-102,-29,-13,-11,-111,-15,-12,3],"c":"{\\"1\\":{\\"title\\":\\"\\\\\\"SURAXANI\\\\\\" GƏMİ-MUZEYİ\\"}}"},{"id":"0x40307ef2d0ca64f5:0x1a49d38c498337a7","a":[-235520,286720],"bb":[-30,-6,31,7],"c":"{\\"1\\":{\\"title\\":\\"Badamdar\\"}}"},{"id":"0x40307f313225359b:0x255ac335cc7eec77","a":[-247808,425984],"bb":[-10,-6,10,7],"c":"{\\"1\\":{\\"title\\":\\"Şıx\\"}}"},{"id":"17572405317745359751","a":[-94208,387072,1370974208,810500096,1370974208,810500096,1370974208,810500096],"bb":[-14,-29,13,2,-14,-29,13,2,-14,-29,13,2,-14,-29,13,2],"c":"{\\"1\\":{\\"title\\":\\"Congress Hall Of Baku Higher Oil School\\"}}","io":[0,-13]},{"id":"0x40307e1995e6c287:0x31fe749fd726789b","a":[-460800,6144],"bb":[-21,-6,21,7],"c":"{\\"1\\":{\\"title\\":\\"Şubanı\\"}}"}]},{"id":"vuwtttvvuvvv","base":[1371213824,809900032],"zrange":[12,12],"layer":"m@762526034","features":[{"id":"12160506185835364285","a":[0,0,1371213824,809900032,1371213824,809900032,1371213824,809900032],"bb":[-23,-30,22,-1,-23,-30,22,-1,-23,-30,22,-1,-23,-30,22,-1,-72,-1,72,17],"c":"{\\"1\\":{\\"title\\":\\"Heydər Əliyev Mərkəzi\\"}}","io":[0,-15]},{"id":"4168587451644942235","a":[-45056,169984,1371168768,810070016,1371168768,810070016,1371168768,810070016],"bb":[-14,-29,13,2,-14,-29,13,2,-14,-29,13,2,-14,-29,13,2],"c":"{\\"1\\":{\\"title\\":\\"Crescent Mall\\"}}","io":[0,-13]},{"id":"5371833984757620636","a":[186368,-126976,1371400192,809773056,1371400192,809773056,1371400192,809773056],"bb":[-14,-29,13,2,-14,-29,13,2,-14,-29,13,2,-14,-29,13,2,-91,-20,-12,-5],"c":"{\\"1\\":{\\"title\\":\\"Yeni klinika\\"}}","io":[0,-13]},{"id":"11271902678587595986","a":[-378880,-38912],"bb":[13,-29,114,-11],"c":"{\\"1\\":{\\"title\\":\\"Milli Onkologiya Mərkəzi\\"}}"},{"id":"12578913194700600236","a":[444416,-364544],"bb":[-153,-22,-13,-4],"c":"{\\"1\\":{\\"title\\":\\"Sabunçu Xəstəxanası\\"}}"},{"id":"16664794742510893433","a":[303104,8192,1371516928,809908224,1371516928,809908224,1371516928,809908224],"bb":[-14,-29,13,2,-14,-29,13,2,-14,-29,13,2,-14,-29,13,2,-57,-20,-12,-5],"c":"{\\"1\\":{\\"title\\":\\"Nizami Tibb Mərkəzi\\"}}","io":[0,-13]},{"id":"683751674163756123","a":[309248,-266240,1371523072,809633792,1371523072,809633792,1371523072,809633792],"bb":[-14,-29,13,2,-14,-29,13,2,-14,-29,13,2,-14,-29,13,2],"c":"{\\"1\\":{\\"title\\":\\"Baku Olimpiya Stadionu\\"}}","io":[0,-13]},{"id":"0x40307cdf33e7abbb:0xf979dab1ed9eb65e","a":[122880,108544],"bb":[-33,-6,33,7],"c":"{\\"1\\":{\\"title\\":\\"Bakı Ağ Şəhər\\"}}"},{"id":"0x40306335a0c8dd1f:0x7f369f6d5741db4d","a":[337920,106496],"bb":[-39,-6,40,7],"c":"{\\"1\\":{\\"title\\":\\"Həzi Aslanov\\"}}"},{"id":"0x403087e3311eb40f:0xeb77e0f88e990f48","a":[-104448,-192512],"bb":[-30,-6,31,7],"c":"{\\"1\\":{\\"title\\":\\"Dərnəgül\\"}}"},{"id":"0x4030632d47f219ef:0x9893884279aee17b","a":[276480,73728],"bb":[-11,-6,12,7],"c":"{\\"1\\":{\\"title\\":\\"NZS\\"}}"}]},{"id":"vuwtttvvuvvw","base":[1371068416,810113024],"zrange":[12,12],"layer":"m@762526034","features":[{"id":"17432410328216189643","a":[0,0],"bb":[-39,-6,39,12],"c":"{\\"1\\":{\\"title\\":\\"Bakı bulvarı\\"}}"},{"id":"12011582899010022726","a":[-88064,86016],"bb":[13,-22,100,-4],"c":"{\\"1\\":{\\"title\\":\\"Dağüstü park\\"}}"},{"id":"4168587451644942235","a":[100352,-43008,1371168768,810070016,1371168768,810070016,1371168768,810070016],"bb":[-14,-29,13,2,-14,-29,13,2,-14,-29,13,2,-14,-29,13,2,-102,-22,-12,-4],"c":"{\\"1\\":{\\"title\\":\\"Crescent Mall\\"}}","io":[0,-13]},{"id":"14393325598320405505","a":[-8192,243712,1371060224,810356736,1371060224,810356736,1371060224,810356736],"bb":[-14,-29,13,2,-14,-29,13,2,-14,-29,13,2,-14,-29,13,2,-102,-29,-13,-11,-111,-15,-12,3],"c":"{\\"1\\":{\\"title\\":\\"\\\\\\"SURAXANI\\\\\\" GƏMİ-MUZEYİ\\"}}","io":[0,-13]},{"id":"14757268932298243222","a":[624640,59392],"bb":[-96,-22,-12,-4],"c":"{\\"1\\":{\\"title\\":\\"Gənclik Park\\"}}"}]},{"id":"vuwtttvvvuuu","base":[1371658240,809535488],"zrange":[12,12],"layer":"m@762526034","features":[{"id":"12578913194700600236","a":[0,0,1371658240,809535488,1371658240,809535488,1371658240,809535488],"bb":[-14,-29,13,2,-14,-29,13,2,-14,-29,13,2,-14,-29,13,2,-153,-22,-13,-4],"c":"{\\"1\\":{\\"title\\":\\"Sabunçu Xəstəxanası\\"}}","io":[0,-13]},{"id":"6419138971600186060","a":[411648,-34816,1372069888,809500672,1372069888,809500672,1372069888,809500672],"bb":[-14,-29,13,2,-14,-29,13,2,-14,-29,13,2,-14,-29,13,2,-108,-22,-12,-4],"c":"{\\"1\\":{\\"title\\":\\"Appro Hospital\\"}}","io":[0,-13]},{"id":"8650908147141480002","a":[225280,-108544,1371883520,809426944,1371883520,809426944,1371883520,809426944],"bb":[-14,-29,13,2,-14,-29,13,2,-14,-29,13,2,-14,-29,13,2,-111,-22,-13,-4],"c":"{\\"1\\":{\\"title\\":\\"Ramana qalası\\"}}","io":[0,-13]},{"id":"0x4030898dd6144c29:0x6fab276612ee2bb3","a":[-116736,-141312],"bb":[-30,-6,31,7],"c":"{\\"1\\":{\\"title\\":\\"Balakhani\\"}}"},{"id":"16064703533987623102","a":[167936,-425984,1371826176,809109504,1371826176,809109504,1371826176,809109504],"bb":[-14,-29,13,2,-14,-29,13,2,-14,-29,13,2,-14,-29,13,2,-94,-29,-13,-11,-59,-15,-13,3],"c":"{\\"1\\":{\\"title\\":\\"Zabrat Hava Limanı\\"}}","io":[0,-13]},{"id":"137759950603449650","a":[315392,-303104,1371973632,809232384,1371973632,809232384,1371973632,809232384],"bb":[-14,-29,13,2,-14,-29,13,2,-14,-29,13,2,-14,-29,13,2,13,-29,119,-11,13,-15,160,3],"c":"{\\"1\\":{\\"title\\":\\"Ramana Yaşayış kompleksi Grandmart supermarket\\"}}","io":[0,-13]}]},{"id":"vuwtttvvvuuw","base":[1372313600,809353216],"zrange":[12,12],"layer":"m@762526034","features":[{"id":"4741234976255598300","a":[0,0,1372313600,809353216,1372313600,809353216,1372313600,809353216],"bb":[-14,-29,13,2,-14,-29,13,2,-14,-29,13,2,-14,-29,13,2,-62,-43,-13,-25,-95,-29,-12,-11,-85,-15,-13,3,-95,-1,-12,17],"c":"{\\"1\\":{\\"title\\":\\"Heydər Əliyev Adına Beynəlxalq Hava Limanı\\"}}","io":[0,-13]},{"id":"6419138971600186060","a":[-243712,147456,1372069888,809500672,1372069888,809500672,1372069888,809500672],"bb":[-14,-29,13,2,-14,-29,13,2,-14,-29,13,2,-14,-29,13,2],"c":"{\\"1\\":{\\"title\\":\\"Appro Hospital\\"}}","io":[0,-13]},{"id":"7820914312166501524","a":[133120,-53248,1372446720,809299968,1372446720,809299968,1372446720,809299968],"bb":[-14,-29,13,2,-14,-29,13,2,-14,-29,13,2,-14,-29,13,2,13,-29,86,-11,13,-15,133,3],"c":"{\\"1\\":{\\"title\\":\\"Agilli Bala- montoseri merkezi\\"}}","io":[0,-13]},{"id":"0x403060833e46869b:0x9a5cb6608e1ca621","a":[290816,61440],"bb":[-14,-6,14,7],"c":"{\\"1\\":{\\"title\\":\\"Binə\\"}}"},{"id":"137759950603449650","a":[-339968,-120832],"bb":[13,-29,119,-11,13,-15,160,3],"c":"{\\"1\\":{\\"title\\":\\"Ramana Yaşayış kompleksi Grandmart supermarket\\"}}"}]},{"id":"vuwtttvvwttt","base":[1371791360,809908224],"zrange":[12,12],"layer":"m@762526034","features":[{"id":"6598440366699089205","a":[0,0,1371791360,809908224,1371791360,809908224,1371791360,809908224],"bb":[-14,-29,13,2,-14,-29,13,2,-14,-29,13,2,-14,-29,13,2],"c":"{\\"1\\":{\\"title\\":\\"Baku Medical Plaza\\"}}","io":[0,-13]},{"id":"12578913194700600236","a":[-133120,-372736,1371658240,809535488,1371658240,809535488,1371658240,809535488],"bb":[-14,-29,13,2,-14,-29,13,2,-14,-29,13,2,-14,-29,13,2,-153,-22,-13,-4],"c":"{\\"1\\":{\\"title\\":\\"Sabunçu Xəstəxanası\\"}}","io":[0,-13]},{"id":"16664794742510893433","a":[-274432,0,1371516928,809908224,1371516928,809908224,1371516928,809908224],"bb":[-14,-29,13,2,-14,-29,13,2,-14,-29,13,2,-14,-29,13,2],"c":"{\\"1\\":{\\"title\\":\\"Nizami Tibb Mərkəzi\\"}}","io":[0,-13]},{"id":"4186798481689838179","a":[-59392,-100352,1371731968,809807872,1371731968,809807872,1371731968,809807872],"bb":[-14,-29,13,2,-14,-29,13,2,-14,-29,13,2,-14,-29,13,2,13,-29,139,-11,13,-15,69,3],"c":"{\\"1\\":{\\"title\\":\\"Mәlhәm Beynəlxalq Hospital\\"}}","io":[0,-13]},{"id":"683751674163756123","a":[-268288,-274432,1371523072,809633792,1371523072,809633792,1371523072,809633792],"bb":[-14,-29,13,2,-14,-29,13,2,-14,-29,13,2,-14,-29,13,2],"c":"{\\"1\\":{\\"title\\":\\"Baku Olimpiya Stadionu\\"}}","io":[0,-13]},{"id":"0x4030623a1e06d9ed:0xd97657279cc3c71a","a":[-86016,-235520],"bb":[-31,-6,32,7],"c":"{\\"1\\":{\\"title\\":\\"Bakıxanov\\"}}"},{"id":"6419138971600186060","a":[278528,-407552,1372069888,809500672,1372069888,809500672,1372069888,809500672],"bb":[-14,-29,13,2,-14,-29,13,2,-14,-29,13,2,-14,-29,13,2],"c":"{\\"1\\":{\\"title\\":\\"Appro Hospital\\"}}","io":[0,-13]},{"id":"0x40306367e92de657:0xc6159ae7f4a0fee4","a":[-81920,100352],"bb":[-25,-6,25,7],"c":"{\\"1\\":{\\"title\\":\\"Əhmədli\\"}}"},{"id":"0x40306335a0c8dd1f:0x7f369f6d5741db4d","a":[-239616,98304],"bb":[-39,-6,40,7],"c":"{\\"1\\":{\\"title\\":\\"Həzi Aslanov\\"}}"},{"id":"0x4030649b906e4d39:0x5bf31674360301e","a":[98304,71680],"bb":[-38,-6,39,7],"c":"{\\"1\\":{\\"title\\":\\"Yeni Günəşli\\"}}"},{"id":"0x4030622c9ded6657:0xbaad2527dff48460","a":[135168,-249856],"bb":[-25,-6,26,7],"c":"{\\"1\\":{\\"title\\":\\"Əmircan\\"}}"},{"id":"0x40306391bbbc51d9:0xaef398d069185c51","a":[147456,-34816],"bb":[-39,-6,39,7],"c":"{\\"1\\":{\\"title\\":\\"Şərq Massivi\\"}}"},{"id":"0x403061614795cac9:0xacd5512270f4d818","a":[286720,-202752],"bb":[-31,-6,32,7],"c":"{\\"1\\":{\\"title\\":\\"6th Madan\\"}}"}]},{"id":"vuwtttvvwttu","base":[1371693056,810172416],"zrange":[12,12],"layer":"m@762526034","features":[{"id":"14757268932298243222","a":[0,0,1371693056,810172416,1371693056,810172416,1371693056,810172416],"bb":[-14,-29,13,2,-14,-29,13,2,-14,-29,13,2,-14,-29,13,2,-96,-22,-12,-4],"c":"{\\"1\\":{\\"title\\":\\"Gənclik Park\\"}}","io":[0,-13]},{"id":"0x403064d35ad50583:0x9b3f57d79832c3da","a":[178176,122880],"bb":[-10,-6,10,7],"c":"{\\"1\\":{\\"title\\":\\"Zığ\\"}}"}]},{"id":"vuwtttvvwttv","base":[1372069888,809500672],"zrange":[12,12],"layer":"m@762526034","features":[{"id":"6419138971600186060","a":[0,0,1372069888,809500672,1372069888,809500672,1372069888,809500672],"bb":[-14,-29,13,2,-14,-29,13,2,-14,-29,13,2,-14,-29,13,2],"c":"{\\"1\\":{\\"title\\":\\"Appro Hospital\\"}}","io":[0,-13]},{"id":"9350492220224658328","a":[497664,333824,1372567552,809834496,1372567552,809834496,1372567552,809834496],"bb":[-14,-29,13,2,-14,-29,13,2,-14,-29,13,2,-14,-29,13,2],"c":"{\\"1\\":{\\"title\\":\\"Dreamland Golf Club\\"}}","io":[0,-13]},{"id":"0x40306115eb476ab1:0x253eaddb516f470c","a":[139264,129024],"bb":[-42,-6,42,7],"c":"{\\"1\\":{\\"title\\":\\"Yeni Suraxanı\\"}}"},{"id":"13728869851961683600","a":[743424,428032],"bb":[-125,-15,-12,3],"c":"{\\"1\\":{\\"title\\":\\"Aviamodellərin uçuş meydançası\\"}}"},{"id":"0x403061614795cac9:0xacd5512270f4d818","a":[8192,204800],"bb":[-31,-6,32,7],"c":"{\\"1\\":{\\"title\\":\\"6th Madan\\"}}"}]},{"id":"vuwtttvvwttw","base":[1372454912,810178560],"zrange":[12,12],"layer":"m@762526034","features":[{"id":"7693610960282791512","a":[0,0,1372454912,810178560,1372454912,810178560,1372454912,810178560],"bb":[-14,-29,13,2,-14,-29,13,2,-14,-29,13,2,-14,-29,13,2,-93,-22,-12,-4],"c":"{\\"1\\":{\\"title\\":\\"Hövsan Mall\\"}}","io":[0,-13]}]}]'''

data = json.loads(response_text)

def world_coords_to_latlon(world_x, world_y):
    """Convert Google Maps world coordinates to lat/lon"""
    # World coordinates are in range [0, 256] at zoom 0
    # At higher zoom levels they're scaled up by 2^zoom
    # We need to normalize them back to [0, 1] range
    
    # The coordinates appear to be at a high precision scale
    # Let's use a scale factor that works for Baku's coordinate range
    SCALE = 2 ** 21  # This works for the coordinate range we're seeing
    
    x = world_x / SCALE
    y = world_y / SCALE
    
    # Convert to lon/lat using Web Mercator inverse
    lon = x * 360 - 180
    
    # Inverse Mercator projection for latitude
    lat_rad = math.atan(math.sinh(math.pi * (1 - 2 * y)))
    lat = math.degrees(lat_rad)
    
    return lat, lon

# Extract locations
locations = []
seen_coords = set()

for tile in data:
    base = tile.get('base', [None, None])
    if base[0] is None or base[1] is None:
        continue
        
    features = tile.get('features', [])
    
    for feature in features:
        c_field = feature.get('c', '{}')
        try:
            c_data = json.loads(c_field)
            title = c_data.get('1', {}).get('title', 'Unknown')
        except:
            title = 'Unknown'
        
        coords_a = feature.get('a', [])
        
        if len(coords_a) >= 2:
            world_x = base[0] + coords_a[0]
            world_y = base[1] + coords_a[1]
        else:
            world_x = base[0]
            world_y = base[1]
        
        lat, lon = world_coords_to_latlon(world_x, world_y)
        
        coord_key = (round(lat, 5), round(lon, 5), title)
        if coord_key not in seen_coords:
            seen_coords.add(coord_key)
            locations.append({'title': title, 'lat': lat, 'lon': lon, 'id': len(locations)})

# Generate HTML
html_content = f'''<!DOCTYPE html>
<html>
<head>
    <title>Baku Locations - Interactive Map</title>
    <meta charset="utf-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <link rel="stylesheet" href="https://unpkg.com/leaflet@1.9.4/dist/leaflet.css" />
    <script src="https://unpkg.com/leaflet@1.9.4/dist/leaflet.js"></script>
    <style>
        body {{ margin: 0; padding: 0; font-family: Arial, sans-serif; }}
        #container {{ display: flex; height: 100vh; }}
        #sidebar {{ 
            width: 350px; 
            background: #f5f5f5; 
            overflow-y: auto; 
            border-right: 2px solid #ddd;
            box-shadow: 2px 0 5px rgba(0,0,0,0.1);
        }}
        #map {{ flex: 1; }}
        .sidebar-header {{
            background: #2c3e50;
            color: white;
            padding: 20px;
            position: sticky;
            top: 0;
            z-index: 100;
        }}
        .sidebar-header h2 {{
            margin: 0 0 5px 0;
            font-size: 20px;
        }}
        .sidebar-header p {{
            margin: 0;
            font-size: 13px;
            opacity: 0.9;
        }}
        .search-box {{
            padding: 15px;
            background: white;
            border-bottom: 1px solid #ddd;
            position: sticky;
            top: 85px;
            z-index: 99;
        }}
        .search-box input {{
            width: 100%;
            padding: 10px;
            border: 1px solid #ccc;
            border-radius: 4px;
            font-size: 14px;
            box-sizing: border-box;
        }}
        .location-list {{
            padding: 10px;
        }}
        .location-item {{
            background: white;
            padding: 12px 15px;
            margin-bottom: 8px;
            border-radius: 6px;
            cursor: pointer;
            transition: all 0.2s;
            border-left: 4px solid #3498db;
        }}
        .location-item:hover {{
            background: #e3f2fd;
            transform: translateX(5px);
            box-shadow: 0 2px 5px rgba(0,0,0,0.1);
        }}
        .location-item.active {{
            background: #2196f3;
            color: white;
            border-left-color: #1976d2;
        }}
        .location-title {{
            font-weight: bold;
            font-size: 14px;
            margin-bottom: 3px;
        }}
        .location-coords {{
            font-size: 11px;
            color: #666;
        }}
        .location-item.active .location-coords {{
            color: rgba(255,255,255,0.8);
        }}
        .no-results {{
            text-align: center;
            padding: 30px;
            color: #999;
        }}
    </style>
</head>
<body>
    <div id="container">
        <div id="sidebar">
            <div class="sidebar-header">
                <h2>📍 Baku Locations</h2>
                <p>{len(locations)} locations found</p>
            </div>
            <div class="search-box">
                <input type="text" id="searchInput" placeholder="🔍 Search locations..." />
            </div>
            <div class="location-list" id="locationList"></div>
        </div>
        <div id="map"></div>
    </div>

    <script>
        var map = L.map('map').setView([40.4093, 49.8671], 11);
        
        L.tileLayer('https://{{s}}.tile.openstreetmap.org/{{z}}/{{x}}/{{y}}.png', {{
            attribution: '&copy; OpenStreetMap contributors',
            maxZoom: 19
        }}).addTo(map);
        
        var locations = {json.dumps(locations, ensure_ascii=False)};
        var markers = {{}};
        var activeMarker = null;
        
        locations.forEach(function(loc) {{
            var marker = L.marker([loc.lat, loc.lon]).addTo(map);
            marker.bindPopup('<div style="font-weight:bold; font-size:14px;">' + loc.title + '</div>');
            markers[loc.id] = marker;
            
            marker.on('click', function() {{
                highlightLocation(loc.id);
            }});
        }});
        
        function renderList(filteredLocations) {{
            var listHtml = '';
            if (filteredLocations.length === 0) {{
                listHtml = '<div class="no-results">No locations found</div>';
            }} else {{
                filteredLocations.forEach(function(loc) {{
                    listHtml += '<div class="location-item" data-id="' + loc.id + '" onclick="flyToLocation(' + loc.id + ')">' +
                        '<div class="location-title">' + loc.title + '</div>' +
                        '<div class="location-coords">' + loc.lat.toFixed(5) + ', ' + loc.lon.toFixed(5) + '</div>' +
                        '</div>';
                }});
            }}
            document.getElementById('locationList').innerHTML = listHtml;
        }}
        
        renderList(locations);
        
        document.getElementById('searchInput').addEventListener('input', function(e) {{
            var searchTerm = e.target.value.toLowerCase();
            var filtered = locations.filter(function(loc) {{
                return loc.title.toLowerCase().includes(searchTerm);
            }});
            renderList(filtered);
        }});
        
        function flyToLocation(id) {{
            var loc = locations.find(l => l.id === id);
            if (loc) {{
                map.flyTo([loc.lat, loc.lon], 15, {{
                    duration: 1.5
                }});
                markers[id].openPopup();
                highlightLocation(id);
            }}
        }}
        
        function highlightLocation(id) {{
            document.querySelectorAll('.location-item').forEach(function(item) {{
                item.classList.remove('active');
            }});
            
            var item = document.querySelector('[data-id="' + id + '"]');
            if (item) {{
                item.classList.add('active');
                item.scrollIntoView({{ behavior: 'smooth', block: 'nearest' }});
            }}
        }}
    </script>
</body>
</html>'''

with open('baku_map_fixed.html', 'w', encoding='utf-8') as f:
    f.write(html_content)

print(f"✅ Map with CORRECTED coordinates created!")
print(f"✅ Total locations: {len(locations)}")
print("\n📍 Sample locations with coordinates:")
for i, loc in enumerate(locations[:5], 1):
    print(f"   {i}. {loc['title']}")
    print(f"      Lat: {loc['lat']:.5f}, Lon: {loc['lon']:.5f}")

print("\n🌐 Open 'baku_map_fixed.html' in your browser!")