# アセットディレクトリ

このディレクトリにはゲームで使用する各種アセットファイルを配置します。

## ディレクトリ構造

```
assets/
├── fonts/          # フォントファイル
│   └── umplus_j10r.bdf  # 日本語BDFフォント
├── sprites/        # スプライト画像
│   ├── buildings/  # 建物スプライト
│   ├── terrain/    # 地形スプライト
│   └── ui/         # UIスプライト
└── ui/             # UI要素画像
    ├── icons/      # アイコン
    └── buttons/    # ボタン画像
```

## フォントファイルについて

日本語フォント（umplus_j10r.bdf）は以下からダウンロードできます：
- UMplus フォント: https://github.com/umuplus-font/umuplus-font

または、以下のコマンドでダウンロード：
```bash
# Ubuntu/Debian
sudo apt-get install fonts-umeplus

# または直接ダウンロード
wget https://github.com/umuplus-font/umuplus-font/raw/master/umplus_j10r.bdf
```

## スプライトファイルについて

現在、スプライトはプログラムで動的に生成されています。
実際のPNGファイルを使用する場合は、以下の仕様に従ってください：

- フォーマット: PNG（透過対応）
- 透過色: #FF00FF（マゼンタ）
- 建物スプライト: 64x64ピクセル（等角投影）
- 地形スプライト: 32x32ピクセル
- UIアイコン: 32x32ピクセル

## アセット生成スクリプト

`create_postwar_assets.py`を実行すると、基本的なスプライトを自動生成できます：

```bash
python create_postwar_assets.py
```