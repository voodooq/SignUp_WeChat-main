<template>
	<view class="min-h-screen bg-gray-50">
		<!-- 顶部用户区 -->
		<view class="bg-blue-600 pt-8 pb-12 px-4">
			<view class="flex items-center">
				<image class="w-16 h-16 rounded-full bg-white" src="/static/logo.png" mode="aspectFill" />
				<view class="ml-4 flex-1">
					<text class="text-white text-lg font-bold block">{{ $t('my.nickname') }}</text>
					<text class="text-blue-200 text-xs mt-1 block" v-if="isLoggedIn">{{ $t('my.logged_in') }}</text>
					<text class="text-blue-200 text-xs mt-1 block" v-else>{{ $t('my.logging_in') }}</text>
				</view>
			</view>
		</view>

		<!-- 功能列表 -->
		<view class="mx-3 -mt-6 bg-white rounded-xl overflow-hidden">
			<view class="p-4 flex items-center border-b border-gray-100" @tap="goMyRegistrations">
				<text class="text-base mr-2">📋</text>
				<text class="flex-1 text-gray-800 text-sm">{{ $t('my.my_registration') }}</text>
				<text class="text-gray-400 text-sm">›</text>
			</view>
			<view class="p-4 flex items-center border-b border-gray-100" @tap="goMyTicket">
				<text class="text-base mr-2">📜</text>
				<text class="flex-1 text-gray-800 text-sm">{{ $t('my.my_ticket') }}</text>
				<text class="text-gray-400 text-sm">›</text>
			</view>
			<view class="p-4 flex items-center" @tap="goDisclaimer">
				<text class="text-base mr-2">📄</text>
				<text class="flex-1 text-gray-800 text-sm">{{ $t('my.disclaimer') }}</text>
				<text class="text-gray-400 text-sm">›</text>
			</view>
		</view>

		<!-- 管理员入口 -->
		<view v-if="isAdmin" class="mx-3 mt-3 bg-white rounded-xl overflow-hidden">
			<view class="p-4 flex items-center" @tap="goAdmin">
				<text class="text-base mr-2">⚙️</text>
				<text class="flex-1 text-gray-800 text-sm font-medium">{{ $t('index.admin') }}</text>
				<text class="text-gray-400 text-sm">›</text>
			</view>
		</view>

		<!-- 退出登录 -->
		<view v-if="isLoggedIn" class="mx-3 mt-3 bg-white rounded-xl overflow-hidden">
			<view class="p-4 flex items-center justify-center" @tap="handleLogout">
				<text class="text-red-500 text-sm">{{ $t('my.logout') }}</text>
			</view>
		</view>
	</view>
</template>

<script>
import { useUserStore } from '@/services/store/user.js';

export default {
	computed: {
		userStore() {
			return useUserStore();
		},
		isLoggedIn() {
			return this.userStore.isLoggedIn;
		},
		isAdmin() {
			return this.userStore.isAdmin;
		}
	},
	async onShow() {
		uni.setNavigationBarTitle({
			title: this.$t('my.profile')
		});
		const userStore = useUserStore();
		if (!userStore.isLoggedIn) {
			try {
				await userStore.login();
			} catch (e) {
				console.log('Silent login failed:', e);
			}
		} else {
			await userStore.fetchUserInfo();
		}
	},
	methods: {
		handleLogout() {
			uni.showModal({
				title: this.$t('common.info'),
				content: this.$t('my.logout_confirm'),
				success: (res) => {
					if (res.confirm) {
						this.userStore.logout();
						uni.showToast({ title: this.$t('message.success'), icon: 'success' });
					}
				}
			});
		},
		goMyRegistrations() {
			if (!this.isLoggedIn) {
				uni.showToast({ title: this.$t('message.login_expired'), icon: 'none' });
				return;
			}
			uni.navigateTo({ url: '/pages/register/result' });
		},
		goMyTicket() {
			if (!this.isLoggedIn) {
				uni.showToast({ title: this.$t('message.login_expired'), icon: 'none' });
				return;
			}
			uni.navigateTo({ url: '/pages/ticket/ticket' });
		},
		goDisclaimer() {
			uni.navigateTo({ url: '/pages/disclaimer/disclaimer' });
		},
		goAdmin() {
			uni.navigateTo({ url: '/pages/admin/index' });
		}
	}
};
</script>

<style>
</style>
