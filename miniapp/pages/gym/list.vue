<template>
  <view class="min-h-screen bg-gray-50">
    <!-- 顶部搜索与定位 -->
    <view class="bg-white px-4 pt-2 pb-1 sticky top-0 z-50">
      <view class="flex items-center gap-3">
        <view class="flex items-center text-sm font-medium text-gray-800" @tap="refreshLocation">
          <text class="iconfont icon-location text-blue-600 mr-1"></text>
          <text>{{ currentCity }}</text>
          <text class="iconfont icon-down text-[10px] ml-1 text-gray-400"></text>
        </view>
        <view class="flex-1 bg-gray-100 rounded-full h-9 flex items-center px-4">
          <text class="iconfont icon-search text-gray-400 text-sm mr-2"></text>
          <input class="text-sm flex-1" placeholder="搜索场馆、教练、赛事" />
        </view>
      </view>
      
      <!-- 排序 Tab -->
      <view class="flex mt-4 border-b border-gray-50">
        <view 
          v-for="tab in sortTabs" 
          :key="tab.key"
          class="mr-8 pb-2 relative"
          @tap="changeSort(tab.key)"
        >
          <text :class="sortBy === tab.key ? 'text-gray-900 font-bold' : 'text-gray-500'" class="text-base">
            {{ tab.name }}
          </text>
          <view v-if="sortBy === tab.key" class="absolute bottom-0 left-0 right-0 h-0.5 bg-gray-900 rounded-full"></view>
        </view>
      </view>
    </view>

    <!-- 场馆列表 -->
    <view class="p-4">
      <view 
        v-for="gym in gyms" 
        :key="gym.id"
        class="bg-white rounded-2xl p-4 mb-4 shadow-sm flex items-start gap-4 active:bg-gray-50 transition-colors"
        @tap="goDetail(gym.id)"
      >
        <image 
          :src="gym.images[0] || '/static/default-gym.png'" 
          mode="aspectFill" 
          class="w-24 h-24 rounded-xl bg-gray-100 flex-shrink-0"
        />
        <view class="flex-1 min-w-0 flex flex-col h-24 justify-between py-1">
          <view>
            <view class="flex justify-between items-start">
              <text class="text-base font-bold text-gray-900 truncate pr-2">{{ gym.name }}</text>
              <text v-if="gym.distance !== null" class="text-xs text-gray-400 flex-shrink-0 mt-1">{{ gym.distance }}km</text>
            </view>
            <view class="flex items-start text-gray-400 text-xs mt-1">
              <text class="iconfont icon-location mr-1 mt-0.5"></text>
              <text class="line-clamp-2 leading-relaxed">{{ gym.address }}</text>
            </view>
          </view>
          
          <view class="flex items-center text-xs text-gray-500">
            <text class="iconfont icon-phone mr-1"></text>
            <text>{{ gym.contact || '客服电话' }}</text>
          </view>
        </view>
      </view>

      <view v-if="loading" class="py-10 text-center">
        <text class="text-gray-400 text-sm">加载中...</text>
      </view>
      
      <view v-if="!loading && gyms.length === 0" class="py-20 flex flex-col items-center">
        <text class="text-4xl mb-4">🏠</text>
        <text class="text-gray-400 text-sm">暂无场馆数据</text>
      </view>
    </view>
  </view>
</template>

<script>
import { getGymList } from '@/services/api/gym-api.js';

export default {
  data() {
    return {
      gyms: [],
      sortBy: 'heat',
      currentCity: '北京市',
      userLocation: null,
      loading: false,
      sortTabs: [
        { name: '默认排序', key: 'heat' },
        { name: '距离最近', key: 'distance' }
      ]
    };
  },
  onShow() {
    uni.setNavigationBarTitle({
      title: '附近的场馆'
    });
  },
  onLoad() {
    this.refreshLocation();
  },
  methods: {
    async refreshLocation() {
      this.loading = true;
      uni.getLocation({
        type: 'wgs84',
        success: (res) => {
          this.userLocation = { lng: res.longitude, lat: res.latitude };
          this.loadGyms();
        },
        fail: (err) => {
          console.warn('定位失败:', err);
          this.loadGyms();
        }
      });
    },
    async loadGyms() {
      this.loading = true;
      try {
        const params = {
          sort_by: this.sortBy
        };
        if (this.userLocation) {
          params.lng = this.userLocation.lng;
          params.lat = this.userLocation.lat;
        }
        const res = await getGymList(params);
        if (res.code === 200) {
          this.gyms = res.data;
        }
      } catch (e) {
        console.error(e);
      } finally {
        this.loading = false;
      }
    },
    changeSort(key) {
      if (this.sortBy === key) return;
      this.sortBy = key;
      this.loadGyms();
    },
    goDetail(id) {
      uni.navigateTo({
        url: `/pages/gym/detail?id=${id}`
      });
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
