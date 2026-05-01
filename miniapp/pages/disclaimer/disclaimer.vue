<template>
	<view class="min-h-screen bg-gray-50 p-4">
		<view class="bg-white rounded-xl p-6">
			<text class="block text-gray-800 font-bold text-lg mb-4">{{ $t('my.disclaimer') }}</text>
			<view class="text-gray-600 text-sm leading-relaxed">
				<text class="block mb-3">{{ $t('my.disclaimer_t1') }}</text>
				<text class="block mb-3">{{ $t('my.disclaimer_t2') }}</text>
				<text class="block mb-3">{{ $t('my.disclaimer_t3') }}</text>
				<text class="block mb-3">{{ $t('my.disclaimer_t4') }}</text>
				<text class="block mb-3">{{ $t('my.disclaimer_t5') }}</text>
				<text class="block mb-3">{{ $t('my.disclaimer_t6') }}</text>
			</view>
		</view>
	</view>
</template>

<script>
export default {
	onShow() {
		uni.setNavigationBarTitle({
			title: this.$t('my.disclaimer')
		});
	}
};
</script>

<style>
</style>
