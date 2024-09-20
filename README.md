# blender egg exporter
write egg file for Panda3d

Blenderのモデルから、Panda3Dで使うためのeggファイルを作成します。
現時点では完全に自分用です。しかし、他ユーザーの参考になるかもしれないので、公開しておきます。

## 現時点の注意点
出力パスを手書きで指定します。

エクスポートしたいモデルを全て選択し、Armatureをアクティブ選択状態にしてください。

名前にcontrolが入っているboneは出力されません。
シェイプキーの名前に空白や特殊文字を含めないでください。

flat shade には対応していません。
シェイプキーのアニメーションのエクスポートは対応していません。

## 参考文献 - Reference
PRPEE
[https://github.com/kergalym/PRPEE](https://github.com/kergalym/PRPEE)

omUlette
[https://discourse.panda3d.org/t/blender-egg-exporter-plugin-omulette/29275](https://discourse.panda3d.org/t/blender-egg-exporter-plugin-omulette/29275)

Microsoft Copilot
