<template>
	<view class="min-h-screen bg-gray-50">
		<view class="bg-white p-4">
			<text class="text-gray-800 font-bold text-lg block">赛事助手</text>
			<text class="text-gray-500 text-xs block mt-1">为您提供赛事相关信息和帮助</text>
		</view>

		<!-- 快捷入口 -->
		<view class="px-3 mt-3">
			<view class="bg-white rounded-xl overflow-hidden">
				<view class="p-4 flex items-center border-b border-gray-100" @tap="goRegisterQuery">
					<text class="text-base mr-3">📋</text>
					<view class="flex-1">
						<text class="text-gray-800 text-sm font-medium block">报名查询</text>
						<text class="text-gray-400 text-xs mt-1 block">查询您的报名状态和证书信息</text>
					</view>
					<text class="text-gray-400 text-sm">›</text>
				</view>
				<view class="p-4 flex items-center border-b border-gray-100" @tap="goTicket">
					<text class="text-base mr-3">🎫</text>
					<view class="flex-1">
						<text class="text-gray-800 text-sm font-medium block">证书查看</text>
						<text class="text-gray-400 text-xs mt-1 block">查看和保存您的参赛证书</text>
					</view>
					<text class="text-gray-400 text-sm">›</text>
				</view>
			</view>
		</view>

		<!-- 报名流程 -->
		<view class="px-3 mt-3">
			<view class="bg-white rounded-xl p-4">
				<text class="text-gray-800 font-bold text-sm block mb-3">报名流程</text>
				<view class="flex items-start mb-3">
					<view class="w-6 h-6 rounded-full bg-blue-500 flex items-center justify-center mr-3 mt-0">
						<text class="text-white text-xs font-bold">1</text>
					</view>
					<view class="flex-1">
						<text class="text-gray-800 text-sm font-medium block">登录账号</text>
						<text class="text-gray-500 text-xs block mt-1">在"我的"页面点击登录，完成微信授权</text>
					</view>
				</view>
				<view class="flex items-start mb-3">
					<view class="w-6 h-6 rounded-full bg-blue-500 flex items-center justify-center mr-3 mt-0">
						<text class="text-white text-xs font-bold">2</text>
					</view>
					<view class="flex-1">
						<text class="text-gray-800 text-sm font-medium block">填写报名信息</text>
						<text class="text-gray-500 text-xs block mt-1">点击首页"立即报名"，填写姓名、学校、身份证等信息</text>
					</view>
				</view>
				<view class="flex items-start mb-3">
					<view class="w-6 h-6 rounded-full bg-blue-500 flex items-center justify-center mr-3 mt-0">
						<text class="text-white text-xs font-bold">3</text>
					</view>
					<view class="flex-1">
						<text class="text-gray-800 text-sm font-medium block">缴纳报名费</text>
						<text class="text-gray-500 text-xs block mt-1">报名成功后进入缴费页面，完成微信支付</text>
					</view>
				</view>
				<view class="flex items-start">
					<view class="w-6 h-6 rounded-full bg-blue-500 flex items-center justify-center mr-3 mt-0">
						<text class="text-white text-xs font-bold">4</text>
					</view>
					<view class="flex-1">
						<text class="text-gray-800 text-sm font-medium block">获取证书</text>
						<text class="text-gray-500 text-xs block mt-1">缴费完成后即可查看证书，请截图保存</text>
					</view>
				</view>
			</view>
		</view>

		<!-- 报名须知 -->
		<view class="px-3 mt-3">
			<view class="bg-white rounded-xl p-4">
				<text class="text-gray-800 font-bold text-sm block mb-3">报名须知</text>
				<view class="mb-2">
					<text class="text-gray-600 text-xs block">1. 每位选手每个项目只能报名一次，请勿重复报名。</text>
				</view>
				<view class="mb-2">
					<text class="text-gray-600 text-xs block">2. 报名信息请如实填写，身份证号将加密存储保护隐私。</text>
				</view>
				<view class="mb-2">
					<text class="text-gray-600 text-xs block">3. 报名成功后请尽快缴费，未缴费的报名可能会被取消。</text>
				</view>
				<view class="mb-2">
					<text class="text-gray-600 text-xs block">4. 缴费成功后报名费不予退还，请确认后再缴费。</text>
				</view>
				<view class="mb-2">
					<text class="text-gray-600 text-xs block">5. 比赛当天请携带证书或有效身份证件入场。</text>
				</view>
				<view>
					<text class="text-gray-600 text-xs block">6. 如有疑问请联系赛事组委会。</text>
				</view>
			</view>
		</view>

		<!-- 常见问题 -->
		<view class="px-3 mt-3 mb-4">
			<view class="bg-white rounded-xl p-4">
				<text class="text-gray-800 font-bold text-sm block mb-3">常见问题</text>
				<view class="mb-3">
					<text class="text-gray-800 text-xs font-medium block">Q: 报名后可以修改信息吗？</text>
					<text class="text-gray-500 text-xs block mt-1">A: 报名提交后暂不支持自行修改，如需修改请联系管理员。</text>
				</view>
				<view class="mb-3">
					<text class="text-gray-800 text-xs font-medium block">Q: 缴费后可以退款吗？</text>
					<text class="text-gray-500 text-xs block mt-1">A: 缴费成功后报名费不予退还，请确认后再缴费。</text>
				</view>
				<view>
					<text class="text-gray-800 text-xs font-medium block">Q: 证书丢失怎么办？</text>
					<text class="text-gray-500 text-xs block mt-1">A: 可在"我的"页面重新查看和截图保存证书。</text>
				</view>
			</view>
		</view>
	</view>
</template>

<script>
import { useUserStore } from '@/services/store/user.js';

export default {
	methods: {
		goRegisterQuery() {
			const userStore = useUserStore();
			if (!userStore.isLoggedIn) {
				uni.showToast({ title: '请先登录', icon: 'none' });
				return;
			}
			uni.navigateTo({ url: '/pages/register/result' });
		},
		goTicket() {
			const userStore = useUserStore();
			if (!userStore.isLoggedIn) {
				uni.showToast({ title: '请先登录', icon: 'none' });
				return;
			}
			uni.navigateTo({ url: '/pages/ticket/ticket' });
		}
	}
};
</script>

<style>
</style>
