<template>
  <view class="min-h-screen">
    <!-- 比赛说明图片 -->
    <view class="mx-3 mt-3" v-if="images.length > 0">
      <view v-for="(img, index) in images" :key="index" class="mb-1">
        <image
          class="w-full rounded-xl"
          :src="img"
          mode="widthFix"
          @tap="previewImage(img)"
        />
      </view>
    </view>
    <view class="mx-3 mt-3" v-else>
      <view class="text-center py-8">
        <text class="text-gray-400 text-sm">{{ $t('common.loading') }}</text>
      </view>
    </view>

    <!-- 同意勾选 -->
    <view class="mx-3 mt-4 flex items-center" @tap="agreed = !agreed">
      <view
        class="flex items-center justify-center rounded-full border"
        style="width: 40rpx; height: 40rpx"
        :class="agreed ? 'bg-blue-500 border-blue-500' : 'bg-gray-200 border-gray-300'"
      >
        <text v-if="agreed" class="text-white text-xs">✓</text>
      </view>
      <text class="text-gray-700 text-sm ml-2">{{ $t('confirm.agreed') }}</text>
    </view>

    <!-- 确定按钮（5秒倒计时） -->
    <view class="mx-3 mt-4 mb-6">
      <button
        class="w-full rounded-xl py-3 text-base font-medium"
        :class="canConfirm ? 'bg-blue-500 text-white' : 'bg-gray-300 text-gray-500'"
        :disabled="!canConfirm"
        @tap="handleConfirm"
      >
        {{ btnText }}
      </button>
    </view>

    <!-- 占位符 增加高度 -->
    <view class="h-20"></view>

  </view>
</template>

<script>
export default {
  data() {
    return {
      countdown: 5,
      agreed: false,
      timer: null,
      images: []
    };
  },
  computed: {
    canConfirm() {
      return this.countdown <= 0 && this.agreed;
    },
    btnText() {
      if (this.countdown > 0) {
        return `${this.$t('confirm.wait_prefix')}${this.countdown}${this.$t('confirm.wait_suffix')}`;
      }
      return this.$t('confirm.confirm');
    }
  },
  onShow() {
    uni.setNavigationBarTitle({
      title: this.$t('confirm.title')
    });
  },
  onLoad() {
    this.startCountdown();
    this.loadImages();
  },
  onUnload() {
    if (this.timer) {
      clearInterval(this.timer);
      this.timer = null;
    }
  },
  methods: {
    startCountdown() {
      this.countdown = 5;
      this.timer = setInterval(() => {
        this.countdown--;
        if (this.countdown <= 0) {
          clearInterval(this.timer);
          this.timer = null;
        }
      }, 1000);
    },
    async loadImages() {
      try {
        const { getNoticeImages } = require('@/services/api/register-api.js');
        const result = await getNoticeImages();
        if (result.code === 200 && result.data && result.data.length > 0) {
          // NOTE: 本地后端直接返回可访问URL，不再需要 getTempFileURL
          this.images = result.data
            .map(item => item.image_url)
            .filter(Boolean);
        } else {
          this.images = [];
        }
      } catch (e) {
        console.error('加载参赛须知图片失败:', e);
        this.images = [];
      }
    },
    previewImage(url) {
      uni.previewImage({
        urls: this.images,
        current: url
      });
    },
    handleConfirm() {
      if (!this.canConfirm) return;
      uni.removeStorageSync('register_commitment_signatures');
      uni.redirectTo({
        url: '/pages/register/promise-personal'
      });
    }
  }
};
</script>

<style></style>
