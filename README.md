# AirCard 🎴

[English README](README.en.md) · 简体中文

> **为 iOS 18 及以上版本更换 Apple 钱包卡面和锁屏密码键盘外观，无需越狱。**
> 基于上游 [Mak5er/AirCard v1.2.4](https://github.com/Mak5er/AirCard/releases/tag/v1.2.4) 的简体中文版本；上游说明称已在 iOS 27 正式版测试。本汉化版尚未完成 iPhone 实机写入验证。底层使用 `airlift` 的 AirTraffic 同步机制漏洞。

本仓库保留了[原版英文说明](README.en.md)，并提供中文界面、中文操作提示、中文设备日志及[配套中文文档](#文档)。这是本地汉化版本，不是上游项目的官方发布包。

<p align="left">
  <a href="https://www.paypal.com/donate/?hosted_button_id=98QRTC2HFRA4Y"><img src="https://img.shields.io/badge/Donate-PayPal-00457C?style=flat-square&logo=paypal" alt="通过 PayPal 支持原作者" /></a>
</p>

---

## 功能

- 🎨 **更换钱包卡面：**为 Apple Pay 和“钱包”中的卡片设置自定义图片、纹理或银行标志。
- 🔢 **更换锁屏密码键盘：**导入 `.passthm` 主题包，修改数字键外观。
- 🧩 **制作密码键盘主题：**用一张海报或壁纸拼接出键盘图案，也可以逐键设置图片。
- 🔍 **直接调整图片位置：**在预览中拖动和缩放，实时查看 iPhone 锁屏效果。
- ✏️ **编辑现有主题：**导入 Cowabunga 或 Nugget 的主题包，修改图片和位置后重新导出或写入。
- ⚡ **单张或批量设置：**每张卡片可使用不同图片，也可让选中的卡片共用一张图片。
- 📱 **识别钱包卡片：**在 iPhone 上打开 Apple Pay 并点选卡片，Mac 端即可尝试识别卡片标识。
- 🚀 **适配两种 Mac 架构：**应用同时包含 Apple 芯片和 Intel（x86_64）版本，设备连接工具随应用打包。

---

## 安装

1. 下载仓库中的 [AirCard 简体中文版安装包](dist/AirCard-v1.2.4-简体中文.dmg)。
2. 打开 DMG，把 `AirCard.app` 拖入 Mac 的“应用程序”文件夹，或复制到你希望保存的位置。
3. 在 Finder 中打开 AirCard。安装包使用时不需要另行安装 Homebrew 或 Python 软件包。

> [!NOTE]
> 这份安装包采用临时签名。如果 macOS 首次打开时提示无法验证开发者，请在 Finder 中按住 Control 点按 `AirCard.app`，选择“打开”，再确认系统提示。安装包的校验值和验证范围见 [dist/README.md](dist/README.md)。

## 更换钱包卡面

1. 用 USB 将 iPhone 连接到 Mac，解锁手机并选择“信任此电脑”。
2. 在 AirCard 的“钱包卡片”页点击“识别卡片”。
3. 在 iPhone 上双击侧边按钮打开 Apple Pay，通过面容 ID 验证，再点选要修改的卡片。如果没有立即出现，可再点选一次。
4. 在 Mac 上点击识别出的卡片选择图片，或直接把图片拖到卡片上。
5. 点击“写入卡面”。完成后，在 iPhone 上强制关闭并重新打开“钱包”；如未更新，可重启手机。

### 没有识别到卡片时

程序读取 iPhone 的统一日志，包括 Info 和 Debug 级别的信息。上游在 iOS 18.6.2 上发现，旧日志服务虽能看到“钱包”活动，却可能缺少包含卡片标识的资源查询记录；新的读取方式及验证情况见[卡片识别验证记录](docs/wallet-card-detection.zh-CN.md)。

先打开“日志”，确认出现 `AirCard 扫描器：已连接设备日志流。`，再在手机上双击侧边按钮、完成验证并点选或切换卡片。如果日志读取停止，请重新连接并解锁 iPhone，再次点击“识别卡片”。iOS 将某些值替换为 `<private>` 时，程序无法从日志中恢复这些值。

如果设备已连接但仍识别不到卡片，请记录 iPhone 型号、iOS 版本、macOS 版本及所用的 AirCard 版本或提交编号，并反馈是否在点选卡片后出现。**不要公开完整设备日志或卡片标识。**

## 更换锁屏密码键盘

1. 在 AirCard 顶部进入“密码键盘主题”页，选择“应用主题包”。
2. 拖入 `.passthm` 文件，或点击“选择 .passthm 文件…”。
3. 检查数字键（0–9、`*`、`#`）预览，再点击“写入密码键盘主题”。
4. 锁定 iPhone 查看效果；如未更新，请重启手机。

> [!TIP]
> 应用可按设备语言和粗体设置选择要写入的素材。选择“所有语言（通用）”会生成更多文件，覆盖不同语言和常规、粗体显示；选择手机当前语言通常更快。素材文件名中的 `--white` 和 `--white-bold` 是 iOS 缓存格式的一部分，不要手动翻译。

## 制作自己的主题

在“密码键盘主题”页切换到“主题制作”，可选择“海报拼图”或“逐键设置”。导入图片后，在预览中调整位置和缩放；完成后可导出 `.passthm` 文件，或直接写入已连接的 iPhone。

---

## 从源码构建

在本仓库根目录运行：

```sh
./build.sh
```

构建脚本使用 macOS 命令行开发工具，生成同时包含 `arm64` 和 `x86_64` 的 `build/AirCard.app`，以及 `build/AirCard-v1.2.4-简体中文.dmg`。译文清单位于 `localization/`。当前源码已经应用汉化，无需在每次构建前再次运行翻译脚本。

## 文档

- [卡片识别验证记录（中文）](docs/wallet-card-detection.zh-CN.md) · [English](docs/wallet-card-detection.md)
- [密码键盘主题制作设计说明（中文）](docs/superpowers/specs/2026-09-17-passcode-theme-creator-design.zh-CN.md) · [English](docs/superpowers/specs/2026-09-17-passcode-theme-creator-design.md)
- [密码键盘主题制作历史实施计划（中文）](docs/superpowers/plans/2026-09-17-passcode-theme-creator.zh-CN.md) · [English](docs/superpowers/plans/2026-09-17-passcode-theme-creator.md)

后两份文档记录的是上游在 2026 年 9 月制定的设计与实施计划，其中的英文界面要求、测试路径和命令属于历史上下文；请以当前源码及本页使用说明为准。

## 贡献者与鸣谢

- [@mak5er](https://github.com/mak5er)：原项目开发者。[GitHub](https://github.com/mak5er) · [X](https://x.com/mak5er)
- [@Lumid-Off](https://github.com/Lumid-Off)：原项目贡献者与开发者。[GitHub](https://github.com/Lumid-Off) · [X](https://x.com/LumidOff)
- [AirLift](https://github.com/0xjohnnydev/airlift) 由 [0xjohnny（@0xjohnnydev）](https://github.com/0xjohnnydev)开发，提供 AirTraffic/ATAirlock 沙盒逃逸的原始概念与验证代码；AirCard 的 `AirliftFFI` 以此为基础。
- 底层机制基于 `airlift` 的 AirTraffic 同步机制漏洞。本汉化版保留原项目的 MIT 许可证及作者署名。

## 支持原作者

如果 AirCard 对你有帮助，可通过以下方式支持原项目开发：

- **PayPal：**[前往捐赠页面](https://www.paypal.com/donate/?hosted_button_id=98QRTC2HFRA4Y)
- **TON：**`UQBm9KPhtMw-XVVjirUoa09wzrlyWsbeZhKfefl1Uw-qNZ-r`
- **USDT（TRC20）：**`TDkDMCyjYxgvkWUnQiF5Erk2RyPQMT6G1n`
- **USDT / BNB（BEP20）：**`0x0954dc491c502849d04956ef74634aa5931a08e8`
