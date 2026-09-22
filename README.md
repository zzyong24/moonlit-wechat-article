![公众号写作：让主张、证据和解释，组成一篇文章](assets/readme/hero.png)

# 月明·公众号写作

把已确认选题、事实和经历组织成一篇能独立读懂的公众号文章，并为需要视觉解释的段落安排配图。

## 你会得到什么

- 围绕核心主张展开的 Markdown 正文
- 事实、因果、边界与语言审读
- 配图需求、素材引用和文章使用清单

## 试着这样说

```text
用 moonlit-wechat-article。根据这些已确认材料写公众号文章。先组织主张和证据，再写正文；需要配图的段落说明图要解释什么。
```

## 安装与首次使用

将本仓库的完整目录交给支持本地 Skill 的 Agent 安装，保留 `SKILL.md` 与随附资源。已有同名版本时先检查差异；使用版本锁的工作区沿用自身升级机制。

让 Agent 安装：

```text
请安装这个 Skill：https://github.com/zzyong24/moonlit-wechat-article
```

也可通过 Skills CLI 安装：

```bash
npx skills add zzyong24/moonlit-wechat-article
```

## 配置与依赖

需要选题、证据和使用方品牌规范。公共编辑要求来自 moonlit-content-engine，成稿使用 moonlit-de-ai-perception；线稿、素材契约与材料图分别配合 moonlit-astronaut-illustration、moonlit-material-illustration。

## 数据与使用边界

正文由当前 Agent 处理，图像输入交给所选生图服务。正文、图片与工程留在作品工作区；微信 HTML 排版和草稿箱写入由 moonlit-wechat-publisher 承接。

## 配套 Skill

[astronaut-illustration](https://github.com/zzyong24/moonlit-astronaut-illustration) · [content-engine](https://github.com/zzyong24/moonlit-content-engine) · [de-ai-perception](https://github.com/zzyong24/moonlit-de-ai-perception) · [material-illustration](https://github.com/zzyong24/moonlit-material-illustration) · [wechat-publisher](https://github.com/zzyong24/moonlit-wechat-publisher)

## 详细说明

执行流程与资源导航见 [SKILL.md](SKILL.md)。安装检查不代表真实业务验收；需要外部服务、账号登录或付费生成的步骤，应在使用者自己的环境中验证。

---

月明水清深 · `moonlit-wechat-article`

首图为 AI 生成的品牌概念插画，不是工具截图或执行结果。
