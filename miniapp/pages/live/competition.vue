<template>
  <view class="min-h-screen bg-black text-white">
    <!-- 直播视频展示区 (占位) -->
    <view class="relative w-full h-56 bg-gray-900 flex flex-col items-center justify-center border-b border-gray-800">
      <image 
        src="https://images.unsplash.com/photo-1522163182402-834f871fd851?ixlib=rb-1.2.1&auto=format&fit=crop&w=800&q=80" 
        mode="aspectFill" 
        class="absolute inset-0 w-full h-full opacity-40"
      />
      <view class="relative z-10 flex flex-col items-center">
        <text class="iconfont icon-play text-5xl mb-2 text-white opacity-80"></text>
        <text class="text-sm font-bold tracking-widest">LIVE STREAMING</text>
        <view class="mt-2 flex items-center bg-red-600 px-2 py-0.5 rounded text-[10px] animate-pulse">
          <view class="w-1.5 h-1.5 bg-white rounded-full mr-1"></view>
          {{ $t('live.live_tag') }}
        </view>
      </view>
      
      <!-- 赛道切换 (示意) -->
      <view class="absolute bottom-3 left-3 flex gap-2">
        <view class="px-2 py-1 bg-white/20 rounded text-[10px] border border-white/50">TRACK 1</view>
        <view class="px-2 py-1 bg-black/40 rounded text-[10px]">TRACK 2</view>
      </view>
    </view>

    <!-- 实时排行榜标题 -->
    <view class="p-4 flex justify-between items-end">
      <view>
        <text class="block text-2xl font-black italic tracking-tighter">{{ $t('live.leaderboard') }}</text>
        <text class="text-[10px] text-gray-500 uppercase">{{ $t('live.update_tip') }}</text>
      </view>
      <text class="text-xs text-blue-500 font-bold" @tap="loadLeaderboard">{{ $t('live.refresh') }}</text>
    </view>

    <!-- 排名列表 -->
    <view class="px-3 pb-10">
      <view class="bg-gray-900/50 rounded-lg overflow-hidden">
        <!-- 表头 -->
        <view class="flex items-center p-3 text-[10px] text-gray-500 font-bold border-b border-gray-800">
          <text class="w-10">{{ $t('live.ranking') }}</text>
          <text class="flex-1">{{ $t('live.athlete') }}</text>
          <text class="w-20 text-right">{{ $t('live.score_time') }}</text>
        </view>

        <!-- 数据行 -->
        <view 
          v-for="(item, index) in leaderboard" 
          :key="item.ticket_no"
          class="flex items-center p-3 border-b border-gray-800/50 animate-fade-in"
          :class="index < 3 ? 'bg-white/5' : ''"
        >
          <!-- 排名 -->
          <view class="w-10">
            <text v-if="index >= 3" class="text-sm font-bold text-gray-600">{{ index + 1 }}</text>
            <view v-else class="w-6 h-6 flex items-center justify-center rounded bg-yellow-500 text-black font-black text-xs">
              {{ index + 1 }}
            </view>
          </view>
          
          <!-- 选手 -->
          <view class="flex-1 flex flex-col">
            <text class="text-sm font-bold">{{ item.name }}</text>
            <text class="text-[10px] text-gray-500">{{ item.school || 'Independent' }}</text>
          </view>

          <!-- 成绩 -->
          <view class="w-24 text-right flex flex-col">
            <text class="text-sm font-black text-yellow-500">{{ formatScore(item) }}</text>
            <text class="text-[9px] text-gray-600">FINISHED: {{ item.finished_count }}</text>
          </view>
        </view>

        <view v-if="leaderboard.length === 0" class="py-20 text-center">
          <text class="text-gray-600 text-sm italic">{{ $t('live.waiting') }}</text>
        </view>
      </view>
    </view>
  </view>
</template>

<script>
import { getLeaderboard } from '@/services/api/register-api.js';

export default {
  data() {
    return {
      compId: '',
      leaderboard: [],
      timer: null
    };
  },
  onShow() {
    uni.setNavigationBarTitle({
      title: this.$t('live.title')
    });
  },
  onLoad(options) {
    this.compId = options.id || '';
    this.loadLeaderboard();
    // 每 30 秒自动刷新一次
    this.timer = setInterval(() => {
      this.loadLeaderboard();
    }, 30000);
  },
  onUnload() {
    if (this.timer) clearInterval(this.timer);
  },
  methods: {
    async loadLeaderboard() {
      if (!this.compId) return;
      try {
        const res = await getLeaderboard(this.compId);
        if (res.code === 200) {
          this.leaderboard = res.data;
        }
      } catch (e) {
        console.error(e);
      }
    },
    formatScore(item) {
      if (item.best_time_ms && item.best_time_ms < 99999999) {
        const sec = (item.best_time_ms / 1000).toFixed(2);
        return `${sec}s`;
      }
      return `${item.finished_count} TOP`;
    }
  }
};
</script>

<style>
@keyframes fade-in {
  from { opacity: 0; transform: translateY(10rpx); }
  to { opacity: 1; transform: translateY(0); }
}
.animate-fade-in {
  animation: fade-in 0.5s ease-out forwards;
}
</style>
