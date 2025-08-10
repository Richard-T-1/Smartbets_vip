import logging
import os
import json
import time
import requests
from flask import Flask, request, jsonify

# Vypnutie verbose logov
logging.basicConfig(level=logging.WARNING)
logging.getLogger("httpx").setLevel(logging.WARNING)

# Konfigurácia
BOT_TOKEN = os.environ.get('BOT_TOKEN', '8244776373:AAEBQhyFvtBI2BAbnNZSNLKDO5esd4600WM')
CHANNEL_ID = os.environ.get('CHANNEL_ID', '-1002328280528')
ADMIN_ID = int(os.environ.get('ADMIN_ID', '7626888184'))
PORT = int(os.environ.get('PORT', 10000))
WEBHOOK_URL = os.environ.get('WEBHOOK_URL', 'https://vip-tikety.onrender.com')

# Flask aplikácia
app = Flask(__name__)

# Globálne premenné
bot_initialized = False
start_time = time.time()

# Databáza zápasov - pridajte sem všetky zápasy, ktoré chcete poslať
MATCHES = {
    "match1": {
        'team1': 'V. Kudermetová',
        'team2': 'B. Bencic',
        'tournament': 'WTA Cincinnati',
        'time': '17:05',
        'pick': 'Bencic vyhrá + bude viac ako 17.5 gemu',
        'odds': '2.05',
        'betting_url': 'https://www.tipsport.sk/kurzy/zapas/tenis-kudermetova-veronika-bencic-belinda/7310190/co-sa-tipuje',
        'image': 'Cincinnati 5.png' 
    },
    
     "match2": {
         'team1': 'J. Menšík',
         'team2': 'E. Quinn', 
         'tournament': 'ATP Cincinnati',
         'time': '18:10',
         'pick': 'Quinn + 3.5 gemu',
         'odds': '1.65 (Tipos)',
         'betting_url': 'https://tipkurz.etipos.sk/zapasy/0/1990396cxx4199/267724046?searchBy=Men%C5%A1%C3%AD&gameGroup=69&categoryId=0',
         'image': 'Cincinnati 4.png'
     }
    
#     "match3": {
#         'team1': 'L. Zhu',
#         'team2': 'L. Bronzetti', 
#         'tournament': 'WTA Cincinnati',
#         'time': '17:05',
#         'pick': 'L. Zhu vyhrá - 1',
#         'odds': '1.60 x 1.27',
#         'betting_url': 'https://www.tipsport.sk/kurzy/zapas/tenis-zhu-lin-bronzetti-lucia/7303609/co-sa-tipuje',
#         'image': 'Zhu - Bronzetti.png'
#     },
    
#    "match4": {
#        'team1': 'H. Dellien',
#        'team2': 'R. Opelka', 
#        'tournament': 'ATP Cincinnati',
#        'time': '19:20',
#        'pick': 'Opelka -2.5 gemu',
#        'odds': '1.27 x 1.60',
#        'betting_url': 'https://www.tipsport.sk/kurzy/zapas/tenis-dellien-hugo-opelka-reilly/7301514/co-sa-tipuje',
#        'image': 'Dellien - Opelka.png'
#    }
}

ANALYSES = {
    "Analýza 1": {
        "title": "🎾 V. Kudermetová - B. Bencic",
        "text": """📊 *ANALÝZA ZÁPASU:  V. Kudermetová - B. Bencic*

Vraciame sa späť do Cincinnati, kde momentálne prebieha 2. kolo pavúka. Tu sa stretne Veronika Kudermetová s Belindou Bencic 🎾

_Belinda Bencic (WTA 19) je 28-ročná švajčiarska hráčka, ktorá sa nedávno vrátila po materskej dovolenke (ako sme už spomínali naposledy), a tento návrat zvládla výborne (o čom hovorí jej umietnenie v rebričku). Má deväť WTA titulov a je známa svojou všestrannosťou na rôznych povrchoch. V roku 2025 už vyhrala titul v Abu Dhabi a dosiahla semifinále Wimbledonu, kde prehrala s Igou Swiatek. Bencic je technicky vyspelá hráčka s výborným returnom a schopnosťou adaptovať sa na rôzne herné štýly. Na tvrdých povrchoch má takisto výborné výsledky 🇨🇭 

Veronika Kudermetová (WTA 36)  je 28-ročná ruská hráčka, ktorá prežíva zmiešanú sezónu. Je bývalou svetovou deviatkou (najvyšší ranking v októbri 2022) a špecializuje sa na antuku. Má za sebou skvelý doubles úspech - nedávno vyhrala Wimbledon s Elise Mertens a je bývalou dvojkovou hráčkou sveta v debli. Jej hra je založená na silných základných úderoch a vynikajúcej kondícii, ale má problémy s konzistentnosťou na rýchlych tvrdých povrchoch. 🇷🇺

Vzájomne majú vyrovnanú bilanciu, ale ich posledné stretnutie v Abu Dhabi 2025 jasne vyhrala Bencic 6-0, 6-0, čo bolo devastačné víťazstvo pre Švajčiarku. To ukazuje aktuálny pomer síl medzi nimi. _

*V tomto zápase sa prikláňam k Belinde Bencic. Zároveň verím, že minulý debakel 6-0, 6-0 bol skôr anomáliou a Kudermetovej sa podarí uhrať aspoň tých 6 gemov. Odporúčam staviť 1u ✅*  """
    },
    
    "Analýza 2": {
        "title": "🎾 J. Menšík - E. Quinn",
        "text": """📊 *ANALÝZA ZÁPASU: J. Menšík - E. Quinn*

Druhý zápas bude takisto zo Cincinnati. Bude to zápas Jakuba Menšíka s Ethanom Quinnom 🎾

_Ethan Quinn (ATP 82) je 21-ročný americký hráč. V roku 2025 má bilanciu 36-20, na tvrdých kurtoch 18-9. Quinn je bývalý majster NCAA z roku 2023 za University of Georgia a profesionálnu kariéru začal až po skončení štúdia. Jeho hlavná zbraň je podanie v spojení so silným forehandom. Výmeny hrá agresívne, kde mu pomáha aj jeho tenisové IQ (ako sa o ňom vyjadril jeho tréner). Môžeme teda dedukovať, že aj tvrdý povrch mu k tomu bude dnes dopomáhať 🇺🇸 

 Jakub Mensík (ATP 17) je 19-ročný český hráč narodený, ktorý má za sebou výnimočný rok 2025. Jeho najväčším úspechom v roku 2025 bolo víťazstvo na Masters 1000 v Miami, kde vo finále porazil Novaka Djokoviča 7-6(4), 7-6(4). Jeho hra je založená na agresívnych baseline úderoch a vynikajúcej fyzickej pripravenosti. V Cincinnatiho minulom roku dosiahol iba kvalifikácie, kde prehral s Aleksandarom Vukicom 7-6(5), 6-2 🇨🇿 
 
 Ich vzájomná bilancia je 1:0 pre Menšíka, keď na madridskej antuke porazil Quinna 2:0_

*Jakub Menšík je v tomto zápase favorit, ale nie až taký veľký ako ho niektoré stávkovky opisujú. Quinnov herný štýl výborne zapadá k povrchu a má aj svoje zbrane, ktorými bude proti Menšíkovi bojovať. Odporúčam staviť 1u na Quinna +3.5 gemu * ✅ """               
        
 }
    
#    "Analýza 3": {
#        "title": "🎾  L. Zhu - L. Bronzetti",
#        "text": """📊 *ANALÝZA ZÁPASU:  L. Zhu - L. Bronzetti*

#Teraz presedláme na tenis a pozrieme si konkrétne ten ženský 🎾

#_Lin Zhu (WTA 304) je čínska hráčka s veľmi agresívnym herným štýlom. Jej najlepší a obľúbený úder je forhend, ktorým dokáže diktovať tempo hry. Má rýchly, útočný prístup a snaží sa skracovať body tvrdými údermi. Prežíva síce dramatický pokles z WTA 31 kvôli zraneniu, ale už sa zotavuje. To sa potvrdio aj v Montreali, kde sa dostala do 4. kola. Zároveň je tvrdý povrch je najlepším 🇨🇳

#Lucia Bronzetti (WTA 61) je talianska hráčka s vyváženou baseline hrou a dobrým taktickým cítením. Je všestranná - dokáže adaptovať svoju hru na rôznym súperkám. Je to však najmä antukárka, čo potvrdzuje mimo jej štýlu aj negatívna bilancia na ostatných povrchoch. Momentálne nie je ani v bohvieakej forme 🇮🇹

#Odohrali spolu zatiaľ jeden zápas minulý rok, ktorý Zhu vyhrala 7-5, 6-1 _

#* Tu sa teda prikláňam k zdatnej Číňanke a verím, že zápas vyhrá. Odporúčam staviť 1u v kombinácii s ďalším zápasom *✅"""
#  },

#    "Analýza 4": {
#        "title": "🎾  H. Dellien - R. Opelka",
#        "text": """📊 *ANALÝZA ZÁPASU:  H. Dellien - R. Opelka*

#Dodatočnú príležitosť na tikete som vybral zo zápasu Opelku s Dellienom 🎾

#_Reilly Opelka (ATP 73) je moderna verzia "servebot" hráča s vylepšenou baseline hrou. Jeho hra je postavená na Devastačnom servise, agresívnej hre a silovom tenise. Takisto má výškovú výhodu (211cm), čo mu umožňuje byť tak nepríjemný na podaní. Z tohto nám už môže vyplývať, že preferuje rýchlejšie povrchy, čo mu dnes hrá do karát 🇺🇸

#Hugo Dellien (ATP 108) je klasický clay-court specialist s defenzívnym baseline herným štýlom. Je to vytrvalostný hráč typu "counterpuncher", ktorý stavá na konzistentnosti a vysokom tenisovom IQ. Využíva pokrytie kurtu a svoju kondíciu na prekonanie súperov. Môžeme však tušiť, že je najmä antukár a na harde odohral len 4 zápasy, kde má skóre 2-2 🇧🇴 _

#*Myslím, že Opelka je suverénny favorit a -2.5 gemu je ten najmenší problém. Verím mu, že tento zápas s prehľadom vyhrá *✅

#Alternatíva: Dá sa uvažovať aj o tom, že Opelka vyhrá 0:2 """
        
#  }

}

statistics_text = """📈 *SMART BETS ŠTATISTIKY* 

📊 *Naše výsledky za posledné obdobie:*

🏆 *BILANCIA TIKETOV - AUGUST*
• Výherné tikety: 4✅
• Prehraté tikety: 2❌
• Dlhodobá úspešnosť: 74% 

📈 *NAŠA ÚSPEŠNOSŤ*
• Navrátnosť za dané obdobie: 0.3% 
• Zisk za dané obdobie: +0.05u

💰 *CELKOVÝ ZISK V €*
⏩pri vklade 100€ ZISK 270€
⏩pri vklade 200€ ZISK 540€
⏩pri vklade 500€ ZISK 1350€

💰 *CELKOVÝ ZISK V KC*
⏩pri vklade 2500KC ZISK 6750KC
⏩pri vklade 5000KC ZISK 13500KC
⏩pri vklade 12500KC ZISK 33750KC

💬[AK CHCETE AJ VY ZARÁBAŤ TIETO SUMY S NAŠOU VIP](https://t.me/SmartTipy)"""

def is_admin(user_id):
    """Kontrola admin práv"""
    return user_id == ADMIN_ID

def send_telegram_message(chat_id, text, reply_markup=None, parse_mode=None):
    """Pošle správu cez Telegram API"""
    telegram_url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    payload = {
        'chat_id': chat_id,
        'text': text
    }
    
    if reply_markup:
        payload['reply_markup'] = reply_markup
    if parse_mode:
        payload['parse_mode'] = parse_mode
    
    try:
        resp = requests.post(telegram_url, json=payload, timeout=10)
        print(f"📤 Message sent: {resp.status_code}")
        
        if resp.status_code != 200:
            print(f"❌ Telegram API error: {resp.text}")
            
        return resp.status_code == 200
    except Exception as e:
        print(f"❌ Error sending message: {e}")
        return False

def send_telegram_photo(chat_id, photo_path, caption, reply_markup=None):
    """Pošle obrázok cez Telegram API"""
    telegram_url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendPhoto"
    
    try:
        with open(photo_path, 'rb') as photo:
            files = {'photo': photo}
            data = {
                'chat_id': chat_id,
                'caption': caption
            }
            
            if reply_markup:
                data['reply_markup'] = json.dumps(reply_markup)
            
            resp = requests.post(telegram_url, files=files, data=data, timeout=15)
            print(f"📤 Photo sent: {resp.status_code}")
            
            if resp.status_code != 200:
                print(f"❌ Photo send error: {resp.text}")
                
            return resp.status_code == 200
            
    except FileNotFoundError:
        print(f"❌ Photo not found: {photo_path}")
        return False
    except Exception as e:
        print(f"❌ Error sending photo: {e}")
        return False

def answer_callback_query(callback_query_id, text=""):
    """Odpovie na callback query"""
    telegram_url = f"https://api.telegram.org/bot{BOT_TOKEN}/answerCallbackQuery"
    payload = {
        'callback_query_id': callback_query_id,
        'text': text,
        'show_alert': False
    }
    
    try:
        resp = requests.post(telegram_url, json=payload, timeout=10)
        print(f"📤 Callback answered: {resp.status_code}")
        if resp.status_code != 200:
            print(f"❌ Callback answer error: {resp.text}")
        return resp.status_code == 200
    except Exception as e:
        print(f"❌ Error answering callback: {e}")
        return False

def create_analyses_menu():
    """Vytvorí menu s dostupnými analýzami"""
    keyboard = {"inline_keyboard": []}
    
    # Pridá každú analýzu ako button
    for analysis_id, analysis_data in ANALYSES.items():
        button_text = f"{analysis_data['title']}"
        keyboard["inline_keyboard"].append([
            {"text": button_text, "callback_data": f"analysis_{analysis_id}"}
        ])
    
    # Pridá tlačidlo späť
    keyboard["inline_keyboard"].append([
        {"text": "◀️ Späť do menu", "callback_data": "back_to_main"}
    ])
    
    return keyboard

def create_main_menu():
    """Vytvorí hlavné menu"""
    return {
        "inline_keyboard": [
            [{"text": "📊 ANALÝZY", "callback_data": "show_analyses"}],
            [{"text": "📈 ŠTATISTIKY", "callback_data": "user_statistics"}]
        ]
    }

def handle_start_command(chat_id, user_id, user_name, text):
    """Spracuje /start príkaz"""
    
    keyboard = create_main_menu()
    
    if is_admin(user_id):
        # Admin má aj príkazy aj menu s analýzami
        send_telegram_message(
            chat_id,
            f'Vitajte v Sports Tips Bot! 🏆\n'
            f'Vaše ID: {user_id} (ADMIN)\n\n'
            '🔧 **ADMIN PRÍKAZY:**\n'
            '/tiket - Odoslať tiket do kanála\n'
            '/status - Stav bota\n'
            '/help - Zobrazí nápovedu\n\n'
            '👥 **POUŽÍVATEĽSKÉ FUNKCIE:**'
        )
        
        # Pošle aj menu pre admina
        send_telegram_message(
            chat_id,
            '🏆 **SMART BETS** - Váš expert na športové stávky\n\n'
            '📊 **ANALÝZY** - Vyberte si z dostupných analýz zápasov\n'
            '📈 **ŠTATISTIKY** - Sledujte naše výsledky a úspešnosť\n\n'
            '🎯 Vyberte si možnosť:',
            reply_markup=keyboard,
            parse_mode='Markdown'
        )
    else:
        # Bežný používateľ
        send_telegram_message(
            chat_id,
            f'Vitajte {user_name}! 👋\n\n'
            '🏆 **SMART BETS** - Váš expert na športové stávky\n\n'
            '📊 **ANALÝZY** - Vyberte si z dostupných analýz zápasov\n'
            '📈 **ŠTATISTIKY** - Sledujte naše výsledky a úspešnosť\n\n'
            '🎯 Vyberte si možnosť:',
            reply_markup=keyboard,
            parse_mode='Markdown'
        )

def send_analysis(chat_id, analysis_id):
    """Pošle konkrétnu analýzu"""
    if analysis_id not in ANALYSES:
        send_telegram_message(chat_id, "❌ Analýza nebola nájdená!")
        return
    
    analysis = ANALYSES[analysis_id]
    
    # Pošle analýzu
    success = send_telegram_message(chat_id, analysis['text'], parse_mode='Markdown')
    if not success:
        # Fallback bez markdown
        send_telegram_message(chat_id, analysis['text'].replace('*', ''))
    
    # Pridá tlačidlo späť na výber analýz
    back_keyboard = {
        "inline_keyboard": [
            [{"text": "📊 Ďalšie analýzy", "callback_data": "show_analyses"}],
            [{"text": "◀️ Hlavné menu", "callback_data": "back_to_main"}]
        ]
    }
    
    send_telegram_message(
        chat_id,
        "📊 Chcete si pozrieť ďalšie analýzy?",
        reply_markup=back_keyboard
    )

def send_analyses_menu(chat_id):
    """Pošle menu s dostupnými analýzami"""
    keyboard = create_analyses_menu()
    
    send_telegram_message(
        chat_id,
        "📊 **DOSTUPNÉ ANALÝZY**\n\n"
        "Vyberte si zápas, ktorého analýzu chcete vidieť:",
        reply_markup=keyboard,
        parse_mode='Markdown'
    )

def send_statistics(chat_id):
    """Pošle štatistiky"""
    success = send_telegram_message(chat_id, statistics_text, parse_mode='Markdown')
    if not success:
        # Fallback bez markdown
        send_telegram_message(chat_id, statistics_text.replace('*', ''))
    
    # Pridá tlačidlo späť
    back_keyboard = {
        "inline_keyboard": [
            [{"text": "◀️ Späť do menu", "callback_data": "back_to_main"}]
        ]
    }
    
    send_telegram_message(
        chat_id,
        "📈 Chcete sa vrátiť do hlavného menu?",
        reply_markup=back_keyboard
    )

def handle_tiket_command(chat_id):
    """Spracuje /tiket príkaz - pošle všetky aktívne zápasy"""
    try:
        active_matches = {k: v for k, v in MATCHES.items() if k not in []}  # Môžete pridať zoznam excluded matches
        
        if not active_matches:
            send_telegram_message(chat_id, "❌ Žiadne aktívne zápasy na odoslanie!")
            return
            
        sent_count = 0
        failed_count = 0
        
        for match_id, match_data in active_matches.items():
            try:
                success = send_ticket_to_channel(match_data)
                if success:
                    sent_count += 1
                    print(f"✅ Ticket {match_id} sent successfully")
                    # Pauza medzi odosielaním, aby sme nepretažili API
                    time.sleep(1)
                else:
                    failed_count += 1
                    print(f"❌ Failed to send ticket {match_id}")
            except Exception as e:
                failed_count += 1
                print(f"❌ Error sending ticket {match_id}: {e}")
        
        # Správa o výsledku
        result_message = f"📊 **VÝSLEDOK ODOSIELANIA:**\n\n"
        result_message += f"✅ Odoslané: {sent_count} tiketov\n"
        if failed_count > 0:
            result_message += f"❌ Nepodarilo sa: {failed_count} tiketov"
        else:
            result_message += f"🎉 Všetky tikety úspešne odoslané!"
            
        send_telegram_message(chat_id, result_message, parse_mode='Markdown')
        
    except Exception as e:
        print(f"❌ Error in handle_tiket_command: {e}")
        send_telegram_message(chat_id, f"❌ Chyba pri odosielaní tiketov: {str(e)}")

def send_ticket_to_channel(match_data=None):
    """Odošle jeden tiket do kanála"""
    if match_data is None:
        # Fallback na prvý zápas ak nie je špecifikovaný
        if MATCHES:
            match_data = list(MATCHES.values())[0]
        else:
            print("❌ No matches available")
            return False
    
    caption = (f"🏆 {match_data['team1']} vs {match_data['team2']}\n"
              f"🎾 {match_data['tournament']}\n"
              f"🕘 {match_data['time']}\n\n"
              f"🎯 {match_data['pick']}\n"
              f"💰 Kurz: {match_data['odds']}")
    
    keyboard = {
        "inline_keyboard": [
            [{"text": "🎯 STAV TERAZ!", "url": match_data['betting_url']}],
            [{"text": "📊 ANALÝZA", "url": "https://t.me/viptikety_bot?start=analysis"}]
        ]
    }
    
    if 'image' in match_data and match_data['image']:
        image_path = f"images/{match_data['image']}"
        
        if send_telegram_photo(CHANNEL_ID, image_path, caption, keyboard):
            print(f"✅ Ticket with image sent to channel: {match_data['team1']} vs {match_data['team2']}")
            return True
        else:
            print(f"⚠️ Image failed, sending as text: {match_data['team1']} vs {match_data['team2']}")
    
    # Pošli len text (ak nie je obrázok alebo zlyhalo odoslanie obrázka)
    text_message = f"{caption}\n\n🎯 [STAV TERAZ!]({match_data['betting_url']})"
    success = send_telegram_message(CHANNEL_ID, text_message, parse_mode='Markdown')
    if success:
        print(f"✅ Ticket as text sent to channel: {match_data['team1']} vs {match_data['team2']}")
    return success

def handle_status_command(chat_id):
    """Spracuje /status príkaz"""
    uptime = time.time() - start_time
    status_text = f"""🤖 **Bot Status**
🔄 Mode: Webhook
🌐 Port: {PORT}
⏰ Uptime: {round(uptime/3600, 1)} hodín
🔗 Webhook: {WEBHOOK_URL}/webhook
✅ Status: Running
🤖 Bot: {'✅ Initialized' if bot_initialized else '❌ Not initialized'}"""
    
    send_telegram_message(chat_id, status_text, parse_mode='Markdown')

def handle_help_command(chat_id):
    """Spracuje /help príkaz"""
    help_text = """📋 **DOSTUPNÉ PRÍKAZY:**

🎯 **/tiket** - Odošle všetky aktívne zápasy do kanála
🔍 **/status** - Zobrazí stav bota  
❓ **/help** - Zobrazí túto nápovedu

📊 **SPRÁVA ZÁPASOV:**
• Upravte `MATCHES` v kóde pre pridanie nových zápasov
• Zakomentujte zápasy ktoré nechcete poslať
• Jeden príkaz `/tiket` pošle všetky aktívne zápasy

🎮 **TLAČIDLÁ:**
• 📊 ANALÝZY - Zobraziť dostupné analýzy
• 📈 ŠTATISTIKY - Zobraziť výsledky a úspešnosť"""
    
    send_telegram_message(chat_id, help_text, parse_mode='Markdown')

def setup_webhook():
    """Nastavenie webhook"""
    global bot_initialized
    
    try:
        # Zruš starý webhook
        delete_url = f"https://api.telegram.org/bot{BOT_TOKEN}/deleteWebhook"
        requests.post(delete_url, json={'drop_pending_updates': True}, timeout=10)
        print("🗑️ Old webhook deleted")
        
        time.sleep(1)
        
        # Nastav nový webhook
        webhook_url = f"{WEBHOOK_URL}/webhook"
        set_url = f"https://api.telegram.org/bot{BOT_TOKEN}/setWebhook"
        payload = {
            'url': webhook_url,
            'drop_pending_updates': True,
            'max_connections': 40
        }
        
        resp = requests.post(set_url, json=payload, timeout=10)
        print(f"✅ Webhook setup: {resp.status_code}")
        
        if resp.status_code == 200:
            bot_initialized = True
            print(f"✅ Webhook set: {webhook_url}")
            
            # Overenie
            info_url = f"https://api.telegram.org/bot{BOT_TOKEN}/getWebhookInfo"
            info_resp = requests.get(info_url, timeout=10)
            if info_resp.status_code == 200:
                info = info_resp.json().get('result', {})
                print(f"🔍 Webhook verification:")
                print(f"   URL: {info.get('url', 'N/A')}")
                print(f"   Pending: {info.get('pending_update_count', 0)}")
                if info.get('last_error_message'):
                    print(f"   ⚠️ Last error: {info.get('last_error_message')}")
                    
            return True
        else:
            print(f"❌ Webhook setup failed: {resp.text}")
            return False
            
    except Exception as e:
        print(f"❌ Webhook setup error: {e}")
        return False

# Flask routes
@app.route('/')
def health_check():
    """Health check endpoint"""
    uptime = time.time() - start_time
    return jsonify({
        'status': 'ok',
        'service': 'telegram-bot',
        'mode': 'webhook',
        'uptime_hours': round(uptime / 3600, 2),
        'port': PORT,
        'webhook_url': f"{WEBHOOK_URL}/webhook",
        'bot_initialized': bot_initialized,
        'timestamp': time.strftime('%Y-%m-%d %H:%M:%S'),
        'available_analyses': len(ANALYSES),
        'available_matches': len(MATCHES)
    })

@app.route('/health')
def health():
    """Health endpoint pre monitoring"""
    return jsonify({
        'status': 'healthy',
        'bot_active': bot_initialized,
        'uptime_hours': round((time.time() - start_time) / 3600, 2)
    })

@app.route('/debug')
def debug_info():
    """Debug informácie"""
    return jsonify({
        'bot_token': BOT_TOKEN[:10] + "..." if BOT_TOKEN else "NOT SET",
        'webhook_url': WEBHOOK_URL,
        'bot_initialized': bot_initialized,
        'webhook_endpoint': f"{WEBHOOK_URL}/webhook",
        'analyses_count': len(ANALYSES),
        'matches_count': len(MATCHES)
    })

@app.route('/webhook', methods=['POST'])
def webhook():
    """Webhook endpoint pre Telegram"""
    if not bot_initialized:
        print("❌ Bot not initialized")
        return jsonify({'error': 'Bot not initialized'}), 500
    
    try:
        update_data = request.get_json()
        
        if not update_data:
            print("❌ No JSON data received")
            return jsonify({'error': 'No data received'}), 400
        
        print(f"📨 Received update: {update_data.get('update_id', 'unknown')}")
        
        # Spracovanie správ
        if 'message' in update_data:
            message = update_data['message']
            chat_id = message['chat']['id']
            text = message.get('text', '')
            user_name = message['from'].get('first_name', 'Unknown')
            user_id = message['from']['id']
            
            print(f"📝 Message from {user_name} (ID: {user_id}): {text}")
            
            # Handle commands
            if text.startswith('/start'):
                handle_start_command(chat_id, user_id, user_name, text)
            elif text == '/tiket' and is_admin(user_id):
                handle_tiket_command(chat_id)
            elif text == '/status' and is_admin(user_id):
                handle_status_command(chat_id)
            elif text == '/help' and is_admin(user_id):
                handle_help_command(chat_id)
                
        # Spracovanie callback queries (buttony)
        elif 'callback_query' in update_data:
            callback = update_data['callback_query']
            chat_id = callback['message']['chat']['id']
            user_name = callback['from'].get('first_name', 'Unknown')
            user_id = callback['from']['id']
            data = callback['data']
            callback_query_id = callback['id']
            
            print(f"🔘 Button clicked: {data} by {user_name} (ID: {user_id})")
            
            # Odpoveď na callback query
            answer_callback_query(callback_query_id, "📊 Načítavam...")
            
            # Spracovanie akcií
            if data == "show_analyses":
                print("📊 Showing analyses menu...")
                send_analyses_menu(chat_id)
            elif data.startswith("analysis_"):
                analysis_id = data.replace("analysis_", "")
                print(f"📊 Sending analysis: {analysis_id}")
                send_analysis(chat_id, analysis_id)
            elif data == "user_statistics":
                print("📈 Sending statistics...")
                send_statistics(chat_id)
            elif data == "back_to_main":
                print("🔙 Going back to main menu...")
                keyboard = create_main_menu()
                send_telegram_message(
                    chat_id,
                    '🏆 **SMART BETS** - Váš expert na športové stávky\n\n'
                    '📊 **ANALÝZY** - Vyberte si z dostupných analýz zápasov\n'
                    '📈 **ŠTATISTIKY** - Sledujte naše výsledky a úspešnosť\n\n'
                    '🎯 Vyberte si možnosť:',
                    reply_markup=keyboard,
                    parse_mode='Markdown'
                )
            else:
                print(f"❓ Unknown callback data: {data}")
        
        return jsonify({'status': 'ok'})
        
    except Exception as e:
        print(f"❌ Webhook error: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500

def main():
    """Spustenie aplikácie"""
    print("🚀 Starting Telegram Bot with Webhook...")
    print(f"📊 Loaded {len(ANALYSES)} analyses")
    print(f"🎯 Loaded {len(MATCHES)} matches")
    
    # Setup webhook
    if setup_webhook():
        print("✅ Bot ready for requests")
    else:
        print("❌ Failed to setup webhook, but starting server anyway...")
    
    print(f"✅ Starting Flask server on port {PORT}")
    print(f"✅ Webhook URL: {WEBHOOK_URL}/webhook")
    print(f"✅ Health check: {WEBHOOK_URL}/")
    
    # Spustenie Flask servera
    app.run(host='0.0.0.0', port=PORT, debug=False)

if __name__ == '__main__':
    main()
