# Dropbox C2 Connection

Dropboxを用いたPowerAutomate C2との通信の仕様。
ファイルシステムへの書き込み情報を元にUploadはHTTP通信へ変換する。


## Threads

### SetupClientThread

DBのclient一覧を取得し、その内容に合わせて、マウントされたDropbox上にクライアント通信に用いるフォルダ構成を作成する。

フォルダ構成
```
/{client_id}
    key                      # XOR鍵
    payload                  # 取得するペイロードを設置する
                             # Beaconは取得後、ペイロードを削除する
    upload/
        connections.json     # 接続情報をPOSTする
        {task_id}_{idx}.json # Beaconのupload先
```

処理手順:
- DBからdropboxクライアン一覧を取得する
- クライアンとごとに上記フォルダ構成作成する
- クライアントごとに必要ファイルを設置する
    - connectionsが存在しない場合はからファイルを作成
    - XOR Encodeが有効化されている場合はkey情報を設置
        - 毎回鍵を書き換える場合はこのThreadが定期的に
    - initファイルの作成
        - `true`と書き込む（Beaconが次のペイロード作成後に`false`を書き込む）
    - 初期ペイロードの設置

### PutPayloadThread

`/{client_id}/payload`へペイロードを設置する処理を行う。

処理手順:
- `/{client_id}/payload`が存在しない場合
    - DBよりclientに紐付いたタスク一覧を取得する
    - タスクに応じたペイロードを生成する
    - `/{client_id}/payload`を設置する
    - DBのタスクのstateを更新する

### PostDataThread

`/{client_id}/upload/*.json`に書き込まれた内容を読み取り以下の処理を行う。

処理手順:
- `/{client_id}/upload/connections.json`を読み込み、WebAPIへポストする
- `/{client_id}/upload/{task_id}_{idx}.json`を読み込む
    - `@odata.context`に基づきPOST先APIを選択
    - jsonデータを選択したWebAPIへPOSTする
    - Taskのステータスを更新する
    - ファイルを削除する
