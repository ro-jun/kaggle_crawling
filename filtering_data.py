from selenium import webdriver
from selenium.webdriver.common.by import By
import time

# Chrome 브라우저 자동 관리 및 실행
options = webdriver.ChromeOptions()
options.add_argument("--disable-gpu")  # GPU 가속 비활성화
options.add_argument("--no-sandbox")  # 샌드박스 모드 비활성화(권한 문제 방지)

# ChromeDriver 없이 실행
driver = webdriver.Chrome(options=options)  

# Kaggle 필터 적용된 URL로 이동 (csv, 24-12-08 당시 Highly-voted: LLM Fine-Tuning)
url = "https://www.kaggle.com/datasets?fileType=csv&feedbackIds=16"
driver.get(url)

# 페이지 로드 대기 (JavaScript 렌더링을 위해)
time.sleep(3)

datasets = []

while True:
    # 데이터셋 카드 요소 찾기
    dataset_cards = driver.find_elements(By.XPATH, '//div[contains(@class, "sc-kqLymz")]/ul[contains(@class, "MuiList-root km-list css-1uzmcsd")]/li/div')

    for card in dataset_cards:
        try:
            # 제목, 파일타입, 링크 추출
            title = card.find_element(By.CSS_SELECTOR, 'a').get_attribute("aria-label") # 제목
            file_type = card.find_element(By.XPATH, './/span[2][contains(@class, "sc-geXuza")]').text  # 유용성, 파일타입, 파일크기
            link = card.find_element(By.CSS_SELECTOR, 'a').get_attribute("href")  # 링크(url)
            datasets.append({
                "title": title,
                "file_type":file_type,
                "url": link,
            })
        except Exception as e:
            print(f"오류 발생: {e}")

    # 다음 페이지 버튼 찾기
    try:
        next_button = driver.find_element(By.XPATH, '//button[contains(@aria-label, "Go to next page")]')
        # 버튼이 비활성화된 경우 종료
        if "disabled" in next_button.get_attribute("class"):
            print("더 이상 페이지가 없습니다. 종료합니다.")
            break

        # 다음 페이지 버튼 클릭
        driver.execute_script("arguments[0].click();", next_button)
        time.sleep(3)  # 페이지 로드 대기
    except Exception as e:
        print(f"다음 페이지 버튼을 찾을 수 없습니다: {e}")
        break  # 버튼이 없을 경우 종료

# 브라우저 종료
driver.quit()

# 결과 출력
print("데이터셋 목록:")
for dataset in datasets:
    print(dataset)
print(f"데이터 추출 갯수: {len(datasets)}")