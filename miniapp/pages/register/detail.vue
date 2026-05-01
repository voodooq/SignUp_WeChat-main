<template>
  <view class="min-h-screen bg-gray-50">
    <!-- 顶部轮播图（和首页一样） -->
    <view class="px-3 pt-3">
      <BannerSwiper :banners="topBanners" />
    </view>

    <!-- 赛事信息卡片 -->
    <view class="mx-3 mt-3 bg-white rounded-xl p-4 shadow-sm">
      <text class="block text-gray-900 text-lg font-bold mb-3">
        {{ eventTitle }}
      </text>

      <view class="flex items-start py-2" v-if="eventLocation">
        <text class="iconfont icon-location text-sm mr-2 mt-1"></text>
        <view>
          <text class="text-gray-600 text-sm block">{{ eventLocation }}</text>
        </view>
      </view>

      <view class="flex items-center py-2" v-if="eventDate">
        <text class="iconfont icon-time-circle text-sm mr-2"></text>
        <text class="text-blue-600 text-sm font-medium">
          {{ $t('ticket.time') }} {{ eventDate }}
        </text>
      </view>

      <view class="flex items-center py-2">
        <text class="iconfont icon-tags text-sm mr-2"></text>
        <text class="text-sm" :class="statusClass">{{ statusText }}</text>
      </view>

      <view class="flex items-center py-2" v-if="contactName">
        <text class="iconfont icon-user text-sm mr-2"></text>
        <text class="text-gray-600 text-sm">{{ $t('common.contact') }} {{ contactName }}</text>
        <text v-if="contactPhone" class="text-sm ml-2" @tap="callPhone">
          {{ contactPhone }}
        </text>
      </view>
    </view>

    <!-- 报名倒计时 + 立即报名 -->
    <view class="mx-3 mt-3 bg-white rounded-xl p-4 shadow-sm">
      <view class="flex items-center justify-between">
        <view class="flex-1">
          <view class="flex flex-col items-start">
            <text class="block text-gray-600 text-sm mb-2">{{ $t('index.deadline') }}</text>
            <CountDown
              v-if="registrationDeadline"
              :deadline="registrationDeadline"
              @finished="onDeadlineFinished"
            />
          </view>
        </view>
        <view
          class="ml-4 rounded-full px-6 py-3"
          :class="isDeadlineFinished ? 'bg-gray-300' : 'bg-blue-500'"
          @tap="goRegister"
        >
          <text class="text-white text-sm font-bold">{{ $t('index.register') }}</text>
        </view>
      </view>
    </view>
    <view class="h-6"></view>
  </view>
</template>

<script>
import BannerSwiper from '@/components/BannerSwiper.vue';
import CountDown from '@/components/CountDown.vue';
import { request } from '@/services/api/request.js';

export default {
  components: { BannerSwiper, CountDown },
  data() {
    return {
      topBanners: [],
      registrationDeadline: '',
      isDeadlineFinished: false,
      eventTitle: '',
      eventLocation: '',
      eventDate: '',
      contactName: '',
      contactPhone: '',
    };
  },
  computed: {
    statusText() {
      if (this.isDeadlineFinished) return this.$t('common.ended');
      return this.$t('common.registering');
    },
    statusClass() {
      if (this.isDeadlineFinished) return 'text-red-500 font-medium';
      return 'text-green-600 font-medium';
    },
  },
  onShow() {
    uni.setNavigationBarTitle({
      title: this.$t('index.title')
    });
  },
  onLoad() {
    this.loadBanners();
    this.loadSettings();
  },
  methods: {
    async loadBanners() {
      try {
        const res = await request('/api/register/banners', 'GET', { position: 'top' });
        if (res.code === 200 && res.data) {
          this.topBanners = res.data;
        }
      } catch (e) {
        console.log('加载轮播图跳过');
      }
    },
    async loadSettings() {
      try {
        const res = await request('/api/register/settings');
        if (res.code === 200 && res.data) {
          const settings = res.data;
          this.registrationDeadline = settings.registration_deadline?.value || '';
          this.eventTitle = settings.event_title?.value || '';
          this.eventLocation = settings.event_location?.value || '';
          this.eventDate = settings.event_date?.value || '';
          this.contactName = settings.contact_name?.value || '';
          this.contactPhone = settings.contact_phone?.value || '';
        }
      } catch (e) {
        console.log('加载配置跳过');
      }
    },
    callPhone() {
      if (this.contactPhone) {
        uni.makePhoneCall({ phoneNumber: this.contactPhone });
      }
    },
    goRegister() {
      if (this.isDeadlineFinished) {
        uni.showToast({ title: this.$t('common.ended'), icon: 'none' });
        return;
      }
      uni.navigateTo({ url: '/pages/register/register' });
    },
    onDeadlineFinished() {
      this.isDeadlineFinished = true;
    },
  },
};
</script>

<style></style>
