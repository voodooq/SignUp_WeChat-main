import { defineStore } from 'pinia';
import { 
  login as apiLogin, 
  checkAdmin as apiCheckAdmin,
  getUserInfo as apiGetUserInfo 
} from '../api/user-api.js';
import { setToken, getToken, clearToken } from '../api/config.js';

export const useUserStore = defineStore('user', {
  state: () => ({
    token: getToken() || '',
    isAdmin: false,
    userInfo: null,
    lang: uni.getStorageSync('lang') || (uni.getSystemInfoSync().language.toLowerCase().startsWith('en') ? 'en' : 'zh')
  }),

  getters: {
    isLoggedIn: (state) => !!state.token
  },

  actions: {
    /**
     * 微信静默登录
     */
    async login() {
      return new Promise((resolve, reject) => {
        uni.login({
          provider: 'weixin',
          success: async (res) => {
            if (res.code) {
              try {
                const loginRes = await apiLogin(res.code);
                if (loginRes.code === 200 && loginRes.data.token) {
                  const token = loginRes.data.token;
                  this.token = token;
                  setToken(token);
                  resolve(loginRes.data);
                } else {
                  reject(loginRes);
                }
              } catch (err) {
                reject(err);
              }
            } else {
              reject(new Error('微信登录失败'));
            }
          },
          fail: (err) => {
            reject(err);
          }
        });
      });
    },

    /**
     * 检查管理员权限
     */
    async checkAdmin() {
      if (!this.isLoggedIn) return false;
      try {
        const res = await apiCheckAdmin();
        if (res.code === 200 && res.data) {
          this.isAdmin = res.data.is_admin;
          return this.isAdmin;
        }
      } catch (e) {
        console.error('管理员校验失败', e);
      }
      return false;
    },

    /**
     * 获取用户信息
     */
    async fetchUserInfo() {
      if (!this.isLoggedIn) return;
      try {
        const res = await apiGetUserInfo();
        if (res.code === 200) {
          this.userInfo = res.data;
        }
      } catch (e) {
        console.log('获取用户信息失败');
      }
    },

    /**
     * 切换语言
     */
    setLanguage(lang) {
      this.lang = lang;
      uni.setStorageSync('lang', lang);
    },

    /**
     * 退出登录
     */
    logout() {
      clearToken();
      this.token = '';
      this.isAdmin = false;
      this.userInfo = null;
    }
  }
});

