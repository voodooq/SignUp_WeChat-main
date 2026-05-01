<template>
  <view class="min-h-screen bg-white">
    <!-- 顶部 Tab (Level 1) -->
    <view class="flex border-b border-gray-50 sticky top-0 bg-white z-50">
      <view 
        v-for="(tab, idx) in tabs" 
        :key="idx"
        class="flex-1 py-4 text-center relative"
        @tap="activeTab = idx"
      >
        <text :class="activeTab === idx ? 'text-black font-bold' : 'text-gray-400'" class="text-lg">
          {{ tab.name }}
        </text>
        <view v-if="activeTab === idx" class="absolute bottom-1 left-1/2 -translate-x-1/2 w-8 h-1 bg-black rounded-full"></view>
      </view>
    </view>

    <!-- 列表内容 -->
    <scroll-view scroll-y class="h-[calc(100vh-100rpx)]">
      <view class="p-4 space-y-6">
        <view 
          v-for="item in filteredList" 
          :key="item._id"
          class="group"
          @tap="goEventDetail(item)"
        >
          <!-- 海报卡片 -->
          <view class="relative rounded-2xl overflow-hidden aspect-[16/9] shadow-sm mb-3">
            <image :src="item.poster_url || '/static/default-banner.png'" mode="aspectFill" class="w-full h-full" />
            
            <!-- 顶部标签覆盖层 -->
            <view class="absolute top-3 left-3 bg-black/80 px-3 py-1 rounded-md backdrop-blur-sm">
              <text class="text-white text-xs font-medium">{{ formatLocationDate(item) }}</text>
            </view>
            
            <!-- 状态标签 -->
            <view 
              class="absolute top-3 right-3 px-3 py-1 rounded-md shadow-sm"
              :class="getStatusColor(item)"
            >
              <text class="text-xs font-bold">{{ getStatusText(item) }}</text>
            </view>
          </view>

          <!-- 文字信息 -->
          <view class="px-1">
            <text class="block text-xl font-bold text-gray-900 mb-2">{{ item.title }}</text>
            <text class="block text-sm text-gray-400 leading-relaxed line-clamp-2">
              {{ item.description || item.intro || '暂无详细介绍' }}
            </text>
          </view>
        </view>

        <view v-if="loading" class="py-20 text-center text-gray-400">
          <text class="text-sm">加载中...</text>
        </view>
        
        <view v-else-if="filteredList.length === 0" class="py-20 text-center">
          <text class="block text-4xl mb-4">📅</text>
          <text class="text-gray-400 text-sm">暂无相关{{ tabs[activeTab].name }}</text>
        </view>
      </view>
    </scroll-view>
  </view>
</template>

<script>
import { GET } from '@/services/api/request.js';
import dayjs from 'dayjs';

export default {
  data() {
    return {
      activeTab: 0,
      tabs: [
        { name: '赛事信息', type: 'event' },
        { name: '活动报名', type: 'activity' }
      ],
      competitions: [],
      loading: true
    };
  },
  computed: {
    filteredList() {
      const type = this.tabs[this.activeTab].type;
      return this.competitions.filter(item => (item.type || 'event') === type);
    }
  },
  onShow() {
    uni.setNavigationBarTitle({
      title: '赛事'
    });
    this.loadCompetitions();
  },
  methods: {
    async loadCompetitions() {
      this.loading = true;
      try {
        const res = await GET('/api/register/competitions', {}, { silent: true });
        if (res.code === 200) {
          this.competitions = res.data || [];
        }
      } catch (e) {
        console.log('加载失败');
      } finally {
        this.loading = false;
      }
    },
    formatLocationDate(item) {
      // 提取城市名和日期
      const city = item.location.split(' ')[0] || '全国';
      const date = dayjs(item.start_time).format('MM月DD日');
      return `${city}站 | ${date}`;
    },
    getStatusText(item) {
      const now = dayjs();
      if (now.isBefore(dayjs(item.reg_start_time))) return '未开始';
      if (now.isAfter(dayjs(item.reg_end_time))) return '已结束';
      // 检查是否名额已满 (假设有一个 is_full 字段，或者检查 categories)
      if (item.is_full) return '已报满';
      return '报名中';
    },
    getStatusColor(item) {
      const text = this.getStatusText(item);
      if (text === '报名中') return 'bg-yellow-400 text-black';
      if (text === '已结束') return 'bg-black/50 text-white';
      return 'bg-gray-200 text-gray-600';
    },
    goEventDetail(item) {
      uni.navigateTo({ url: `/pages/event/detail?id=${item._id}` });
    }
  }
};
</script>

<style scoped>
.line-clamp-2 {
  display: -webkit-box;
  -webkit-box-orient: vertical;
  -webkit-line-clamp: 2;
  overflow: hidden;
}
</style>

<style scoped>
.space-y-4 > view + view {
  margin-top: 1rem;
}
</style>
