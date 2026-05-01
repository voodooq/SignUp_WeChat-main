<template>
  <view v-if="!deadline" class="text-center text-gray-400 text-sm">
    {{ $t('common.loading') }}
  </view>
  <view
    class="s-x-2 flex items-center justify-center"
    v-else-if="timeLeft.total > 0"
  >
    <view
      class="bg-gray-800 text-white rounded px-2 py-1 text-center font-bold text-lg"
    >
      {{ timeLeft.days }}
    </view>
    <text class="mx-1 text-gray-600 text-sm">{{ $t('common.days') }}</text>
    <view
      class="bg-gray-800 text-white rounded px-2 py-1 text-center font-bold text-lg"
    >
      {{ padZero(timeLeft.hours) }}
    </view>
    <text class="mx-1 text-gray-600 text-sm">{{ $t('common.hours') }}</text>
    <view
      class="bg-gray-800 text-white rounded px-2 py-1 text-center font-bold text-lg"
    >
      {{ padZero(timeLeft.minutes) }}
    </view>
    <text class="mx-1 text-gray-600 text-sm">{{ $t('common.minutes') }}</text>
    <view
      class="bg-gray-800 text-white rounded px-2 py-1 text-center font-bold text-lg"
      style="min-width: 60rpx;"
    >
      {{ padZero(timeLeft.seconds) }}
    </view>
    <text class="mx-1 text-gray-600 text-sm">{{ $t('common.seconds') }}</text>
  </view>
  <view
    v-else-if="deadline"
    class="text-center text-red-500 font-bold text-base"
  >
    {{ $t('common.ended') }}
  </view>
</template>

<script>
import dayjs from 'dayjs';

export default {
  name: 'CountDown',
  props: {
    deadline: {
      type: [String, Number],
      required: true,
    },
    // 服务器时间偏移量 (serverTime - clientTime)
    offset: {
      type: Number,
      default: 0,
    },
  },
  data() {
    return {
      timer: null,
      timeLeft: {
        total: 0,
        days: 0,
        hours: 0,
        minutes: 0,
        seconds: 0,
      },
    };
  },
  watch: {
    deadline() {
      this.startTimer();
    },
  },
  mounted() {
    this.startTimer();
  },
  beforeUnmount() {
    if (this.timer) {
      clearInterval(this.timer);
      this.timer = null;
    }
  },
  methods: {
    startTimer() {
      if (this.timer) {
        clearInterval(this.timer);
        this.timer = null;
      }
      this.calcTime();
      this.timer = setInterval(() => {
        this.calcTime();
      }, 1000);
    },
    calcTime() {
      if (!this.deadline) return;
      // 基于服务器偏移量校准当前时间
      const now = dayjs(Date.now() + this.offset);
      // 处理 iOS 兼容性：将 - 替换为 /
      let deadlineStr = String(this.deadline);
      if (deadlineStr.includes('-')) {
        deadlineStr = deadlineStr.replace(/-/g, '/');
      }
      const end = dayjs(deadlineStr);
      const diff = end.diff(now);

      if (diff <= 0) {
        this.timeLeft = { total: 0, days: 0, hours: 0, minutes: 0, seconds: 0 };
        if (this.timer) {
          clearInterval(this.timer);
          this.timer = null;
        }
        this.$emit('finished');
        return;
      }

      this.timeLeft = {
        total: diff,
        days: Math.floor(diff / (1000 * 60 * 60 * 24)),
        hours: Math.floor((diff / (1000 * 60 * 60)) % 24),
        minutes: Math.floor((diff / (1000 * 60)) % 60),
        seconds: Math.floor((diff / 1000) % 60),
      };
    },
    padZero(num) {
      return String(num).padStart(2, '0');
    },
  },
};
</script>
