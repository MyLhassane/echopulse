import json
import os
from datetime import datetime, timedelta

import requests

# --- 1. إعدادات الزمان والمكان ---
now = datetime.now()
# فلسفة الجلب: البحث عن مشاريع ولدت في آخر 7 أيام لضمان الجودة
seven_days_ago = (now - timedelta(days=7)).strftime("%Y-%m-%d")

year, month, day = now.strftime("%Y"), now.strftime("%m"), now.strftime("%d")
daily_path = f"archive/{year}/{month}/{day}"
os.makedirs(daily_path, exist_ok=True)


# --- 2. جلب البيانات (الذهب التقني) ---
def fetch_tech_gold():
    print(f"📡 جاري البحث عن نبض التقنية منذ {seven_days_ago}...")
    # استعلام ذكي: مشاريع جديدة + زخم عالي + وسم تقني عام
    url = f"https://api.github.com/search/repositories?q=created:>{seven_days_ago}&sort=stars&order=desc&per_page=10"

    try:
        response = requests.get(url, timeout=15)
        response.raise_for_status()
        return response.json().get("items", [])
    except Exception as e:
        print(f"❌ خطأ في الاتصال: {e}")
        return []


# --- 3. بناء صفحة التقرير اليومي (واجهة الأنا) ---
def create_daily_html(repos):
    html = f"""
    <!DOCTYPE html>
    <html lang="ar" dir="rtl">
    <head>
        <meta charset="UTF-8"><script src="https://cdn.tailwindcss.com"></script>
        <title>تقرير {year}-{month}-{day}</title>
    </head>
    <body class="bg-[#0f172a] text-slate-200 p-8">
        <div class="max-w-4xl mx-auto">
            <a href="../../../../index.html" class="text-blue-400 hover:underline">← العودة للفهرس الرئيسي</a>
            <h1 class="text-4xl font-bold my-6 text-emerald-400">حصاد {day}-{month}-{
        year
    }</h1>
            <div class="space-y-6">
                {
        "".join(
            [
                f'''
                <div class="p-6 bg-slate-800 rounded-xl border border-slate-700">
                    <h2 class="text-2xl font-bold text-white">{r['name']}</h2>
                    <p class="text-slate-400 my-2">{r['description'] or 'لا وصف'}</p>
                    <div class="flex justify-between items-center mt-4">
                        <span class="text-xs font-mono bg-blue-900/30 text-blue-300 px-3 py-1 rounded">{r['license']['name'] if r['license'] else 'License: N/A'}</span>
                        <span class="text-yellow-500 font-bold">⭐ {r['stargazers_count']}</span>
                    </div>
                    <a href="{r['html_url']}" target="_blank" class="inline-block mt-4 text-emerald-400 hover:text-emerald-300">فتح المستودع ↗</a>
                </div>
                '''
                for r in repos
            ]
        )
    }
            </div>
        </div>
    </body>
    </html>
    """
    return html


# --- 4. بناء الفهرس الرئيسي (The Portal) ---
def update_root_index():
    print("📂 جاري تحديث الفهرس الرئيسي...")
    reports = []
    # مسح المجلدات للعثور على التقارير
    for root, dirs, files in os.walk("archive"):
        if "index.html" in files:
            # استخراج التاريخ من المسار
            parts = root.split(os.sep)
            if len(parts) >= 4:  # archive/YYYY/MM/DD
                date_str = f"{parts[1]}-{parts[2]}-{parts[3]}"
                reports.append({"date": date_str, "path": f"{root}/index.html"})

    # ترتيب التقارير من الأحدث للأقدم
    reports.sort(key=lambda x: x["date"], reverse=True)

    root_html = f"""
    <!DOCTYPE html>
    <html lang="ar" dir="rtl">
    <head>
        <meta charset="UTF-8"><script src="https://cdn.tailwindcss.com"></script>
        <title>EchoPulse Portal | صدى التقنية</title>
    </head>
    <body class="bg-[#0f172a] text-slate-200 p-12">
        <div class="max-w-3xl mx-auto text-center">
            <h1 class="text-6xl font-black text-transparent bg-clip-text bg-gradient-to-r from-blue-400 to-emerald-400 mb-4">EchoPulse</h1>
            <p class="text-slate-400 mb-12 italic">"عين المارد على مستقبل الكود"</p>
            <div class="bg-slate-800/50 rounded-3xl p-8 border border-slate-700">
                <h2 class="text-2xl font-bold mb-6 border-b border-slate-700 pb-4 text-right">الأرشيف الزمني</h2>
                <ul class="space-y-4 text-right">
                    {"".join([f'<li><a href="{r["path"]}" class="text-xl text-blue-400 hover:text-emerald-400 transition-colors">📅 تقرير يوم {r["date"]}</a></li>' for r in reports])}
                </ul>
            </div>
        </div>
    </body>
    </html>
    """
    with open("index.html", "w", encoding="utf-8") as f:
        f.write(root_html)


# --- 5. تشغيل المحرك ---
if __name__ == "__main__":
    repos = fetch_tech_gold()
    if repos:
        # حفظ البيانات اليومية
        with open(f"{daily_path}/raw_data.json", "w", encoding="utf-8") as f:
            json.dump(repos, f, ensure_ascii=False, indent=4)
        with open(f"{daily_path}/index.html", "w", encoding="utf-8") as f:
            f.write(create_daily_html(repos))

        # تحديث البوابة الرئيسية
        update_root_index()
        print("✅ تم التحديث بنجاح. المارد والأنا في وئام الآن!")
