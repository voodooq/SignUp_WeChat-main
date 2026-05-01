# 阶段一：构建管理端 React 产物
FROM node:20-alpine as build-stage

WORKDIR /app

# 安装依赖
COPY package.json package-lock.json* ./
RUN npm install

# 拷贝源代码并构建
COPY . .
# 生产环境中 API 会走同源的 /api 进行代理
ENV VITE_API_URL=/api
RUN npm run build

# 阶段二：配置 Nginx 服务器
FROM nginx:alpine as production-stage

# 清理默认静态文件
RUN rm -rf /usr/share/nginx/html/*

# 复制前端编译产物
COPY --from=build-stage /app/dist /usr/share/nginx/html

# 复制 Nginx 配置文件
COPY nginx.conf /etc/nginx/conf.d/default.conf

EXPOSE 80

CMD ["nginx", "-g", "daemon off;"]
