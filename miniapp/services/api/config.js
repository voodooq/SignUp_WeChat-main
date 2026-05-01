/**
 * API 基础配置
 * 后台接口地址默认 localhost:8000，可通过设置修改
 */

// NOTE: 默认后端地址，生产环境需修改为实际域名
const DEFAULT_BASE_URL = 'http://localhost:8000';

/**
 * 获取 API 基础地址
 * 优先从本地存储读取用户配置的地址
 */
export function getBaseUrl() {
  try {
    const customUrl = uni.getStorageSync('api_base_url');
    if (customUrl && customUrl.trim()) {
      return customUrl.trim().replace(/\/+$/, '');
    }
  } catch (e) {
    // ignore
  }
  return DEFAULT_BASE_URL;
}

/**
 * 设置 API 基础地址
 * @param {string} url 后端 API 地址
 */
export function setBaseUrl(url) {
  uni.setStorageSync('api_base_url', url.trim().replace(/\/+$/, ''));
}

/**
 * 获取存储的 JWT Token
 */
export function getToken() {
  return uni.getStorageSync('jwt_token') || '';
}

/**
 * 保存 JWT Token
 * @param {string} token JWT Token 字符串
 */
export function setToken(token) {
  uni.setStorageSync('jwt_token', token);
}

/**
 * 清除 JWT Token
 */
export function clearToken() {
  uni.removeStorageSync('jwt_token');
}
