# AirCard 密码键盘主题制作与通用写入设计说明

[English](2026-09-17-passcode-theme-creator-design.md) · 简体中文

> 历史设计文档。以下内容记录上游当时的方案与目标，并非当前版本功能或兼容性的验证结论。原方案要求英文界面；本仓库已另行制作简体中文界面。代码示例中的标识和文件名保持原样。

## 1. 概述

本文说明以下功能的架构、数据模型、界面组件和实现思路：

1. **通用密码键盘主题写入（`aircard_backend.py`）：**解决旧主题及多语言主题的兼容问题。例如 `MinePass_Nightly.passthm` 使用 `ru-` 文件名前缀，且按键副文字的配置并不统一。设计目标是让设备语言或源文件结构的差异不再导致漏写。
2. **内置主题制作（`AirCardApp.swift`）：**在“密码键盘主题”页提供可视化编辑器，包含两种模式：
   - **海报拼图：**把一张壁纸或图片铺到符合 iOS 锁屏密码键盘布局的 3×4 按键上。
   - **逐键设置：**通过拖放或文件选择器，分别设置数字 0–9 的图片。
3. **输出方式：**通过 `airlift` 直接写入已连接的 iOS 设备，或导出标准 `.passthm` ZIP 主题包。
4. **原方案的语言要求：**macOS 应用界面文案和标签全部使用英语。这是历史要求；当前汉化版已改为简体中文。

---

## 2. 通用写入修复（`aircard_backend.py`）

### 2.1 漏写的原因

- `MinePass_Nightly.passthm` 一类主题可能包含 `ru-2-A B C--white.png`，而不是 `en-2-A B C--white.png`。
- 数字键 0 和 1 没有字母副文字，例如 `ru-0---white.png`、`ru-1---white.png`，所以简单替换文件名前缀时，这两个键可能恰好有效。
- 数字键 2–9 需要副文字。按系统语言不同，iOS 会查找 `en-{digit}-{letters}--white.png` 或 `other-{digit}-{letters}--white.png`；缺少对应文件便会漏写。

### 2.2 标准副文字表

```python
KEYPAD_SUBTEXTS = {
    "0": "+",
    "1": "",
    "2": "A B C",
    "3": "D E F",
    "4": "G H I",
    "5": "J K L",
    "6": "M N O",
    "7": "P Q R S",
    "8": "T U V",
    "9": "W X Y Z",
}
```

### 2.3 提取与生成规则

对主题包中每张有效按键图片，设目标数字键为 `D`（0–9），副文字为 `LETTERS`：

1. 保留主题包中的原始文件名。
2. 如 `LETTERS` 非空，生成带字母的英语文件名：`en-{D}-{LETTERS}--white.png`。
3. 生成不带字母的英语文件名：`en-{D}---white.png`。
4. 如 `LETTERS` 非空，生成带字母的其他语言文件名：`other-{D}-{LETTERS}--white.png`。
5. 生成不带字母的其他语言文件名：`other-{D}---white.png`。
6. 如果原文件没有副文字，或副文字并非标准内容，还要根据 `KEYPAD_SUBTEXTS[D]` 生成 `en-{D}-{KEYPAD_SUBTEXTS[D]}--white.png` 和 `other-{D}-{KEYPAD_SUBTEXTS[D]}--white.png`。

目标目录为 `/var/mobile/Library/Caches/{telephony_ver}`。原方案举例：`TelephonyUI-10` 用于 iOS 18 及以上版本，`TelephonyUI-9` 用于 iOS 15–17；具体目标应以当前程序和设备识别结果为准。

---

## 3. 密码键盘主题制作架构

### 3.1 数据模型

原设计在 `AirCardApp.swift` 中使用以下模型；代码片段保留当时的英文显示值：

```swift
enum PasscodeTabMode: String, CaseIterable, Identifiable {
    case applyTheme = "Apply .passthm"
    case themeCreator = "Theme Creator"
    var id: String { rawValue }
}

enum CreatorSubMode: String, CaseIterable, Identifiable {
    case posterSlice = "Poster Slice"
    case individualKeys = "Individual Keys"
    var id: String { rawValue }
}

struct KeypadButtonGeometry {
    let digit: String
    let letters: String
    let row: Int
    let col: Int
}
```

### 3.2 键盘布局常量

- 网格为 3 列、4 行。
- 按键位置：
  - 第 0 行：`1` 在第 0 列、`2` 在第 1 列、`3` 在第 2 列。
  - 第 1 行：`4`、`5`、`6` 分别在第 0、1、2 列。
  - 第 2 行：`7`、`8`、`9` 分别在第 0、1、2 列。
  - 第 3 行：`0` 在第 1 列。
- 原方案希望比例和间距接近 iOS 锁屏密码键盘：
  - 按键直径：75 pt。
  - 水平间距：24 pt。
  - 垂直间距：18 pt。
  - 网格总宽度：`(3 × 75) + (2 × 24) = 273 pt`。
  - 网格总高度：`(4 × 75) + (3 × 18) = 354 pt`。

### 3.3 海报拼图引擎

- 用户导入一张 `NSImage`。
- 裁切计算：
  - 将图片缩放到适合或填满键盘边界。
  - 计算 10 个按键各自的归一化中心 `(cx, cy)` 和半径 `r`。
  - 以高分辨率渲染圆形遮罩。原方案以 `@3x` Super Retina 显示为例，采用 300×300 像素。
  - 为数字 `0` 至 `9` 分别生成一张圆形 `NSImage`。
- 用户可拖入图片，使用 0.5×–2.5× 缩放滑块，以及 X/Y 偏移或直接拖动来调整位置。交互预览显示图片在 10 个圆形按键中的裁切效果。

### 3.4 逐键设置

- 使用 3×4 网格表示密码键盘。
- 每个按键都可独立接收拖入的图片，也可点击选择文件。
- 用户可以只修改部分数字键，也可以清除单个数字键的自定义图片。
- 未设置图片的按键回退为透明背景或标准数字字形。

### 3.5 直接写入与导出

1. **写入 iPhone：**把当前 10 张按键图片编排为临时 PNG 文件，放在内存或临时 `.passthm` 目录中；调用 `aircard_backend.py` 的 `cmd_flash_passthm`；按步骤更新进度条。
2. **导出 `.passthm`：**打开 `NSSavePanel`。原方案中的英文标题为“Save Passcode Theme”；汉化版使用中文。标准 ZIP 包包含 `TelephonyUI-10/` 目录及其 `en-`、`other-` 文件，并带 `_big` 或 `_small` 标记，保存时使用 `.passthm` 扩展名。

---

## 4. 界面设计与布局（原方案为英语）

### 4.1 密码键盘页顶部

分段选择器原文为 `[Apply .passthm] | [Theme Creator]`；汉化版分别显示为“应用主题包”和“主题制作”。

### 4.2 主题制作界面

- 顶部控制栏：模式选择为“海报拼图”或“逐键设置”；操作包括重置或清空、导出 `.passthm`、写入 iPhone。
- 内容区：
  - **海报拼图模式：**一侧是图片导入区及选择图片、缩放、适合或填满等控制，另一侧是按真实布局展示的交互式锁屏键盘预览。
  - **逐键设置模式：**3×4 的圆形按键网格。点击按键可选择图片，把图片拖到按键上则直接设置该键。
- 底部状态栏：沿用现有进度条和操作日志，显示写入进度。

---

## 5. 原定测试与验证计划

1. **主题兼容性：**用 `MinePass_Nightly.passthm` 验证数字 0–9 均生成 `en-` 和 `other-` 变体，并能写入 `TelephonyUI-10`；再用 `тцк.passthm` 验证旧主题仍可使用。
2. **海报裁切：**分别导入 16:9 和 19.5:9 的壁纸，检查是否为所有 10 个按键生成 300×300 像素的圆形 PNG，且圆形外部透明。
3. **逐键设置：**为数字键 1、2、0 指定不同图片，写入设备并导出 `.passthm`；检查 ZIP 目录结构是否符合 iOS 缓存格式。
