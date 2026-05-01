<template>
  <view class="min-h-screen bg-gray-50 p-3">
    <view class="bg-white rounded-xl p-4">
      <text class="block text-gray-900 text-base font-bold">
        {{ $t('register.personal_title') }}
      </text>
      <image
        v-if="promiseImageUrl"
        :src="promiseImageUrl"
        mode="widthFix"
        class="promise-image mt-2"
      />
      <text v-else class="block text-gray-400 text-sm mt-2">{{ $t('register.no_promise_image') }}</text>
    </view>

    <view class="bg-white rounded-xl p-4 mt-3">
      <text class="block text-gray-700 text-sm mb-2">{{ $t('register.sign_personal') }}</text>
      <canvas
        canvas-id="personalSignCanvas"
        id="personalSignCanvas"
        class="sign-canvas"
        @touchstart.stop.prevent="onTouchStart('personal', $event)"
        @touchmove.stop.prevent="onTouchMove('personal', $event)"
        @touchend.stop.prevent="onTouchEnd('personal')"
      ></canvas>
      <text class="block text-gray-700 text-sm mt-4 mb-2">{{ $t('register.sign_guardian') }}</text>
      <canvas
        canvas-id="personalGuardianSignCanvas"
        id="personalGuardianSignCanvas"
        class="sign-canvas"
        @touchstart.stop.prevent="onTouchStart('guardian', $event)"
        @touchmove.stop.prevent="onTouchMove('guardian', $event)"
        @touchend.stop.prevent="onTouchEnd('guardian')"
      ></canvas>
      <view class="flex mt-3">
        <button
          class="flex-1 bg-gray-100 py-3 text-gray-700 text-sm rounded-lg mr-2"
          @tap="clearSigns"
        >
          {{ $t('register.clear_btn') }}
        </button>
        <button
          class="flex-1 bg-blue-500 py-3 text-white text-sm rounded-lg ml-2"
          @tap="saveAndNext"
          :disabled="saving"
        >
          {{ saving ? $t('register.saving') : $t('register.next_step') }}
        </button>
      </view>
    </view>
  </view>
</template>

<script>
import { request, uploadFile } from '@/services/api/request.js';

export default {
  data() {
    return {
      promiseImageUrl: '',
      personalCtx: null,
      guardianCtx: null,
      personalLastPoint: null,
      guardianLastPoint: null,
      hasPersonalSigned: false,
      hasGuardianSigned: false,
      saving: false,
    };
  },
  onShow() {
    uni.setNavigationBarTitle({
      title: this.$t('register.personal_title')
    });
  },
  onLoad() {
    this.loadPromiseImage();
  },
  onReady() {
    this.personalCtx = uni.createCanvasContext('personalSignCanvas', this);
    this.guardianCtx = uni.createCanvasContext('personalGuardianSignCanvas', this);
    [this.personalCtx, this.guardianCtx].forEach((ctx) => {
      ctx.setStrokeStyle('#111827');
      ctx.setLineWidth(2);
      ctx.setLineCap('round');
      ctx.setLineJoin('round');
    });
  },
  methods: {
    async loadPromiseImage() {
      try {
        const res = await request('/api/public/settings');
        const fileId =
          res?.code === 200
            ? String(res.data.personal_promise_image || '').trim()
            : '';
        if (!fileId) {
          this.promiseImageUrl = '';
          return;
        }
        if (fileId.startsWith('cloud://')) {
          /* temp link removed */
          const file = ($1 || [])[0] || {};
          this.promiseImageUrl = file.tempFileURL || fileId;
          return;
        }
        this.promiseImageUrl = fileId;
      } catch (e) {
        this.promiseImageUrl = '';
        console.log('加载承诺书图片失败');
      }
    },
    onTouchStart(type, e) {
      const p = e.touches[0];
      if (!p) return;
      if (type === 'personal') {
        this.personalLastPoint = { x: p.x, y: p.y };
        this.hasPersonalSigned = true;
        return;
      }
      this.guardianLastPoint = { x: p.x, y: p.y };
      this.hasGuardianSigned = true;
    },
    onTouchMove(type, e) {
      const p = e.touches[0];
      if (!p) return;
      const isPersonal = type === 'personal';
      const ctx = isPersonal ? this.personalCtx : this.guardianCtx;
      const lastPoint = isPersonal ? this.personalLastPoint : this.guardianLastPoint;
      if (!ctx || !lastPoint) return;
      ctx.beginPath();
      ctx.moveTo(lastPoint.x, lastPoint.y);
      ctx.lineTo(p.x, p.y);
      ctx.stroke();
      ctx.draw(true);
      if (isPersonal) {
        this.personalLastPoint = { x: p.x, y: p.y };
      } else {
        this.guardianLastPoint = { x: p.x, y: p.y };
      }
    },
    onTouchEnd(type) {
      if (type === 'personal') {
        this.personalLastPoint = null;
      } else {
        this.guardianLastPoint = null;
      }
    },
    clearSigns() {
      [this.personalCtx, this.guardianCtx].forEach((ctx) => {
        if (!ctx) return;
        ctx.clearRect(0, 0, 10000, 10000);
        ctx.draw();
      });
      this.hasPersonalSigned = false;
      this.hasGuardianSigned = false;
      this.personalLastPoint = null;
      this.guardianLastPoint = null;
    },
    async saveAndNext() {
      if (!this.hasPersonalSigned || !this.hasGuardianSigned) {
        uni.showToast({ title: this.$t('register.sign_must'), icon: 'none' });
        return;
      }
      if (this.saving) return;
      this.saving = true;
      try {
        const personalTempRes = await new Promise((resolve, reject) => {
          uni.canvasToTempFilePath(
            {
              canvasId: 'personalSignCanvas',
              fileType: 'png',
              quality: 1,
              success: resolve,
              fail: reject,
            },
            this
          );
        });
        const guardianTempRes = await new Promise((resolve, reject) => {
          uni.canvasToTempFilePath(
            {
              canvasId: 'personalGuardianSignCanvas',
              fileType: 'png',
              quality: 1,
              success: resolve,
              fail: reject,
            },
            this
          );
        });

        const uploadPersonalRes = await uploadFile(personalTempRes.tempFilePath);
        const uploadGuardianRes = await uploadFile(guardianTempRes.tempFilePath);

        const cached =
          uni.getStorageSync('register_commitment_signatures') || {};
        uni.setStorageSync('register_commitment_signatures', {
          ...cached,
          personal_promise_signature: uploadPersonalRes.data.url,
          personal_guardian_signature: uploadGuardianRes.data.url,
        });

        uni.redirectTo({ url: '/pages/register/promise-health' });
      } catch (e) {
        console.error('保存个人承诺签名失败', e);
        uni.showToast({ title: this.$t('register.save_failed'), icon: 'none' });
      }
      this.saving = false;
    },
  },
};
</script>

<style>
.sign-canvas {
  width: 100%;
  height: 360rpx;
  border: 1px dashed #d1d5db;
  border-radius: 12rpx;
  background: #fff;
}

.promise-image {
  width: 100%;
  border-radius: 12rpx;
}
</style>
