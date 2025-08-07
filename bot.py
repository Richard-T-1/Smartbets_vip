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
        'team1': 'J. Thompson',
        'team2': 'A. Mannarino',
        'tournament': 'ATP Cincinnati',
        'time': '20:30',
        'pick': 'Mannarino vyhrá - 2',
        'odds': '1.83',
        'betting_url': 'https://www.tipsport.sk/kurzy/zapas/tenis-thompson-jordan-mannarino-adrian/7305162/co-sa-tipuje',
        'image': 'ATP Cincinnati 1.png' 
    },
    
     "match2": {
         'team1': 'T. M. Etcheverry',
         'team2': 'J. Shang',
         'tournament': 'ATP Cincinnati',
         'time': '19:20',
         'pick': 'Etcheverry vyhrá - 1',
         'odds': '1.65',
         'betting_url': 'https://www.tipsport.sk/kurzy/zapas/tenis-etcheverry-tomas-martin-shang-juncheng/7301501/co-sa-tipuje',
         'image': 'ATP Cincinnati 2.png'
     },
    
#     "match3": {
#         'team1': 'E. Hozumi',
#         'team2': 'E. Shibahara', 
#         'tournament': 'WTA Cincinnati',
#         'time': '22:30',
#         'pick': 'Shibahara vyhrá 0:2',
#         'odds': '1.32',
#         'betting_url': 'https://www.tipsport.sk/kurzy/zapas/tenis-hozumi-eri-shibahara-ena/7297947/co-sa-tipuje',
#         'image': 'ATP Cincinnati 2.png'
#     }
}

ANALYSES = {
    "ATP Cincinnati 1": {
        "title": "🎾 J. Thompson - A. Mannarino",
        "text": """📊 *ANALÝZA ZÁPASU:  J. Thompson - A. Mannarino*

V turnaji ATP Cincinnati začína vyraďovacia časť, ktorá nám priniesla aj zápas Jordana Thompsona a Adriana Mannarina 🎾

_Adrian Mannarino (ATP 94) je výborný tenista aj napriek tomu, že už má pokročilejší vek. Túto sezónu nezačal najlepšie, ale už je konečne vo forme. To potvrdzujú jeho zápasy so Svrčinom a Kruegerom, ktoré vyhral suverénne. Takisto porazil Girona 2:0. Jeho herný štýl je defenzívny, zároveň to je baseliner a majster kontraúderov. Dokáže presmerovať silu súpera a dostať ho do nepríjemných pozícií. Používa extrémne nízke napätie strún, čo mu umožňuje hrať plochými údermi s krátkym rozšvihuom a sústrediť sa na presnosť namiesto sily. Jeho ľavácky servis vytvára výborné uhly a dokáže rozhádzať súperov z jednej strany na druhú. Mannarino je známy svojou rýchlosťou po kurte a konzistentnosťou z baseline. Jeho kariérne maximum bola ATP 17 začiatkom minulého roka. Problémom je skorej jeho kolísavá forma. Tráva je jeho najlepší povrch, ale aj na harde je nebezpečný súper 🇫🇷 

Jordan Thompson (ATP 44) je hráč s rastúcou formou v svetovom tenise. Jeho herný štýl je založený na silnej baseline hre a výbornej fyzickej kondícii. Austrálčan má za sebou fantastický rok 2024, keď získal svoj prvý ATP titul v Los Cabos. Má výborný servis a solídnu baseline hru, pričom vyniká vo vypätých situáciach. Slabšou stránkou je, že občas má problémy s koncentráciou a horšie štarty do zápasov 🇦🇺

Z vzájomných zápasov vyplýva, že Mannarino vedie celkovú bilanciu 5:4, ale Thompson vyhral ich posledné stretnutie 7-5, 7-6 _

*V tomto zápase sa prikláňam k Mannarinovi kvôli jeho forme a celkovej kvalite hry. Tento zápas bude každopádne vyrovnaný, teda odporúčam staviť 1u (poprípade 0.75u) ✅*  """
    },
    
    "ATP Cincinnati 2": {
        "title": "🎾 T. M. Etcheverry - J. Shang",
        "text": """📊 *ANALÝZA ZÁPASU: T. M. Etcheverry - J. Shang*

V Cincinnati ešte ostaneme a pozrieme sa na zápas Tomasa Etcheverryho s Junchengom Shangom  🎾

_Tomas Martin Etcheverry (ATP 60) má klasický antukársky štýl s bohatými skúsenosťami. Jeho štýl je založený na silnej baseline hre s dôrazom na topspin údery a fyzickú odolnosť. Argentínčan dosiahol kariérne maximum ATP 27 a má za sebou tri finále ATP turnajov. Etcheverry má výborný bekhend s oboma rukami a vie hrať dlhé výmeny s vysokou intenzitou. Silnou stránkou je jeho mentálna odolnosť a skúsenosti z veľkých zápasov. Jeho výkony na tvrdom kurte sú horšie ako na antuke, ale už aj tu si zobral pál skalpov - napr. minulý týždeň porazil Griekspoora. Zároveň treba spomenúť, mesiac dozadu porazil Bena Sheltona  🇦🇷
 
Juncheng Shang (ATP 109) reprezentuje novú generáciu čínskych tenistov s veľkým potenciálom.  Jeho herný štýl je all-court s výbornou technikou a rýchlosťou po kurte. Jeho ľavácky herný štýl vytvára problémy súperom a má výborné anticipovanie. Shang je syn bývalého futbalistu a majsterky sveta v stolnom tenise, čo mu dáva športové gény. Problémom je jeho mladý vek a niekedy nedostatočné skúsenosti v kľúčových momentoch, najmä proti skúsenejším súperom. Tento rok však toho neodohral. Zranil sa na začiatku sezóny v Hongkongu a potom aj na Australian open s Fokinou 🇨🇳

Zatiaľ spolu odohrali 2 zápasy a oba vyhrala Shang. Verím však, že teraz je Etcheverry v lepšej forme a Shang nebude po zraneniach hrať tak dobre _

*Tento zápas bude však vyrovnaný, kde môže rozhodnúť Etcheverryho forma a herné skúsenosti. Odporúčam staviť 1u (poprípade 0.75u ako zápas predtým) * ✅ """               
        
 }
    
#    "Ordabasy - Atyrau": {
#        "title": "🎾  E. Hozumi - E. Shibahara",
#        "text": """📊 *ANALÝZA ZÁPASU:  E. Hozumi - E. Shibahara*

#V Cincinnati ešte ostaneme a pozrieme si duel 2 Japoniek - Eri Hozumi s Enou Shibaharou 🎾

#_Ena Shibahara (WTA 124) je 27 ročná Japonka s all-court štýlom. Toto je aj vďaka jej minulosti, kde hrávala 4hry. V 2hre dosiahli prielom minulý rok, keď postúpila 570. na 119. miesto v rebríčku. Jej forma stále rastie a zároveň tvrdý povrch je jej obľúbený 🇯🇵

#Eri Hozumi (WTA 1447) zažíva výrazný pokles formy. Je opakom Shibahary, keďže prešla z 2hry na 4hry - z kariérneho maxima v 2hre klesla o viac ako 1300 priečok. Jej bilancia je teda každý rok negatívna. Má takisto all-court štýl hry s dobrým pohybom po dvorci a takticky inteligentnou hrou. Slušný return a hra na tvrdom povrchu je tiež jednou z jej dobrých stránok 🇯🇵 _

#* Každopádne v tomto zápase je priepasť medzi hráčkami (keď berieme do úvahy 2hru) výrazná a Shibahare ako mladšej hráčke s oveľa lepšou hrou plne verím. Tento zápas som skombinoval s predlošlým a odporúčam dať na túto akovku 1u *✅"""
#  }
}

statistics_text = """📈 *SMART BETS ŠTATISTIKY* 

📊 *Naše výsledky za posledné obdobie:*

🏆 *BILANCIA TIKETOV*
• Výherné tikety: 36✅
• Prehraté tikety: 12 ❌
• Úspešnosť: 75% 

📈 *NAŠA ÚSPEŠNOSŤ*
• Navrátnosť za dané obdobie: 17,68% 
• Zisk za dané obdobie: +19.63u

💰 *CELKOVÝ ZISK V €*
⏩pri vklade 100€ ZISK 393€
⏩pri vklade 200€ ZISK 785€
⏩pri vklade 500€ ZISK 1963€

💰 *CELKOVÝ ZISK V KC*
⏩pri vklade 2500KC ZISK 9815KC
⏩pri vklade 5000KC ZISK 19630KC
⏩pri vklade 12500KC ZISK 49075KC

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
              f"🎾{match_data['tournament']}\n"
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
