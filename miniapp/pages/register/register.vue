<template>
  <view class="min-h-screen bg-gray-50 flex flex-col">
    <!-- 顶部状态 (如果是分步骤，这里可以放进度) -->
    <view class="bg-white px-4 py-3 border-b border-gray-50">
      <text class="text-xl font-black text-gray-900">{{ event.title }}</text>
    </view>

    <!-- 步骤 1: 类别选择 -->
    <view v-if="step === 1" class="flex-1 p-4">
      <!-- 组别选择 -->
      <view class="mb-8">
        <view class="flex justify-between items-center mb-4">
          <text class="text-base font-black text-gray-900">请选择参赛组别</text>
          <text class="text-xs text-blue-600" @tap="showIntro">查看《组别介绍》</text>
        </view>
        <view class="flex gap-3">
          <view 
            v-for="group in event.categories" 
            :key="group.id"
            class="flex-1 py-4 px-2 rounded-xl flex flex-col items-center justify-center border-2 transition-all"
            :class="selectedGroup?.id === group.id ? 'bg-black border-black text-white shadow-lg' : 'bg-white border-transparent text-gray-400'"
            @tap="selectGroup(group)"
          >
            <text class="text-sm font-bold">{{ group.name }}</text>
            <text class="text-[10px] opacity-60 mt-1">{{ group.name_en }}</text>
          </view>
        </view>
      </view>

      <!-- 性别选择 (如果组别有子类) -->
      <view v-if="selectedGroup?.children" class="mb-8 animate-fade-in">
        <text class="block text-base font-black text-gray-900 mb-4">请选择</text>
        <view class="flex gap-3">
          <view 
            v-for="gender in selectedGroup.children" 
            :key="gender.id"
            class="flex-1 py-4 px-2 rounded-xl flex flex-col items-center justify-center border-2 transition-all"
            :class="selectedGender?.id === gender.id ? 'bg-black border-black text-white shadow-lg' : 'bg-white border-transparent text-gray-400'"
            @tap="selectGender(gender)"
          >
            <text class="text-sm font-bold">{{ gender.name }}</text>
            <text class="text-[10px] opacity-60 mt-1">{{ gender.name_en }}</text>
          </view>
        </view>
      </view>

      <!-- 具体项目选择 -->
      <view v-if="selectedGender?.children" class="mb-8 animate-fade-in">
        <text class="block text-base font-black text-gray-900 mb-4">请选择</text>
        <view class="flex gap-3">
          <view 
            v-for="cat in selectedGender.children" 
            :key="cat.id"
            class="flex-1 py-4 px-2 rounded-xl flex flex-col items-center justify-center border-2 transition-all"
            :class="selectedCat?.id === cat.id ? 'bg-black border-black text-white shadow-lg' : 'bg-white border-transparent text-gray-400'"
            @tap="selectCat(cat)"
          >
            <text class="text-sm font-bold">{{ cat.name }}</text>
            <text class="text-[10px] opacity-60 mt-1">{{ cat.name_en }}</text>
          </view>
        </view>
      </view>

      <!-- 日期展示 -->
      <view v-if="selectedCat" class="bg-white rounded-xl p-4 flex justify-between items-center shadow-sm animate-fade-in">
        <view>
          <text class="block text-sm font-bold text-gray-900">组别日期</text>
          <text class="text-[10px] text-gray-400 mt-1">Category Date</text>
        </view>
        <view class="text-right">
          <text class="block text-lg font-black text-gray-900">{{ formatDate(selectedCat.date) }}</text>
          <text class="text-xs text-gray-400">{{ formatDayOfWeek(selectedCat.date) }}</text>
        </view>
      </view>
    </view>

    <!-- 步骤 2: 信息填写 (原有表单逻辑) -->
    <view v-if="step === 2" class="flex-1 p-4 animate-fade-in">
       <!-- ... 原有的表单字段 ... -->
       <view class="bg-white rounded-2xl p-4 space-y-4 shadow-sm">
         <view class="flex items-center border-b border-gray-50 pb-3">
           <text class="w-20 text-sm font-bold">姓名</text>
           <input v-model="form.name" placeholder="请输入真实姓名" class="flex-1 text-right text-sm" />
         </view>
         <view class="flex items-center border-b border-gray-50 pb-3">
           <text class="w-20 text-sm font-bold">电话</text>
           <input v-model="form.phone" type="number" maxlength="11" placeholder="请输入手机号" class="flex-1 text-right text-sm" />
         </view>
         <view class="flex items-center border-b border-gray-50 pb-3">
           <text class="w-20 text-sm font-bold">身份证</text>
           <input v-model="form.id_card" maxlength="18" placeholder="请输入身份证号" class="flex-1 text-right text-sm" />
         </view>
       </view>
    </view>

    <!-- 底部按钮 -->
    <view class="p-5 bg-white/60 backdrop-blur-xl border-t border-gray-100 safe-bottom">
      <button 
        class="w-full bg-yellow-400 active:bg-yellow-500 text-black font-black h-14 rounded-2xl shadow-lg flex items-center justify-center text-lg transition-all active:scale-95"
        :class="canNext ? '' : 'grayscale opacity-50 pointer-events-none'"
        @tap="handleNext"
      >
        {{ step === 1 ? '立即报名' : '提交报名' }}
      </button>
    </view>

    <!-- 报名已满弹窗 -->
    <view v-if="showFullPopup" class="fixed inset-0 z-[1000] flex items-center justify-center p-8 bg-black/60 backdrop-blur-sm">
      <view class="bg-white rounded-3xl w-full max-w-sm overflow-hidden animate-scale-in">
        <view class="p-8 flex flex-col items-center">
          <view class="w-20 h-20 bg-gray-100 rounded-full flex items-center justify-center text-4xl mb-6">🙁</view>
          <text class="text-xl font-black text-gray-900 mb-2">组别报名已满</text>
          <text class="text-sm text-gray-400 text-center leading-relaxed">~ 组别已满员，请关注我们获得最新资讯！</text>
        </view>
        <view class="p-4 bg-gray-50 flex gap-3">
          <button class="flex-1 h-12 bg-white border border-gray-200 rounded-xl font-bold text-gray-900 flex items-center justify-center" @tap="showFullPopup = false">关闭</button>
        </view>
      </view>
    </view>
  </view>
</template>

<script>
import { GET } from '@/services/api/request.js';
import { submitRegistration } from '@/services/api/register-api.js';
import dayjs from 'dayjs';
import 'dayjs/locale/zh-cn';
dayjs.locale('zh-cn');

export default {
  data() {
    return {
      compId: '',
      event: { categories: [] },
      step: 1,
      selectedGroup: null,
      selectedGender: null,
      selectedCat: null,
      showFullPopup: false,
      form: {
        name: '',
        phone: '',
        id_card: ''
      },
      submitting: false
    };
  },
  computed: {
    canNext() {
      if (this.step === 1) return !!this.selectedCat;
      return this.form.name && this.form.phone.length === 11 && this.form.id_card.length === 18;
    }
  },
  onLoad(options) {
    this.compId = options.compId || '';
    this.loadEvent();
  },
  methods: {
    async loadEvent() {
      if (!this.compId) return;
      const res = await GET(`/api/register/competition/${this.compId}`);
      if (res.code === 200) {
        this.event = res.data;
        // 默认选中第一个
        if (this.event.categories?.[0]) this.selectGroup(this.event.categories[0]);
      }
    },
    selectGroup(group) {
      this.selectedGroup = group;
      this.selectedGender = group.children?.[0] || null;
      this.selectedCat = this.selectedGender?.children?.[0] || null;
    },
    selectGender(gender) {
      this.selectedGender = gender;
      this.selectedCat = gender.children?.[0] || null;
    },
    selectCat(cat) {
      if (cat.is_full) {
        this.showFullPopup = true;
        return;
      }
      this.selectedCat = cat;
    },
    formatDate(date) {
      return dayjs(date).format('YYYY-MM-DD');
    },
    formatDayOfWeek(date) {
      return dayjs(date).format('dddd');
    },
    handleNext() {
      if (this.step === 1) {
        this.step = 2;
        uni.setNavigationBarTitle({ title: '完善信息' });
      } else {
        this.submit();
      }
    },
    async submit() {
      if (this.submitting) return;
      this.submitting = true;
      uni.showLoading({ title: '提交中' });
      try {
        const payload = {
          comp_id: this.compId,
          category_id: this.selectedCat.id,
          category_name: `${this.selectedGroup.name}-${this.selectedGender.name}-${this.selectedCat.name}`,
          ...this.form
        };
        const res = await submitRegistration(payload);
        if (res.code === 200) {
          uni.redirectTo({ url: `/pages/register/result?id=${res.data.id}` });
        } else {
          uni.showToast({ title: res.message || '提交失败', icon: 'none' });
        }
      } finally {
        this.submitting = false;
        uni.hideLoading();
      }
    },
    showIntro() {
       uni.showModal({ title: '组别介绍', content: '这里是各个组别的详细介绍说明...', showCancel: false });
    }
  }
};
</script>

<style scoped>
@keyframes fade-in {
  from { opacity: 0; transform: translateY(10rpx); }
  to { opacity: 1; transform: translateY(0); }
}
@keyframes scale-in {
  from { opacity: 0; transform: scale(0.9); }
  to { opacity: 1; transform: scale(1); }
}
.animate-fade-in { animation: fade-in 0.3s ease-out forwards; }
.animate-scale-in { animation: scale-in 0.2s ease-out forwards; }

.safe-bottom {
  padding-bottom: calc(20px + constant(safe-area-inset-bottom));
  padding-bottom: calc(20px + env(safe-area-inset-bottom));
}
</style>

<script>
import { useUserStore } from '@/services/store/user.js';
import { GET } from '@/services/api/request.js';
import { submitRegistration, checkDuplicate } from '@/services/api/register-api.js';
import { uploadFile } from '@/services/api/request.js';

export default {
  data() {
    return {
      form: {
        name: '',
        gender: '',
        school: '',
        phone: '',
        id_card: '',
        avatar_url: '',
        avatar_temp_url: '',
        optional_events: [],
        is_sports_talent: false,
      },
      genderOptions: [
        { label: this.$t('register.gender_male'), value: 'male' },
        { label: this.$t('register.gender_female'), value: 'female' },
      ],
      genderIndex: 0,

      schoolOptions: [],
      schoolIndex: 0,
      schoolPickerVisible: false,
      schoolSearchKeyword: '',
      requiredEvents: [],
      optionalEvents: [],
      commitmentSignatures: {
        personal_promise_signature: '',
        health_promise_signature: '',
        personal_guardian_signature: '',
        health_guardian_signature: '',
      },
      submitting: false,
    };
  },
  computed: {
    requiredEventName() {
      if (!this.requiredEvents.length) return '';
      if (this.requiredEvents.length === 1) return this.requiredEvents[0];
      const femaleMatch = this.requiredEvents.find((name) => String(name).includes('800'));
      const maleMatch = this.requiredEvents.find((name) => String(name).includes('1000'));
      if (this.form.gender === 'female') return femaleMatch || this.requiredEvents[0];
      return maleMatch || this.requiredEvents[0];
    },
    schoolNames() {
      return this.schoolOptions.map((s) => s.name);
    },
    filteredSchoolNames() {
      const kw = (this.schoolSearchKeyword || '').trim();
      if (!kw) return this.schoolNames;
      return this.schoolNames.filter((n) => n.includes(kw));
    },
    allSelectedText() {
      const items = [];
      if (this.requiredEventName) items.push(this.requiredEventName);
      items.push(...this.form.optional_events);
      return items.length > 0 ? items.join('、') : this.$t('register.none_selected');
    },
  },
  onLoad() {
    this.checkLogin();
    this.loadEvents();
    this.loadSchools();
    this.loadCommitmentSignatures();
  },
  onShow() {
    uni.setNavigationBarTitle({
      title: this.$t('register.form_title')
    });
    this.loadCommitmentSignatures();
  },
  methods: {
    async checkLogin() {
      const userStore = useUserStore();
      if (!userStore.isLoggedIn) {
        try {
          await userStore.login();
        } catch (e) {
          console.error('Silent login failed:', e);
          uni.showToast({ title: this.$t('message.login_failed'), icon: 'none' });
        }
      }
    },
    loadCommitmentSignatures() {
      const cached = uni.getStorageSync('register_commitment_signatures') || {};
      this.commitmentSignatures = {
        personal_promise_signature: cached.personal_promise_signature || '',
        health_promise_signature: cached.health_promise_signature || '',
        personal_guardian_signature: cached.personal_guardian_signature || '',
        health_guardian_signature: cached.health_guardian_signature || '',
      };
    },
    async loadEvents() {
      try {
        const result = await GET('/api/register/events', {}, { silent: true });
        const rows = (result.code === 200 ? result.data : []) || [];
        this.requiredEvents = rows.filter((e) => !!e.is_required).map((e) => e.name).filter(Boolean);
        this.optionalEvents = rows.filter((e) => !e.is_required).map((e) => e.name).filter(Boolean);
        this.form.optional_events = (this.form.optional_events || []).filter((name) =>
          this.optionalEvents.includes(name)
        );
      } catch (e) {
        this.requiredEvents = [];
        this.optionalEvents = [];
        console.log('Skip loading events');
      }
    },
    async loadSchools() {
      try {
        const result = await GET('/api/register/schools', {}, { silent: true });
        this.schoolOptions = (result.code === 200 ? result.data : []) || [];
      } catch (e) {
        console.log('加载学校列表跳过');
      }
    },
    onGenderChange(e) {
      this.genderIndex = e.detail.value;
      this.form.gender = this.genderOptions[this.genderIndex].value;
    },

    onSchoolChange(e) {
      this.schoolIndex = e.detail.value;
      this.form.school = this.schoolNames[this.schoolIndex] || '';
    },
    openSchoolPicker() {
      this.schoolSearchKeyword = '';
      this.schoolPickerVisible = true;
    },
    selectSchool(name) {
      this.form.school = name;
      this.schoolPickerVisible = false;
    },
    toggleOptionalEvent(item) {
      const idx = this.form.optional_events.indexOf(item);
      if (idx > -1) {
        this.form.optional_events.splice(idx, 1);
      } else {
        if (this.form.optional_events.length >= 2) {
          uni.showToast({ title: this.$t('register.optional_limit'), icon: 'none' });
          return;
        }
        this.form.optional_events.push(item);
      }
    },
    chooseAvatar() {
      uni.chooseImage({
        count: 1,
        sizeType: ['compressed'],
        sourceType: ['album', 'camera'],
        success: async (res) => {
          const filePath = res.tempFilePaths[0];
          if (!filePath) return;
          uni.showLoading({ title: this.$t('common.loading') });
          try {
            const uploadRes = await uploadFile(filePath);
            this.form.avatar_url = uploadRes.url || '';
            this.form.avatar_temp_url = filePath;
            uni.hideLoading();
            uni.showToast({ title: this.$t('message.success'), icon: 'success' });
          } catch (e) {
            uni.hideLoading();
            console.error('Upload avatar failed:', e);
            uni.showToast({ title: this.$t('message.upload_failed'), icon: 'none' });
          }
        },
      });
    },
    previewAvatar() {
      if (!this.form.avatar_temp_url && !this.form.avatar_url) return;
      const current = this.form.avatar_temp_url || this.form.avatar_url;
      uni.previewImage({
        urls: [current],
        current,
      });
    },
    clearAvatar() {
      this.form.avatar_url = '';
      this.form.avatar_temp_url = '';
    },
    validateForm() {
      const { name, gender, school } = this.form;
      const phone = String(this.form.phone || '').replace(/\D/g, '');
      this.form.phone = phone;
      const id_card = String(this.form.id_card || '').trim().toUpperCase();
      this.form.id_card = id_card;
      if (!name || !name.trim()) {
        uni.showToast({ title: this.$t('register.name_placeholder'), icon: 'none' });
        return false;
      }
      if (!gender) {
        uni.showToast({ title: this.$t('register.gender_placeholder'), icon: 'none' });
        return false;
      }

      if (!school || !school.trim()) {
        uni.showToast({ title: this.$t('register.school_placeholder'), icon: 'none' });
        return false;
      }
      if (!phone || phone.length !== 11) {
        uni.showToast({ title: this.$t('message.error_phone'), icon: 'none' });
        return false;
      }
      if (!/^1[3-9]\d{9}$/.test(phone)) {
        uni.showToast({ title: this.$t('message.error_phone'), icon: 'none' });
        return false;
      }
      if (!id_card || id_card.length !== 18) {
        uni.showToast({ title: this.$t('message.error_id_card'), icon: 'none' });
        return false;
      }
     
      if (!this.requiredEventName) {
        uni.showToast({ title: this.$t('message.request_failed'), icon: 'none' });
        return false;
      }
      if (this.form.optional_events.length !== 2) {
        uni.showToast({ title: this.$t('register.optional_limit'), icon: 'none' });
        return false;
      }
      return true;
    },
    async handleSubmit() {
      if (!this.validateForm()) return;
      if (this.submitting) return;

      const userStore = useUserStore();
      if (!userStore.isLoggedIn) {
        uni.showToast({ title: this.$t('message.login_expired'), icon: 'none' });
        return;
      }

      this.submitting = true;

      if (
        !this.commitmentSignatures.personal_promise_signature ||
        !this.commitmentSignatures.health_promise_signature ||
        !this.commitmentSignatures.personal_guardian_signature ||
        !this.commitmentSignatures.health_guardian_signature
      ) {
        uni.showToast({ title: this.$t('message.param_error'), icon: 'none' });
        this.submitting = false;
        setTimeout(() => {
          uni.navigateTo({ url: '/pages/register/confirm' });
        }, 300);
        return;
      }

      // 构建报考项目名称
      const allEvents = [this.requiredEventName, ...this.form.optional_events];
      const eventName = allEvents.join('、');

      try {
        // 检查是否重复报名
        const checkRes = await checkDuplicate(this.form.id_card);
        if (checkRes.code === 200 && checkRes.data.is_duplicate) {
          const reg = checkRes.data.registration;
          uni.showModal({
            title: this.$t('common.info'),
            content: `${this.$t('message.error_duplicate')}, ID: ${reg.ticket_no}`,
            showCancel: false,
          });
          this.submitting = false;
          return;
        }

        // 提交报名
        const result = await submitRegistration({
          name: this.form.name,
          gender: this.form.gender,
          school: this.form.school,
          phone: this.form.phone,
          id_card: this.form.id_card,
          avatar_url: this.form.avatar_url,
          required_event: this.requiredEventName,
          optional_events: this.form.optional_events,
          event_name: eventName,
          is_sports_talent: this.form.is_sports_talent,
          personal_promise_signature:
            this.commitmentSignatures.personal_promise_signature,
          health_promise_signature:
            this.commitmentSignatures.health_promise_signature,
          personal_guardian_signature:
            this.commitmentSignatures.personal_guardian_signature,
          health_guardian_signature:
            this.commitmentSignatures.health_guardian_signature,
        });

        if (result.code === 200) {
          uni.removeStorageSync('register_commitment_signatures');
          const data = encodeURIComponent(JSON.stringify(result.data));
          uni.redirectTo({
            url: `/pages/register/result?data=${data}`,
          });
        } else if (result.code === 409) {
          uni.showModal({
            title: this.$t('common.info'),
            content: result.message,
            showCancel: false,
          });
        } else {
          uni.showToast({ title: result.message || this.$t('message.request_failed'), icon: 'none' });
        }
      } catch (e) {
        console.error('Registration failed:', e);
        uni.showToast({ title: this.$t('message.network_error'), icon: 'none' });
      } finally {
        this.submitting = false;
      }
    },
  },
};
</script>

<style>
.form-row {
  display: flex;
  align-items: center;
  padding: 28rpx 32rpx;
  border-bottom: 1rpx solid #f3f4f6;
}
.form-row:last-child {
  border-bottom: none;
}
.form-label {
  width: 160rpx;
  font-size: 28rpx;
  color: #374151;
  flex-shrink: 0;
}
.form-control {
  flex: 1;
}
.form-input {
  flex: 1;
  font-size: 28rpx;
  color: #111827;
  text-align: right;
}
.form-picker-wrap {
  display: block;
  width: 100%;
}
.form-picker {
  flex: 1;
  display: flex;
  align-items: center;
  justify-content: flex-end;
}
.avatar-preview {
  width: 120rpx;
  height: 160rpx;
  border-radius: 12rpx;
  background: #f3f4f6;
}
.avatar-placeholder {
  width: 120rpx;
  height: 160rpx;
  border-radius: 12rpx;
  background: #f9fafb;
  border: 1rpx dashed #d1d5db;
  display: flex;
  align-items: center;
  justify-content: center;
}
.school-picker-mask {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.5);
  z-index: 999;
}
.school-picker-panel {
  position: absolute;
  bottom: 0;
  left: 0;
  right: 0;
  background: #fff;
  border-radius: 24rpx 24rpx 0 0;
}
.school-search-input {
  width: 100%;
  height: 72rpx;
  line-height: 72rpx;
  background: #f3f4f6;
  border-radius: 12rpx;
  padding: 0 24rpx;
  font-size: 28rpx;
  color: #111827;
  box-sizing: border-box;
}
.school-picker-list {
  height: 700rpx;
}
.school-picker-item {
  padding: 28rpx 32rpx;
  border-bottom: 1rpx solid #f9fafb;
}
.school-picker-item-active {
  background: #eff6ff;
}
</style>
