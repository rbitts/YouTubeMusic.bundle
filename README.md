# YouTubeMusic.bundle
유튜브 음원용 에이전트
# 설치 및 준비
 1. 플렉스 Plug-ins에 설치
 2. 에이전트 설정에 google api 키 입력 (아래 참조)
 
 https://bonniness.tistory.com/m/entry/%EA%B5%AC%EA%B8%80-Youtube-API-%EC%82%AC%EC%9A%A9-%EC%82%AC%EC%9A%A9%EC%84%A4%EC%A0%95-KEY-%EB%B0%9C%EA%B8%89-%ED%85%8C%EC%8A%A4%ED%8A%B8?category=688269
 
# 라이브러리 폴더 구조
에이전트 동작을 위해 아래의 구조와 같이 라이브러리를 구성해 주세요.

- 채널명 [채널아이디]
   - 플레이리스트명 [플레이리스트아이디]
      - 음원
      - 음원
      
# SJVA youtube-dl 저장형식
%(uploader)s [%(channel_id)s]/%(playlist_title)s[%(playlist_id)s]/%(playlist_index)s - %(title)s [%(id)s].%(ext)s
