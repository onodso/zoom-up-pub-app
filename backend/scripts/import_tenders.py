import requests
import xml.etree.ElementTree as ET
import datetime
import os
import sys

# Add backend to path
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from database import SessionLocal, engine, Base
from models.tenders import Tender
from models.entities import Entity

# Sales Playbook Definition (From docs/SALES_PLAYBOOK_PATTERNS.md)
# Usage Category -> List of Pattern Rules

PLAYBOOK_RULES = [
    {
        "usage": "完全デジタル市役所 (Nara Model)",
        "pattern": "🏛️ ZCC+ZP+ZVA (Nara Model)",
        "keywords": ["デジタル市役所", "奈良市モデル", "24時間365日", "自己解決", "ワンストップ", "ZCC", "ZVA", "職員の負荷減少"]
    },
    {
        "usage": "遠隔授業/教育 (Education)",
        "pattern": "🏫 ZM+ZR+ZRA (Oita Model)",
        "keywords": ["学校", "GIGA", "教委", "教育", "授業", "校務", "学習用", "不登校", "遠隔", "会話の資産化", "インサイト取得", "大分モデル"]
    },
    {
        "usage": "窓口DX (Window DX)",
        "pattern": "🎯 ZP+AI Concierge",
        "keywords": ["シンプル版コールセンター", "自動応答", "窓口", "AIボイスエージェント", "コンタクトセンター", "チャットボット"]
    },
    {
        "usage": "品質向上/カスハラ対策 (Quality/ZRA)",
        "pattern": "🔑 ZP+AIC+ZRA (会話分析)",
        "keywords": ["通話分析", "音声認識", "テキスト化", "感情分析", "モニタリング", "品質向上", "声の", "カスハラ", "リスク検知", "トーク分析", "会話資産", "構造化", "スコアカード", "カスタマイズ要約", "全文文字起こし"]
    },
    {
        "usage": "庁内ICT (Internal)",
        "pattern": "📞 ZP+AIC (電話リプレイス)",
        "keywords": ["PBX", "電話交換機", "内線", "固定電話", "電話網", "IP電話", "通話録音", "自動通話録音", "通話要約", "簡易議事録"]
    },
    {
        "usage": "働き方改革 (Work Style)",
        "pattern": "💻 ZM+AIC (Web会議)",
        "keywords": ["Web会議", "Zoom", "Teams", "Webex", "オンライン会議", "テレワーク"]
    },
    {
        "usage": "情報発信 (Events)",
        "pattern": "🎥 Zoom Events (配信)",
        "keywords": ["議会中継", "配信", "ウェビナー", "動画", "オンラインイベント"]
    },
    {
        "usage": "庁内ICT (Internal)",
        "pattern": "📺 Zoom Rooms (会議室)",
        "keywords": ["テレビ会議", "会議室", "端末", "マイクスピーカー"]
    },
    {
        "usage": "全庁DX (All-in)",
        "pattern": "🌐 Integrated (All-in)",
        "keywords": ["自治体DX", "庁内ネットワーク", "グループウェア", "スマートシティ", "デジタル田園", "デジタルツイン"]
    }
]

# Flatten keywords for API search query
SEARCH_KEYWORDS = set()
for rule in PLAYBOOK_RULES:
    for k in rule["keywords"]:
        SEARCH_KEYWORDS.add(k)

API_URL = "https://www.kkj.go.jp/api/"

def setup_database():
    print("🛠️ Creating tables if not exist...")
    # Drop table to ensure clean schema (Dev mode)
    try:
        Tender.__table__.drop(engine, checkfirst=True)
    except Exception as e:
        print(f"Warning dropping table: {e}")
        
    Base.metadata.create_all(bind=engine)

def determine_patterns_and_usage(title, raw_text=""):
    text = (title + " " + raw_text).lower()
    
    matched_patterns = []
    matched_usages = set()
    
    for rule in PLAYBOOK_RULES:
        # Check if ANY keyword matches
        if any(k.lower() in text for k in rule["keywords"]):
            matched_patterns.append(rule["pattern"])
            matched_usages.add(rule["usage"])
    
    if not matched_patterns:
        return "その他", "その他"
        
    # Join with comma
    pattern_str = ", ".join(matched_patterns)
    usage_str = ", ".join(list(matched_usages))
    
    return pattern_str, usage_str

def fetch_and_import():
    db = SessionLocal()
    
    print("📚 Caching entities for matching...")
    entities = db.query(Entity).all()
    name_map = {}
    for e in entities:
        if e.name not in name_map:
            name_map[e.name] = []
        name_map[e.name].append(e)
    
    # Clear existing
    db.query(Tender).delete()
    db.commit()
    
    total_imported = 0

    for keyword in SEARCH_KEYWORDS:
        print(f"🔍 Searching for '{keyword}'...")
        
        params = {
            "Query": keyword,
            "Count": 50, 
        }
        
        try:
            resp = requests.get(API_URL, params=params, timeout=20)
            if resp.status_code != 200:
                print(f"❌ Failed to fetch {keyword}: {resp.status_code}")
                continue
            
            try:
                root = ET.fromstring(resp.content)
                items = root.findall(".//SearchResult")
                print(f"   Found {len(items)} hits.")
                
                for item in items:
                    title_e = item.find("ProjectName")
                    title = title_e.text if title_e is not None else "No Title"
                    
                    date_e = item.find("Date")
                    date_str = date_e.text if date_e is not None else None
                    published_date = None
                    if date_str:
                        try:
                            published_date = datetime.datetime.fromisoformat(date_str).date()
                        except:
                            pass
                    
                    link_e = item.find("ExternalDocumentURI")
                    link = link_e.text if link_e is not None else ""
                    
                    key_e = item.find("Key")
                    source_id = key_e.text if key_e is not None else title
                    
                    lg_code_e = item.find("LgCode") 
                    lg_code = lg_code_e.text if lg_code_e is not None else None
                    
                    if db.query(Tender).filter(Tender.source_id == source_id).first():
                        continue
                    
                    municipality_id = None
                    agency_name = None
                    
                    matches = []
                    for name, entity_list in name_map.items():
                        if name in title:
                            for e in entity_list:
                                if lg_code and e.prefecture_code == lg_code:
                                    matches.append(e)
                                elif not lg_code:
                                    matches.append(e)
                    
                    if matches:
                        matches.sort(key=lambda x: len(x.name), reverse=True)
                        best_entity = matches[0]
                        municipality_id = best_entity.entity_id
                        agency_name = best_entity.name
                    
                    # Determine Patterns (Multi)
                    pattern_str, usage_str = determine_patterns_and_usage(title)
                        
                    tender = Tender(
                        title=title,
                        source_id=source_id,
                        source_url=link,
                        published_date=published_date,
                        agency_name=agency_name,
                        municipality_id=municipality_id,
                        suggested_pattern=pattern_str, 
                        category=usage_str,
                        api_source="KKJ",
                        sales_status="Lead", 
                        raw_data=ET.tostring(item, encoding='unicode')
                    )
                    db.add(tender)
                    total_imported += 1
                
                db.commit()
                
            except ET.ParseError as e:
                print(f"   XML Error: {e}")
            except Exception as e:
                db.rollback()
                print(f"   DB/Process Error: {e}")
                
        except Exception as e:
            print(f"   Network/Outer Error: {e}")

    print(f"✅ Imported {total_imported} tenders.")
    db.close()

if __name__ == "__main__":
    setup_database()
    fetch_and_import()
