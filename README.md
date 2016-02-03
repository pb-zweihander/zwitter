
CUI에서 돌아가는 트위터 클라이언트인 Zwitter입니다!

남에게 배포해보는 첫 파이썬 애플리케이션이고, 또한 반 농담으로 만든 것이기 때문에 완성도는 매우 떨어집니다 ㅠㅠ

자잘한 버그나 부족한 부분은 너그러이 눈감아 주세요!!

## 설치법 ##

Zwitter의 동작에는 [npyscreen](http://www.npcole.com/npyscreen/)이 필요합니다.

```bash
sudo pip3 install npyscreen
sudo python3 setup.py install
```

## 실행법 ##

```bash
zwitter
```

## 사용법 ##

먼저 홈 폴더의 .zwitter.conf.ini 파일에 Consumer 토큰을 입력해야 합니다

토큰의 발급 방법은 생략하겠습니다.

```bash
vi ~/.zwitter.conf.ini
```

```ini
[Consumer]
key = yourconsumerkey
secret = yourconsumersecret
```

만약 엑세스 토큰까지 발급 받으셨다면 훨씬 편합니다. 엑세스 토큰까지 입력해줍니다

```ini
[Consumer]
key = yourconsumerkey
secret = yourconsumersecret

[AccessToken]
key = youraccesstokenkey
secret = youraccesstokensecret
```

그리고 Zwitter를 실행시키면 됩니다

만약 엑세스 토큰을 발급받지 않아 적지 않았다면 웹 브라우저를 이용해 Pin 코드를 발급받게 됩니다

한번 Pin 코드를 이용하여 발급 받은 이후에는 자동으로 엑세스 토큰을 저장하게 되어있습니다

메인화면에서는 Ctrl-R을 통해 새로고침, Ctrl-T로 트윗, Ctrl-D로 나갈 수 있습니다

트윗 보기 화면에셔는 Ctrl-R을 통해 리트윗, Ctrl-G를 통해 (만약 트윗이 답글이라면) 이전 트윗으로 점프, Ctrl-F를 통해 답글을 작성 할 수 있습니다.

트윗 작성 화면에서는 그냥 트윗 작성하고 Ok 하면 됩니다

끝!! 간단합니다

자세한 문의는 트위터 @panzerbruder로 연락주세요
