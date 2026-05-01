import {
	createPinia,
} from 'pinia';
import piniaPluginPersistedstate from 'pinia-plugin-persistedstate'
import { TRANSLATIONS } from './constants/i18n.js';
import { useUserStore } from './services/store/user.js';
import App from './App';

const getCurrentPageRoute = () => {
	try {
		const pages = getCurrentPages();
		const current = pages[pages.length - 1];
		if (!current) return '/pages/index/index';
		return `/${current.route || 'pages/index/index'}`;
	} catch (e) {
		return '/pages/index/index';
	}
};

const buildSharePayload = () => ({
	title: '赛事报名',
	path: getCurrentPageRoute(),
});

const shareMixin = {
	onLoad() {
		if (typeof uni.showShareMenu === 'function') {
			uni.showShareMenu({
				menus: ['shareAppMessage', 'shareTimeline'],
				fail: (err) => {
					// Silence common AppID permission errors in developer mode
					// console.warn('showShareMenu failed:', err);
				}
			});
		}
	},
	onShareAppMessage() {
		return buildSharePayload();
	},
	onShareTimeline() {
		return {
			title: '赛事报名',
			query: getCurrentPageRoute().replace(/^\//, ''),
		};
	},
};

// #ifdef VUE3
const pinia = createPinia()
import {
	createSSRApp,
} from 'vue'
export function createApp() {
	const app = createSSRApp(App)
	app.use(pinia.use(piniaPluginPersistedstate));
	app.mixin(shareMixin);

    // 全局翻译函数 $t
    app.config.globalProperties.$t = (key) => {
      const lang = uni.getStorageSync('lang') || (uni.getSystemInfoSync().language.toLowerCase().startsWith('en') ? 'en' : 'zh');
      const keys = key.split('.');
      let result = TRANSLATIONS[lang];
      for (const k of keys) {
        if (!result || result[k] === undefined) return key;
        result = result[k];
      }
      return result;
    };

	return {
		app,
        pinia
	}
}
// #endif