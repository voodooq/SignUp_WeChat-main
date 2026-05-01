<template>
	<swiper
		v-if="banners.length > 0"
		class="w-full rounded-lg overflow-hidden"
		:style="{ height: swiperHeight }"
		:indicator-dots="banners.length > 1"
		indicator-color="rgba(255,255,255,0.5)"
		indicator-active-color="#ffffff"
		:autoplay="true"
		:interval="4000"
		:circular="true"
	>
		<swiper-item v-for="(item, index) in banners" :key="index">
			<image
				class="w-full h-full"
				:src="item.image_temp_url || item.image_url"
				mode="aspectFill"
				@load="onImageLoad"
			/>
		</swiper-item>
	</swiper>
	<view v-if="banners.length === 0" class="w-full bg-gray-200 rounded-lg flex items-center justify-center" :style="{ height: swiperHeight }">
		<text class="text-gray-400 text-sm">{{ $t('common.no_image') }}</text>
	</view>
</template>

<script>
export default {
	name: 'BannerSwiper',
	props: {
		banners: {
			type: Array,
			default: () => []
		},
		height: {
			type: String,
			default: '360rpx'
		}
	},
	computed: {
		swiperHeight() {
			return this.height;
		}
	},
	methods: {
		onImageLoad() {}
	}
};
</script>
