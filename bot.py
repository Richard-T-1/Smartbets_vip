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
        'team1': 'V Gracheva',
        'team2': 'V. Kudermetova',
        'tournament': 'WTA Cincinnati',
        'time': '23:10',
        'pick': 'Kudermetová -2.5 gemu',
        'odds': '1.67 (Doxxbet)',
        'betting_url': 'https://www.doxxbet.sk/sk/sportove-tipovanie-online/kurzy/tenis/wta/cincinnati?event=64853624&name=gracheva-varvara-vs-kudermetova-veronika',
        'image': 'Cincinnati 10.png' 
    },
    
     "match2": {
         'team1': 'J. Paolini',
         'team2': 'C. Gauff', 
         'tournament': 'WTA Cincinnati',
         'time': '16.8. 3:00',
         'pick': 'Gauff -2.5 gemu',
         'odds': '1.63',
         'betting_url': 'https://www.tipsport.sk/kurzy/zapas/tenis-paolini-jasmine-gauff-cori/7329992',
         'image': 'Cincinnati 11.png'
     }
    
#     "match3": {
#         'team1': 'V. Kudermetova',
#         'team2': 'M. Linette', 
#         'tournament': 'WTA Cincinnati',
#         'time': '15.8. 1:00',
#         'pick': 'Kudermetová vyhrá - 1',
#         'odds': '1.59 x 1.34',
#         'betting_url': 'https://www.tipsport.sk/kurzy/zapas/tenis-kudermetova-veronika-linette-magda/7324520/co-sa-tipuje',
#         'image': 'Cincinnati 9.png'
#     }
    
 #   "match4": {
 #       'team1': 'M. Talha',
 #       'team2': 'S. Baysangur', 
 #       'tournament': 'D.W. Contender Series',
 #       'time': '13.8. 1:00',
 #       'pick': 'Talha vyhrá - 1',
 #       'odds': '3.74',
 #       'betting_url': 'https://www.tipsport.sk/kurzy/zapas/bojove-sporty-talha-murtaza-baysangur-susurkaev/7313974',
 #       'image': 'D.W. Contender Series.png'
 #   }
}

ANALYSES = {
    "Analýza 1": {
        "title": "🎾 V Gracheva - V. Kudermetova",
        "text": """📊 *ANALÝZA ZÁPASU: V Gracheva - V. Kudermetova*

Dnes máme opäť tenisový deň. Veronika Kudermetová nás už jeden deň podržala a rozhodol som sa jej veriť aj dnes 🎾

_Veronika Kudermetova (WTA 36) je 28-ročná Ruska s výrazne agresívnym baseline štýlom a dvojručným bekhendom. Má career high 9. miesto a vyhrala 2 WTA tituly vrátane nedávneho Grand Slam víťazstva v doubles na Wimbledone 2025. Je známa svojim silným servisom a mocnými údermi z baseline, dokáže diktovať tempo hry a preferuje rýchly, agresívny štýl. Najelpšia je na tráve, ale aj na tvrdých kurtoch má slušnú bilanciu 🇷🇺

Varvara Gracheva (WTA 103) je 24-ročná Francúzka s konzistentným baseline štýlom charakterizovaným silnými defenzívnymi schopnosťami a mocnými údermi zo základnej čiary. Je známa svojou vytrvalosťou, taktickou inteligenciou. Jej problémom môže byť zakončovanie zápasov v kritických situáciach. Na tvrdých kurtoch má slušnú bilanciu, ale v poslednej dobe bojuje s formou. Tvrdý povrch vyhovuje však viac štýlu Kudermetovej 🇫🇷

Tieto tenistky sa stretli vo svojej kariére 2 krát, a oba zápasy vyhrala Kudermetová._

*Kudermetová už ukázala, že sa dá na ňu spoľahnúť a v priebehu Cincinnati porazila aj silnejšie súperky. Je vo forme, vyhovuje jej povrch a -2.5 gemu vidím ešte ako celkom konzervatívne. Odporúčam staviť však 1u ✅*  """
    },
    
    "Analýza 2": {
        "title": "🎾 J. Paolini - C. Gauff",
        "text": """📊 *ANALÝZA ZÁPASU: J. Paolini - C. Gauff*

Znova podporíme aj Cori Gauff, ktorá je stále favoritkou a proti Paolini je takisto verím 🎾

_Cori Gauff (WTA 2) je 21-ročná americká superstar s extrémne rýchlym a atletickým štýlom. Konvertuje 55% brejkových príležitostí a má vysoké tempo hry so schopnosťou rýchlo prejsť z obrany do útoku. Je to typický moderný power hráč s výborným returnom a fyzickou dominanciou. Jej menšou slabinou môže byť občasná netrpezlivosť a forsírovanie úderov 🇺🇸

Jasmine Paolini (WTA 9) je 29-ročná Talianka s konzistentným baseline štýlom a výnimočnou bojovnosťou. Má career high 4. miesto, 3 WTA tituly vrátane WTA 1000 Dubai 2024 a finále na Roland Garros aj Wimbledone 2024. Je známa svojou vytrvalosťou, taktickou inteligenciou a schopnosťou hrať dlhé rallye. Má výšku len 163 cm, ale kompenzuje to rýchlosťou a perfektným pohybom po kurte. Jej štýlu však vyhovuje pomalá antuka, čiže tu jej hard dáva nevýhodu 🇮🇹
 
Majú spolu odohraté 4 zápasy a stav je 2-2. Je dobré si však uvedomiť, že Paolini vyhrala oba zápasy na antuke a Guaff na tvrdom povrchu. _

*Cori Gauff je v dobrej forme a jej agresívny štýl bude určite Paolini robiť veľké problémy. To súdim aj z toho, že na harde ešte s Paolini neprehrala a ide si po svoju 3. výhru* ✅ """               
        
 }
    
#    "Analýza 3": {
#        "title": "🎾  V. Kudermetova - M. Linette",
#        "text": """📊 *ANALÝZA ZÁPASU:  V. Kudermetova - M. Linette*

#Druhým zápasom na tikete bude súboj Veroniky Kudermetovej s Magdou Linette z osemfinále WTA Cincinnati 🎾

#_Veronika Kudermetova (WTA 36) je 28-ročná Ruska s výrazne agresívnym baseline štýlom a dvojručným bekhendom. Má career high 9. miesto a vyhrala 2 WTA tituly vrátane nedávneho Grand Slam víťazstva v doubles na Wimbledone 2025. Je známa svojim silným servisom a mocnými údermi z baseline, dokáže diktovať tempo hry a preferuje rýchly, agresívny štýl. Najelpšia je na tráve, ale aj na tvrdých kurtoch má slušnú bilanciu 🇷🇺

#Magda Linette (WTA 40) je 33-ročná Poľka s takticky vyspelým baseline štýlom charakterizovaným silnou základnou hrou. Má career high 19. miesto a 3 WTA tituly vrátane semifinále Australian Open 2023. Je známa svojou vytrvalosťou, taktickou inteligenciou a schopnosťou hrať dlhé rallye. Na indoor hard kurtoch má najlepšiu bilanciu (62%), celkovo na hardoch je tiež silná 🇵🇱

#Odohrali spolu zatiaľ 1 zápas, ktorý vyhrala Linette otočkou po prehre 1. setu _

#*Po dôkladnom uvážení vyberám Kudermetovú, ktorá je vo výbornej forme a rýchly tvrdý povrch jej silu ešte zvyšuje. Odporúčam ju pridať na tiket s Guaff a stávkou 0.75u *✅"""
        
#  }

#    "Analýza 4": {
#        "title": "🥊  M. Talha - S. Baysangur",
#        "text": """📊 *ANALÝZA ZÁPASU:  M. Talha - S. Baysangu*

#Ako čerešničku na torte si zvolíme zápas uchádzačov do UFC: Murtaza Talha - Susurkaev Baysangur 🥊

#_Murtaza Talha (7-1) je 29-ročný bojovník z Bahrajnu, ktorý má za sebou druhú šancu na DWCS po neúspešnom pokuse v roku 2023, keď prehral s Rodolfom Bellatom KO v druhom kole. Talha má bohatú amatérsku kariéru s bilanciou 12-0 a bol niekoľkonásobným majstrom sveta IMMAF aj Európy. Jeho profesionálna kariéra začala výborne - všetkých prvých šesť súperov porazil finišom, pričom len jeden zápas sa dostal do druhého kola. Talhov herný štýl je založený na bezuzdnej agresivite a explozívnosti. Je známy divokými, looping údermi s plnou silou zameranými na knockout. Z týchto úderov prechádza priamo na double leg takedowny a keď dostane súpera na zem, aplikuje devastačný ground-and-pound, až kým rozhodca nezastaví zápas. Jeho kmeňové bojové umenie je wrestling a grappling, čo mu umožňuje efektívne kombinovať úder-takedown. Problémom je, že v dlhších zápasoch má tendenciu sa vyčerpať 🇧🇭

#Susurkaev Baysangur (8-0) je 24-ročný neporazený bojovník z Čečenska, ktorý vstupuje do DWCS s perfektným rekordom. Má sedem víťazstiev KO/TKO a jedno na body, pričom šesť finišov dosiahol už v prvom kole. Jeho posledný zápas bol v februári na Fury FC 102, kde finišoval Irakliho Kuchukhidzeho TKO v druhom kole. Susurkaev prijal tento zápas na týždeň pred súbojom ako náhradník a je na radaroch UFC už dlhší čas. Kľúčovým faktorom je, že je jedným z hlavných tréningových partnerov Khamzata Chimaeva pri príprave na Dricusa Du Plessisa. Susurkaev je metodický striker s technickým prístupom. Na rozdiel od Talhovej divokosti je systematický v svojom rozklade súperov. Využíva calf kick, útoky na telo a hlavu. Je tiež známy svojimi kolenami smerom nahor, ktoré môžu zastaviť grapplingové pokusy súperov 🇷🇺_

#*Baysangur je v tomto zápase favoritom vďaka dobrej technickej stránke a postoju. Talha s kurzom 3.74 mi však príde veľmi podceňovaný. Je to stále výborný bojovník, ktorý má len jedinu prehru a vie dobre kombinovať postoj so zemou. Odporúčam si staviť 0.25-0.5u  *✅ """
        
#  }

}

statistics_text = """📈 *SMART BETS ŠTATISTIKY* 

📊 *Naše výsledky za posledné obdobie:*

🏆 *BILANCIA TIKETOV - AUGUST*
• Výherné tikety: 12✅
• Prehraté tikety: 4❌
• Dlhodobá úspešnosť: 75% 

📈 *NAŠA ÚSPEŠNOSŤ - AUGUST*
• Navrátnosť: 22.55% 
• Zisk: +10.26u

💰 *CELKOVÝ ZISK V €*
⏩pri vklade 100€ ZISK 525€
⏩pri vklade 200€ ZISK 1050€
⏩pri vklade 500€ ZISK 2625€

💰 *CELKOVÝ ZISK V KC*
⏩pri vklade 2500KC ZISK 12125KC
⏩pri vklade 5000KC ZISK 26250KC
⏩pri vklade 12500KC ZISK 65625KC

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
