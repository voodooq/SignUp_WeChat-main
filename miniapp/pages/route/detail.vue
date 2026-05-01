<template>
  <view class="min-h-screen bg-gray-50 pb-20">
    <!-- 线路图片 -->
    <image :src="route.image_url" mode="aspectFill" class="w-full h-80 bg-gray-200" />

    <!-- 线路基础信息 -->
    <view class="mx-3 -mt-6 relative z-10 bg-white rounded-xl p-4 shadow-md mb-4">
      <view class="flex justify-between items-center mb-2">
        <text class="text-xl font-bold">{{ route.name }}</text>
        <text class="text-sm px-3 py-1 bg-blue-100 text-blue-600 rounded-full font-bold">
          {{ route.difficulty }}
        </text>
      </view>
      <text class="text-sm text-gray-500">{{ route.description || '暂无说明' }}</text>
    </view>

    <!-- 完攀记录列表 -->
    <view class="px-4 mb-4">
      <view class="flex justify-between items-center mb-3">
        <text class="text-lg font-bold text-gray-900">{{ $t('gym.evaluation') }}</text>
        <text class="text-xs text-gray-400">共 {{ attempts.length }} 人完攀</text>
      </view>

      <view v-for="item in attempts" :key="item.id" class="bg-white rounded-xl p-3 mb-3 shadow-sm">
        <view class="flex items-center mb-3">
          <image :src="item.user_avatar || '/static/default-avatar.png'" class="w-8 h-8 rounded-full mr-2 bg-gray-100" />
          <view class="flex-1">
            <text class="text-sm font-medium block">{{ item.user_nickname }}</text>
            <text class="text-xs text-gray-400">{{ formatDate(item.create_time) }}</text>
          </view>
          <view class="flex">
            <text v-for="i in 5" :key="i" class="iconfont icon-star text-xs" :class="i <= item.rating ? 'text-yellow-400' : 'text-gray-200'"></text>
          </view>
        </view>
        <text class="text-sm text-gray-700 mb-3 block" v-if="item.comment">{{ item.comment }}</text>
        <video 
          v-if="item.video_url" 
          :src="item.video_url" 
          class="w-full h-48 rounded-lg" 
          object-fit="contain"
        ></video>
      </view>

      <view v-if="attempts.length === 0" class="py-10 text-center text-gray-400 text-sm">
        还没有人上传过完攀视频，快来做第一个吧！
      </view>
    </view>

    <!-- 底部操作栏 -->
    <view class="fixed bottom-0 left-0 right-0 p-3 bg-white border-t border-gray-100 flex gap-2">
      <button 
        class="flex-1 bg-blue-600 text-white rounded-full py-2 font-bold text-sm flex items-center justify-center"
        @tap="onUpload"
      >
        <text class="iconfont icon-video mr-1"></text>
        上传完攀视频
      </button>
    </view>
  </view>
</template>

<script>
import { getRouteAttempts, submitAttempt } from '@/services/api/gym-api.js';
import { uploadFile } from '@/services/api/request.js';
import dayjs from 'dayjs';

export default {
  data() {
    return {
      route: {},
      attempts: []
    };
  },
  onLoad(options) {
    if (options.data) {
      this.route = JSON.parse(decodeURIComponent(options.data));
      this.loadAttempts();
    }
  },
  methods: {
    async loadAttempts() {
      const res = await getRouteAttempts(this.route.id);
      if (res.code === 200) {
        this.attempts = res.data;
      }
    },
    formatDate(ts) {
      return dayjs(ts).format('YYYY-MM-DD');
    },
    onUpload() {
      uni.chooseVideo({
        sourceType: ['album', 'camera'],
        maxDuration: 60,
        success: async (res) => {
          uni.showLoading({ title: '视频上传中...' });
          try {
            const uploadRes = await uploadFile(res.tempFilePath);
            if (uploadRes.url) {
              await submitAttempt({
                route_id: this.route.id,
                video_url: uploadRes.url,
                rating: 5,
                comment: '完攀打卡！'
              });
              uni.showToast({ title: '提交成功' });
              this.loadAttempts();
            }
          } finally {
            uni.hideLoading();
          }
        }
      });
    }
  }
};
</script>
