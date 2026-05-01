/**
 * 用户相关 API
 */
import { POST, GET } from './request';

/**
 * 微信登录
 * @param {string} code wx.login() 获取的 code
 */
export function login(code) {
  return POST('/api/user/login', { code });
}

/**
 * 获取用户信息
 */
export function getUserInfo() {
  return GET('/api/user/info');
}

/**
 * 检查管理员身份
 */
export function checkAdmin() {
  return GET('/api/user/check-admin');
}
