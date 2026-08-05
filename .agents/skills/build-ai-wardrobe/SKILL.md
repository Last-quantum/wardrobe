---
name: build-ai-wardrobe
description: 使用 Marvis 内置视觉理解和图片生成能力，将穿搭照或衣物照片整理为单件服装图、可选的个人上身图、结构化衣橱清单和离线 HTML 衣橱。适用于用户提出“整理衣柜”“从照片提取衣物”“生成数字衣橱”“生成试穿图”或“制作穿搭图库”等需求；全程不得要求用户提供 API Key。
---

# 构建 AI 数字衣橱

把用户提供的衣物照片整理成可浏览、可继续扩展的本地数字衣橱。

## 来源与许可

本 Skill 发布于公开 fork [Last-quantum/wardrobe](https://github.com/Last-quantum/wardrobe)，改编自上游 [tandpfun/wardrobe](https://github.com/tandpfun/wardrobe) 仓库中的 `import-clothes` Skill。上游项目由 Open Wardrobe contributors 按 MIT License 发布；许可证全文见本目录的 [LICENSE](LICENSE)。当前适配新增 Marvis 无用户 Key 约束、独立清单格式和离线 HTML 衣橱生成器，不声称独占上游工作流的作者身份。

## 无 Key 约束

- 只使用 Marvis 已提供的视觉理解、内置 Imagegen/图片生成和本地文件能力。
- 不读取或要求 `OPENAI_API_KEY`，不调用 HTTP 图片接口、SDK、CLI API 或其他需要用户密钥的服务。
- 不因内置图片能力不可用而切换到需要密钥的备用方案；此时保留清单和原图索引，并明确报告未生成的图片。
- 保持源照片不变，不把人物参考照片写入公开案例包或代码仓库。

## 输入

取得以下信息；用户已经提供时不要重复询问：

1. 衣物或穿搭照片所在文件夹。
2. 可选的人物参考照片，用于生成个人上身图。
3. 可选的输出目录和衣橱名称。

若没有人物参考照片，继续完成衣物识别、单品图、清单和离线衣橱，只跳过个人上身图，不阻塞任务。

## 输出目录

默认在当前工作区新建 `AI数字衣橱-YYYYMMDD-HHMMSS/`，不要覆盖已有目录：

```text
AI数字衣橱-YYYYMMDD-HHMMSS/
├── items/              # 单件服装 PNG
├── modeled/            # 可选上身图
├── source-index/       # 源文件索引；不复制私人原图
├── wardrobe.json       # 结构化衣橱数据
└── wardrobe.html       # 可直接打开的离线图库
```

所有临时裁剪、色键图和 QA 文件放在系统临时目录，不能混入最终输出。

## 工作流

### 1. 盘点照片

先用文件搜索枚举 JPEG、PNG、WebP、HEIC/HEIF、TIFF、BMP 和 AVIF，排除输出目录、隐藏缓存和重复副本。检查全部图片，按“同一件实物”去重，而不是按相似款式去重。

记录每件衣物的最佳证据照片、类别、主色、辅色、材质、版型、图案、可确认细节和无法确认的细节。遮挡严重、无法可靠还原的衣物标记为 `hold`，不要编造结构。

### 2. 建立清单

按 [manifest-schema.md](references/manifest-schema.md) 创建工作清单。ID 使用小写连字符格式；类别只使用 `tops`、`outerwear`、`bottoms`、`accessories`、`shoes`。

### 3. 生成单件服装图

按 [image-prompts.md](references/image-prompts.md) 使用内置 Imagegen。每次只处理一件衣物，最多使用两张互补参考图。优先要求直接输出带透明通道的完整服装 PNG，并去除人物、皮肤、头发、衣架、其他衣物、道具、场景和阴影。

若宿主图片能力无法直接生成可靠透明背景，再改用纯色色键：优先使用 `#00ff00`；绿色衣物改用 `#ff00ff`。不要让色键颜色出现在衣物本体。

### 4. 移除色键

仅当第 3 步使用了色键时执行。先完整阅读宿主已安装的 Imagegen/图片处理 Skill 说明，再按其公开入口调用本地抠图或色键移除能力。本 Skill 不复制、不打包宿主内部脚本，也不要猜测未记录的脚本路径。

验证输出是带 alpha 通道的 PNG，四角透明、边缘无明显色溢、衣物没有被裁断。失败时换一个与衣物差异更大的色键重新生成，不要使用需要 API Key 的透明图备用流程。

如果宿主没有可用的透明背景或本地色键移除能力，保留清单和临时色键图，把对应记录标记为 `hold` 并明确报告；不要把色键图当成已完成单品，也不要切换到外部 API。

### 5. 生成可选上身图

仅在用户提供人物参考照片时执行。使用人物参考图作为第一张参考，单件服装 PNG 作为第二张参考，按 [image-prompts.md](references/image-prompts.md) 生成 3:2 横版编辑感照片。

保持人物可识别特征和衣物的颜色、材质、结构、图案、文字、比例及闭合方式；配套服装应低调，不遮挡目标衣物。身份漂移、衣物重设计、肢体异常或遮挡关键细节时重新生成。

### 6. 构建离线衣橱

将通过审核的记录写入 `wardrobe.json`，然后运行：

```text
python scripts/build_gallery.py --manifest OUTPUT/wardrobe.json --output OUTPUT/wardrobe.html
```

该脚本会校验清单、图片路径、类别、颜色和重复 ID，并生成无需服务器、无需联网即可打开的单文件图库页面。

### 7. 最终验收

- 每个 `accepted` 记录恰好对应一张存在的单件图。
- 有人物参考时，每个要求上身图的记录对应一张通过审核的上身图。
- `wardrobe.html` 可直接打开，数量、搜索和分类筛选正常。
- 最终目录不含 API Key、`.env`、人物参考原图、临时裁剪或接口响应。
- 报告成功、跳过和 `hold` 数量，并列出需要补拍的衣物。

## 交付

返回最终输出目录、`wardrobe.json` 和 `wardrobe.html` 的绝对路径。展示不超过 12 张通过审核的单件图；若生成了上身图，再展示不超过 6 张。
