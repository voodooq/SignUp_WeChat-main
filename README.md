# 赛事报名微信小程序 (私有化部署版)

基于 `UniApp (Vue3) + FastAPI + MongoDB + Docker` 的微信小程序项目，用于体育赛事报名、支付、准考证生成及成绩管理。



## 功能特性

- 参赛须知确认（倒计时 + 勾选同意）后进入报名流程
- 报名表单支持必考/选考规则（选考最多 2 项）
- 微信支付与支付结果回调
- 准考证生成与条形码展示
- 独立的 Web 管理员后台（React）：包含报名查询、扫码查询、项目管理、图片管理、系统配置及数据看板
- 支持赛事图片化展示与多项系统配置

## 技术栈 (迁移后新架构)

- **小程序端**：`UniApp (Vue3)` + `TailwindCSS 3.x`
- **后台管理端**：`React` + `Vite` + `TailwindCSS`
- **后端服务**：`FastAPI` (Python)
- **数据库**：`MongoDB`

## 目录结构（核心）

```text
.
├── miniapp/                # UniApp 小程序原目录
├── frontend/               # React Web 管理端
├── backend/                # Python FastAPI 后端服务
├── docs/                   # 项目说明与部署文档
├── mongo-init/             # MongoDB 初始数据加载脚本
└── docker-compose.yml      # 全局 Docker 容器编排文件
```

## 本地开发与容器部署

由于本项目已拆分为前后端分离以及小程序三个部分，本地进行联调最为方便的做法是使用 Docker compose 打包好后端与管理端（以及数据库），随后在微信开发者平台本地配置小程序的反向链接。

**一键启动与调试：**

```bash
docker-compose up -d --build
```
启动完成之后：
- FastAPI 服务会运行在端口 `:8000` (`http://localhost:8000/docs` 可见 Swagger UI）
- React 后台管理端会运行在端口 `:8080` (通过 nginx 并实现了对应 API 反代)
- 本地调试小程序无需打包进容器，只需使用 HBuilderX （或开发者工具）编译 `miniapp` 并设置请求 Base URL 即可。

如果想查看详细的步骤指导，请务必查看：[docs/部署文档.md](docs/部署文档.md)

## 初始化数据

利用 Docker compose 我们引入了 `mongo-init` 文件夹存放的数据库初始录入。  
只要构建 MongoDB 镜像，表数据即会被自然初始化完毕。
不需要像以往手动在后台界面进行建表并填数据。

## 配置说明

推荐使用后端 **`.env`** 环境变量或分布式配置中心管理敏感信息：

- 微信小程序 `appid` / `secret`
- 支付密钥与回调地址
- 数据库连接字符串 (默认由 Docker 编排自动处理)

详细配置示例见 `docs/项目初始化.md`。

## 安全说明

- 身份证号在后端加密存储（AES）
- 管理员接口在 Service 层做 JWT 鉴权与角色校验
- 支付金额由服务端计算，回调做签名校验
- 不信任前端传入角色、金额、关键身份信息

## 开源文档

完整开源说明见：`docs/开源文档.md`

## 许可证

本项目当前采用 `ISC` 协议（见 `package.json`）。如需更换为 `MIT`/`Apache-2.0`，请同步更新许可证文件与说明文档。

## 联系作者

![微信](docs/img/ea7a2f90d56d53fd2df5bd0bc53c28c0.png)

## 页面效果预览

![首页效果](docs/img/Screenshot_2026-04-21-15-39-54-29_e39d2c7de19156b0683cd93e8735f348.jpg)
![页面截图1](docs/img/Screenshot_2026-04-21-15-39-59-89_e39d2c7de19156b0683cd93e8735f348.jpg)
![页面截图2](docs/img/Screenshot_2026-04-21-15-40-13-76_e39d2c7de19156b0683cd93e8735f348.jpg)
![页面截图3](docs/img/Screenshot_2026-04-21-15-40-41-39_e39d2c7de19156b0683cd93e8735f348.jpg)
![页面截图4](docs/img/Screenshot_2026-04-21-15-41-02-51_e39d2c7de19156b0683cd93e8735f348.jpg)