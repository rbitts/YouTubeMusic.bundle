# YouTubeMusic.bundle
유튜브 음원용 에이전트
# 라이브러리 폴더 구조
에이전트 동작을 위해 아래의 구조와 같이 라이브러리를 구성해 주세요.

- 채널명 [채널아이디]
   - 플레이리스트명 [플레이리스트아이디]
      - 음원
      - 음원
      
# SJVA youtube-dl 저장형식
%(uploader)s [%(channel_id)s]/%(playlist_title)s[%(playlist_id)s]/%(playlist_index)s - %(title)s [%(id)s].%(ext)s
