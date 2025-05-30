# discord翻訳bot
ばにたすᓀ‸ᓂ

## お役立ちリンク

[装備覚醒効率(awakening efficiency)](https://docs.google.com/spreadsheets/d/1778ykEIFAdwmHKsvD7eO6IZwJJDqwM1aIkb6-1SG3fs/edit?gid=582548854#gid=582548854)

[幻想Aの装備の利用効率(エゴか村か）(fantA sword usage)](https://github.com/vanitas743/discord_translator/blob/main/casual_player_path.pdf)

[マスタリー効率(mastery)](https://docs.google.com/spreadsheets/d/1tvkYtDlSYwzMNbKAKzib7faO735zEF8lbaB-u7hQWFs/edit?gid=925000323#gid=925000323)

[次元の欠片ギア(dimensional shard gear)](https://docs.google.com/spreadsheets/d/1SSxR3do2473shLlToiq-zJzLkjfY7rl-4jkmwtC7aoE/edit?gid=1538649277#gid=1538649277)

[星座(zodiac)](https://docs.google.com/spreadsheets/d/1Zxched7d37tyqGwqLSZYUcTD3dI6QDPyqiPSQ-h-_00/edit?gid=1366379943#gid=1366379943)

[お知らせ(info ja)](https://announcement.ekgamesserver.com/?ppk=42f47521-f47a-496b-9e90-af01f0f10c37&l=ja)


## 機能
- 全チャンネルの日本語を「translated」チャンネルに翻訳して出力。

- 「english」チャンネル内の英語を「translated」チャンネルに翻訳して出力。

- 新しいクーポンの情報があれば「coupon」チャンネルに送信。

ご自身のサーバーで使うときは上記の名前のチャンネルを作ってください。（大文字小文字、空白に注意）

他に機能を追加したい場合は、main.pyを書き換えるかdiscordのdm等で追加してほしい機能を教えてください。

固有名詞を翻訳されないようにしたい場合は

>def translate_to_english(text):
>
>    placeholder_map = {
>
>        "葬送": "__SOUSOU__",
>
>        "ふわあに": "[[FUWAHNI]]"
>
>    }
>
の部分に"翻訳したくない言葉": "__xXXx__"

のように書くだけでよいのでお好きに追加してください。右はとにかく翻訳されないようなものにすればよいって感じです。今のところの最適解は[[xXXx]]っぽいです。カンマを忘れないようにご注意ください（一敗）。（他の機能もお好きに追加してください！）

書き換えが完了してから１分後くらいにbotに反映されます。




## 動作
Railwayを使っており、月500時間の制限があるため1am ~ 6am(jst)くらいの時間でbotを停止させることがあるかもしれません。

また、翻訳はdeepl apiで行っているので月50万文字までの制限があるようですが到底その制限に引っかかるとは思えないので大丈夫かと思います。月末に動かない等があったら上の方だと思います。
