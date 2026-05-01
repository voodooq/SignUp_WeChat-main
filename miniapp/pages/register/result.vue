<template>
  <view class="min-h-screen bg-gray-50">
    <!-- 模式一：报名成功（从报名页跳转过来） -->
    <view v-if="mode === 'single'">
      <view class="bg-blue-500 pt-10 pb-16 flex flex-col items-center">
        <view class="w-16 h-16 rounded-full bg-white flex items-center justify-center mb-3">
          <text class="text-blue-500 text-3xl font-bold">✓</text>
        </view>
        <text class="text-white text-lg font-bold">{{ $t('result.success') }}</text>
      </view>

      <view class="mx-3 -mt-8 bg-white rounded-xl p-4 shadow-sm">
        <view class="text-center border-b border-gray-100 pb-4 mb-4">
          <text class="block text-gray-500 text-sm mb-1">{{ $t('result.ticket_no') }}</text>
          <text class="block text-gray-800 text-2xl font-bold">{{ regData.ticket_no }}</text>
        </view>
        <view v-for="row in singleRows" :key="row.label" class="flex py-2">
          <text class="text-gray-500 text-sm" style="width: 180rpx">{{ row.label }}</text>
          <text class="flex-1 text-sm" :class="row.cls || 'text-gray-800'">{{ row.value }}</text>
        </view>
      </view>

      <view v-if="regData.payment_status === 'unpaid'" class="mx-3 mt-3 bg-yellow-50 rounded-xl p-4">
        <text class="text-yellow-700 text-sm block">{{ $t('result.pay_tip') }}</text>
        <text v-if="regData.fee" class="text-yellow-700 text-sm block mt-1">
          {{ $t('result.fee') }}：¥{{ (regData.fee / 100).toFixed(2) }}
        </text>
      </view>

      <view class="mx-3 mt-4">
        <view v-if="regData.payment_status === 'unpaid'" class="bg-blue-500 rounded-xl py-3 text-center mb-3" @tap="goPayment">
          <text class="text-white text-base font-medium">{{ $t('result.go_pay') }}</text>
        </view>
        <view class="bg-white rounded-xl py-3 text-center border border-gray-200" @tap="goHome">
          <text class="text-gray-600 text-base">{{ $t('result.back_home') }}</text>
        </view>
      </view>
    </view>

    <!-- 模式二：我的报名列表（从个人中心进入） -->
    <view v-if="mode === 'list'">
      <view class="px-3 mt-3">
        <view class="bg-white rounded-xl p-3 shadow-sm">
          <view class="flex items-center bg-gray-100 rounded-lg px-3 py-2">
            <input
              class="flex-1 text-sm"
              v-model="ticketNoQuery"
              :placeholder="$t('result.search_placeholder')"
              confirm-type="search"
              @input="onTicketInput"
              @confirm="searchByTicketNo"
            />
            <text
              v-if="ticketNoQuery"
              class="text-gray-400 text-xs ml-2"
              @tap="clearTicketNo"
            >
              {{ $t('score.clear') }}
            </text>
          </view>
          <view class="mt-2 bg-blue-500 rounded-lg py-2 text-center" @tap="searchByTicketNo">
            <text class="text-white text-xs">{{ $t('result.search_btn') }}</text>
          </view>
        </view>
      </view>

      <view v-if="loading" class="text-center py-8">
        <text class="text-gray-400 text-sm">{{ $t('common.loading') }}</text>
      </view>
      <view v-else-if="registrations.length === 0" class="text-center py-16">
        <text class="block text-gray-300 text-5xl mb-4">📋</text>
        <text class="block text-gray-400 text-sm">{{ $t('result.no_reg') }}</text>
      </view>
      <view v-else class="px-3 mt-3">
        <view
          v-for="item in registrations"
          :key="item._id"
          class="bg-white rounded-xl p-4 mb-3 shadow-sm"
          @tap="viewTicket(item)"
        >
          <view class="flex items-center mb-2">
            <text class="text-gray-900 text-xs font-medium bg-gray-100 px-2 py-1 rounded">
              {{ item.ticket_no }}
            </text>
            <view class="flex-1"></view>
            <text
              class="text-xs px-2 py-1 rounded"
              :class="paymentClass(item.payment_status)"
            >
              {{ paymentText(item.payment_status) }}
            </text>
          </view>
          <view class="flex items-center mb-1">
            <text class="text-gray-800 text-sm font-medium">{{ item.name }}</text>
            <text class="text-gray-500 text-xs ml-2">{{ item.gender === 'male' ? $t('register.gender_male') : $t('register.gender_female') }}</text>
          </view>
          <view class="flex items-center">
            <text class="text-gray-600 text-sm">{{ item.event_name }}</text>
            <text class="text-gray-400 text-xs ml-2">{{ item.school }}</text>
          </view>
          <view v-if="item.payment_status === 'unpaid'" class="mt-2">
            <view class="bg-blue-500 rounded-lg py-2 text-center" @tap.stop="goPaymentFromList(item)">
              <text class="text-white text-xs">{{ $t('result.go_pay') }}</text>
            </view>
          </view>
        </view>
      </view>
    </view>

    <view class="h-6"></view>
  </view>
</template>

<script>
import { useUserStore } from '@/services/store/user.js';
import { getMyRegistrations, getTicket } from '@/services/api/register-api.js';

export default {
  data() {
    return {
      mode: 'list',
      regData: {},
      registrations: [],
      loading: false,
      ticketNoQuery: ''
    };
  },
  computed: {
    singleRows() {
      const d = this.regData;
      return [
        { label: this.$t('register.name'), value: d.name },
        { label: this.$t('register.gender'), value: d.gender === 'male' ? this.$t('register.gender_male') : this.$t('register.gender_female') },
        { label: this.$t('register.school'), value: d.school },
        { label: this.$t('register.phone'), value: d.phone },
        { label: this.$t('register.id_card'), value: d.id_card_masked },
        { label: this.$t('ticket.events'), value: d.event_name },
        { label: this.$t('result.pay_status'), value: this.paymentText(d.payment_status), cls: d.payment_status === 'paid' ? 'text-green-600 font-medium' : d.payment_status === 'admin_free' ? 'text-blue-600 font-medium' : 'text-red-500 font-medium' }
      ];
    }
  },
  onShow() {
    uni.setNavigationBarTitle({
      title: this.mode === 'single' ? this.$t('result.title') : this.$t('result.list_title')
    });
  },
  onLoad(options) {
    if (options.data) {
      try {
        this.regData = JSON.parse(decodeURIComponent(options.data));
        this.mode = 'single';
      } catch (e) {
        console.error('解析报名数据失败:', e);
        this.mode = 'list';
        this.loadRegistrations();
      }
    } else {
      this.mode = 'list';
      this.loadRegistrations();
    }
  },
  methods: {
    clearTicketNo() {
      this.ticketNoQuery = '';
      this.loadRegistrations();
    },
    onTicketInput(e) {
      const value = String((e && e.detail && e.detail.value) || this.ticketNoQuery || '').trim();
      if (!value) {
        this.loadRegistrations();
      }
    },
    async searchByTicketNo() {
      const ticketNo = String(this.ticketNoQuery || '').trim();
      if (!ticketNo) {
        uni.showToast({ title: this.$t('score.search_placeholder'), icon: 'none' });
        return;
      }

      this.loading = true;
      try {
        const result = await getTicket(ticketNo);
        if (result.code === 200 && result.data) {
          this.registrations = [result.data];
        } else {
          this.registrations = [];
          uni.showToast({ title: result.message || this.$t('score.no_match'), icon: 'none' });
        }
      } catch (e) {
        console.error(e);
        this.registrations = [];
        uni.showToast({ title: this.$t('message.request_failed'), icon: 'none' });
      }
      this.loading = false;
    },
    async loadRegistrations() {
      this.loading = true;
      try {
        const result = await getMyRegistrations();
        if (result.code === 200) {
          this.registrations = result.data;
        }
      } catch (e) {
        console.error(e);
      }
      this.loading = false;
    },
    paymentText(status) {
      const map = { 
        paid: this.$t('result.paid'), 
        unpaid: this.$t('result.unpaid'), 
        admin_free: this.$t('result.admin_free') 
      };
      return map[status] || status;
    },
    paymentClass(status) {
      const map = {
        paid: 'text-green-600 bg-gray-50',
        unpaid: 'text-orange-600 bg-orange-50',
        admin_free: 'text-purple-600 bg-purple-50'
      };
      return map[status] || 'text-gray-600 bg-gray-50';
    },
    viewTicket(item) {
      if (item.payment_status === 'unpaid') {
        this.goPaymentFromList(item);
        return;
      }
      uni.navigateTo({
        url: `/pages/ticket/ticket?ticket_no=${item.ticket_no}`
      });
    },
    goPayment() {
      const data = encodeURIComponent(JSON.stringify(this.regData));
      uni.navigateTo({
        url: `/pages/payment/payment?registration_id=${this.regData._id}&data=${data}`
      });
    },
    goPaymentFromList(item) {
      const data = encodeURIComponent(JSON.stringify(item));
      uni.navigateTo({
        url: `/pages/payment/payment?registration_id=${item._id}&data=${data}`
      });
    },
    goHome() {
      uni.reLaunch({ url: '/pages/index/index' });
    },
  }
};
</script>

<style></style>
