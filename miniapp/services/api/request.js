/**
 * 统一 HTTP 请求封装
 * - 自动携带 JWT Token
 * - 统一错误处理
 * - 支持请求/响应拦截
 */
import { getBaseUrl, getToken, clearToken } from './config';
import { TRANSLATIONS } from '../../constants/i18n.js';

const getT = (key) => {
  const lang = uni.getStorageSync('lang') || (uni.getSystemInfoSync().language.toLowerCase().startsWith('en') ? 'en' : 'zh');
  const keys = key.split('.');
  let result = TRANSLATIONS[lang];
  for (const k of keys) {
    if (!result || result[k] === undefined) return key;
    result = result[k];
  }
  return result;
};

/**
 * 通用请求方法
 * @param {string} url 接口路径（不含 baseUrl）
 * @param {string} method 请求方法
 * @param {object} data 请求数据
 * @param {object} options 额外选项
 * @returns {Promise<object>} 响应数据
 */
export function request(url, method = 'GET', data = {}, options = {}) {
  return new Promise((resolve, reject) => {
    const baseUrl = getBaseUrl();
    const token = getToken();
    const lang = uni.getStorageSync('lang') || (uni.getSystemInfoSync().language.toLowerCase().startsWith('en') ? 'en' : 'zh');

    uni.request({
      url: `${baseUrl}${url}`,
      method,
      data,
      header: {
        'Content-Type': 'application/json',
        'x-lang': lang,
        ...(token ? { Authorization: `Bearer ${token}` } : {}),
        ...options.headers,
      },
      timeout: options.timeout || 15000,
      success: (res) => {
        const { statusCode, data: resData } = res;

        if (statusCode >= 200 && statusCode < 300) {
          resolve(resData);
        } else if (statusCode === 401) {
          // Token 过期或无效
          clearToken();
          uni.showToast({ title: getT('message.login_expired'), icon: 'none' });
          reject(resData);
        } else if (statusCode === 403) {
          uni.showToast({ title: resData?.detail || getT('message.no_permission'), icon: 'none' });
          reject(resData);
        } else if (statusCode === 422) {
          // Pydantic 参数校验失败
          const msg = resData?.detail?.[0]?.msg || getT('message.param_error');
          uni.showToast({ title: msg, icon: 'none' });
          reject(resData);
        } else {
          const errorMsg = resData?.message || resData?.detail || getT('message.request_failed');
          if (!options.silent) {
            uni.showToast({ title: errorMsg, icon: 'none' });
          }
          reject(resData);
        }
      },
      fail: (err) => {
        console.error('请求失败:', url, err);
        if (!options.silent) {
          uni.showToast({ title: getT('message.network_error'), icon: 'none' });
        }
        reject(err);
      },
    });
  });
}

/**
 * 文件上传
 * @param {string} filePath 本地文件路径
 * @returns {Promise<object>} 上传结果 { url, filename }
 */
export function uploadFile(filePath) {
  return new Promise((resolve, reject) => {
    const baseUrl = getBaseUrl();
    const token = getToken();

    uni.uploadFile({
      url: `${baseUrl}/api/upload`,
      filePath,
      name: 'file',
      header: {
        ...(token ? { Authorization: `Bearer ${token}` } : {}),
      },
      success: (res) => {
        try {
          const data = JSON.parse(res.data);
          if (data.code === 200) {
            // 将相对路径转为完整 URL
            const fileUrl = data.data.url.startsWith('http')
              ? data.data.url
              : `${baseUrl}${data.data.url}`;
            resolve({ ...data.data, url: fileUrl });
          } else {
            uni.showToast({ title: data.message || getT('message.upload_failed'), icon: 'none' });
            reject(data);
          }
        } catch (e) {
          reject(e);
        }
      },
      fail: (err) => {
        console.error('上传失败:', err);
        uni.showToast({ title: getT('message.upload_failed'), icon: 'none' });
        reject(err);
      },
    });
  });
}

// 快捷方法
export const GET = (url, params, options) => request(url, 'GET', params, options);
export const POST = (url, data, options) => request(url, 'POST', data, options);
export const PUT = (url, data, options) => request(url, 'PUT', data, options);
export const DELETE = (url, data, options) => request(url, 'DELETE', data, options);
