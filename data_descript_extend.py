import json
from selenium import webdriver
from selenium.webdriver.common.by import By
import os
import time

# JSON 파일 경로 설정
input_file = "D:/kaggle/Kaggle_crawling/kaggle_datasets/filtered_datasets/Well-documented.json."
output_folder = "D:/kaggle/Kaggle_crawling/kaggle_datasets/description_extended_datasets"
os.makedirs(output_folder, exist_ok=True)  # 결과 저장 폴더 생성
output_file = os.path.join(output_folder, "Well-documented_Extended.json")

# JSON 데이터 로드
with open(input_file, "r", encoding="utf-8") as f:
    datasets = json.load(f)

# Chrome 브라우저 자동 관리 및 실행
options = webdriver.ChromeOptions()
options.add_argument("--disable-gpu")  # GPU 가속 비활성화
options.add_argument("--no-sandbox")  # 샌드박스 모드 비활성화(권한 문제 방지)
driver = webdriver.Chrome(options=options)

# 확장된 데이터셋 리스트
extended_datasets = []

# URL마다 접속하여 필요한 정보 크롤링
for dataset in datasets:
    try:
        print(f"URL 접속 중: {dataset['url']}")
        driver.get(dataset["url"])
        time.sleep(3)  # 페이지 로드 대기

        # 필요 정보 크롤링 (예제: 데이터셋 설명과 컬럼 정보)
        try:
            # 데이터셋 설명 가져오기
            data_description = driver.find_element(By.XPATH, '//*[@id="site-content"]/div[2]/div/div[2]/div/div[5]/div[1]/div[1]/div[2]/div/div/div').text

            # 추가 정보 저장
            dataset["data_description"] = data_description
        except Exception as e:
            print(f"추가 정보 크롤링 중 오류 발생: {e}")

        extended_datasets.append(dataset)
        print(f"데이터셋 '{dataset['title']}' 크롤링 완료.")
    except Exception as e:
        print(f"URL '{dataset['url']}' 접속 중 오류 발생: {e}")

# 브라우저 종료
driver.quit()

# 확장된 데이터셋을 JSON 파일로 저장
with open(output_file, "w", encoding="utf-8") as f:
    json.dump(extended_datasets, f, ensure_ascii=False, indent=4)

print(f"확장된 데이터가 {output_file}에 저장되었습니다.")
