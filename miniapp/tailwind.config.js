/** @type {import('tailwindcss').Config} */
module.exports = {
	content: ['./pages/**/*.{vue,js}', 'App.vue', './components/**/*.{vue,js}'],
	theme: {
		extend: {},
	},
	// 微信小程序 WXSS 不支持伪类选择器中的反斜杠转义，禁用这些变体
	corePlugins: {
		preflight: false,
	},
	variants: {
		extend: {},
	},
	plugins: [],
	// 仅保留小程序兼容的变体
	safelist: [],
	blocklist: [],
}