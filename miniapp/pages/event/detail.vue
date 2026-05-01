<template>
  <view class="min-h-screen bg-gray-50 pb-24">
    <!-- 顶部沉浸式海报 -->
    <view class="relative w-full h-[60vh]">
      <image :src="event.poster_url || '/static/default-banner.png'" mode="aspectFill" class="w-full h-full" />
      <!-- 渐变阴影 -->
      <view class="absolute inset-0 bg-gradient-to-b from-black/30 via-transparent to-gray-50"></view>
      
      <!-- 自定义导航栏占位 -->
      <view class="absolute top-10 left-4 z-50 flex gap-2">
        <view class="w-8 h-8 rounded-full bg-black/20 backdrop-blur-md flex items-center justify-center text-white border border-white/20" @tap="goBack">
          <text class="iconfont icon-left text-sm"></text>
        </view>
        <view class="w-8 h-8 rounded-full bg-black/20 backdrop-blur-md flex items-center justify-center text-white border border-white/20" @tap="goHome">
          <text class="iconfont icon-home text-sm"></text>
        </view>
      </view>
      
      <view class="absolute top-10 left-1/2 -translate-x-1/2 z-50">
        <text class="text-white font-bold text-lg">赛事详情</text>
      </view>
    </view>

    <!-- 基础信息卡片 -->
    <view class="mx-4 -mt-32 relative z-10 bg-white rounded-3xl p-6 shadow-2xl">
      <view class="flex justify-between items-start mb-4">
        <text class="text-2xl font-black text-gray-900 pr-2 flex-1">{{ event.title }}</text>
        <view class="bg-black text-white px-3 py-1 rounded-md text-[10px] font-bold">{{ event.location_short || '上海站' }}</view>
      </view>
      
      <text class="block text-gray-400 text-sm leading-relaxed mb-8">{{ event.description || event.intro }}</text>
      
      <!-- 详情行 -->
      <view class="space-y-8">
        <view class="flex items-start">
          <text class="w-24 text-gray-900 font-bold text-sm">赛事地址：</text>
          <view class="flex-1 flex justify-between items-start">
            <text class="text-gray-600 text-sm leading-relaxed pr-4">{{ event.location }}</text>
            <view class="flex flex-col items-center flex-shrink-0" v-if="distance">
              <text class="iconfont icon-location text-gray-400 text-lg"></text>
              <text class="text-[10px] text-gray-300 mt-1">{{ distance }}km</text>
            </view>
          </view>
        </view>

        <view class="flex items-start">
          <text class="w-24 text-gray-900 font-bold text-sm">报名时间：</text>
          <text class="text-gray-600 text-sm flex-1">{{ formatDateTime(event.reg_start_time) }} – {{ formatDateTime(event.reg_end_time) }}</text>
        </view>

        <view class="flex items-start">
          <text class="w-24 text-gray-900 font-bold text-sm">赛事时间：</text>
          <text class="text-gray-600 text-sm flex-1">{{ formatDateTime(event.start_time) }} – {{ formatDateTime(event.end_time || event.start_time) }}</text>
        </view>
      </view>
    </view>

    <!-- 详情介绍 (Level 2 Content) -->
    <view class="mt-10 px-4">
      <view class="flex items-center mb-6">
        <view class="w-1 h-5 bg-yellow-400 rounded-full mr-2"></view>
        <text class="text-xl font-black text-gray-900">赛事详情</text>
      </view>
      
      <view class="space-y-4">
        <template v-if="event.detail_images && event.detail_images.length > 0">
          <image 
            v-for="(img, idx) in event.detail_images" 
            :key="idx" 
            :src="img" 
            mode="widthFix" 
            class="w-full rounded-2xl shadow-sm" 
          />
        </template>
        <view v-else class="bg-white p-6 rounded-2xl text-gray-400 text-center italic text-sm">
          暂无图文详情
        </view>
      </view>
    </view>

    <!-- 底部吸底按钮 (Sticky Action) -->
    <view class="fixed bottom-0 left-0 right-0 p-5 bg-white/60 backdrop-blur-xl border-t border-gray-100 flex items-center justify-center safe-bottom z-[100]">
      <button 
        class="w-full bg-yellow-400 active:bg-yellow-500 text-black font-black h-14 rounded-2xl shadow-lg shadow-yellow-100 flex items-center justify-center text-lg transition-transform active:scale-95"
        @tap="goRegister"
      >
        立即报名
      </button>
    </view>
    
    <view class="h-20"></view>
  </view>
</template>

<script>
import { GET } from '@/services/api/request.js';
import dayjs from 'dayjs';

export default {
  data() {
    return {
      compId: '',
      event: {},
      distance: null,
      userLocation: null
    };
  },
  onLoad(options) {
    this.compId = options.id || '';
    this.init();
  },
  methods: {
    async init() {
      // 1. 先获取位置
      uni.getLocation({
        type: 'wgs84',
        success: (res) => {
          this.userLocation = { lng: res.longitude, lat: res.latitude };
          this.loadEvent();
        },
        fail: () => {
          this.loadEvent();
        }
      });
    },
    async loadEvent() {
      if (!this.compId) return;
      uni.showLoading({ title: '加载中' });
      try {
        const params = {};
        if (this.userLocation) {
          params.lng = this.userLocation.lng;
          params.lat = this.userLocation.lat;
        }
        const res = await GET(`/api/register/competition/${this.compId}`, params, { silent: true });
        if (res.code === 200) {
          this.event = res.data;
          // 如果后端没返回距离，前端算一下（演示用）
          if (res.data.distance) {
             this.distance = res.data.distance;
          } else if (this.userLocation && this.event.lng && this.event.lat) {
             this.distance = this.calculateDistance(this.userLocation.lat, this.userLocation.lng, this.event.lat, this.event.lng);
          }
        }
      } finally {
        uni.hideLoading();
      }
    },
    calculateDistance(lat1, lon1, lat2, lon2) {
      const R = 6371; // km
      const dLat = (lat2 - lat1) * Math.PI / 180;
      const dLon = (lon2 - lon1) * Math.PI / 180;
      const a = Math.sin(dLat / 2) * Math.sin(dLat / 2) +
                Math.cos(lat1 * Math.PI / 180) * Math.cos(lat2 * Math.PI / 180) *
                Math.sin(dLon / 2) * Math.sin(dLon / 2);
      const c = 2 * Math.atan2(Math.sqrt(a), Math.sqrt(1 - a));
      return (R * c).toFixed(1);
    },
    formatDateTime(val) {
      if (!val) return '--';
      return dayjs(val).format('YYYY.MM.DD HH:mm');
    },
    goBack() {
      uni.navigateBack();
    },
    goHome() {
      uni.reLaunch({ url: '/pages/index/index' });
    },
    goRegister() {
      const now = dayjs();
      if (now.isBefore(dayjs(this.event.reg_start_time))) {
        uni.showToast({ title: '报名尚未开始', icon: 'none' });
        return;
      }
      if (now.isAfter(dayjs(this.event.reg_end_time))) {
        uni.showToast({ title: '报名已结束', icon: 'none' });
        return;
      }
      uni.navigateTo({ url: `/pages/register/register?compId=${this.compId}` });
    }
  }
};
</script>

<style scoped>
.safe-bottom {
  padding-bottom: calc(20px + constant(safe-area-inset-bottom));
  padding-bottom: calc(20px + env(safe-area-inset-bottom));
}
</style>
