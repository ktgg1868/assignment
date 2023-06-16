from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from bs4 import BeautifulSoup as bs
import pandas as pd
import time
import os

#작업시간을 변수에 저장
now = time.localtime()
s = '%04d년 %02d월 %02d일 %02d시 %02d분 %02d초' % (now.tm_year, now.tm_mon, now.tm_mday, now.tm_hour, now.tm_min, now.tm_sec)

# 사용자로부터 키워드, 영상 개수, 댓글 개수, 저장 경로를 입력받습니다.
keyword = input("검색할 키워드를 입력하세요: ")
num_videos = int(input("검색할 영상의 개수를 입력하세요: "))
num_comments = int(input("추출할 댓글의 개수를 입력하세요: "))
file_path = input("크롤링한 결과를 저장할 경로를 입력하세요(예: C:/data/): ")
save_xlsx = f"{file_path}{s} {keyword}.xlsx"

#입력받은 폴더경로가 없을 경우 생성
if not os.path.exists(file_path):
    print(f"입력하신 폴더경로인 {file_path} 가 존재하지 않아 경로 생성 후 크롤링 작업을 진행합니다.")
    os.makedirs(file_path)
else:
    print(f"입력한 경로인 {file_path} 가 존재하어 바로 크롤링 작업을 시작하겠습니다.")

#웹드라이버 설정
print("웹드라이버 설정 시작")
path = ChromeDriverManager().install()
driver = webdriver.Chrome(path)
print("웹드라이버 설정 완료")

# 유튜브 검색 페이지로 이동합니다.
driver.get(f"https://www.youtube.com/results?search_query={keyword}")

# 검색 결과에서 영상 링크를 추출합니다.
video_links = []
while len(video_links) < num_videos:
    # 페이지 스크롤을 아래로 내립니다.
    driver.find_element(By.TAG_NAME,'body').send_keys(Keys.END)
    driver.implicitly_wait(3)
    time.sleep(3)  # 페이지 로딩을 위해 잠시 대기합니다.

    soup = bs(driver.page_source, 'html.parser')

    # 영상 링크를 추출하여 리스트에 추가합니다.
    for link in soup.find_all('a', {'id': 'video-title'}):
        video_links.append("https://www.youtube.com" + link['href'])

# 데이터를 저장할 리스트를 생성합니다.
data = []

# 댓글 추출.
num = int(0)
for video_url in video_links[:num_videos]:
    driver.get(video_url)

    time.sleep(3)
    soup = bs(driver.page_source, 'html.parser')

    # 댓글추출 -> 리스트에 추가
    comments = soup.find_all('yt-formatted-string', {'id': 'content-text'})
    content_titles = soup.find('yt-formatted-string', {'class': 'style-scope ytd-watch-metadata'})
    comment_authors = soup.find_all('a', {'id': 'author-text'})
    comment_timestamps = soup.find_all('yt-formatted-string', {'class': 'published-time-text'})
    num_comments_actual = min(num_comments, len(comments), len(comment_authors), len(comment_timestamps))
    
    for i in range(num_comments_actual):
        comment = comments[i]
        title = content_titles.text
        author = comment_authors[i].text.strip()
        timestamp = comment_timestamps[i].text
        content = comment.text
        
        print("-"*30)
        print("영상 URL: ", video_url)
        print("영상 제목: ", title)
        print("댓글 작성자명: ", author)
        print("댓글 작성시간: ", timestamp)
        print("댓글 내용: ", content)
        print("-"*30)
        print("\n")

        # 데이터를 리스트에 추가합니다.
        data.append([num, video_url, title, author, timestamp, content])
        
        num += 1

# WebDriver를 종료합니다.
driver.quit()

# 데이터를 데이터프레임으로 변환합니다.
df = pd.DataFrame(data, columns=['','영상 URL', '영상 제목', '댓글 작성자명', '댓글 작성시간', '댓글 내용'])

# xlsx 파일로 저장합니다.
df.to_excel(save_xlsx, index=False, header=True)

print("데이터 저장이 완료되었습니다.")