import asyncio
import aiohttp
import os

# تنظیمات
INPUT_FILE = 'urls.txt'
ALIVE_FILE = 'alive.txt'
DEAD_FILE = 'dead.txt'
CONCURRENCY_LIMIT = 200 # تعداد تست همزمان (بیشتر از این ممکنه گیت‌هاب بلاک کنه)
TIMEOUT = 10 # مهلت پاسخگویی هر لینک به ثانیه

async def check_url(session, url, semaphore):
    async with semaphore:
        url = url.strip()
        if not url:
            return None
        
        try:
            # ارسال درخواست فقط برای گرفتن هدر (سریع‌تر از دانلود کل محتواست)
            async with session.head(url, timeout=TIMEOUT, allow_redirects=True) as response:
                if response.status == 200:
                    print(print_msg(url, "ALIVE", "🟢"))
                    return url, True
                else:
                    print(print_msg(url, f"DEAD (Status: {response.status})", "🔴"))
                    return url, False
        except Exception as e:
            print(print_msg(url, f"DEAD (Error)", "🔴"))
            return url, False

def print_msg(url, status, emoji):
    # برای اینکه لاگ‌ها خیلی طولانی نشن، فقط اول و آخر لینک رو نشون میدیم
    short_url = url Hellenic = url[:40] + "..." if len(url) > 40 else url
    return f"{emoji} {status}: {short_url}"

async def main():
    if not os.path.exists(INPUT_FILE):
        print(f"Error: {INPUT_FILE} not found!")
        return

    with open(INPUT_FILE, 'r', encoding='utf-8') as f:
        urls = [line.strip() for line in f if line.strip()]

    print(f"Total URLs to check: {len(urls)}")

    semaphore = asyncio.Semaphore(CONCURRENCY_LIMIT)
    
    # تنظیمات مرورگر فرضی برای اینکه سرورها رد نکنن درخواست رو
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
    
    async with aiohttp.ClientSession(headers=headers) as session:
        tasks = [check_url(session, url, semaphore) for url in urls]
        results = await asyncio.gather(*tasks)

    # جداسازی زنده و مرده‌ها
    alive_urls = []
    dead_urls = []
    for res in results:
        if res:
            url, is_alive = res
            if is_alive:
                alive_urls.append(url)
            else:
                dead_urls.append(url)

    # ذخیره در فایل
    with open(ALIVE_FILE, 'w', encoding='utf-8') as f:
        f.write('\n'.join(alive_urls))
        
    with open(DEAD_FILE, 'w', encoding='utf-8') as f:
        f.write('\n'.join(dead_urls))

    print("\n--- Done! ---")
    print(f"🟢 Alive: {len(alive_urls)}")
    print(f"🔴 Dead: {len(dead_urls)}")

if __name__ == '__main__':
    asyncio.run(main())
