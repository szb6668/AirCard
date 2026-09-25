# 密码键盘主题制作与通用写入历史实施计划

[English](2026-09-17-passcode-theme-creator.md) · 简体中文

> **历史文档，请勿直接照此执行。** 这份计划记录上游在 2026 年 9 月提出的开发步骤。文中的示例文件位于原作者电脑上，安装命令还会替换 `/Applications/AirCard.app`；它们不是当前汉化版的使用或发布流程。原文面向代理开发者，要求使用 `superpowers:subagent-driven-development`（推荐）或 `superpowers:executing-plans` 逐项执行，并用 `- [ ]` 跟踪进度；这里仅保留历史背景，不对当前工作发出指令。

**目标：**让 `.passthm` 主题包能按不同语言生成密码键盘缓存文件，修复 MinePass 等主题缺少部分数字键的问题；同时为 AirCard 增加“海报拼图”和“逐键设置”的内置主题制作功能。

**架构：**Python 后端 `aircard_backend.py` 根据数字键及副文字规则解析主题包，为 iOS 18/17/16 的不同语言生成可匹配的缓存文件。macOS 原生 SwiftUI 编辑器位于 `AirCardApp.swift`，提供交互式 3×4 键盘裁切、逐键图片设置、直接写入和 `.passthm` 导出。

**技术栈：**Python 3、Swift 5.9、SwiftUI、AppKit / CoreGraphics、ZIP 打包、macOS Sequoia / Darwin。

---

### 任务 1：修复 `aircard_backend.py` 的通用密码键盘主题写入

**涉及文件：**

- 修改：`aircard_backend.py`
- 测试：`tests/test_backend_passthm.py`

- [ ] **步骤 1：先编写会失败的测试**

编写 `tests/test_backend_passthm.py`，确认 `parse_passthm_archive` 从 `MinePass_Nightly.passthm` 和 `тцк.passthm` 提取数字键 0–9 时，都能生成所需的 `en-` 和 `other-` 文件。原文曾把函数称为 `extract_passthm_items`；以下示例实际调用 `parse_passthm_archive`。

```python
import sys
from pathlib import Path

# Add project root to sys.path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from aircard_backend import parse_passthm_archive, KEYPAD_SUBTEXTS

def test_minepass_nightly_extraction():
    minepass_path = "/Users/mak5er/Downloads/MinePass_Nightly.passthm"
    items = parse_passthm_archive(minepass_path, "TelephonyUI-10")

    # Verify all digits 0 through 9 are present
    digits_found = set()
    leaves = [item[1] for item in items]

    for d in range(10):
        digit_str = str(d)
        has_en = any(f"en-{digit_str}-" in l for l in leaves)
        has_other = any(f"other-{digit_str}-" in l for l in leaves)
        assert has_en, f"Missing en- variant for digit {digit_str}"
        assert has_other, f"Missing other- variant for digit {digit_str}"
        digits_found.add(digit_str)

    assert len(digits_found) == 10
    print("✓ MinePass_Nightly parsed all 10 digits successfully")

if __name__ == "__main__":
    test_minepass_nightly_extraction()
```

- [ ] **步骤 2：运行测试，确认修改前失败**

原计划命令：

```bash
python3 tests/test_backend_passthm.py
```

预期：失败，可能为 `ImportError` 或 `AssertionError`。此脚本依赖原作者本地的主题文件；在其他电脑上缺少文件时，失败不能用于判断功能是否正确。

- [ ] **步骤 3：实现通用主题文件提取**

在 `aircard_backend.py` 中定义 `KEYPAD_SUBTEXTS` 和 `parse_passthm_archive(passthm_path, telephony_ver)`：

- 使用正则表达式 `r'(?:^[a-zA-Z]+-)?([0-9*#])(?:-([^-
]+))?'` 提取数字键。
- 缺少副文字时，使用标准副文字表补齐。
- 为每个按键生成下列文件名：
  - `en-{digit}-{subtext}--white.png`
  - `en-{digit}---white.png`
  - `other-{digit}-{subtext}--white.png`
  - `other-{digit}---white.png`
- 让 `cmd_flash_passthm` 和 `cmd_inspect_passthm` 共用 `parse_passthm_archive`。

- [ ] **步骤 4：再次运行测试，确认通过**

原计划仍使用：

```bash
python3 tests/test_backend_passthm.py
```

预期：通过，并输出“MinePass_Nightly 的 10 个数字键均已解析成功”一类结果。实际仍需提供对应的测试主题文件。

- [ ] **步骤 5：提交改动**

原计划提交命令如下，仅作历史记录：

```bash
git add aircard_backend.py tests/test_backend_passthm.py
git commit -m "fix(backend): universal passcode theme parsing for all locales and archives"
```

---

### 任务 2：用 Swift 实现键盘图片裁切与主题导出

**涉及文件：**修改 `AirCardApp.swift`。

- [ ] **步骤 1：实现 `KeypadSlicer` 和 `PasscodeThemeExporter`**

原计划新增的接口包括：

- `KeypadSlicer.slicePoster(image: NSImage, zoom: Double, offset: CGPoint) -> [String: NSImage]`：为数字 `0`–`9` 生成 10 张 300×300 像素的圆形裁切图，圆形外部保持透明，布局比例对应 iOS 的 3×4 键盘。
- `PasscodeThemeExporter.exportTheme(keys: [String: NSImage], targetURL: URL) throws`：生成 `TelephonyUI-10/` 目录、完整的 `en-` 和 `other-` 文件名组合及 `TelephonyUI-10/_big` 标记，再压缩成 `.passthm`。
- `PasscodeThemeExporter.stageTemporaryTheme(keys: [String: NSImage]) -> URL?`：为直接写入准备临时 `.passthm` 包。

- [ ] **步骤 2：检查裁切与导出代码能否编译**

原计划命令：

```bash
swiftc -parse AirCardApp.swift
```

预期：无语法错误。此命令只检查语法，不等于完整类型检查或应用构建成功。

- [ ] **步骤 3：提交改动**

```bash
git add AirCardApp.swift
git commit -m "feat(keypad): add KeypadSlicer and PasscodeThemeExporter engine"
```

---

### 任务 3：在 `AirCardApp.swift` 中构建密码键盘主题制作界面

**涉及文件：**修改 `AirCardApp.swift`。原计划要求界面全部使用英语；当前汉化版改用简体中文。

- [ ] **步骤 1：为 `AppViewModel` 添加状态和操作**

- `passcodeTabMode: PasscodeTabMode = .applyTheme`
- `creatorSubMode: CreatorSubMode = .posterSlice`
- `creatorPosterImage: NSImage?`
- `creatorPosterZoom: Double = 1.0`
- `creatorPosterOffset: CGPoint = .zero`
- `creatorCustomKeys: [String: NSImage] = [:]`
- 对应方法：`sliceCurrentPoster()`、`setIndividualKeyImage(digit: String, image: NSImage)`、`clearCreator()`、`flashCreatedTheme()`、`exportCreatedTheme(to: URL)`。

- [ ] **步骤 2：实现主题制作界面组件**

在 `AirCardApp.swift` 中：

- 顶部分段选择器：原文为 `[Apply .passthm] | [Theme Creator]`，汉化版为“应用主题包 / 主题制作”。
- `themeCreatorView` 中的模式选择：原文为 `[Poster Slice] | [Individual Keys]`，汉化版为“海报拼图 / 逐键设置”。
- 海报拼图模式：图片拖入区、选择图片按钮、0.5×–3.0× 缩放滑块、重置位置按钮，以及展示裁切效果的交互式 3×4 键盘预览。
- 逐键设置模式：每个圆形按键可单独点击选择图片，也可接收拖放图片。
- 底部操作：清空、导出 `.passthm`、写入 iPhone。

- [ ] **步骤 3：编译并检查界面结构**

原计划命令：

```bash
./build.sh
```

当前汉化版的预期产物是 `build/AirCard.app` 和 `build/AirCard-v1.2.4-简体中文.dmg`；原计划记录的 `build/AirCard.dmg` 属于旧构建脚本。

- [ ] **步骤 4：提交改动**

```bash
git add AirCardApp.swift
git commit -m "feat(ui): implement interactive Passcode Theme Creator in English"
```

---

### 任务 4：端到端测试与验证

**原计划所需的真实设备和文件：**

- `/Users/mak5er/Downloads/MinePass_Nightly.passthm`
- `/Users/mak5er/Downloads/AyuGram Desktop/тцк.passthm`
- AirCard 主题制作功能新生成的主题

- [ ] **步骤 1：通过后端写入 `MinePass_Nightly.passthm`**

原计划命令仅为示例，其中设备标识和文件路径必须替换为测试者自己的值：

```bash
python3 aircard_backend.py flash-passthm 00008120-001A1D0A1EE9A01E "/Users/mak5er/Downloads/MinePass_Nightly.passthm" TelephonyUI-10
```

预期：10 个数字键均写入成功，数字键 2–9 不再漏写。这是计划中的验收标准，不代表汉化版已完成该实机测试。

- [ ] **步骤 2：部署更新后的应用**

原计划使用以下命令直接替换 `/Applications/AirCard.app`：

```bash
rm -rf /Applications/AirCard.app && cp -R build/AirCard.app /Applications/AirCard.app && xattr -cr /Applications/AirCard.app
```

该命令会删除现有应用，**不要直接运行**。当前汉化版采用并排安装，原版应用保留。原计划的预期验收是：应用能打开两个页面，并能在“应用主题包”和“主题制作”之间切换。

- [ ] **步骤 3：最终提交与清理**

```bash
git add .
git commit -m "chore: finalize Passcode Theme Creator and verified build v1.2"
```
