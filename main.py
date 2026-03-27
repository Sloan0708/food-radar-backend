import requests
from fastapi import FastAPI

app = FastAPI()

# 🗝️ 把你的 Google API 金鑰貼在這裡 (請保留前後的引號)
GOOGLE_API_KEY = "AIzaSyANjHGjjXr28Fu4_L2Qq-ACYueqnglOaoE"

# 🧠 核心商業邏輯：業配文掃雷演算法
def analyze_real_score(reviews: list) -> float:
    if not reviews:
        return 0.8  # 如果是沒有評論的新店，給個 80% 的觀望分數
        
    # 網紅常用的浮誇業配詞彙 (你可以隨時擴充！)
    red_flags = ["入口即化", "超推", "必吃", "絕美", "專屬優惠", "天啊", "神級", "CP值"]
    score = 100
    
    # 把這家店的「所有評論」合併成一大串文字來檢查
    all_text = " ".join([r.get("text", "") for r in reviews])
    
    for flag in red_flags:
        if flag in all_text:
            score -= 20  # 抓到一個業配詞就重扣 20 分！
            
    # 確保分數在 10~100 之間，並轉換成小數點 (0.1 ~ 1.0) 讓 Flutter 看得懂
    return max(10, score) / 100.0

@app.get("/api/restaurants")
def get_real_world_data(lat: float = 24.6877, lng: float = 120.9081):
    results = []
    
    try:
        # 1. 呼叫 Google 抓取附近的餐廳 (半徑 1500 公尺)
        search_url = f"https://maps.googleapis.com/maps/api/place/nearbysearch/json?location={lat},{lng}&radius=1500&type=restaurant&language=zh-TW&key={GOOGLE_API_KEY}"
        search_res = requests.get(search_url).json()
        
        # 只取前 5 家店，避免手機等太久
        places = search_res.get("results", [])[:5]
        
        for place in places:
            place_id = place.get("place_id")
            name = place.get("name")
            
            # 2. 呼叫 Google 抓取這家店的「真實網友評論」
            details_url = f"https://maps.googleapis.com/maps/api/place/details/json?place_id={place_id}&fields=name,reviews&language=zh-TW&key={GOOGLE_API_KEY}"
            details_res = requests.get(details_url).json()
            
            reviews_data = details_res.get("result", {}).get("reviews", [])
            display_review = reviews_data[0].get("text") if reviews_data else "這家店目前還沒有評論喔！"
            
            # 3. 丟進演算法，算出「真實度」
            real_score = analyze_real_score(reviews_data)
            
            # 整理成 Flutter App 規定的格式
            results.append({
                "name": name,
                "review": display_review,
                "score": real_score,
                "distanceMeters": 500  # 距離計算比較複雜，我們先統一顯示 500m 避免前端報錯
            })
            
        return results
        
    except Exception as e:
        # 如果發生任何錯誤，回傳一個防呆假資料給手機，避免 App 崩潰
        print("發生錯誤:", e)
        return [{"name": "雷達連線異常", "review": str(e), "score": 0.0, "distanceMeters": 0}]