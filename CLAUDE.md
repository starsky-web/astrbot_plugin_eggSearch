# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## 项目概述

这是一个 AstrBot 插件项目 —— "洛克王国世界查蛋器"，用于根据蛋的尺寸和重量匹配精灵种类。

## 插件开发

### 插件结构
- `metadata.yaml` - 插件元数据配置（名称、版本、作者、描述等）
- `main.py` - 插件主代码

### 关键装饰器
- `@register(name, author, desc, version)` - 注册插件类
- `@filter.command("cmd_name")` - 注册指令，用户发送 `/cmd_name` 触发

### 消息处理
- `event.message_str` - 获取用户发送的纯文本消息
- `event.get_messages()` - 获取消息链
- `event.get_sender_name()` - 获取发送者名称
- `yield event.plain_result("text")` - 返回纯文本消息

### 日志
- `from astrbot.api import logger`
- `logger.info()`, `logger.error()` 等

## 参考资源
- [AstrBot 插件开发文档 (中文)](https://docs.astrbot.app/dev/star/plugin-new.html)
- [AstrBot 插件开发文档 (English)](https://docs.astrbot.app/en/dev/star/plugin-new.html)
- [AstrBot 仓库](https://github.com/AstrBotDevs/AstrBot)