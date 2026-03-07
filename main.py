import json
import os
from datetime import datetime, timedelta

import requests

# --- 1. إعدادات الزمان والمكان ---
now = datetime.now()
seven_days_ago = (now - timedelta(days=7)).strftime("%Y-%m-%d")

year, month, day = now.strftime("%Y"), now.strftime("%m"), now.strftime("%d")
daily_path = f"archive/{year}/{month}/{day}"
os.makedirs(daily_path, exist_ok=True)


# --- 2. جلب البيانات (التنقيب الموضوعي) ---
def fetch_tech_gold():
    print(f"📡 رادار EchoPulse يبحث في مشاريع منذ {seven_days_ago}...")
    url = f"https://api.github.com/search/repositories?q=created:>{seven_days_ago}&sort=stars&order=desc&per_page=12"

    headers = {"Accept": "application/vnd.github.v3+json"}
    try:
        response = requests.get(url, headers=headers, timeout=15)
        response.raise_for_status()
        return response.json().get("items", [])
    except Exception as e:
        print(f"❌ خطأ في الجلب: {e}")
        return []


# --- 3. بناء تقرير اليوم (مع ميزة الفلترة بالوسوم) ---
def create_daily_html(repos):
    print(f"🎨 توليد تقرير اليوم البصري...")

    cards_html = ""
    for r in repos:
        topics = r.get("topics", [])
        topics_joined = ",".join(topics)  # تجهيز الوسوم للفلترة البرمجية

        # تحويل الوسم لزر قابل للضغط يقوم بتشغيل دالة الفلترة
        topics_html = "".join(
            [
                f'<button onclick="filterByTag(\'{t}\')" class="bg-emerald-500/10 hover:bg-emerald-500/20 text-emerald-400 text-[10px] px-2 py-0.5 rounded border border-emerald-500/20 mr-1 mb-1 lowercase transition-colors cursor-pointer">#{t}</button>'
                for t in topics[:6]
            ]
        )

        # أضفنا الكلاس repo-card و data-topics لتتعرف عليها الجافا سكريبت
        cards_html += f"""
        <div class="repo-card group bg-[#1e293b] p-6 rounded-2xl border border-slate-800 hover:border-emerald-500/40 transition-all shadow-xl" data-topics="{topics_joined}">
            <div class="flex justify-between items-start">
                <h2 class="text-xl font-bold text-white group-hover:text-emerald-400 transition-colors">{r["name"]}</h2>
                <div class="flex items-center gap-2">
                    <span class="text-yellow-500 text-sm">⭐ {r["stargazers_count"]}</span>
                </div>
            </div>
            <p class="mt-3 text-slate-400 text-sm leading-relaxed h-12 overflow-hidden">{r["description"] or "لا يوجد وصف من المصدر."}</p>

            <div class="mt-4 flex flex-wrap">
                {topics_html}
            </div>

            <div class="mt-6 flex items-center justify-between border-t border-slate-700/50 pt-4">
                <span class="text-xs text-slate-500 font-mono">{r["language"] or "Mixed"}</span>
                <a href="{r["html_url"]}" target="_blank" class="text-xs bg-slate-700 hover:bg-emerald-600 text-white px-3 py-1.5 rounded-lg transition-colors">كود المصدر ↗</a>
            </div>
        </div>
        """

    html = f"""
    <!DOCTYPE html>
    <html lang="ar" dir="rtl">
    <head>
        <meta charset="UTF-8"><meta name="viewport" content="width=device-width, initial-scale=1.0">
        <script src="https://cdn.tailwindcss.com"></script>
        <title>EchoPulse | حصاد {day}-{month}-{year}</title>
    </head>
    <body class="bg-[#0f172a] text-slate-200 p-6 md:p-12">
        <div class="max-w-5xl mx-auto">
            <header class="flex justify-between items-center mb-6">
                <div>
                    <a href="../../../../index.html" class="text-emerald-400 hover:underline text-sm">← الفهرس الرئيسي</a>
                    <h1 class="text-3xl font-black text-white mt-2">نبض التقنية <span class="text-emerald-500">{day}.{month}.{year}</span></h1>
                </div>
                <div class="text-left">
                    <span class="block text-xs text-slate-500">تم الرصد بواسطة</span>
                    <span class="font-mono text-emerald-400">EchoPulse_Bot</span>
                </div>
            </header>

            <div id="filter-status" class="mb-6 h-8 flex items-center text-sm font-bold text-emerald-300"></div>

            <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6" id="repos-container">
                {cards_html}
            </div>
        </div>

        <script>
            function filterByTag(tag) {{
                let cards = document.querySelectorAll('.repo-card');
                let count = 0;
                cards.forEach(function(card) {{
                    let tags = card.getAttribute('data-topics').split(',');
                    if (tags.includes(tag)) {{
                        card.style.display = 'block';
                        count++;
                    }} else {{
                        card.style.display = 'none';
                    }}
                }});

                // تحديث حالة الفلتر وإظهار زر الإلغاء
                document.getElementById('filter-status').innerHTML =
                    'تصفية حسب: <span class="bg-emerald-500/20 px-2 py-1 rounded mx-2">#' + tag + '</span> (' + count + ' نتائج) ' +
                    '<button onclick="resetFilter()" class="mr-4 text-red-400 hover:text-red-300 underline text-xs">✖ إلغاء الفلتر</button>';
            }}

            function resetFilter() {{
                let cards = document.querySelectorAll('.repo-card');
                cards.forEach(function(card) {{
                    card.style.display = 'block';
                }});
                document.getElementById('filter-status').innerHTML = '';
            }}
        </script>
    </body>
    </html>
    """
    return html


# --- 4. بناء واجهة الهبوط (كما هي دون تغيير) ---
def update_root_index():
    print("🌐 تحديث واجهة الهبوط التعريفية...")
    reports = []
    for root, dirs, files in os.walk("archive"):
        if "index.html" in files:
            p = root.split(os.sep)
            if len(p) >= 4:
                date_str = f"{p[1]}-{p[2]}-{p[3]}"
                reports.append({"date": date_str, "path": f"{root}/index.html"})

    reports.sort(key=lambda x: x["date"], reverse=True)

    root_html = f"""
    <!DOCTYPE html>
    <html lang="ar" dir="rtl">
    <head>
        <meta charset="UTF-8"><meta name="viewport" content="width=device-width, initial-scale=1.0">
        <script src="https://cdn.tailwindcss.com"></script>
        <title>EchoPulse | رادار الاستكشاف التقني</title>
    </head>
    <body class="bg-[#020617] text-slate-300 font-sans">
        <div class="max-w-5xl mx-auto pt-24 pb-16 px-6 text-center">
            <h1 class="text-7xl font-black text-white mb-6">Echo<span class="text-emerald-500">Pulse</span></h1>
            <p class="text-xl text-slate-400 max-w-2xl mx-auto leading-relaxed mb-10">
                نظام مستقل للأرشفة التقنية. نقوم بمسح مستودعات GitHub يومياً لتوثيق ولادة الأدوات والبرمجيات الصاعدة، مع استخلاص وسومها البرمجية مباشرة من المنبع.
            </p>

            <div class="grid gap-6 max-w-2xl mx-auto text-right">
                <div class="bg-slate-900/50 border border-slate-800 rounded-3xl p-8 backdrop-blur-sm">
                    <h2 class="text-xl font-bold text-white mb-6 border-r-4 border-emerald-500 pr-4">سجل الأرشفة اليومي</h2>
                    <div class="space-y-3">
                        {
        "".join(
            [
                f'''
                        <a href="{r['path']}" class="group flex items-center justify-between p-4 rounded-xl border border-slate-800 hover:border-emerald-500/50 transition-all">
                            <span class="text-slate-300 group-hover:text-emerald-400 font-medium">📅 تقرير يوم {r['date']}</span>
                            <span class="text-slate-600 group-hover:text-emerald-400 group-hover:translate-x-[-5px] transition-all">←</span>
                        </a>
                        '''
                for r in reports
            ]
        )
    }
                    </div>
                </div>
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
        with open(f"{daily_path}/raw_data.json", "w", encoding="utf-8") as f:
            json.dump(repos, f, ensure_ascii=False, indent=4)

        with open(f"{daily_path}/index.html", "w", encoding="utf-8") as f:
            f.write(create_daily_html(repos))

        update_root_index()
        print("✅ اكتمل التحديث. الرادار جاهز للعرض!")
    else:
        print("📭 لم يتم العثور على نبضات جديدة اليوم.")
