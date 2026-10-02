# YouTube Selenium Video Automation

使用 **Python + Selenium + Chrome WebDriver** 自動搜尋 YouTube 影片、篩選符合條件的影片並自動播放。

## Features

- 🔎 自動搜尋 YouTube 關鍵字
- 📊 依觀看次數篩選影片
- 🚫 排除廣告、播放清單等非一般影片
- 🎬 自動選擇符合條件的影片
- ▶️ 自動播放影片
- ⏳ 確認影片實際開始播放
- 🏁 等待影片播放完成
- ❌ 播放結束後自動關閉瀏覽器

## Workflow

```text
YouTube Search
      ↓
Filter Results
      ↓
Exclude Ads / Playlists
      ↓
Select Video
      ↓
Open Video
      ↓
Check Playback
      ↓
Start Playback
      ↓
Wait for Video End
      ↓
Close Browser
```

## How It Works

### 1. YouTube Search

使用 Selenium 開啟 YouTube 搜尋頁面，並根據指定的關鍵字取得搜尋結果。

### 2. Video Filtering

取得搜尋結果中的影片網址，確認網址符合：

```text
/watch?v=VIDEO_ID
```

避免選擇播放清單或其他非一般影片。

### 3. Automatic Playback

透過 YouTube HTML5 Video Player：

```text
video.html5-main-video
```

檢查影片播放狀態，並嘗試自動開始播放。

### 4. Playback Completion

使用 JavaScript `ended` event 判斷影片是否播放完成：

```javascript
video.addEventListener('ended', ...)
```

### 5. Browser Cleanup

影片播放完成後執行：

```python
driver.quit()
```

自動關閉 Chrome WebDriver。

## Usage

修改搜尋關鍵字：

```python
SEARCH_TERM = "幸祜"
```

例如：

```python
SEARCH_TERM = "YOASOBI"
```

程式即可自動搜尋指定關鍵字並播放符合條件的影片。

## Requirements

安裝 Selenium：

```bash
pip install selenium
```

## Notes

YouTube 頁面結構、播放器行為及瀏覽器的 autoplay policy
可能隨版本更新而改變，因此 Selenium selector 與自動播放功能
可能需要進行調整。
