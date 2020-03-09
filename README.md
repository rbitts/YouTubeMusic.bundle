# YouTubeMusic.bundle
유튜브 음원용 에이전트
# 설치 및 준비
 1. 플렉스 Plug-ins에 설치
 2. 에이전트 설정에 google api 키 입력 (아래 참조)
 https://www.google.com/url?sa=t&source=web&rct=j&url=https://bonniness.tistory.com/entry/%25EA%25B5%25AC%25EA%25B8%2580-Youtube-API-%25EC%2582%25AC%25EC%259A%25A9-%25EC%2582%25AC%25EC%259A%25A9%25EC%2584%25A4%25EC%25A0%2595-KEY-%25EB%25B0%259C%25EA%25B8%2589-%25ED%2585%258C%25EC%258A%25A4%25ED%258A%25B8&ved=2ahUKEwjW4bn1jozoAhVPa94KHbo4ALsQFjACegQIBBAB&usg=AOvVaw2NWR-Pfy67gZHoRsXBdLTN&cshid=1583713095368
 
# 라이브러리 폴더 구조
에이전트 동작을 위해 아래의 구조와 같이 라이브러리를 구성해 주세요.

- 채널명 [채널아이디]
   - 플레이리스트명 [플레이리스트아이디]
      - 음원
      - 음원
      
# SJVA youtube-dl 저장형식
%(uploader)s [%(channel_id)s]/%(playlist_title)s[%(playlist_id)s]/%(playlist_index)s - %(title)s [%(id)s].%(ext)s
