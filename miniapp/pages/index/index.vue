<template>
  <view class="min-h-screen bg-gray-50">
    <!-- 顶部轮播图 -->
    <view class="px-3 pt-3">
      <BannerSwiper :banners="topBanners" />
    </view>

    <!-- 顶部导航/扫码 -->
    <view class="mx-3 mt-3 flex justify-between items-center">
      <text class="text-xl font-black italic">CLIMB ON</text>
      <view 
        class="bg-white p-2 rounded-full shadow-sm flex items-center justify-center"
        @tap="onScan"
      >
        <text class="iconfont icon-scan text-blue-600 text-lg"></text>
      </view>
    </view>

    <!-- 搜索框 (Level 1) -->
    <view class="mx-3 mt-3">
      <view class="bg-white rounded-full px-4 py-2 flex items-center shadow-sm border border-gray-100" @tap="goGymList">
        <text class="iconfont icon-search text-gray-300 mr-2"></text>
        <text class="text-gray-400 text-sm">搜索岩馆、赛事、内容...</text>
      </view>
    </view>

    <!-- 报名倒计时 (保留核心赛事) -->
    <view class="mx-3 mt-3 bg-white rounded-xl p-4 shadow-sm" v-if="registrationDeadline">
      <text class="block text-center text-gray-600 text-xs mb-2">
        {{ $t('index.deadline') }}
      </text>
      <CountDown
        v-if="registrationDeadline"
        :deadline="registrationDeadline"
        :offset="serverOffset"
        @finished="onDeadlineFinished"
      />
    </view>

    <!-- 语言切换 (Level 1) -->
    <view class="mx-3 mt-3 flex justify-end">
      <view class="bg-white px-3 py-1 rounded-full shadow-sm" @tap="toggleLang">
        <text class="text-[10px] text-blue-600 font-bold">
          {{ lang === 'zh' ? 'ENGLISH' : '中文' }}
        </text>
      </view>
    </view>

    <!-- 核心功能金刚区 (Level 1) -->
    <view class="mx-3 mt-3 flex justify-between gap-2">
      <view class="flex-1 bg-white rounded-2xl px-1 py-4 flex flex-col items-center shadow-sm" @tap="goRegister">
        <view class="w-10 h-10 bg-yellow-400 rounded-xl flex items-center justify-center mb-2">
          <text class="iconfont icon-edit text-white text-xl"></text>
        </view>
        <text class="text-[11px] font-bold text-gray-800 whitespace-nowrap">{{ $t('index.register') }}</text>
      </view>
      <view class="flex-1 bg-white rounded-2xl px-1 py-4 flex flex-col items-center shadow-sm" @tap="goGymList">
        <view class="w-10 h-10 bg-blue-500 rounded-xl flex items-center justify-center mb-2">
          <text class="iconfont icon-location text-white text-xl"></text>
        </view>
        <text class="text-[11px] font-bold text-gray-800 whitespace-nowrap">岩馆搜索</text>
      </view>
      <view class="flex-1 bg-white rounded-2xl px-1 py-4 flex flex-col items-center shadow-sm" @tap="goScore">
        <view class="w-10 h-10 bg-green-500 rounded-xl flex items-center justify-center mb-2">
          <text class="iconfont icon-trophy text-white text-xl"></text>
        </view>
        <text class="text-[11px] font-bold text-gray-800 whitespace-nowrap">成绩/排名</text>
      </view>
      <view class="flex-1 bg-white rounded-2xl px-1 py-4 flex flex-col items-center shadow-sm" @tap="goQuery">
        <view class="w-10 h-10 bg-gray-800 rounded-xl flex items-center justify-center mb-2">
          <text class="iconfont icon-user text-white text-xl"></text>
        </view>
        <text class="text-[11px] font-bold text-gray-800 whitespace-nowrap">我的报名</text>
      </view>
    </view>

    <!-- 正在举办赛事 (Level 2 List) -->
    <view class="mx-3 mt-6">
      <view class="flex justify-between items-end mb-3">
        <text class="text-lg font-black italic">ACTIVE EVENTS</text>
        <text class="text-xs text-blue-600 font-bold" @tap="goAllEvents">查看全部</text>
      </view>
      <scroll-view scroll-x class="whitespace-nowrap w-full" :show-scrollbar="false">
        <view 
          v-for="item in competitions" 
          :key="item._id"
          class="inline-block w-64 mr-3 bg-white rounded-2xl overflow-hidden shadow-sm border border-gray-50"
          @tap="goEventDetail(item)"
        >
          <image :src="item.poster_url || '/static/default-banner.png'" mode="aspectFill" class="w-full h-32" />
          <view class="p-3">
            <text class="block font-bold text-sm truncate mb-1">{{ item.title }}</text>
            <view class="flex items-center justify-between">
              <text class="text-[10px] text-gray-400">{{ item.location }}</text>
              <text class="text-[10px] px-2 py-0.5 bg-red-50 text-red-500 rounded" v-if="item.status === 'active'">LIVE</text>
            </view>
          </view>
        </view>
        <view v-if="competitions.length === 0" class="inline-block w-full text-center py-10 text-gray-300 text-xs italic">
          暂无进行的赛事
        </view>
      </scroll-view>
    </view>

    <!-- 功能按钮第二排：管理员入口（仅管理员可见） -->
    <view v-if="isAdmin" class="mx-3 mt-3 flex">
      <view
        class="flex-1 bg-white rounded-xl p-4 flex flex-col items-center"
        @tap="goAdmin"
      >
        <view
          class="flex items-center justify-center mb-2"
          style="width: 72rpx; height: 72rpx"
        >
          <text
            class="iconfont icon-setting"
            style="font-size: 56rpx; color: #111827"
          ></text>
        </view>
        <text class="text-sm font-medium text-gray-800">{{ $t('index.admin') }}</text>
      </view>
    </view>

    <!-- 赛事信息（图片展示） -->
    <view
      class="mx-3 mt-3 bg-white rounded-xl p-4"
      v-if="eventImages.length > 0"
    >
      <text
        class="block text-center text-gray-800 font-bold text-base mb-3 border-b border-gray-100 pb-3"
      >
        {{ $t('common.info') }}
      </text>
      <view>
        <image
          v-for="(img, index) in eventImages"
          :key="img._id"
          class="w-full rounded-lg"
          :class="index < eventImages.length - 1 ? 'mb-2' : ''"
          :src="img.image_url"
          mode="widthFix"
          @tap="previewEventImage(index)"
        />
      </view>
    </view>

    <!-- 底部轮播图 -->
    <view class="px-3 py-3" v-if="bottomBanners.length > 0">
      <BannerSwiper :banners="bottomBanners" height="400rpx" />
    </view>

    <!-- 底部安全区 -->
    <view class="h-4"></view>
  </view>
</template>

<script>
import BannerSwiper from '@/components/BannerSwiper.vue';
import CountDown from '@/components/CountDown.vue';
import { useUserStore } from '@/services/store/user.js';
import { getSettings } from '@/services/api/register-api.js';
import { GET } from '@/services/api/request.js';

export default {
  components: { BannerSwiper, CountDown },
  data() {
    return {
      topBanners: [],
      bottomBanners: [],
      registrationDeadline: '',
      eventImages: [],
      competitions: [],
      isDeadlineFinished: false,
      isAdmin: false,
      serverOffset: 0,
      lang: 'zh'
    };
  },
  onShow() {
    const userStore = useUserStore();
    this.lang = userStore.lang;
    uni.setNavigationBarTitle({
      title: this.$t('index.title')
    });
  },
  onLoad() {
    this.silentLogin();
    this.loadBanners();
    this.loadSettings();
    this.loadEventImages();
    this.loadCompetitions();
  },
  methods: {
    toggleLang() {
      const userStore = useUserStore();
      const newLang = this.lang === 'zh' ? 'en' : 'zh';
      userStore.setLanguage(newLang);
      this.lang = newLang;
      uni.setNavigationBarTitle({
        title: this.$t('index.title')
      });
      // 刷新数据（部分需要后端翻译的数据）
      this.loadBanners();
      this.loadEventImages();
      this.loadCompetitions();
    },
    async silentLogin() {
      const userStore = useUserStore();
      try {
        await userStore.login();
      } catch (e) {
        console.log('Silent login failed:', e);
      }
      if (userStore.isLoggedIn) {
        this.isAdmin = await userStore.checkAdmin();
      }
    },
    async loadCompetitions() {
      try {
        const res = await GET('/api/register/competitions', {}, { silent: true });
        if (res.code === 200) {
          this.competitions = res.data || [];
        }
      } catch (e) {
        console.log('加载赛事列表失败');
      }
    },
    async loadBanners() {
      try {
        const topRes = await GET('/api/register/banners?position=top', {}, { silent: true });
        if (topRes.code === 200) {
          this.topBanners = (topRes.data || []).map((b) => ({
            ...b,
            image_temp_url: b.image_url,
          }));
        }
        const bottomRes = await GET('/api/register/banners?position=bottom', {}, { silent: true });
        if (bottomRes.code === 200) {
          this.bottomBanners = (bottomRes.data || []).map((b) => ({
            ...b,
            image_temp_url: b.image_url,
          }));
        }
      } catch (e) {
        console.log('加载轮播图失败');
      }
    },
    async loadSettings() {
      try {
        const result = await getSettings();
        if (result.code === 200 && result.data) {
          this.registrationDeadline = result.data.registration_deadline || '';
          if (result.server_time) {
            this.serverOffset = result.server_time - Date.now();
          }
        }
      } catch (e) {
        console.log('加载配置失败');
      }
    },
    async loadEventImages() {
      try {
        const result = await GET('/api/register/event-images', {}, { silent: true });
        if (result.code === 200) {
          this.eventImages = (result.data || []).map((img) => ({
            ...img,
            image_temp_url: img.image_url,
          }));
        }
      } catch (e) {
        console.log('加载赛事信息图片失败');
      }
    },
    previewEventImage(index) {
      const urls = this.eventImages.map((img) => img.image_url);
      uni.previewImage({ urls, current: urls[index] });
    },
    async goRegister() {
      if (this.isDeadlineFinished) {
        uni.showToast({ title: this.$t('message.deadline_reached'), icon: 'none' });
        return;
      }
      uni.navigateTo({ url: '/pages/register/confirm' });
    },
    goQuery() {
      uni.navigateTo({ url: '/pages/register/result?mode=list' });
    },
    goScore() {
      uni.navigateTo({ url: '/pages/score/score' });
    },
    goGymList() {
      uni.navigateTo({ url: '/pages/gym/list' });
    },
    goEventDetail(item) {
      uni.navigateTo({ url: `/pages/event/detail?id=${item._id}` });
    },
    goAllEvents() {
      // 如果有专门的全部赛事页面，跳到那里，否则默认展示首页列表
      uni.showToast({ title: '已展示全部正在进行的赛事', icon: 'none' });
    },
    goLive() {
      uni.navigateTo({ url: '/pages/live/competition?id=latest' });
    },
    goAdmin() {
      uni.navigateTo({ url: '/pages/admin/index' });
    },
    onScan() {
      uni.scanCode({
        success: (res) => {
          const result = res.result;
          uni.navigateTo({
            url: `/pages/route/detail?id=${result}`
          });
        }
      });
    },
    onDeadlineFinished() {
      this.isDeadlineFinished = true;
    },
  },
};
</script>

<style></style>
