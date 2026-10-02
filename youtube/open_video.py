from urllib.parse import urlencode, urlparse, parse_qs

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

from selenium.common.exceptions import (
    TimeoutException,
    NoSuchElementException,
    StaleElementReferenceException
)

import time

# ============================================================
# 設定
# ============================================================

SEARCH_TERM = "rick astley"  # 要搜尋的關鍵字
WAIT_TIME = 20

# ============================================================
# Chrome 設定
# ============================================================

options = webdriver.ChromeOptions()

# 允許網頁自動播放
options.add_argument(
    "--autoplay-policy=no-user-gesture-required"
)

# 避免部分自動化環境造成播放器行為異常
options.add_argument("--disable-blink-features=AutomationControlled")

# ============================================================
# 開啟 Chrome
# ============================================================

driver = webdriver.Chrome(options=options)
driver.maximize_window()
wait = WebDriverWait(driver, WAIT_TIME)

try:
    # ========================================================
    # 1. YouTube 搜尋
    # ========================================================
    query = urlencode({
        "search_query": SEARCH_TERM,
        "sp": "CAM="
    })
    search_url = f"https://www.youtube.com/results?{query}"
    print("搜尋：", SEARCH_TERM)
    driver.get(search_url)

    # ========================================================
    # 2. 等待搜尋結果
    # ========================================================
    wait.until(
        EC.presence_of_element_located(
            (By.CSS_SELECTOR, "ytd-video-renderer")
        )
    )
    time.sleep(2)

    # ========================================================
    # 3. 找第一個「一般影片」
    # ========================================================
    video_results = driver.find_elements(
        By.CSS_SELECTOR,
        "ytd-video-renderer"
    )
    first_video_id = None
    first_video_title = None

    for result in video_results:
        try:
            link = result.find_element(
                By.CSS_SELECTOR,
                "a#video-title"
            )
            href = link.get_attribute("href")
            title = (
                link.get_attribute("title")
                or link.text.strip()
            )
            if not href:
                continue

            # ------------------------------------------------
            # 解析網址
            # ------------------------------------------------
            parsed = urlparse(href)
            params = parse_qs(parsed.query)
            # 只接受：https://www.youtube.com/watch?v=xxxx
            #
            if parsed.path != "/watch":
                continue

            if "v" not in params:
                continue

            video_id = params["v"][0]

            if not video_id:
                continue

            # ------------------------------------------------
            # 排除廣告
            # ------------------------------------------------
            result_text = result.text.lower()
            ad_keywords = [
                "sponsored",
                "廣告",
                "贊助內容"
            ]
            if any(
                keyword in result_text
                for keyword in ad_keywords
            ):
                print("跳過疑似廣告：", title)
                continue

            # ------------------------------------------------
            # 找到了
            # ------------------------------------------------
            first_video_id = video_id
            first_video_title = title
            break
        except (
            StaleElementReferenceException,
            NoSuchElementException
        ):
            continue

    # ========================================================
    # 4. 確認找到影片
    # ========================================================
    if first_video_id is None:
        raise Exception("找不到符合條件的一般影片")

    print()
    print("選擇影片：", first_video_title)
    print("Video ID：", first_video_id)

    # ========================================================
    # 5. 開啟單一影片
    # ========================================================
    video_url = (
        f"https://www.youtube.com/watch?v={first_video_id}"
    )
    print("開啟影片...")
    driver.get(video_url)
    
    # ========================================================
    # 6. 等待 video 元素
    # ========================================================
    wait.until(
        EC.presence_of_element_located(
            (By.CSS_SELECTOR, "video.html5-main-video")
        )
    )
    print("Video 元素已載入")
    time.sleep(2)

    # ========================================================
    # 7. 查看目前播放器狀態
    # ========================================================
    state = driver.execute_script("""
        const video = document.querySelector(
            'video.html5-main-video'
        );

        if (!video) {
            return null;
        }
        return {
            paused: video.paused,
            ended: video.ended,
            currentTime: video.currentTime,
            duration: video.duration
        };
    """)
    print()
    print("目前播放器狀態：")
    print(state)

    # ========================================================
    # 8. 如果影片暫停，直接點 YouTube 播放按鈕
    # ========================================================
    if state and state["paused"]:
        print("影片目前是暫停狀態")
        print("嘗試點擊 YouTube 播放按鈕...")
        try:

            play_button = WebDriverWait(
                driver,
                10
            ).until(
                EC.element_to_be_clickable(
                    (
                        By.CSS_SELECTOR,
                        ".ytp-play-button"
                    )
                )
            )
            
            # 查看按鈕目前狀態
            aria_label = play_button.get_attribute(
                "aria-label"
            )
            print("播放按鈕：", aria_label)

            # 如果按鈕是「播放」，才點
            if aria_label and (
                "播放" in aria_label
                or "Play" in aria_label
            ):
                driver.execute_script(
                    "arguments[0].click();",
                    play_button
                )
                print("已點擊播放按鈕")
        except Exception as e:
            print("第一次點擊播放按鈕失敗：", e)

    # ========================================================
    # 9. 確認影片真的開始播放
    # ========================================================
    print("等待影片開始播放...")

    def video_is_playing(driver):
        try:
            return driver.execute_script("""
                const video = document.querySelector(
                    'video.html5-main-video'
                );

                if (!video) {
                    return false;
                }

                return (
                    !video.paused &&
                    !video.ended &&
                    video.currentTime > 0
                );
            """)
        except Exception:
            return False
    try:
        WebDriverWait(
            driver,
            10
        ).until(video_is_playing)
        print("================================")
        print("影片已經開始播放！")
        print("================================")
    except TimeoutException:

        # ====================================================
        # 10. 如果仍然暫停，再點一次
        # ====================================================
        print("影片仍然沒有播放")
        print("再次嘗試播放...")
        try:
            play_button = driver.find_element(
                By.CSS_SELECTOR,
                ".ytp-play-button"
            )
            driver.execute_script(
                "arguments[0].click();",
                play_button
            )
            time.sleep(2)
        except Exception as e:
            print("第二次點擊失敗：", e)

        # 再確認一次
        WebDriverWait(
            driver,
            10
        ).until(video_is_playing)
        print("影片開始播放！")

    # ========================================================
    # 11. 等待影片播放完畢
    # ========================================================
    print()
    print("影片正在播放...")
    print("等待影片播放完畢...")
    driver.set_script_timeout(
        24 * 60 * 60
    )
    result = driver.execute_async_script("""
        const video = document.querySelector(
            'video.html5-main-video'
        );
        const done = arguments[
            arguments.length - 1
        ];
        if (!video) {
            done("找不到 video");
            return;
        }
        // 已經播放完畢
        if (video.ended) {
            done("影片已播放完畢");
            return;
        }
        // 監聽 ended
        video.addEventListener(
            'ended',
            () => {
                done("影片播放完畢");
            },
            {
                once: true
            }
        );
    """)
    print(result)
except TimeoutException:
    print()
    print("等待逾時")
    print("影片可能沒有正常載入或播放")
except Exception as e:
    print()
    print("發生錯誤：")
    print(e)
finally:
    print()
    print("關閉瀏覽器")
    driver.quit()