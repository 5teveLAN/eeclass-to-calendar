from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.safari.options import Options
import time, os
from bs4 import BeautifulSoup
from ics import Calendar, Event
from datetime import datetime

# 登入網址與作業頁面
LOGIN_URL = "https://eeclass.utaipei.edu.tw/index/login"  # 你的學校登入網址
HOMEWORK_URL = "https://eeclass.utaipei.edu.tw/dashboard/latestEvent"  # 公告頁面
USERNAME = "u11107001"
PASSWORD = "20040616s"

# 設置 Safari WebDriver
options = Options()
driver = webdriver.Safari(options=options)

# 開啟登入頁面
driver.get(LOGIN_URL)

# 填寫帳號密碼並提交
try:
    username_field = driver.find_element(By.NAME, "account")
    password_field = driver.find_element(By.NAME, "password")
    
    # 填寫帳號與密碼
    username_field.send_keys(USERNAME)
    password_field.send_keys(PASSWORD)
    
    
    # 點擊登入按鈕
    login_button = driver.find_element(By.CLASS_NAME, "btn-lg")
    login_button.click()


    login_button = WebDriverWait(driver, 10).until(
    EC.presence_of_element_located((By.CLASS_NAME, "keepLoginBtn"))
    )
    login_button.click()


    # 等待跳轉至首頁或公告頁面
    WebDriverWait(driver, 10).until(
        EC.url_changes(LOGIN_URL)
    )
    print("登入成功!")
except Exception as e:
    print("登入過程中發生錯誤:", e)
    driver.quit()
    exit(1)

# 進入公告頁面
time.sleep(3)
driver.get(HOMEWORK_URL)

# 等待頁面加載
time.sleep(3)  # 等待頁面完全加載

# 使用 BeautifulSoup 抓取作業公告

soup = BeautifulSoup(driver.page_source, "html.parser")

# 抓取作業表格
table = soup.find('table', {'id': 'recentEventTable'})
rows = table.find_all('tr')
assignments = []
# 迭代每一行並抓取作業的標題、來源和期限
for row in rows:
    columns = row.find_all('td')
    if len(columns) > 0:
        title = columns[0].get_text(strip=True)
        source = columns[1].get_text(strip=True)
        deadline = columns[2].get_text(strip=True)
        
        assignments.append({
            "title": title,
            "source": source,
            "deadline": deadline
        })
        

# 完成後關閉瀏覽器
driver.quit()

cal = Calendar()

for assignment in assignments:
    event = Event()
    event.name = f"{assignment['title']} - {assignment['source']}"
    event.begin = datetime.strptime(assignment['deadline'], "%Y-%m-%d")
    # 使用課程名稱 + 作業名稱來生成固定的 UID，避免重複
    event.uid = f"{assignment['source']}-{assignment['title']}".replace(" ", "_")
    cal.events.add(event)
    
# 將行事曆存成 .ics 檔案
with open("eeclass_assignments.ics", "w", encoding="utf-8") as f:
    f.writelines(cal)

os.system(f"open {"eeclass_assignments.ics"}")