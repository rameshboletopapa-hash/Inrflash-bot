import telebot
from telebot import types
from telebot.types import MessageEntity
import random
import emoji
import time
import os
import json
from datetime import datetime

# ╔══════════════════════════════════════════════════════════════╗
# ║   〲𝑃𝑹𝐄𝐌𝑰𝐔𝑴】𝐄𝑴𝐎𝑱𝑰𝑺】𝑩𝑶𝑻࿐            ║
# ║   Developer: @itzraj_kumar                                     ║
# ╚══════════════════════════════════════════════════════════════╝

TOKEN    = "8889067156:AAEFNFtHx1tewAOzFhOhz_JKQrEbRBSQq_Y"

import json
import os

CONFIG_FILE = "config.json"
DEFAULT_CONFIG = {
    "admins": [8414537711],
    "channels": [
        {"id": "-1003788328311", "name": "💀⃤ 𝐃𝐄𝐕〆𝐖𝐎𝐑𝐋𝐃", "link": "https://t.me/+wG2dgmlLkqZiYmI1"},
        {"id": "-1003628619423", "name": "💀⃤ 𝐙𝐀𝐈𝐍𝐔〆𝐁𝐇𝐀𝐈", "link": "https://t.me/IshrakShadman1"},
        {"id": "-1003615870308", "name": "⚡ SHADMAN CODEX⚡", "link": "https://t.me/SHADMANx69"}
    ],
    "premium_emojis": []
}

import requests
import threading

FIREBASE_URL = "https://zenith-all-default-rtdb.firebaseio.com/premium.json"

def load_config():
    try:
        resp = requests.get(FIREBASE_URL, timeout=5)
        if resp.status_code == 200 and resp.json():
            cfg = resp.json()
            for k, v in DEFAULT_CONFIG.items():
                if k not in cfg:
                    cfg[k] = v
            with open(CONFIG_FILE, "w") as f:
                json.dump(cfg, f, indent=4)
            return cfg
    except Exception as e:
        print("Firebase load error:", e)
    
    if os.path.exists(CONFIG_FILE):
        with open(CONFIG_FILE, "r") as f:
            return json.load(f)
    return DEFAULT_CONFIG

def _firebase_upload(cfg):
    try:
        requests.put(FIREBASE_URL, json=cfg, timeout=5)
    except Exception as e:
        print("Firebase save error:", e)

def save_config(cfg):
    with open(CONFIG_FILE, "w") as f:
        json.dump(cfg, f, indent=4)
    threading.Thread(target=_firebase_upload, args=(cfg,), daemon=True).start()

config = load_config()

def is_admin(uid):
    return uid in config["admins"]

bot      = telebot.TeleBot(TOKEN)

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
#  BOT STATE
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
bot_active   = True

@bot.message_handler(commands=['setlog'])
def set_log_channel(message):
    if not is_admin(message.from_user.id):
        return
    try:
        channel_id = int(message.text.split()[1])
        config["log_channel"] = channel_id
        save_config(config)
        _send_pe(message.chat.id, f"{P} Log channel set to {channel_id}!", use_main=False)
    except:
        _send_pe(message.chat.id, f"{P} Usage: /setlog <channel_id>", use_main=False)

def send_log(text):
    log_channel = config.get("log_channel")
    if log_channel:
        try:
            _send_pe(log_channel, text, use_main=False)
        except Exception as e:
            print("Log send error:", e)

# Users are now loaded from config!
all_users = set(config.get("users", []))

def save_users(users_set):
    config["users"] = list(users_set)
    save_config(config)


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
#  PREMIUM EMOJI IDs
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
MAIN_EMOJI_ID = "6010060634803148161"

DEFAULT_EMOJIS = [
    "6129399728506412489","6129812419028982717","6129574787078429498","6129477982810545152",
    "6129550284290006595","6129479035077531636","6129932613688764241","6129444065453808638",
    "6129828611055689014","6129472184604695207","6129760505759276442","6129959208126258284",
    "6129705667616841573","6129433877791382400","6129705083501293112","6131660826924292492",
    "6129727043669072880","6129415619885407680","6129909635613726974","6129627894349045589",
    "6129870783339567154","6129779562529168023","6129772480128097710","6129939837823753679",
    "6129694470637100146","6129434968713076807","6129732880529628243","6129570565125577536",
    "6129782440157256336","6129731974291527294","6129532314146838421","6129805465476929485",
    "6129650399977675538","6129801569941592173","6129769198773083022","6129708236007283169",
    "6129906126625447892","6129553312241949602","6129494286506401122","6129778965528713511",
    "6129915811776698328","6132184924603554220","6129572317472233948","6129950489342647259",
    "6131886699254388574","6129492160497589882","6129518870899203008","6129522839448984992",
    "6129903231817488942","6129814111246097614","6129643455015557847","6129736819014639296",
    "6129622134797900004","6129704267457501209","6129653943325694007","6132019972089585518",
    "6129405805885135490","6129639980387015660","6129650743575060215","6129817830687775854",
    "6129812371784342357","6129546277085520554","6129700535130922338","6129771638314523716",
    "6129780730760273719","6129488844782836766","6129672630728400259","6129792056589031358",
    "6129432683790473996","6129579803600231171","6129692490657175257","6129542888356321971",
    "6129566600870764865","6129846551134084367","6129497211379129336","6129499663805456653",
    "6129432481927010933","6129635212973316679","6132195782280879053","6129873716802231439",
    "6129712921816604452","6129903927602190764","6129926111108275647","6129680679497111287",
    "6129704739903906195","6129782715035163979","6129630071897462884","6129704885932794253",
    "6129888444245089008","6129889801454754893","6129891098534877664","6129625171339778354",
    "6129650777934798600","6129780378572954907","6129879029676776924","6129782839589214594",
    "6129616057419175458","6129577213734952104","6129631914438434952","6129509499280563691",
    "6129781254746282923","6129455898088709012","6129776848109836451","6129470861754771141",
    "6129736771769997767","6129589862413638401","6129872028880083998","6129840374971112593",
    "6129776315533893189","6129410405795110009","6129579597441801084","6129913724422593277",
    "6129668331466135693","6129746001654718223","6129574671114313022","6129652186684070216",
    "6129769130053605799","6129895818703936830","6129476453802188018","6129758830722030858",
    "6129602914819250817","6129544215501216365","6129532640564354033","6129520790749584124",
    "6129517792862413944","6129863473305230077","6129440444796378483","6129443429798648428",
    "6129521443584612989","6129593109408913890","6129553763213515073","6129523887421006760",
    "6129530544620314433","6129610250623393142","6129600178925083831","6129418755211533815",
    "6129700689749744824","6129672231296440969","6129741083917162817","6129741453284350735",
    "6129700595260463994","6129766986864924223","6129421254882500490","6129731845442510016",
    "6129913342170506824","6129486856212979482","6129409825974525149","6129711392808247546",
    "6129410818111970687","6129562112629938847","6129695952400820630","6129873536413605540",
    "6129651868856491132","6132198982031513203","6129663516807796597","6129802875611651951",
    "6129897266107915247","6129426142555282578","6129873970205302255","6129527246085429728",
    "6129934104042412999","6131893910504480009","6129758753412619088","6132118786402163360",
    "6129418815341077483","6129911435205024348","6129794302856927889","6129926467590560665",
    "6129786503196319136","6129795982189141421","6136389070521114052","6136461792907370226",
    "6138557745537751767","6136269971077995421","6138763921147829284","6136565769770637814",
    "6138443507997612595","6138957710072223834","6136406830210882173","6136308217761766184",
    "6138514890354071735","6138465562654678199","6136514547990666308","6154335299309672955",
    "6156715484285770345","6156880045957716584","6154421933095000846","6156827067536120729",
    "6156945144777022169","6156936361568901831","6156541396376361727","6154257607646255757",
    "6156558816763714393","6156434919842127016","6154621704908839853","6156436440260549720",
    "6154177180088670691","6156599245290872488","6154294879372450069","6154239663272893260",
    # ── New batch (@Iam_Hacker7 / @fStikBot) ──
    "6147565374289220368","6147464060305676048","6147629438021408084","6147868521670907133",
    "6147617184479711380","6147902731085420231","6147524086768604985","6147698410901214769",
    "6147637448135414816","6147815573314082674","6147460667281511517","6147439566107186310",
    "6238042150324409739","6235478329726604939","6237871554223412862","6235449188373502693",
    "6235375710073000908","6235628846855492222","6235403472741603087","6237702328216982810",
    "6235253239080555488","6235252066554484059","6235646232883107337","6237742262822901946",
    "6237585380552480043","6235475653961979149","6235355429237430006","6237864166879663987",
    "6235373579769222419","6235445786759402354","6235754964275172059","6235417186572178718",
    "6235234890980269200","6235259956409408282","6235459831302460476","6235572922086331108",
    "6237579651066107302","6235722567336859128","6237905016313615867","6237585097084638739",
    "6237490543379619005","6237755976653477546","6235277570070286919","6235314004277859672",
    "6235524376070984680","6235640361662813672","6235505186157107501","6235332768989976110",
    "6235307467337635626","6235447586350699315","6237941218592960218","6235302918967269680",
    "6235778118443865838","6235553568963696976","6237924893422261695","6235534464949163365",
    "6235234190900598910","6235681859636826931","6237703028296653110","6235593671073339928",
    "6237704110628413424","6237485887635067877","6237849327767655690","6235257207630338543",
    "6235599306070430546","6235289248086365655","6235458499862598535","6235411830747959922",
    "6235398361730520088","6235285623133968567","6235439400143034173","6237980431644366455",
    "6235567682226230771","6235430363531843239","6235251284870435787","6235353887344170203",
    "6235717714023814969","6235275083284223858","6235719217262369481","6237718408574539239",
    "6235635353730946325","6235623959182710485","6237774878804545915","6235636139709962407",
    "6235478849417647339","6235750196861474610","6235350382650859086","6238007481348397469",
    "6237697320285115205","6235582469798630291","6237927637906364256","6235622095166904824",
    "6237491767445296588","6237769162203076727","6242510612824332116","6242498410822244114",
    "6242308461598610637","6242135305697106689","6242345153504220696","6242319667168287353",
    "6244492465353529537","6242388034457703713","6244501154072368012","6242353099193718277",
    "6244609189679731707","6242010768825391425","6244416495971996312","6242217932277946089",
    "6242044480023697160","6244317784738632020","6242147417504879292","6242172637552842445",
    "6244779107175895852","6242179058528949496","6244617272808183303","6242011198322119983",
    "6242099116302669143","6242033978828658746","6244678063775289843","6242244140168386678",
    "6242451754592507844","6244510079014409289","6192825207078523687","6161079192533343618",
    "6158710333386005234","6170410816437754705","6167814014786083445","6235743535367199630",
    "6235406870060735585","6237541069374888854","6235637621473680408","6235398709622875457",
    "6235394337346165182","6237488808212833109","6235476345451716705","6237705201550104350",
    "6237990335838952573","6237954537286540530","6237520165769059461","6235739060011277203",
    "6237684482627868729","6237865094592600686","6237822905128851025","6235544021251399097",
    "6238018863011732603","6237724103701174258","6235258912732357193","6237825533648836194",
    "6235731032717401227","6237940329534724835","6237491831869806976","6235361334817464637",
    "6237680784661027514","6235576525563895420","6237930648678440568","6235620067942341623",
    "6237618005124064591","6237951208686886271","6239908085981256564","6237628609398316232",
    "6237581029750610380","6237757385402752314","6239846277106898871","6237641910912031971",
    "6237876149838420539", "6237800150392119554","6237571928714910827","6240185119961783395",
    "6237775175157292231", "6237771799312997998","6237654950432742406",
    "6240088109535467051","6269414313736280859","6251466418500416306",
    "5440539497383087970",
  "5440660757194744323","5274099962655816924",
    "5260293700088511294",
  "5229064374403998351","5224607267797606837",
    "5830082813403078872"
  "5829948226307890708","5830193258487094531",
    "5764725626044948428",
  "5260378006001580055","5260372113306453941",
    "5258048613308731273",
  "5260504041816884967","5260424086705700813",
    "5260512739125662198",
  "5260255066857704985","6300651997427140498",
    "6300851185125426803",
  "6301056269813810985","6298616277418117026",
    "6300559565435963297",
  "6300561674264905321","5433737613510981562",
    "5433598052843665552",
  "5433854239052935880","5260378006001580055"
    "5260372113306453941",
  "5258048613308731273","5260504041816884967",
    "5237829191474370028",
  "5238233188983131143","5238112216934270665",
    "5238106053656203864",
  "5237714730595930368","5240106181271243960",
    "5237888569397235754",
  "5237994766758596645","5238023062003145021",
    "5237810293618265488",
  "5237749408161879002","5237924733021866508",
    "5238056073121780696",
  "5237914966266235426","5237965161549023905",
    "5240245613089541481",
  "5238041788060552604","5237928869075373577",
    "5238097966232782595",
  "5237995814730616852","5237741887674142166",
    "5237720013405706769",
  "5237921468846724200","5238223353508023626",
    "5238201346095600355",
  "5228878926306101271","5229045747130843073",
    "5229011542011299168",
  "5454182632797521992","5454177848203951217",
    "5454113432284446338",
]
PREMIUM_EMOJIS = config['premium_emojis']
if not PREMIUM_EMOJIS:
    config['premium_emojis'] = DEFAULT_EMOJIS
    DEFAULT_EMOJIS = [
    "6129399728506412489","6129812419028982717","6129574787078429498","6129477982810545152",
    "6129550284290006595","6129479035077531636","6129932613688764241","6129444065453808638",
    "6129828611055689014","6129472184604695207","6129760505759276442","6129959208126258284",
    "6129705667616841573","6129433877791382400","6129705083501293112","6131660826924292492",
    "6129727043669072880","6129415619885407680","6129909635613726974","6129627894349045589",
    "6129870783339567154","6129779562529168023","6129772480128097710","6129939837823753679",
    "6129694470637100146","6129434968713076807","6129732880529628243","6129570565125577536",
    "6129782440157256336","6129731974291527294","6129532314146838421","6129805465476929485",
    "6129650399977675538","6129801569941592173","6129769198773083022","6129708236007283169",
    "6129906126625447892","6129553312241949602","6129494286506401122","6129778965528713511",
    "6129915811776698328","6132184924603554220","6129572317472233948","6129950489342647259",
    "6131886699254388574","6129492160497589882","6129518870899203008","6129522839448984992",
    "6129903231817488942","6129814111246097614","6129643455015557847","6129736819014639296",
    "6129622134797900004","6129704267457501209","6129653943325694007","6132019972089585518",
    "6129405805885135490","6129639980387015660","6129650743575060215","6129817830687775854",
    "6129812371784342357","6129546277085520554","6129700535130922338","6129771638314523716",
    "6129780730760273719","6129488844782836766","6129672630728400259","6129792056589031358",
    "6129432683790473996","6129579803600231171","6129692490657175257","6129542888356321971",
    "6129566600870764865","6129846551134084367","6129497211379129336","6129499663805456653",
    "6129432481927010933","6129635212973316679","6132195782280879053","6129873716802231439",
    "6129712921816604452","6129903927602190764","6129926111108275647","6129680679497111287",
    "6129704739903906195","6129782715035163979","6129630071897462884","6129704885932794253",
    "6129888444245089008","6129889801454754893","6129891098534877664","6129625171339778354",
    "6129650777934798600","6129780378572954907","6129879029676776924","6129782839589214594",
    "6129616057419175458","6129577213734952104","6129631914438434952","6129509499280563691",
    "6129781254746282923","6129455898088709012","6129776848109836451","6129470861754771141",
    "6129736771769997767","6129589862413638401","6129872028880083998","6129840374971112593",
    "6129776315533893189","6129410405795110009","6129579597441801084","6129913724422593277",
    "6129668331466135693","6129746001654718223","6129574671114313022","6129652186684070216",
    "6129769130053605799","6129895818703936830","6129476453802188018","6129758830722030858",
    "6129602914819250817","6129544215501216365","6129532640564354033","6129520790749584124",
    "6129517792862413944","6129863473305230077","6129440444796378483","6129443429798648428",
    "6129521443584612989","6129593109408913890","6129553763213515073","6129523887421006760",
    "6129530544620314433","6129610250623393142","6129600178925083831","6129418755211533815",
    "6129700689749744824","6129672231296440969","6129741083917162817","6129741453284350735",
    "6129700595260463994","6129766986864924223","6129421254882500490","6129731845442510016",
    "6129913342170506824","6129486856212979482","6129409825974525149","6129711392808247546",
    "6129410818111970687","6129562112629938847","6129695952400820630","6129873536413605540",
    "6129651868856491132","6132198982031513203","6129663516807796597","6129802875611651951",
    "6129897266107915247","6129426142555282578","6129873970205302255","6129527246085429728",
    "6129934104042412999","6131893910504480009","6129758753412619088","6132118786402163360",
    "6129418815341077483","6129911435205024348","6129794302856927889","6129926467590560665",
    "6129786503196319136","6129795982189141421","6136389070521114052","6136461792907370226",
    "6138557745537751767","6136269971077995421","6138763921147829284","6136565769770637814",
    "6138443507997612595","6138957710072223834","6136406830210882173","6136308217761766184",
    "6138514890354071735","6138465562654678199","6136514547990666308","6154335299309672955",
    "6156715484285770345","6156880045957716584","6154421933095000846","6156827067536120729",
    "6156945144777022169","6156936361568901831","6156541396376361727","6154257607646255757",
    "6156558816763714393","6156434919842127016","6154621704908839853","6156436440260549720",
    "6154177180088670691","6156599245290872488","6154294879372450069","6154239663272893260",
    # ── New batch (@Iam_Hacker7 / @fStikBot) ──
    "6147565374289220368","6147464060305676048","6147629438021408084","6147868521670907133",
    "6147617184479711380","6147902731085420231","6147524086768604985","6147698410901214769",
    "6147637448135414816","6147815573314082674","6147460667281511517","6147439566107186310",
    "6238042150324409739","6235478329726604939","6237871554223412862","6235449188373502693",
    "6235375710073000908","6235628846855492222","6235403472741603087","6237702328216982810",
    "6235253239080555488","6235252066554484059","6235646232883107337","6237742262822901946",
    "6237585380552480043","6235475653961979149","6235355429237430006","6237864166879663987",
    "6235373579769222419","6235445786759402354","6235754964275172059","6235417186572178718",
    "6235234890980269200","6235259956409408282","6235459831302460476","6235572922086331108",
    "6237579651066107302","6235722567336859128","6237905016313615867","6237585097084638739",
    "6237490543379619005","6237755976653477546","6235277570070286919","6235314004277859672",
    "6235524376070984680","6235640361662813672","6235505186157107501","6235332768989976110",
    "6235307467337635626","6235447586350699315","6237941218592960218","6235302918967269680",
    "6235778118443865838","6235553568963696976","6237924893422261695","6235534464949163365",
    "6235234190900598910","6235681859636826931","6237703028296653110","6235593671073339928",
    "6237704110628413424","6237485887635067877","6237849327767655690","6235257207630338543",
    "6235599306070430546","6235289248086365655","6235458499862598535","6235411830747959922",
    "6235398361730520088","6235285623133968567","6235439400143034173","6237980431644366455",
    "6235567682226230771","6235430363531843239","6235251284870435787","6235353887344170203",
    "6235717714023814969","6235275083284223858","6235719217262369481","6237718408574539239",
    "6235635353730946325","6235623959182710485","6237774878804545915","6235636139709962407",
    "6235478849417647339","6235750196861474610","6235350382650859086","6238007481348397469",
    "6237697320285115205","6235582469798630291","6237927637906364256","6235622095166904824",
    "6237491767445296588","6237769162203076727","6242510612824332116","6242498410822244114",
    "6242308461598610637","6242135305697106689","6242345153504220696","6242319667168287353",
    "6244492465353529537","6242388034457703713","6244501154072368012","6242353099193718277",
    "6244609189679731707","6242010768825391425","6244416495971996312","6242217932277946089",
    "6242044480023697160","6244317784738632020","6242147417504879292","6242172637552842445",
    "6244779107175895852","6242179058528949496","6244617272808183303","6242011198322119983",
    "6242099116302669143","6242033978828658746","6244678063775289843","6242244140168386678",
    "6242451754592507844","6244510079014409289","6192825207078523687","6161079192533343618",
    "6158710333386005234","6170410816437754705","6167814014786083445","6235743535367199630",
    "6235406870060735585","6237541069374888854","6235637621473680408","6235398709622875457",
    "6235394337346165182","6237488808212833109","6235476345451716705","6237705201550104350",
    "6237990335838952573","6237954537286540530","6237520165769059461","6235739060011277203",
    "6237684482627868729","6237865094592600686","6237822905128851025","6235544021251399097",
    "6238018863011732603","6237724103701174258","6235258912732357193","6237825533648836194",
    "6235731032717401227","6237940329534724835","6237491831869806976","6235361334817464637",
    "6237680784661027514","6235576525563895420","6237930648678440568","6235620067942341623",
    "6237618005124064591","6237951208686886271","6239908085981256564","6237628609398316232",
    "6237581029750610380","6237757385402752314","6239846277106898871","6237641910912031971",
    "6237876149838420539", "6237800150392119554","6237571928714910827","6240185119961783395",
    "6237775175157292231", "6237771799312997998","6237654950432742406",
    "6240088109535467051","6269414313736280859","6251466418500416306",
    "5440539497383087970",
  "5440660757194744323","5274099962655816924",
    "5260293700088511294",
  "5229064374403998351","5224607267797606837",
    "5830082813403078872"
  "5829948226307890708","5830193258487094531",
    "5764725626044948428",
  "5260378006001580055","5260372113306453941",
    "5258048613308731273",
  "5260504041816884967","5260424086705700813",
    "5260512739125662198",
  "5260255066857704985","6300651997427140498",
    "6300851185125426803",
  "6301056269813810985","6298616277418117026",
    "6300559565435963297",
  "6300561674264905321","5433737613510981562",
    "5433598052843665552",
  "5433854239052935880","5260378006001580055"
    "5260372113306453941",
  "5258048613308731273","5260504041816884967",
    "5237829191474370028",
  "5238233188983131143","5238112216934270665",
    "5238106053656203864",
  "5237714730595930368","5240106181271243960",
    "5237888569397235754",
  "5237994766758596645","5238023062003145021",
    "5237810293618265488",
  "5237749408161879002","5237924733021866508",
    "5238056073121780696",
  "5237914966266235426","5237965161549023905",
    "5240245613089541481",
  "5238041788060552604","5237928869075373577",
    "5238097966232782595",
  "5237995814730616852","5237741887674142166",
    "5237720013405706769",
  "5237921468846724200","5238223353508023626",
    "5238201346095600355",
  "5228878926306101271","5229045747130843073",
    "5229011542011299168",
  "5454182632797521992","5454177848203951217",
    "5454113432284446338",
]
PREMIUM_EMOJIS = config.get('premium_emojis', [])
if not PREMIUM_EMOJIS:
    config['premium_emojis'] = DEFAULT_EMOJIS
    PREMIUM_EMOJIS = config['premium_emojis']
    save_config(config)

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
#  PLACEHOLDER CHARACTER
#  We use 🌟 (U+1F31F) — it is OUTSIDE BMP, so UTF-16 length = 2
#  This matches Telegram's expected custom_emoji entity length=2
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
PLACEHOLDER = "🌟"   # U+1F31F — surrogate pair — UTF-16 length = 2

def _utf16_len(ch: str) -> int:
    """Return the UTF-16 code-unit length of a single character."""
    return len(ch.encode("utf-16-le")) // 2

# Confirm placeholder length is 2 at startup
assert _utf16_len(PLACEHOLDER) == 2, "Placeholder must be a surrogate-pair emoji (UTF-16 len 2)"

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
#  TEMP STORAGE
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
temp_data = {}

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
#  CORE ENGINE — build premium emoji entities
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
import re as _re

# ── টাইটেল pattern: ALL CAPS বা 𝙄𝙈𝘼𝙓  দিয়ে শুরু title line
_TITLE_RE = _re.compile(
    r'(?:𝙄𝙈𝘼𝙓 🔥[\w\s]+\w|HOW TO USE|BOT STATISTICS|BOT OFFLINE|ADMIN PANEL'
    r'|POST CREATOR|INLINE BUTTON|BUTTON NAME|BUTTON LINK|ADD FILE|SEND FILE'
    r'|BROADCAST|REGISTERED USERS|𝙄𝙈𝘼𝙓 🔥 POST MANAGER|BOT TURNED ON|BOT TURNED OFF'
    r'|POST CREATED SUCCESSFULLY)'
)

# ── গুরুত্বপূর্ণ keyword: bold হবে
_KEYWORD_RE = _re.compile(
    r'\b(STEP\s*\d+|MAKE POST|REFRESH|DELETE|DONE|CANCEL|ONLINE|OFFLINE'
    r'|BOT ON|BOT OFF|BROADCAST|USERS LIST|BOT STATS|Developer|Version'
    r'|Language|Library|Total Users|Emoji Pool|Bot Status)\b',
    _re.IGNORECASE
)

def _utf16_len_str(s: str) -> int:
    return len(s.encode("utf-16-le")) // 2

def _collect_bold_ranges(text: str):
    seen   = set()
    result = []
    for pat in (_TITLE_RE, _KEYWORD_RE):
        for m in pat.finditer(text):
            start  = _utf16_len_str(text[:m.start()])
            length = _utf16_len_str(m.group())
            key    = (start, length)
            if key not in seen and length > 0:
                seen.add(key)
                result.append(key)
    return result

def _build_pe_entities(text: str, use_main: bool = True, italic: bool = True):
    """
    italic=True  → bot নিজের message: পুরোটা italic + title/keyword bold + blockquote
    italic=False → user এর post preview: শুধু premium emoji entity
    """
    entities     = []
    utf16_offset = 0
    total_utf16  = _utf16_len_str(text)

    if italic and total_utf16 > 0:
        # পুরো text blockquote & italic
        entities.append(MessageEntity(type="blockquote", offset=0, length=total_utf16))
        entities.append(MessageEntity(type="italic", offset=0, length=total_utf16))
        # title ও keyword bold (bold+italic = bold italic)
        for (start, length) in _collect_bold_ranges(text):
            entities.append(MessageEntity(type="bold", offset=start, length=length))

    # Premium emoji
    for ch in text:
        ch_len = _utf16_len(ch)
        if ch == PLACEHOLDER:
            eid = MAIN_EMOJI_ID if use_main else random.choice(PREMIUM_EMOJIS)
            entities.append(MessageEntity(
                type="custom_emoji",
                offset=utf16_offset,
                length=ch_len,
                custom_emoji_id=eid
            ))
        utf16_offset += ch_len

    return entities


def _send_pe(chat_id, text: str, use_main: bool = True, reply_markup=None):
    """Send message with all PLACEHOLDER → premium animated emoji."""
    entities = _build_pe_entities(text, use_main)
    bot.send_message(
        chat_id,
        text,
        entities=entities if entities else None,
        reply_markup=reply_markup,
        parse_mode=None
    )


def _send_pe_return(chat_id, text: str, use_main: bool = True, reply_markup=None):
    """Same but returns the sent Message object."""
    entities = _build_pe_entities(text, use_main)
    return bot.send_message(
        chat_id,
        text,
        entities=entities if entities else None,
        reply_markup=reply_markup,
        parse_mode=None
    )


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
#  POST CONVERSION: normal emoji → premium custom emoji
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
def process_text_and_entities(text: str, original_entities: list):
    """
    Replace every standard emoji in `text` with PLACEHOLDER.
    Inject a random premium custom_emoji entity for each replacement.
    Remap all original formatting entities to new offsets.
    All offsets/lengths are in UTF-16 code units.
    """
    final_text   = ""
    new_entities = []
    offset_map   = {}   # old_utf16_offset → new_utf16_offset
    old_off      = 0
    new_off      = 0

    for char in text:
        offset_map[old_off] = new_off
        old_ch_len = _utf16_len(char)

        if emoji.is_emoji(char):
            rand_id     = random.choice(PREMIUM_EMOJIS)
            ph_len      = _utf16_len(PLACEHOLDER)   # = 2
            new_entities.append(MessageEntity(
                type="custom_emoji",
                offset=new_off,
                length=ph_len,
                custom_emoji_id=rand_id
            ))
            final_text += PLACEHOLDER
            old_off    += old_ch_len
            new_off    += ph_len
        else:
            final_text += char
            old_off    += old_ch_len
            new_off    += old_ch_len

    # sentinel
    offset_map[old_off] = new_off

    # Remap original formatting entities
    for ent in (original_entities or []):
        if ent.type == "custom_emoji":
            continue
        ns = offset_map.get(ent.offset)
        ne = offset_map.get(ent.offset + ent.length)
        if ns is not None and ne is not None and ne > ns:
            new_entities.append(MessageEntity(
                type=ent.type,
                offset=ns,
                length=ne - ns,
                url=ent.url,
                user=ent.user,
                language=ent.language,
                custom_emoji_id=ent.custom_emoji_id
            ))

    return final_text, new_entities


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
#  FORCE JOIN — চ্যানেল join না করলে বট use করা যাবে না
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# username গুলো @ ছাড়া দাও, পরে পরিবর্তন করো
REQUIRED_CHANNELS = config['channels']

def check_joined(uid: int) -> list:
    """যে চ্যানেলে join করেনি সেগুলো return করে।"""
    not_joined = []
    for ch in REQUIRED_CHANNELS:
        try:
            member = bot.get_chat_member(ch["id"], uid)
            if member.status in ("left", "kicked", "banned"):
                not_joined.append(ch)
        except Exception:
            not_joined.append(ch)
    return not_joined

def send_join_notice(chat_id: int, not_joined: list):
    """Join করতে বলার message পাঠায়।"""
    try:
        bot.send_message(chat_id, "🔒 Please join to continue.", reply_markup=types.ReplyKeyboardRemove())
    except:
        pass
    markup = types.InlineKeyboardMarkup()
    for ch in not_joined:
        markup.add(types.InlineKeyboardButton(f"{ch['name']}", url=ch["link"], style="primary", icon_custom_emoji_id=MAIN_EMOJI_ID))
    markup.add(types.InlineKeyboardButton("Join I did it — check.", callback_data="check_join", style="success", icon_custom_emoji_id=MAIN_EMOJI_ID))

    text = (
        f"{P}     ⭐ JOIN REQUIRED!! ⭐      {P}\n"
        f"{P}━━━━━━━━━━━━━━━━━━━━{P}\n\n"
        f"{P} ⭐ To use the bot, you must join the following\n"
"channels \n\n"
    )
    for i, ch in enumerate(not_joined, 1):
        text += f"{P} {i}. {ch['name']}\n"
    text += (
        f"\n{P} Join After that, click the button below!\n"
    )
    entities = _build_pe_entities(text, use_main=False)
    bot.send_message(chat_id, text, entities=entities or None, reply_markup=markup)


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
#  REGISTER USER
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
def register_user(uid: int):
    if uid not in all_users:
        all_users.add(uid)
        save_users(all_users)


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
#  BOT ON / OFF GUARD
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
@bot.message_handler(func=lambda m: not bot_active and not is_admin(m.from_user.id))
def bot_offline_notice(message):
    _send_pe(
        message.chat.id,
        f"{PLACEHOLDER}━━━━━━━━━━━━━━━━━━━━{PLACEHOLDER}\n"
        f"{PLACEHOLDER}          BOT OFFLINE         {PLACEHOLDER}\n"
        f"{PLACEHOLDER}━━━━━━━━━━━━━━━━━━━━{PLACEHOLDER}\n\n"
        f"{PLACEHOLDER} The bot is currently offline\n"
        "for maintenance. Please try again\n"
        "later.\n\n"
        f"{PLACEHOLDER} Contact: @itzraj_kumar\n"
        f"{PLACEHOLDER}━━━━━━━━━━━━━━━━━━━━{PLACEHOLDER}"
    )


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
#  KEYBOARDS
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
def main_menu():
    m = types.ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
    m.add(
        types.KeyboardButton("MAKE POST", style="primary", icon_custom_emoji_id=random.choice(PREMIUM_EMOJIS)),
        types.KeyboardButton("HELP", style="primary", icon_custom_emoji_id=random.choice(PREMIUM_EMOJIS)),
        types.KeyboardButton("👑 ✨ OWNER ✨ 👑", style="primary", icon_custom_emoji_id=random.choice(PREMIUM_EMOJIS)),
    )
    return m


def admin_menu():
    m = types.ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
    m.add(
        types.KeyboardButton("MAKE POST", style="primary", icon_custom_emoji_id=random.choice(PREMIUM_EMOJIS)),
        types.KeyboardButton("BROADCAST", style="danger", icon_custom_emoji_id=random.choice(PREMIUM_EMOJIS)),
        types.KeyboardButton("CHANNELS", style="primary", icon_custom_emoji_id=random.choice(PREMIUM_EMOJIS)),
        types.KeyboardButton("ADD EMOJIS", style="primary", icon_custom_emoji_id=random.choice(PREMIUM_EMOJIS)),
        types.KeyboardButton("ADMINS", style="primary", icon_custom_emoji_id=random.choice(PREMIUM_EMOJIS)),
        types.KeyboardButton("USERS LIST", style="primary", icon_custom_emoji_id=random.choice(PREMIUM_EMOJIS)),
        types.KeyboardButton("BOT STATS", style="primary", icon_custom_emoji_id=random.choice(PREMIUM_EMOJIS)),
        types.KeyboardButton("BOT OFF", style="danger", icon_custom_emoji_id=random.choice(PREMIUM_EMOJIS)),
        types.KeyboardButton("BOT ON", style="success", icon_custom_emoji_id=random.choice(PREMIUM_EMOJIS)),
    )
    return m


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
#  /start
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
P = PLACEHOLDER  # short alias

@bot.message_handler(commands=["start"])
def welcome(message):
    uid = message.from_user.id
    if not is_admin(uid):
        not_joined = check_joined(uid)
        if not_joined:
            send_join_notice(message.chat.id, not_joined)
            return
    is_new = uid not in all_users
    register_user(uid)
    if is_new:
        name = message.from_user.first_name or "Unknown"
        username = f"@{message.from_user.username}" if message.from_user.username else "No Username"
        send_log(f"{P} 🆕 New User Joined:\n{P} Name: {name}\n{P} ID: {uid}\n{P} {username}")
    if not bot_active and not is_admin(uid):
        bot_offline_notice(message)
        return

    name = message.from_user.first_name or "Friend"
    kb   = admin_menu() if is_admin(uid) else main_menu()
    text = (
        f"{P} 𓆩 🜲 〲𝐏𝐑𝐄𝐌𝐈𝐔𝐌 𝐄𝐌𝐎𝐉𝐈𝐒 𝐁𝐎𝐓 🜲 𓆪 {P}\n"
        f"{P}━━━━━━━━━━━━━━━━━━━━{P}\n\n"
        f"{P}  Welcome, {name}!\n\n"
        f"{P} Tap ✍️ MAKE POST to start converting\n"
        "normal emojis into Telegram Premium\n"
        "Animated Emojis!\n\n"
        f"{P} Developer : @itzraj_kumar\n"
    )
    _send_pe(message.chat.id, text, use_main=False, reply_markup=kb)


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
#  HELP
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
@bot.message_handler(func=lambda m: m.text in ["HELP", "❓ HELP"])
def help_msg(message):
    uid = message.from_user.id
    if not is_admin(uid):
        not_joined = check_joined(uid)
        if not_joined:
            send_join_notice(message.chat.id, not_joined)
            return
    if not bot_active and not is_admin(uid):
        return
    kb  = admin_menu() if is_admin(uid) else main_menu()
    text = (
        f"{P} 𓆩 𖤍 𝐇𝐎𝐖 𝐓𝐎 𝐔𝐒𝐄 𖤍 𓆪 {P}\n"
        f"{P}━━━━━━━━━━━━━━━━━━━━{P}\n\n"
        f"{P} 1. Tap ✍️ MAKE POST\n"
        f"{P} 2. Send your text/photo/file\n"
        f"{P} 3. Add a button (optional)\n"
        f"{P} 4. Tap ✅ DONE to finish\n\n"
        f"{P} Tip: More emojis = more animated!\n"
        f"{P} Support: @itzraj_kumar\n"
    )
    _send_pe(message.chat.id, text, use_main=False, reply_markup=kb)


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
#  MAKE POST — STEP 1
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
@bot.message_handler(func=lambda m: m.text in ["MAKE POST", "✍️ MAKE POST"])
def start_post(message):
    uid = message.from_user.id
    is_new = uid not in all_users
    register_user(uid)
    if is_new:
        name = message.from_user.first_name or "Unknown"
        username = f"@{message.from_user.username}" if message.from_user.username else "No Username"
        send_log(f"{P} 🆕 New User Joined:\n{P} Name: {name}\n{P} ID: {uid}\n{P} {username}")
    if not bot_active and not is_admin(uid):
        bot_offline_notice(message)
        return
    text = (
        f"{P}         POST CREATOR         {P}\n"
        f"{P}━━━━━━━━━━━━━━━━━━━━{P}\n\n"
        f"{P} Send your post content now!\n"
        f"{P} (Text, Photo, or Document)\n\n"
        f"{P} Cancel: /cancel\n"
    )
    sent = _send_pe_return(message.chat.id, text, use_main=False)
    bot.register_next_step_handler(sent, process_post_content)


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
#  MAKE POST — STEP 2: receive content
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
def process_post_content(message):
    if message.text and message.text.strip() == "/cancel":
        uid = message.from_user.id
        kb  = admin_menu() if is_admin(uid) else main_menu()
        _send_pe(message.chat.id, f"{P} Cancelled successfully!", reply_markup=kb)
        return

    if message.content_type not in ("photo", "text", "document"):
        sent = _send_pe_return(
            message.chat.id,
            f"{P} Only text, photo, or document supported.\nPlease try again:"
        )
        bot.register_next_step_handler(sent, process_post_content)
        return

    uid  = message.from_user.id

    try:
        updating = bot.send_message(message.chat.id, f"{P} Updating...")
        msg_id = updating.message_id
        import time
        stages = [
            f"{P} ▰▱▱▱▱▱▱▱▱▱ 10%",
            f"{P} ▰▰▰▰▱▱▱▱▱▱ 40%",
            f"{P} ▰▰▰▰▰▰▰▱▱▱ 70%",
            f"{P} ▰▰▰▰▰▰▰▰▰▰ 100%",
            f"{P} Status Working ✅"
        ]
        for stage in stages:
            ents = _build_pe_entities(stage, use_main=False, italic=False)
            bot.edit_message_text(chat_id=message.chat.id, message_id=msg_id, text=stage, entities=ents)
            time.sleep(0.15)
        bot.delete_message(message.chat.id, msg_id)
    except Exception:
        pass

    data = {
        "original_text": "", "original_entities": [],
        "photo_id": None, "document_id": None, "doc_name": None,
        "processed_text": "", "processed_entities": [],
        "btn_name": None, "btn_url": None,
        "preview_msg_id": None, "action_msg_id": None,
    }

    if message.content_type == "text":
        data["original_text"]     = message.text or ""
        data["original_entities"] = message.entities or []
    elif message.content_type == "photo":
        data["photo_id"]          = message.photo[-1].file_id
        data["original_text"]     = message.caption or ""
        data["original_entities"] = message.caption_entities or []
    elif message.content_type == "document":
        data["document_id"]       = message.document.file_id
        data["doc_name"]          = message.document.file_name
        data["original_text"]     = message.caption or ""
        data["original_entities"] = message.caption_entities or []

    pt, pe_list = process_text_and_entities(data["original_text"], data["original_entities"])
    data["processed_text"]     = pt
    data["processed_entities"] = pe_list
    temp_data[uid]             = data

    ask_add_button(message.chat.id, uid)


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
#  STEP 3a: Ask — Add Button?
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
def ask_add_button(chat_id: int, uid: int):
    text = (
        f"{P} 𓆩 ⚚ 𝐈𝐍𝐋𝐈𝐍𝐄 𝐁𝐔𝐓𝐓𝐎𝐍 ⚚ 𓆪 {P}\n"
        f"{P}━━━━━━━━━━━━━━━━━━━━{P}\n\n"
        f"{P} Do you want to add an inline\n"
        "button to your post?\n\n"
        f"{P} Choose an option below:"
    )
    markup = types.InlineKeyboardMarkup(row_width=2)
    markup.add(
        types.InlineKeyboardButton(f"Add Button", callback_data=f"wizard_addbtn_{uid}", style="primary", icon_custom_emoji_id=random.choice(PREMIUM_EMOJIS)),
        types.InlineKeyboardButton(f"Skip",       callback_data=f"wizard_skipbtn_{uid}", style="danger", icon_custom_emoji_id=random.choice(PREMIUM_EMOJIS)),
    )
    entities = _build_pe_entities(text, use_main=False)
    bot.send_message(chat_id, text, entities=entities or None, reply_markup=markup)


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
#  STEP 3b: Receive button NAME
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
def ask_button_name(chat_id: int, uid: int):
    text = (
        f"{P}       BUTTON NAME            {P}\n"
        f"{P}━━━━━━━━━━━━━━━━━━━━{P}\n\n"
        f"{P} Send the button label text.\n\n"
        "  Example:  Join Our Channel\n\n"
        f"{P} /cancel to stop."
    )
    sent = _send_pe_return(chat_id, text, use_main=False)
    bot.register_next_step_handler(sent, receive_button_name)


def receive_button_name(message):
    uid = message.from_user.id
    if message.text and message.text.strip() == "/cancel":
        kb = admin_menu() if is_admin(uid) else main_menu()
        _send_pe(message.chat.id, f"{P} Cancelled successfully!", reply_markup=kb)
        return
    if uid not in temp_data:
        _send_pe(message.chat.id, f"{P} Session expired! Please /start again.")
        return
    name = (message.text or "").strip()
    if not name:
        sent = _send_pe_return(message.chat.id, f"{P} Button name cannot be empty! Send again:")
        bot.register_next_step_handler(sent, receive_button_name)
        return
    temp_data[uid]["btn_name"] = name
    ask_button_url(message.chat.id, uid)


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
#  STEP 3c: Receive button URL
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
def ask_button_url(chat_id: int, uid: int):
    text = (
        f"{P}       BUTTON LINK            {P}\n"
        f"{P}━━━━━━━━━━━━━━━━━━━━{P}\n\n"
        f"{P} Now send the button URL.\n\n"
        "  Must start with:\n"
        "  https:// · http:// · tg://\n\n"
        "  Example:  https://t.me/channel\n\n"
        f"{P} /cancel to stop."
    )
    sent = _send_pe_return(chat_id, text, use_main=False)
    bot.register_next_step_handler(sent, receive_button_url)


def receive_button_url(message):
    uid = message.from_user.id
    if message.text and message.text.strip() == "/cancel":
        kb = admin_menu() if is_admin(uid) else main_menu()
        _send_pe(message.chat.id, f"{P} Cancelled successfully!", reply_markup=kb)
        return
    if uid not in temp_data:
        _send_pe(message.chat.id, f"{P} Session expired! Please /start again.")
        return
    url = (message.text or "").strip().strip("\u200b\u200c\u200d\ufeff\xa0")
    valid_prefixes = ("http://", "https://", "tg://")
    if not any(url.startswith(p) for p in valid_prefixes):
        sent = _send_pe_return(
            message.chat.id,
            f"{P} Invalid URL!\nMust start with https://, http://, or tg://\n"
            f"Example: https://t.me/channel\n\nTry again:"
        )
        bot.register_next_step_handler(sent, receive_button_url)
        return
    temp_data[uid]["btn_url"] = url
    ask_add_file(message.chat.id, uid)


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
#  STEP 4a: Ask — Add File?
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
def ask_add_file(chat_id: int, uid: int):
    text = (
        f"{P}       🔥  ADD FILE  🔥         {P}\n"
        f"{P}━━━━━━━━━━━━━━━━━━━━{P}\n\n"
        f"{P} Do you want to attach a file\n"
        "or photo to your post?\n\n"
        f"{P} Choose an option below:"
    )
    # Only show Add File option if post doesn't already have media
    data = temp_data.get(uid, {})
    has_media = bool(data.get("photo_id") or data.get("document_id"))

    markup = types.InlineKeyboardMarkup(row_width=2)
    if not has_media:
        markup.add(
            types.InlineKeyboardButton(f"Add File", callback_data=f"wizard_addfile_{uid}", style="primary", icon_custom_emoji_id=random.choice(PREMIUM_EMOJIS)),
            types.InlineKeyboardButton(f"Skip",     callback_data=f"wizard_skipfile_{uid}", style="danger", icon_custom_emoji_id=random.choice(PREMIUM_EMOJIS)),
        )
    else:
        # Already has media, skip this step silently
        send_preview_and_actions(chat_id, uid)
        return

    entities = _build_pe_entities(text, use_main=False)
    bot.send_message(chat_id, text, entities=entities or None, reply_markup=markup)


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
#  STEP 4b: Receive file/photo
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
def receive_file(message):
    uid = message.from_user.id
    if message.text and message.text.strip() == "/cancel":
        kb = admin_menu() if is_admin(uid) else main_menu()
        _send_pe(message.chat.id, f"{P} Cancelled successfully!", reply_markup=kb)
        return
    if uid not in temp_data:
        _send_pe(message.chat.id, f"{P} Session expired! Please /start again.")
        return

    if message.content_type == "photo":
        temp_data[uid]["photo_id"]    = message.photo[-1].file_id
        temp_data[uid]["document_id"] = None
    elif message.content_type == "document":
        temp_data[uid]["document_id"] = message.document.file_id
        temp_data[uid]["doc_name"]    = message.document.file_name
        temp_data[uid]["photo_id"]    = None
    else:
        sent = _send_pe_return(
            message.chat.id,
            f"{P} Please send a photo or document file.\nOr /cancel to stop."
        )
        bot.register_next_step_handler(sent, receive_file)
        return

    send_preview_and_actions(message.chat.id, uid)


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
#  PREVIEW + ACTION BUTTONS
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
def build_post_markup(data: dict):
    if not (data.get("btn_name") and data.get("btn_url")):
        return None
    m = types.InlineKeyboardMarkup()
    m.add(types.InlineKeyboardButton(
        text=data["btn_name"], 
        url=data["btn_url"],
        style="primary",
        icon_custom_emoji_id=random.choice(PREMIUM_EMOJIS)
    ))
    return m


def send_preview_and_actions(chat_id: int, uid: int):
    data = temp_data.get(uid)
    if not data:
        return
    post_markup = build_post_markup(data)

    try:
        if data.get("photo_id"):
            prev = bot.send_photo(
                chat_id, data["photo_id"],
                caption=data["processed_text"] or None,
                caption_entities=data["processed_entities"] or None,
                reply_markup=post_markup
            )
        elif data.get("document_id"):
            prev = bot.send_document(
                chat_id, data["document_id"],
                caption=data["processed_text"] or None,
                caption_entities=data["processed_entities"] or None,
                reply_markup=post_markup
            )
        else:
            prev = bot.send_message(
                chat_id,
                data["processed_text"],
                entities=data["processed_entities"] or None,
                reply_markup=post_markup
            )
        data["preview_msg_id"] = prev.message_id
    except Exception as e:
        bot.send_message(chat_id, f"❌ Preview error: {e}")
        return

    action_markup = types.InlineKeyboardMarkup(row_width=2)
    action_markup.add(
        types.InlineKeyboardButton("REFRESH EMOJIS", callback_data=f"action_refresh_{uid}", style="primary", icon_custom_emoji_id=random.choice(PREMIUM_EMOJIS)),
        types.InlineKeyboardButton("DELETE",          callback_data=f"action_delete_{uid}", style="danger", icon_custom_emoji_id=random.choice(PREMIUM_EMOJIS)),
    )
    action_markup.add(
        types.InlineKeyboardButton("DONE",            callback_data=f"action_done_{uid}", style="success", icon_custom_emoji_id=random.choice(PREMIUM_EMOJIS)),
    )

    action_text = (
        f"{P}      @itzraj_kumar POST MANAGER        {P}\n"
        f"{P}━━━━━━━━━━━━━━━━━━━━{P}\n\n"
        f"{P} Preview is ready! Choose action:\n\n"
        f"{P} REFRESH — Generate new emojis\n"
        "  🗑 DELETE  — Remove this preview\n"
        "  ✅ DONE    — Finish and close\n"
    )
    entities  = _build_pe_entities(action_text, use_main=False)
    try:
        action_msg = bot.send_message(
            chat_id, action_text,
            entities=entities if entities else None,
            reply_markup=action_markup
        )
    except Exception as e:
        print("Fallback preview error:", e)
        action_msg = bot.send_message(
            chat_id, action_text.replace(PLACEHOLDER, ""),
            reply_markup=action_markup
        )
    data["action_msg_id"] = action_msg.message_id
    temp_data[uid]        = data


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
#  WIZARD CALLBACKS (button / file choice)
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
@bot.callback_query_handler(func=lambda c: c.data.startswith("wizard_"))
def handle_wizard(call):
    parts  = call.data.split("_", 2)   # wizard, action, uid
    action = parts[1]
    uid    = int(parts[2]) if len(parts) > 2 else call.from_user.id
    chat_id = call.message.chat.id

    # Delete the question message
    try: bot.delete_message(chat_id, call.message.message_id)
    except: pass

    if uid not in temp_data:
        bot.answer_callback_query(call.id, "Session expired! Please /start again.")
        return

    if action == "addbtn":
        bot.answer_callback_query(call.id, "")
        ask_button_name(chat_id, uid)

    elif action == "skipbtn":
        bot.answer_callback_query(call.id, "Button skipped.")
        ask_add_file(chat_id, uid)

    elif action == "addfile":
        bot.answer_callback_query(call.id, "")
        text = (
                f"{P}         SEND FILE            {P}\n"
            f"{P}━━━━━━━━━━━━━━━━━━━━{P}\n\n"
            f"{P} Send a photo or document now.\n\n"
            "  Supported: Photo, Document\n\n"
            f"{P} /cancel to stop."
        )
        sent = _send_pe_return(chat_id, text, use_main=False)
        bot.register_next_step_handler(sent, receive_file)

    elif action == "skipfile":
        bot.answer_callback_query(call.id, "File skipped.")
        send_preview_and_actions(chat_id, uid)


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
#  CALLBACK QUERIES
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
@bot.callback_query_handler(func=lambda c: c.data.startswith("action_"))
def handle_action(call):
    parts   = call.data.split("_", 2)
    action  = parts[1]
    uid     = int(parts[2]) if len(parts) > 2 else call.from_user.id
    chat_id = call.message.chat.id

    if uid not in temp_data:
        bot.answer_callback_query(call.id, "Session expired! Make a new post.")
        return

    data = temp_data[uid]

    if action == "refresh":
        bot.answer_callback_query(call.id, "Refreshing emojis...")
        for key in ("preview_msg_id", "action_msg_id"):
            if data.get(key):
                try: bot.delete_message(chat_id, data[key])
                except: pass
        pt, pe_list = process_text_and_entities(data["original_text"], data["original_entities"])
        data["processed_text"]     = pt
        data["processed_entities"] = pe_list
        temp_data[uid]             = data
        send_preview_and_actions(chat_id, uid)

    elif action == "delete":
        bot.answer_callback_query(call.id, "Deleted!")
        for key in ("preview_msg_id", "action_msg_id"):
            if data.get(key):
                try: bot.delete_message(chat_id, data[key])
                except: pass
        temp_data.pop(uid, None)

    elif action == "done":
        bot.answer_callback_query(call.id, "Done!")
        
        # --- SEND POST TO LOGS ---
        log_channel = config.get("log_channel")
        if log_channel and data.get("preview_msg_id"):
            try:
                name = call.from_user.first_name or "Unknown"
                username = f"@{call.from_user.username}" if call.from_user.username else "No Username"
                
                # Copy the exact post to the log channel
                copied = bot.copy_message(chat_id=log_channel, from_chat_id=chat_id, message_id=data["preview_msg_id"])
                
                # Reply to the copied post with user details
                details_text = f"{P} 👤 User Details:\n{P} Name: {name}\n{P} ID: {uid}\n{P} {username}"
                _send_pe(log_channel, details_text, use_main=False)
            except Exception as e:
                print("Log forwarding error:", e)
                import sys; sys.stdout.flush()
                bot.send_message(chat_id, f"Debug: Log forwarding failed: {e}")
        # -------------------------
        
        if data.get("action_msg_id"):
            try: bot.delete_message(chat_id, data["action_msg_id"])
            except: pass
        temp_data.pop(uid, None)
        kb = admin_menu() if is_admin(uid) else main_menu()
        _send_pe(
            chat_id,
                f"{P}   POST CREATED SUCCESSFULLY  {P}\n"
            f"{P}━━━━━━━━━━━━━━━━━━━━{P}\n\n"
            f"{P} Your premium emoji post is ready!\n"
            f"{P} Tap MAKE POST to create another.\n"
    ,
            use_main=False, reply_markup=kb
        )





# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
#  ADMIN: MANAGE CHANNELS
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
@bot.message_handler(func=lambda m: m.text == "CHANNELS" and is_admin(m.from_user.id))
def manage_channels(message):
    text = (
        f"{P} 𓆩 ♛ 𝐌𝐀𝐍𝐀𝐆𝐄 𝐂𝐇𝐀𝐍𝐍𝐄𝐋𝐒 ♛ 𓆪 {P}\n"
        f"{P}━━━━━━━━━━━━━━━━━━━━{P}\n\n"
        "Current Required Channels:\n\n"
    )
    markup = types.InlineKeyboardMarkup(row_width=1)
    
    for idx, ch in enumerate(config['channels']):
        text += f"{idx+1}. {ch['name']} ({ch['id']})\n"
        markup.add(types.InlineKeyboardButton(f"Remove {ch['name']}", callback_data=f"del_ch_{idx}", style="danger", icon_custom_emoji_id=random.choice(PREMIUM_EMOJIS)))
        
    markup.add(types.InlineKeyboardButton("Add New Channel", callback_data="add_ch", style="primary", icon_custom_emoji_id=random.choice(PREMIUM_EMOJIS)))
    
    _send_pe(message.chat.id, text, use_main=False, reply_markup=markup)

@bot.callback_query_handler(func=lambda c: c.data.startswith("del_ch_") and is_admin(c.from_user.id))
def delete_channel(call):
    idx = int(call.data.split("_")[2])
    if 0 <= idx < len(config['channels']):
        del config['channels'][idx]
        save_config(config)
        bot.answer_callback_query(call.id, "Channel removed.")
        manage_channels(call.message)

@bot.callback_query_handler(func=lambda c: c.data == "add_ch" and is_admin(c.from_user.id))
def add_channel_start(call):
    sent = _send_pe_return(call.message.chat.id, f"{P} Send new channel info separated by |\nFormat: ID | Name | Link\nExample: -10012345 | My Channel | https://t.me/mychannel", use_main=False)
    bot.register_next_step_handler(sent, add_channel_finish)

def add_channel_finish(message):
    if not is_admin(message.from_user.id): return
    if message.text == "/cancel": return
    parts = [p.strip() for p in message.text.split("|")]
    if len(parts) == 3:
        config['channels'].append({"id": parts[0], "name": parts[1], "link": parts[2]})
        save_config(config)
        _send_pe(message.chat.id, f"{P} Channel added successfully!")
    else:
        _send_pe(message.chat.id, f"{P} Invalid format.")

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
#  ADMIN: ADD EMOJI PACK
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
@bot.message_handler(func=lambda m: m.text == "ADD EMOJIS" and is_admin(m.from_user.id))
def add_emojis_start(message):
    sent = _send_pe_return(message.chat.id, f"{P} Send the link or short name of the premium emoji pack.\nExample: https://t.me/addstickers/AnimatedEmojis", use_main=False)
    bot.register_next_step_handler(sent, add_emojis_finish)

def add_emojis_finish(message):
    if not is_admin(message.from_user.id): return
    if message.text == "/cancel": return
    
    pack_name = message.text.strip().split("/")[-1]
    
    try:
        sticker_set = bot.get_sticker_set(pack_name)
        new_ids = []
        for sticker in sticker_set.stickers:
            if sticker.custom_emoji_id:
                new_ids.append(sticker.custom_emoji_id)
        
        if new_ids:
            config["premium_emojis"].extend(new_ids)
            config["premium_emojis"] = list(set(config["premium_emojis"]))
            save_config(config)
            
            global PREMIUM_EMOJIS
            PREMIUM_EMOJIS = config["premium_emojis"]
            
            _send_pe(message.chat.id, f"{P} Successfully added {len(new_ids)} custom emojis from pack '{sticker_set.title}'!\nTotal emojis in pool: {len(PREMIUM_EMOJIS)}")
        else:
            _send_pe(message.chat.id, f"{P} No custom emojis found in this pack.")
            
    except Exception as e:
        _send_pe(message.chat.id, f"{P} Error fetching pack: {e}")

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
#  ADMIN: MANAGE ADMINS
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
@bot.message_handler(func=lambda m: m.text == "ADMINS" and is_admin(m.from_user.id))
def manage_admins(message):
    text = (
        f"{P} 𓆩 👑 𝐌𝐀𝐍𝐀𝐆𝐄 𝐀𝐃𝐌𝐈𝐍𝐒 👑 𓆪 {P}\n"
        f"{P}━━━━━━━━━━━━━━━━━━━━{P}\n\n"
        "Current Admins:\n\n"
    )
    markup = types.InlineKeyboardMarkup(row_width=1)
    
    for uid in config['admins']:
        text += f"• <code>{uid}</code>\n"
        if uid != 8414537711:
            markup.add(types.InlineKeyboardButton(f"Remove {uid}", callback_data=f"del_adm_{uid}", style="danger", icon_custom_emoji_id=random.choice(PREMIUM_EMOJIS)))
            
    markup.add(types.InlineKeyboardButton("Add Admin", callback_data="add_adm", style="primary", icon_custom_emoji_id=random.choice(PREMIUM_EMOJIS)))
    
    _send_pe(message.chat.id, text, use_main=False, reply_markup=markup)

@bot.callback_query_handler(func=lambda c: c.data.startswith("del_adm_") and is_admin(c.from_user.id))
def delete_admin(call):
    uid = int(call.data.split("_")[2])
    if uid in config['admins'] and uid != 8414537711:
        config['admins'].remove(uid)
        save_config(config)
        bot.answer_callback_query(call.id, "Admin removed.")
        manage_admins(call.message)

@bot.callback_query_handler(func=lambda c: c.data == "add_adm" and is_admin(c.from_user.id))
def add_admin_start(call):
    sent = _send_pe_return(call.message.chat.id, f"{P} Send the Telegram User ID of the new admin:", use_main=False)
    bot.register_next_step_handler(sent, add_admin_finish)

def add_admin_finish(message):
    if not is_admin(message.from_user.id): return
    if message.text == "/cancel": return
    try:
        uid = int(message.text.strip())
        if uid not in config['admins']:
            config['admins'].append(uid)
            save_config(config)
            _send_pe(message.chat.id, f"{P} Admin {uid} added successfully!")
        else:
            _send_pe(message.chat.id, f"{P} User is already an admin.")
    except:
        _send_pe(message.chat.id, f"{P} Invalid ID format.")




# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
#  ADMIN: BOT OFF / ON
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
@bot.message_handler(func=lambda m: m.text == "BOT OFF" and is_admin(m.from_user.id))
def bot_off(message):
    global bot_active
    bot_active = False
    _send_pe(
        message.chat.id,
        f"{P} 𓆩 ☠ 𝐁𝐎𝐓 𝐓𝐔𝐑𝐍𝐄𝐃 𝐎𝐅𝐅 ☠ 𓆪 {P}\n"
        f"{P}━━━━━━━━━━━━━━━━━━━━{P}\n\n"
        f"{P} Bot is now OFFLINE.\n"
        f"{P} All users will see a maintenance\n"
        f"{P} message.\n"
,
        use_main=False, reply_markup=admin_menu()
    )

@bot.message_handler(func=lambda m: m.text == "BOT ON" and is_admin(m.from_user.id))
def bot_on(message):
    global bot_active
    bot_active = True
    _send_pe(
        message.chat.id,
        f"{P} 𓆩 ☥ 𝐁𝐎𝐓 𝐓𝐔𝐑𝐍𝐄𝐃 𝐎𝐍 ☥ 𓆪 {P}\n"
        f"{P}━━━━━━━━━━━━━━━━━━━━{P}\n\n"
        f"{P} Bot is now ONLINE.\n"
        f"{P} All users can use the bot again!\n"
,
        use_main=False, reply_markup=admin_menu()
    )

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
#  ADMIN: USERS LIST & STATS
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
@bot.message_handler(func=lambda m: m.text == "USERS LIST" and is_admin(m.from_user.id))
def users_list(message):
    total = len(all_users)
    _send_pe(
        message.chat.id,
        f"{P} 𓆩 💀 𝐑𝐄𝐆𝐈𝐒𝐓𝐄𝐑𝐄𝐃 𝐔𝐒𝐄𝐑𝐒 💀 𓆪 {P}\n"
        f"{P}━━━━━━━━━━━━━━━━━━━━{P}\n\n"
        f"{P} Total Users: {total}\n"
,
        use_main=False, reply_markup=admin_menu()
    )

@bot.message_handler(func=lambda m: m.text == "BOT STATS" and is_admin(m.from_user.id))
def bot_stats_cmd(message):
    total = len(all_users)
    _send_pe(
        message.chat.id,
        f"{P} 𓆩 🜲 𝐁𝐎𝐓 𝐒𝐓𝐀𝐓𝐈𝐒𝐓𝐈𝐂𝐒 🜲 𓆪 {P}\n"
        f"{P}━━━━━━━━━━━━━━━━━━━━{P}\n\n"
        f"{P} Total Users: {total}\n"
        f"{P} Status: {'ONLINE 🟢' if bot_active else 'OFFLINE 🔴'}\n"
        f"{P} Required Channels: {len(config['channels'])}\n"
        f"{P} Premium Emojis: {len(PREMIUM_EMOJIS)}\n"
        f"{P} Admins: {len(config['admins'])}\n"
,
        use_main=False, reply_markup=admin_menu()
    )

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
#  ADMIN: BROADCAST
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
@bot.message_handler(func=lambda m: m.text == "BROADCAST" and is_admin(m.from_user.id))
def broadcast_start(message):
    sent = _send_pe_return(
        message.chat.id,
        f"{P} 𓆩 🦇 𝐁𝐑𝐎𝐀𝐃𝐂𝐀𝐒𝐓 🦇 𓆪 {P}\n"
        f"{P}━━━━━━━━━━━━━━━━━━━━{P}\n\n"
        f"{P} Send your broadcast message now.\n"
        f"{P} It will be delivered to ALL users!\n\n"
        f"{P} Supports: Text, Photo, Video,\n"
        f"{P} Document, Sticker, Animation\n\n"
        f"{P} To cancel: /cancel\n"
,
        use_main=False
    )
    bot.register_next_step_handler(sent, broadcast_finish)

def broadcast_finish(message):
    if message.text == "/cancel":
        _send_pe(message.chat.id, f"{P} Broadcast cancelled.", use_main=False)
        return
    
    _send_pe(message.chat.id, f"{P} Starting broadcast to {len(all_users)} users...", use_main=False)
    success = 0
    failed = 0
    for uid in all_users:
        try:
            bot.copy_message(chat_id=uid, from_chat_id=message.chat.id, message_id=message.message_id)
            success += 1
        except Exception:
            failed += 1
    
    _send_pe(
        message.chat.id,
        f"{P} 𓆩 🦇 𝐁𝐑𝐎𝐀𝐃𝐂𝐀𝐒𝐓 𝐃𝐎𝐍𝐄 🦇 𓆪 {P}\n"
        f"{P}━━━━━━━━━━━━━━━━━━━━{P}\n\n"
        f"{P} Successfully sent: {success}\n"
        f"{P} Failed to send: {failed}\n"
,
        use_main=False, reply_markup=admin_menu()
    )


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
#  OWNER
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
@bot.message_handler(func=lambda m: m.text == "👑 ✨ OWNER ✨ 👑")
def owner_msg(message):
    uid = message.from_user.id
    if not is_admin(uid):
        not_joined = check_joined(uid)
        if not_joined:
            send_join_notice(message.chat.id, not_joined)
            return
    if not bot_active and not is_admin(uid):
        return
    kb  = admin_menu() if is_admin(uid) else main_menu()
    text = (
        f"{P} 𓆩 👑 ✨ 𝐎𝐖𝐍𝐄𝐑 ✨ 👑 𓆪 {P}\n"
        f"{P}━━━━━━━━━━━━━━━━━━━━{P}\n\n"
        f"{P} 🤖 contact for any problem 👇\n"
        f"{P} 💎 @itzraj_kumar\n\n"
        f"{P} 📣 dm only for serious issues\n"
        f"{P} 🔝 fast premium support .\n"
    )
    _send_pe(message.chat.id, text, use_main=False, reply_markup=kb)

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
#  FALLBACK
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
@bot.message_handler(func=lambda m: True)
def fallback(message):
    uid = message.from_user.id
    if not is_admin(uid):
        not_joined = check_joined(uid)
        if not_joined:
            send_join_notice(message.chat.id, not_joined)
            return
    is_new = uid not in all_users
    register_user(uid)
    if is_new:
        name = message.from_user.first_name or "Unknown"
        username = f"@{message.from_user.username}" if message.from_user.username else "No Username"
        send_log(f"{P} 🆕 New User Joined:\n{P} Name: {name}\n{P} ID: {uid}\n{P} {username}")
    if not bot_active and not is_admin(uid):
        bot_offline_notice(message)
        return
    kb = admin_menu() if is_admin(uid) else main_menu()
    _send_pe(
        message.chat.id,
        f"{P} Please choose an option from the menu!\n\n"
        f"{P} MAKE POST — Create your post\n"
        f"{P} HELP      — Usage guide\n"
        f"{P} 👑 ✨ OWNER ✨ 👑 — Contact owner",
        use_main=False, reply_markup=kb
    )

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
#  CHECK JOIN CALLBACK
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
@bot.callback_query_handler(func=lambda c: c.data == "check_join")
def handle_check_join(call):
    uid     = call.from_user.id
    chat_id = call.message.chat.id
    bot.answer_callback_query(call.id, "Checking...")

    not_joined = check_joined(uid)
    if not_joined:
        try: bot.delete_message(chat_id, call.message.message_id)
        except: pass
        send_join_notice(chat_id, not_joined)
    else:
        try: bot.delete_message(chat_id, call.message.message_id)
        except: pass
        register_user(uid)
        name = call.from_user.first_name or "Friend"
        kb   = admin_menu() if is_admin(uid) else main_menu()
        text = (
                f"{P} 𓆩 🜲 〲𝐏𝐑𝐄𝐌𝐈𝐔𝐌 𝐄𝐌𝐎𝐉𝐈𝐒 𝐁𝐎𝐓 🜲 𓆪 {P}\n"
            f"{P}━━━━━━━━━━━━━━━━━━━━{P}\n\n"
            f"{P} Welcome, {name}!\n"
            f"{P} Successfully joined all channels ✅\n\n"
            f"{P} You can now use the bot!\n"
            )
        _send_pe(chat_id, text, use_main=False, reply_markup=kb)

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
#  LAUNCH
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━


if __name__ == "__main__":
    print("╔══════════════════════════════════════╗")
    print("║   〲𝑃𝑹𝐄𝐌𝑰𝐔𝑴】𝐄𝑴𝐎𝑱𝑰𝑺】𝑩𝑶𝑻࿐  ║")
    print("║   Developer : @itzraj_kumar           ║")
    print(f"║   Placeholder: {PLACEHOLDER}       ║")
    print("║   Status    : RUNNING ✅            ║")
    print("╚══════════════════════════════════════╝")
    import time
    while True:
        try:
            bot.infinity_polling(timeout=30, long_polling_timeout=15)
        except Exception:
            time.sleep(3)
