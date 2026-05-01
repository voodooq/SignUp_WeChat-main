<template>
  <view class="min-h-screen bg-gray-50 pb-10" v-if="gym">
    <!-- 顶部图片轮播 -->
    <swiper class="w-full h-64" indicator-dots autoplay circular>
      <swiper-item v-for="(img, index) in gym.images" :key="index">
        <image :src="img" mode="aspectFill" class="w-full h-full" />
      </swiper-item>
      <swiper-item v-if="!gym.images || gym.images.length === 0">
        <view class="w-full h-full bg-gray-200 flex items-center justify-center">
          <text class="text-gray-400">{{ $t('common.no_image') }}</text>
        </view>
      </swiper-item>
    </swiper>

    <!-- 场馆信息 -->
    <view class="mx-3 -mt-10 relative z-10 bg-white rounded-2xl p-5 shadow-lg mb-4">
      <view class="flex justify-between items-start mb-2">
        <text class="text-2xl font-bold text-gray-900">{{ gym.name }}</text>
      </view>
      <view class="flex items-start text-gray-500 text-sm mb-4">
        <text class="iconfont icon-location mr-1 mt-1"></text>
        <text>{{ gym.address }}</text>
      </view>
      <view class="border-t border-gray-100 pt-4">
        <text class="text-sm font-bold text-gray-800 block mb-2">{{ $t('gym.intro') }}</text>
        <text class="text-sm text-gray-600 leading-relaxed">{{ gym.intro || $t('gym.no_intro') }}</text>
      </view>
    </view>

    <!-- 线路展示 -->
    <view class="px-4 mb-4">
      <text class="text-lg font-bold text-gray-900 block mb-3">{{ $t('gym.routes') }}</text>
      
      <view class="grid grid-cols-2 gap-3">
        <view 
          v-for="route in gym.routes" 
          :key="route.id"
          class="bg-white rounded-xl overflow-hidden shadow-sm"
          @tap="goRouteDetail(route)"
        >
          <image :src="route.image_url" mode="aspectFill" class="w-full h-40 bg-gray-100" />
          <view class="p-2">
            <view class="flex justify-between items-center">
              <text class="text-sm font-bold truncate">{{ route.name }}</text>
              <text class="text-xs px-2 py-0.5 bg-blue-100 text-blue-600 rounded-full">
                {{ route.difficulty }}
              </text>
            </view>
          </view>
        </view>
      </view>

      <view v-if="!gym.routes || gym.routes.length === 0" class="py-10 text-center">
        <text class="text-gray-400 text-sm">{{ $t('gym.no_routes') }}</text>
      </view>
    </view>
  </view>
</template>

<script>
import { getGymDetail } from '@/services/api/gym-api.js';

export default {
  data() {
    return {
      gym: null
    };
  },
  onLoad(options) {
    if (options.id) {
      this.loadDetail(options.id);
    }
  },
  methods: {
    async loadDetail(id) {
      uni.showLoading({ title: this.$t('common.loading') });
      try {
        const res = await getGymDetail(id);
        if (res.code === 200) {
          this.gym = res.data;
          uni.setNavigationBarTitle({ title: this.gym.name });
        }
      } finally {
        uni.hideLoading();
      }
    },
    goRouteDetail(route) {
      uni.navigateTo({
        url: `/pages/route/detail?data=${encodeURIComponent(JSON.stringify(route))}`
      });
    }
  }
};
</script>

<style scoped>
.grid {
  display: flex;
  flex-wrap: wrap;
  margin: 0 -6rpx;
}
.grid-cols-2 > view {
  width: calc(50% - 12rpx);
  margin: 6rpx;
}
</style>
