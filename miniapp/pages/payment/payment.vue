<template>
  <view class="min-h-screen bg-gray-50">
    <!-- 报名信息 -->
    <view class="mx-3 mt-3 bg-white rounded-xl p-4 shadow-sm">
      <text class="block text-gray-800 font-bold text-base mb-3">{{ $t('payment.info') }}</text>
      <view class="flex py-2">
        <text class="text-gray-500 text-sm" style="width: 180rpx">{{ $t('register.name') }}</text>
        <text class="flex-1 text-gray-800 text-sm">{{ regInfo.name }}</text>
      </view>
      <view class="flex py-2">
        <text class="text-gray-500 text-sm" style="width: 180rpx">{{ $t('ticket.events') }}</text>
        <text class="flex-1 text-gray-800 text-sm">{{ regInfo.event_name }}</text>
      </view>
      <view class="flex py-2">
        <text class="text-gray-500 text-sm" style="width: 180rpx">{{ $t('result.ticket_no') }}</text>
        <text class="flex-1 text-gray-800 text-sm">{{ regInfo.ticket_no }}</text>
      </view>
    </view>

    <!-- 缴费金额 -->
    <view class="mx-3 mt-3 bg-white rounded-xl p-4 text-center shadow-sm">
      <text class="block text-gray-500 text-sm mb-2">{{ $t('payment.amount') }}</text>
      <text class="block text-gray-900 text-3xl font-bold">
        ¥{{ displayFee }}
      </text>
    </view>

    <!-- 缴费状态 -->
    <view v-if="paymentStatus === 'paid' || paymentStatus === 'admin_free'" class="mx-3 mt-3 bg-gray-100 rounded-xl p-4 text-center">
      <text class="text-gray-900 text-base font-bold block">✓ {{ $t('result.paid') }}</text>
      <text v-if="paymentTime" class="text-gray-500 text-sm block mt-1">
        {{ $t('payment.pay_time') }}：{{ formatTime(paymentTime) }}
      </text>
    </view>

    <!-- 操作按钮 -->
    <view class="mx-3 mt-4">
      <button
        v-if="paymentStatus === 'unpaid'"
        class="w-full bg-blue-500 text-white rounded-xl py-3 text-base font-medium"
        :class="paying ? 'opacity-50' : ''"
        :disabled="paying"
        @tap="handlePay"
      >
        {{ paying ? $t('payment.paying') : $t('payment.pay_now') }}
      </button>

      <button
        v-if="paymentStatus === 'paid' || paymentStatus === 'admin_free'"
        class="w-full bg-blue-500 text-white rounded-xl py-3 text-base font-medium"
        @tap="goTicket"
      >
        {{ $t('payment.view_ticket') }}
      </button>

      <button
        v-if="paymentStatus === 'paid' || paymentStatus === 'admin_free'"
        class="w-full bg-white text-gray-600 rounded-xl py-3 text-base border border-gray-200 mt-3"
        @tap="goHome"
      >
        {{ $t('result.back_home') }}
      </button>

      <button
        v-if="paymentStatus === 'unpaid'"
        class="w-full bg-white text-gray-600 rounded-xl py-3 text-base border border-gray-200 mt-3"
        @tap="goHome"
      >
        {{ $t('payment.pay_later') }}
      </button>
    </view>

    <view class="h-6"></view>
  </view>
</template>

<script>
import { useUserStore } from '@/services/store/user.js';
import { getMyRegistrations } from '@/services/api/register-api.js';
import { createOrder, mockPay, queryOrder, getSubscribeConfig } from '@/services/api/payment-api.js';
import dayjs from 'dayjs';

export default {
  data() {
    return {
      registrationId: '',
      subscribeTemplateId: '',
      regInfo: {
        name: '',
        event_name: '',
        ticket_no: '',
        fee: 0,
      },
      paymentStatus: 'unpaid',
      paymentTime: null,
      paymentOrderNo: '',
      paying: false,
      pollTimer: null,
    };
  },
  computed: {
    displayFee() {
      const fee = this.regInfo.fee || 0;
      return (fee / 100).toFixed(2);
    },
  },
  onShow() {
    uni.setNavigationBarTitle({
      title: this.$t('payment.title')
    });
  },
  onLoad(options) {
    this.registrationId = options.registration_id || '';
    if (options.data) {
      try {
        const data = JSON.parse(decodeURIComponent(options.data));
        this.regInfo = {
          name: data.name || '',
          event_name: data.event_name || '',
          ticket_no: data.ticket_no || '',
          fee: data.fee || 0,
        };
        this.paymentStatus = data.payment_status || 'unpaid';
        this.registrationId = data._id || this.registrationId;
      } catch (e) {
        console.error('解析缴费数据失败:', e);
      }
    }
    if (this.registrationId) {
      this.loadRegistration();
    }
    this.loadSubscribeConfig();
  },
  onUnload() {
    if (this.pollTimer) {
      clearInterval(this.pollTimer);
      this.pollTimer = null;
    }
  },
  methods: {
    async loadSubscribeConfig() {
      try {
        const result = await getSubscribeConfig();
        if (result.code === 200) {
          this.subscribeTemplateId = (result.data && result.data.template_id) || '';
        }
      } catch (e) {
        this.subscribeTemplateId = '';
      }
    },
    async requestSubscribeBeforePay() {
      // #ifdef MP-WEIXIN
      if (!this.subscribeTemplateId) return null;
      return new Promise((resolve) => {
        wx.requestSubscribeMessage({
          tmplIds: [this.subscribeTemplateId],
          success: (res) => {
            resolve(res[this.subscribeTemplateId] === 'accept');
          },
          fail: () => resolve(false),
        });
      });
      // #endif
      // #ifndef MP-WEIXIN
      return null;
      // #endif
    },
    formatTime(ts) {
      if (!ts) return '';
      return dayjs(ts).format('YYYY-MM-DD HH:mm:ss');
    },
    async loadRegistration() {
      try {
        const result = await getMyRegistrations();
        if (result.code === 200) {
          const list = result.data || [];
          const reg = list.find((r) => r._id === this.registrationId);
          if (reg) {
            this.regInfo = {
              name: reg.name,
              event_name: reg.event_name,
              ticket_no: reg.ticket_no,
              fee: reg.fee || this.regInfo.fee,
            };
            this.paymentStatus = reg.payment_status;
          }
        }
      } catch (e) {
        console.log('加载报名信息失败');
      }
    },
    async handlePay() {
      if (this.paying) return;
      this.paying = true;

      const userStore = useUserStore();
      if (!userStore.isLoggedIn) {
        uni.showToast({ title: this.$t('message.login_expired'), icon: 'none' });
        this.paying = false;
        return;
      }

      try {
        const subscribeAccepted = await this.requestSubscribeBeforePay();
        if (subscribeAccepted === false) {
          uni.showToast({ title: '未授权订阅通知', icon: 'none' });
        }

        const result = await createOrder(this.registrationId);

        if (result.code === 409) {
          this.paymentStatus = 'paid';
          await this.fetchLatestPaidInfo();
          this.showPaidResult(this.paymentOrderNo);
          this.paying = false;
          return;
        }

        if (result.code !== 200) {
          uni.showToast({ title: result.message || this.$t('message.request_failed'), icon: 'none' });
          this.paying = false;
          return;
        }

        const data = result.data;

        // 免费项目
        if (data.free) {
          this.paymentStatus = 'paid';
          this.paymentTime = Date.now();
          uni.showToast({ title: this.$t('message.success'), icon: 'success' });
          this.paying = false;
          return;
        }

        // 模拟支付模式
        if (data.mock) {
          this.handleMockPay(data);
          return;
        }

        // 真实微信支付
        const payParams = data.payParams;
        uni.requestPayment({
          provider: 'wxpay',
          timeStamp: payParams.timeStamp,
          nonceStr: payParams.nonceStr,
          package: payParams.package,
          signType: payParams.signType,
          paySign: payParams.paySign,
          success: () => {
            this.startPolling();
          },
          fail: (err) => {
            if (err.errMsg && err.errMsg.includes('cancel')) {
              uni.showToast({ title: this.$t('payment.cancel'), icon: 'none' });
            } else {
              uni.showToast({ title: this.$t('payment.failed'), icon: 'none' });
            }
            this.paying = false;
          },
        });
      } catch (e) {
        console.error('支付失败:', e);
        uni.showToast({ title: this.$t('message.network_error'), icon: 'none' });
        this.paying = false;
      }
    },
    handleMockPay(data) {
      uni.showModal({
        title: this.$t('payment.mock_title'),
        content: this.$t('payment.mock_tip').replace('{fee}', (data.total_fee / 100).toFixed(2)),
        success: async (res) => {
          if (res.confirm) {
            try {
              const mockRes = await mockPay(this.registrationId);
              if (mockRes.code === 200) {
                this.paymentStatus = 'paid';
                this.paymentTime = mockRes.data.payment_time;
                this.paymentOrderNo = mockRes.data.payment_order_no || '';
                this.showPaidResult(this.paymentOrderNo);
              } else {
                uni.showToast({ title: mockRes.message || this.$t('payment.failed'), icon: 'none' });
              }
            } catch (e) {
              uni.showToast({ title: this.$t('payment.failed'), icon: 'none' });
            }
          }
          this.paying = false;
        },
      });
    },
    startPolling() {
      let count = 0;
      this.pollTimer = setInterval(async () => {
        count++;
        if (count > 10) {
          clearInterval(this.pollTimer);
          this.pollTimer = null;
          this.paying = false;
          uni.showToast({ title: this.$t('message.request_failed'), icon: 'none' });
          return;
        }
        try {
          const result = await queryOrder(this.registrationId);
          if (result.code === 200 && result.data.payment_status === 'paid') {
            clearInterval(this.pollTimer);
            this.pollTimer = null;
            this.paymentStatus = 'paid';
            this.paymentTime = result.data.payment_time;
            this.paymentOrderNo = result.data.payment_order_no || '';
            this.paying = false;
            this.showPaidResult(this.paymentOrderNo);
          }
        } catch (e) {
          // 继续轮询
        }
      }, 2000);
    },
    showPaidResult(orderNo) {
      uni.showModal({
        title: this.$t('payment.success'),
        content: orderNo ? `${this.$t('result.paid')}\n${this.$t('payment.order_no')}：${orderNo}` : this.$t('result.paid'),
        showCancel: false,
      });
    },
    async fetchLatestPaidInfo() {
      try {
        const result = await queryOrder(this.registrationId);
        if (result.code === 200 && result.data) {
          this.paymentTime = result.data.payment_time || this.paymentTime;
          this.paymentOrderNo = result.data.payment_order_no || '';
        }
      } catch (e) {
        // ignore
      }
    },
    goHome() {
      uni.reLaunch({ url: '/pages/index/index' });
    },
    goTicket() {
      if (this.regInfo.ticket_no) {
        uni.navigateTo({
          url: `/pages/ticket/ticket?ticket_no=${this.regInfo.ticket_no}`,
        });
        return;
      }
      uni.navigateTo({ url: '/pages/ticket/ticket' });
    },
  },
};
</script>

<style></style>
