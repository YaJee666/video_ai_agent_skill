# Video AI Agent Skill

English version: [README_EN.md](README_EN.md)

给 Codex、Claude Code 和其他 coding agent 一键装上在线视频理解能力。

Video AI Agent Skill 是一个轻量级 folder-based skill。它不在本地下载、破解或清洗视频站点内容，而是把完整的视频理解请求发送到 Video AI Agent OpenAPI，由线上服务完成视频解析、字幕/转写、清洗、总结和问答。

## 宣传点

- **在线视频智能体能力**：把 B站、YouTube、抖音、TikTok 等视频链接直接交给 Codex / Claude Code，总结、提炼观点、问答、对比都走统一入口。
- **本地零重依赖**：不需要本地 GPU，不需要本地 Whisper，不需要 ffmpeg，不需要维护 yt-dlp、cookies、站点解析器和字幕清洗脚本。
- **对 agent 友好**：skill 只有 `SKILL.md`、一个无第三方依赖的 Python 客户端和少量说明文档，Codex / Claude Code 可以直接读懂怎么调用。
- **在线解析更稳**：复杂的视频下载、转写和清洗由线上服务处理，本地 agent 不直接和视频平台对抗。
- **模型成本更低**：不需要让本地 agent 再用昂贵的 GPT / Opus 模型清洗长字幕，Video AI Agent pipeline 直接返回可用的总结、问答和结构化分析。
- **注册送 10 美金免费额度**：新用户创建 workspace 后可先用免费额度测试视频总结、问答和内容清洗，再决定是否继续使用。

## 支持的平台

当前 README 只列稳定支持的平台。具体可解析范围以线上 API 实际返回为准。

| 平台 | 支持内容 | 示例 |
| --- | --- | --- |
| Bilibili / B站 | BV 号、B站视频链接、常见短链解析 | `https://www.bilibili.com/video/BV...` |
| YouTube | 普通视频、短链、Shorts | `https://www.youtube.com/watch?v=...` |
| Douyin / 抖音 | 抖音视频链接 | `https://www.douyin.com/video/...` |
| TikTok | TikTok 视频链接 | `https://www.tiktok.com/@user/video/...` |
| 直接媒体 URL | 可直接访问的视频、音频或媒体文件 | `https://example.com/video.mp4` |

可能失败的情况包括：私有视频、删除视频、登录墙内容、地区限制内容、平台反爬限制、无字幕且线上服务无法下载或转写的内容。

## 快速上手

### 1. 一句话安装

复制这句话给你的 Codex、Claude Code 或其他 coding agent：

```text
帮我安装 Video AI Agent Skill：https://raw.githubusercontent.com/YaJee666/video_ai_agent_skill/main/docs/install.md
```

Agent 会按安装指南 clone 仓库，并运行无依赖安装脚本，把 `video-ai-agent` skill 安装到 Codex / Claude Code / `.agents` 等常见 skill 目录。

想先预览、不改文件：

```text
帮我安装 Video AI Agent Skill（先预览，不要改文件）：https://raw.githubusercontent.com/YaJee666/video_ai_agent_skill/main/docs/install.md
安装时使用 --dry-run 参数
```

已经安装过，后续更新也可以复制这句话给 agent：

```text
帮我更新 Video AI Agent Skill：https://raw.githubusercontent.com/YaJee666/video_ai_agent_skill/main/docs/update.md
```

### 2. 获取 API key

打开 Video AI Agent 控制台，在 `API Key` 页面创建 workspace API key：

https://www.talkaibot.com/console?tab=keys

```text
chat:write
```

API key 创建后只显示一次，请保存在本地安全位置，不要提交到 Git 仓库。

新用户默认获得 **10 美金免费额度**，可用于首次测试视频解析、总结和问答能力。额度消耗以控制台账单/用量记录为准。

### 3. 自动安装命令

如果你已经 clone 了本仓库，可以直接运行：

```powershell
python .\scripts\install_skill.py --target auto
```

`--target auto` 会安装到已存在的常见 skill 根目录；如果没有发现现有目录，默认创建 Codex 目录：

```text
%USERPROFILE%\.codex\skills\video-ai-agent
```

可选目标：

```powershell
python .\scripts\install_skill.py --target codex
python .\scripts\install_skill.py --target claude
python .\scripts\install_skill.py --target all
python .\scripts\install_skill.py --target auto --dry-run
python .\scripts\install_skill.py --target auto --update
```

### 4. 配置 `.env`

推荐在安装后的 skill 目录创建 `.env` 文件，这样不用每次打开新终端都重新配置环境变量。

Codex 默认位置：

```powershell
Copy-Item "$env:USERPROFILE\.codex\skills\video-ai-agent\.env.example" "$env:USERPROFILE\.codex\skills\video-ai-agent\.env"
notepad "$env:USERPROFILE\.codex\skills\video-ai-agent\.env"
```

`.env` 内容示例：

```text
VIDEO_AI_AGENT_API_KEY=vag_sk_live_xxx
VIDEO_AI_AGENT_ENDPOINT=https://www.talkaibot.com/openapi/v1/chat/completions
VIDEO_AI_AGENT_MODE=jobs
VIDEO_AI_AGENT_TIMEOUT_MS=600000
VIDEO_AI_AGENT_PROJECT_ID=
VIDEO_AI_AGENT_SESSION_ID=
```

脚本会自动读取当前目录、skill 目录或仓库根目录下的 `.env`。优先级是：命令行参数 > 系统环境变量 > `.env` 文件 > 默认值。
默认 `jobs` 模式会调用 `/openapi/v1/jobs` 并轮询结果，适合视频解析、总结、转写清洗和问答；短对话才使用 `--mode sync`。

无需发送请求即可检查配置来源：

```powershell
python .\video-ai-agent\scripts\video_ai_agent_chat.py --debug-config
```

临时使用也可以继续设置环境变量：

```powershell
$env:VIDEO_AI_AGENT_API_KEY = "vag_sk_live_xxx"
```

### 5. 验证调用

从仓库根目录运行：

```powershell
python .\video-ai-agent\scripts\video_ai_agent_chat.py --message "请用中文总结这个视频，并列出 5 个关键观点：https://www.bilibili.com/video/BV..."
```

也可以让 Codex / Claude Code 直接使用 skill：

```text
Use $video-ai-agent to summarize this video in Chinese: https://www.youtube.com/watch?v=...
```

安装后请启动新的 Codex / Claude Code 会话，让 agent 重新发现 skill。

## 在线解析的优点

### 无需代理

本地 agent 不需要直接访问复杂视频站点。视频解析请求发给 Video AI Agent OpenAPI，具体平台访问、下载、字幕获取和转写由线上服务处理。

### 无需 GPU

本地机器不需要跑 Whisper、VLM 或多模态模型。你只需要能运行 Python 标准库脚本并访问 OpenAPI。

### 更快的网速

在线视频解析经常卡在下载、地区网络、字幕接口和转写耗时。线上服务可以使用更适合视频解析的运行环境，避免本地网络慢、下载中断和重复配置。

### 无需昂贵模型做清洗

很多 agent 工作流会先下载字幕，再用 GPT / Opus 清洗、去噪、分段、总结。这个 skill 直接请求 Video AI Agent，让后端 pipeline 输出清洗后的总结、问答和结构化结果。

### 更轻的 agent 工作流

Codex / Claude Code 不需要理解每个平台的解析细节，只需要把完整用户意图和视频 URL 放进 `messageContent`。后端负责识别平台并选择合适的解析链路。

## 常见问题

### 这和 yt-dlp / 本地 Whisper 有什么区别？

yt-dlp 和 Whisper 是本地工具链，需要你维护依赖、处理平台失败、下载媒体、转写和清洗。Video AI Agent Skill 是 OpenAPI 客户端，把这些工作交给线上服务，本地 agent 只负责发起请求和展示结果。

### 这和 Agent-Reach 有什么区别？

Agent-Reach 是互联网能力路由器，帮助 agent 安装和选择各种上游工具。Video AI Agent Skill 专注视频理解，把视频解析、清洗、总结和问答封装成一个在线服务调用。

### 是否需要 API key？

需要。开放接口使用 workspace API key 认证，最小 scope 是 `chat:write`。推荐把 `VIDEO_AI_AGENT_API_KEY` 写到安装后 skill 目录的 `.env`，脚本会自动读取。

### 有免费额度吗？

有。新用户创建 workspace 后默认获得 10 美金免费额度，可用于测试视频解析、总结、问答和内容清洗。免费额度不是无限免费，实际消耗和剩余额度以控制台显示为准。

### 是否需要代理？

通常不需要本地代理，因为本地 agent 不直接解析视频站点。但你的机器仍然需要能访问 Video AI Agent OpenAPI endpoint。

### 是否需要 GPU？

不需要。视频转写、多模态理解和总结由线上服务处理。

### 为什么某些视频解析失败？

常见原因包括视频私有、已删除、地区限制、登录墙、平台临时风控、视频没有字幕且无法下载转写。遇到失败时，把错误信息和原始 URL 一起反馈给维护者更容易定位。

### 支持连续对话吗？

支持。设置 `VIDEO_AI_AGENT_SESSION_ID` 或调用脚本时传 `--session-id`，后续请求可以复用同一会话上下文。

### 请求超时怎么办？

长视频可能需要更久。可以调大超时：

```powershell
python .\video-ai-agent\scripts\video_ai_agent_chat.py --timeout-ms 900000 --message "..."
```

### 如何更新 skill？

复制这句话给你的 agent：

```text
帮我更新 Video AI Agent Skill：https://raw.githubusercontent.com/YaJee666/video_ai_agent_skill/main/docs/update.md
```

更新脚本需要在仓库 checkout 里运行，先 `git pull --ff-only`，再重新同步 `video-ai-agent` skill 目录；它会保留已安装目录里的 `.env`，所以 API key 不需要重新配置。

### 可以把 API key 写进命令吗？

可以用 `--api-key`，但不推荐。更安全的方式是放到安装后 skill 目录的 `.env`、当前 shell 环境变量或你的本地 secrets 管理工具里，避免进入 shell history 或 Git。仓库里的 `.gitignore` 会忽略 `.env` 文件。

## 本地音频上传、转写与撰写

Skill 现在支持把本地 `mp3`、`m4a`、`wav`、`flac`、`aac`、`ogg`、`wma`
音频上传到 Video AI Agent。服务端返回 `resourceId` 后，客户端会自动把该资源附加到聊天请求，
由后端按用户指定的时间范围使用 FFmpeg 裁剪，再通过 Whisper 转写。

转写指定片段：

```powershell
python .\video-ai-agent\scripts\video_ai_agent_chat.py `
  --audio-file "C:\media\lesson.m4a" `
  --message "转写这个音频 2:20 到 2:40 的内容，输出整理后的口语稿"
```

基于音频撰写文章：

```powershell
python .\video-ai-agent\scripts\video_ai_agent_chat.py `
  --audio-file "C:\media\interview.mp3" `
  --write-from-audio
```

也可以在 `--message` 中提出更具体的撰写要求，例如课程讲义、会议纪要、博客文章、
内容提纲或问答总结。已有资源可以使用 `--resource-id 123` 复用。

音频附件当前自动使用同步聊天接口；默认 jobs 模式仍用于在线视频长任务。
API key 需要 `chat:write` scope。

## License

MIT
