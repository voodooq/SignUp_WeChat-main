<template>
  <view class="min-h-screen bg-gray-50 px-2 py-4">
    <view v-if="loading" class="text-center py-16">
      <text class="text-gray-400 text-sm">{{ $t('common.loading') }}</text>
    </view>

    <view v-else-if="!ticket" class="text-center py-16">
      <text class="block text-gray-300 text-5xl mb-4">🎫</text>
      <text class="block text-gray-400 text-sm">{{ $t('ticket.no_ticket') }}</text>
    </view>

    <view v-else>
      <!-- 准考证卡片（横向可滚动） -->
      <scroll-view
        scroll-x
        class="ticket-scroll"
        :show-scrollbar="false"
        enable-flex
      >
        <view class="ticket-card-wrap">
          <view class="bg-white rounded-xl overflow-hidden ticket-card">
            <!-- 顶部标题 -->
            <view class="py-4 px-4 text-center border-b-2 border-gray-900">
              <text class="text-gray-500 text-xs block">
                {{ eventTitle || (lang === 'zh' ? '晟鲸体育赛事' : 'SJ Sports Event') }}
              </text>
              <text class="text-gray-900 font-bold text-xl block mt-1">
                {{ $t('ticket.card_title') }}
              </text>
            </view>

            <!-- 个人信息表格 -->
            <view class="p-2">
              <view class="ticket-main">
                <view class="ticket-info">
                  <view class="ticket-row ticket-row-compact">
                    <text class="ticket-label">{{ $t('ticket.test_center') }}</text>
                    <text class="ticket-value">{{ eventLocation || ticket.event_location || '-' }}</text>
                  </view>
                  <view class="ticket-row ticket-row-compact">
                    <text class="ticket-label">{{ $t('ticket.ticket_no') }}</text>
                    <text class="ticket-value font-bold">
                      {{ ticket.ticket_no }}
                    </text>
                  </view>
                  <view class="ticket-row ticket-row-compact">
                    <text class="ticket-label">{{ $t('ticket.phone') }}</text>
                    <text class="ticket-value">{{ ticket.phone || '-' }}</text>
                  </view>
                  <view class="ticket-row ticket-row-compact">
                    <text class="ticket-label">{{ $t('ticket.name') }}</text>
                    <text class="ticket-value">{{ ticket.name }}</text>
                  </view>
                  <view class="ticket-row ticket-row-compact">
                    <text class="ticket-label">{{ $t('ticket.gender') }}</text>
                    <text class="ticket-value">
                      {{ ticket.gender === 'male' ? $t('register.gender_male') : $t('register.gender_female') }}
                    </text>
                  </view>
                </view>

                <view class="ticket-avatar-wrap">
                  <image
                    v-if="ticketAvatarUrl"
                    class="ticket-avatar"
                    :src="ticketAvatarUrl"
                    mode="aspectFill"
                  />
                  <view
                    v-else
                    class="ticket-avatar ticket-avatar-placeholder"
                    @tap="chooseTicketAvatar"
                  >
                    <text class="ticket-avatar-placeholder-text">
                      {{ $t('ticket.no_photo') }}
                    </text>
                    <text class="ticket-avatar-upload-text">{{ $t('ticket.upload_tip') }}</text>
                  </view>
                </view>
              </view>

              <view class="ticket-full-rows">
                <!-- <view class="ticket-row">
                  <text class="ticket-label">衣服尺码</text>
                  <text class="ticket-value">
                    {{ ticket.clothes_size || '-' }}
                  </text>
                </view> -->
                <view class="ticket-row">
                  <text class="ticket-label">{{ $t('ticket.school') }}</text>
                  <text class="ticket-value">{{ ticket.school }}</text>
                </view>
                <view class="ticket-row">
                  <text class="ticket-label">{{ $t('ticket.time') }}</text>
                  <text class="ticket-value">{{ eventDate || '-' }}</text>
                </view>
                <view class="ticket-row">
                  <text class="ticket-label">{{ $t('ticket.events') }}</text>
                  <text class="ticket-value">{{ ticket.event_name }}</text>
                </view>
                <view v-if="ticket.is_sports_talent" class="ticket-row">
                  <text class="ticket-label">{{ $t('ticket.talent') }}</text>
                  <text
                    class="ticket-value"
                    style="color: #dc2626; font-weight: bold"
                  >
                    {{ $t('register.sports_talent') }}
                  </text>
                </view>
              </view>
            </view>

            <!-- 条形码 -->
            <view class="px-4 pb-4 flex flex-col items-center">
              <Barcode
                :value="ticket.ticket_no"
                :width="260"
                :height="80"
                :showText="true"
                canvasId="ticketBarcode"
              />
            </view>

            <!-- 底部 -->
            <view class="px-4 py-3 text-center">
              <text class="text-gray-400 text-xs block">
                {{ $t('ticket.footer_tip1') }}
              </text>
              <text class="text-gray-400 text-xs block mt-1">
                {{ $t('ticket.footer_tip2') }}
              </text>
            </view>
          </view>
        </view>
      </scroll-view>

      <view
        v-if="ticket.payment_status === 'paid' && ticket.payment_order_no"
        class="mt-3 bg-white rounded-xl p-4"
      >
        <text class="text-gray-500 text-xs block">{{ $t('ticket.pay_no') }}</text>
        <text class="text-gray-900 text-sm block mt-1 break-all">
          {{ ticket.payment_order_no }}
        </text>
      </view>

      <!-- 保存用的隐藏 canvas（逻辑尺寸 375x600，实际绘制 3x） -->
      <canvas
        canvas-id="ticketCanvas"
        id="ticketCanvas"
        style="
          position: fixed;
          left: -9999px;
          top: 0;
          width: 375px;
          height: 600px;
        "
      ></canvas>

      <!-- 操作按钮 -->
      <view class="mt-4 bg-white rounded-xl py-3 text-center" @tap="saveTicket">
        <text class="text-gray-900 text-sm font-medium">{{ $t('ticket.save_btn') }}</text>
      </view>
    </view>
  </view>
</template>

<script>
import { useUserStore } from '@/services/store/user.js';
import Barcode from '@/components/Barcode.vue';
import { getSettings, getTicket, getMyRegistrations, updateAvatar } from '@/services/api/register-api.js';
import { uploadFile } from '@/services/api/request.js';

export default {
  components: { Barcode },
  data() {
    return {
      ticket: null,
      loading: false,
      ticketNo: '',
      eventTitle: '',
      eventLocation: '',
      eventDate: '',
      lang: 'zh'
    };
  },
  computed: {
    ticketAvatarUrl() {
      if (!this.ticket) return '';
      return this.ticket.avatar_temp_url || this.ticket.avatar_url || '';
    },
  },
  onShow() {
    const userStore = useUserStore();
    this.lang = userStore.lang;
    uni.setNavigationBarTitle({
      title: this.$t('ticket.title')
    });
  },
  onLoad(options) {
    this.loadEventTitle();
    if (options.ticket_no) {
      this.ticketNo = options.ticket_no;
      this.loadTicket();
    } else {
      this.loadMyTicket();
    }
  },
  methods: {
    async loadEventTitle() {
      try {
        const res = await getSettings();
        if (res.code === 200) {
          this.eventTitle = (res.data && res.data.event_title) || '';
          this.eventLocation = (res.data && res.data.event_location) || '';
          this.eventDate = (res.data && res.data.event_date) || '';
        }
      } catch (e) {
        this.eventTitle = '';
        this.eventLocation = '';
        this.eventDate = '';
      }
    },
    async loadTicket() {
      this.loading = true;
      try {
        const res = await getTicket(this.ticketNo);
        if (res.code === 200) {
          this.ticket = res.data;
          await this.resolveTicketAvatarUrl();
        } else {
          uni.showToast({ title: res.message, icon: 'none' });
        }
      } catch (e) {
        console.error(e);
        uni.showToast({ title: this.$t('message.request_failed'), icon: 'none' });
      }
      this.loading = false;
    },
    async loadMyTicket() {
      this.loading = true;
      try {
        const res = await getMyRegistrations();
        if (res.code === 200 && res.data.length > 0) {
          const paid = res.data.find(
            (r) =>
              r.payment_status === 'paid' || r.payment_status === 'admin_free'
          );
          const item = paid || res.data[0];
          this.ticketNo = item.ticket_no;
          await this.loadTicket();
          return;
        }
      } catch (e) {
        console.error(e);
      }
      this.loading = false;
    },
    async resolveTicketAvatarUrl() {
      if (!this.ticket || !this.ticket.avatar_url) return;
      this.ticket.avatar_temp_url = this.ticket.avatar_url;
    },
    getLocalFilePath(url) {
      return new Promise((resolve) => {
        if (!url) {
          resolve('');
          return;
        }
        if (url.startsWith('http://') || url.startsWith('https://')) {
          uni.downloadFile({
            url,
            success: (res) => {
              if (res.statusCode === 200 && res.tempFilePath) {
                resolve(res.tempFilePath);
                return;
              }
              resolve('');
            },
            fail: () => resolve(''),
          });
          return;
        }
        resolve(url);
      });
    },
    chooseTicketAvatar() {
      if (!this.ticket || !this.ticket.ticket_no) return;
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
            const avatarUrl = uploadRes.url || '';
            const saveRes = await updateAvatar({
              ticket_no: this.ticket.ticket_no,
              avatar_url: avatarUrl,
            });

            if (saveRes.code !== 200) {
              throw new Error(saveRes.message || '保存头像失败');
            }

            this.ticket.avatar_url = avatarUrl;
            this.ticket.avatar_temp_url = filePath;
            uni.hideLoading();
            uni.showToast({ title: this.$t('message.login_success'), icon: 'success' }); // Fixme: use correct msg
          } catch (e) {
            uni.hideLoading();
            console.error('上传头像失败:', e);
            uni.showToast({ title: this.$t('message.upload_failed'), icon: 'none' });
          }
        },
      });
    },
    async saveTicket() {
      uni.showLoading({ title: this.$t('ticket.saving') });
      const t = this.ticket;
      await this.resolveTicketAvatarUrl();
      const avatarPath = await this.getLocalFilePath(
        t.avatar_temp_url || t.avatar_url || ''
      );
      const ctx = uni.createCanvasContext('ticketCanvas', this);
      const W = 375,
        H = 600;
      const DPR = 3;

      // 缩放到 3x 绘制，输出高清
      ctx.scale(1, 1);

      // 白色背景
      ctx.setFillStyle('#f9fafb');
      ctx.fillRect(0, 0, W, H);

      // 卡片背景
      const cardX = 26,
        cardY = 16,
        cardW = W - 52;
      const cardH = H - 48;
      ctx.setFillStyle('#ffffff');
      ctx.setShadow(0, 1, 8, 'rgba(0,0,0,0.06)');
      ctx.fillRect(cardX, cardY, cardW, cardH);
      ctx.setShadow(0, 0, 0, 'transparent');

      // 标题区
      ctx.setFillStyle('#6b7280');
      ctx.setFontSize(11);
      ctx.setTextAlign('center');
      ctx.fillText(this.eventTitle || (this.lang === 'zh' ? '晟鲸体育赛事' : 'SJ Sports Event'), W / 2, cardY + 28);
      ctx.setFillStyle('#111827');
      ctx.setFontSize(20);
      ctx.fillText(this.$t('ticket.card_title'), W / 2, cardY + 54);

      // 分割线
      ctx.setStrokeStyle('#111827');
      ctx.setLineWidth(2);
      ctx.beginPath();
      ctx.moveTo(cardX, cardY + 66);
      ctx.lineTo(cardX + cardW, cardY + 66);
      ctx.stroke();

      // 信息行（上半部分与头像并排，下半部分全宽）
      const topRows = [
        [this.$t('ticket.test_center'), this.eventLocation || t.event_location || '-'],
        [this.$t('ticket.ticket_no'), t.ticket_no],
        [this.$t('ticket.name'), t.name],
        [this.$t('ticket.gender'), t.gender === 'male' ? this.$t('register.gender_male') : this.$t('register.gender_female')],
        [this.$t('ticket.phone'), t.phone || '-'],
      ];
      const bottomRows = [
        // ['衣服尺码', t.clothes_size || '-'],
        [this.$t('ticket.school'), t.school],
        [this.$t('ticket.time'), this.eventDate || '-'],
        [this.$t('ticket.events'), t.event_name],
      ];
      if (t.is_sports_talent) {
        bottomRows.push([this.$t('ticket.talent'), this.$t('register.sports_talent')]);
      }

      const startY = cardY + 86;
      const rowH = 32;
      const avatarW = 116;
      const avatarH = topRows.length * rowH + 36;
      const avatarX = cardX + cardW - 16 - avatarW;
      const avatarY = startY - 8;
      const valueX = cardX + 82;
      const rowLineRight = avatarX - 12;
      ctx.setTextAlign('left');

      topRows.forEach((row, i) => {
        const y = startY + i * rowH;
        if (i > 0) {
          ctx.setStrokeStyle('#f3f4f6');
          ctx.setLineWidth(0.5);
          ctx.beginPath();
          ctx.moveTo(cardX + 16, y - 6);
          ctx.lineTo(rowLineRight, y - 6);
          ctx.stroke();
        }
        ctx.setFillStyle('#6b7280');
        ctx.setFontSize(13);
        ctx.fillText(row[0], cardX + 16, y + 12);
        if (row[0].includes('特') && row[0].includes('生')) {
          ctx.setFillStyle('#dc2626');
        } else {
          ctx.setFillStyle('#111827');
        }
        ctx.setFontSize(13);
        ctx.fillText(row[1], valueX, y + 12);
      });

      const bottomStartY = startY + topRows.length * rowH;
      bottomRows.forEach((row, i) => {
        const y = bottomStartY + i * rowH;
        ctx.setStrokeStyle('#f3f4f6');
        ctx.setLineWidth(0.5);
        ctx.beginPath();
        ctx.moveTo(cardX + 16, y - 6);
        ctx.lineTo(cardX + cardW - 16, y - 6);
        ctx.stroke();

        ctx.setFillStyle('#6b7280');
        ctx.setFontSize(13);
        ctx.fillText(row[0], cardX + 16, y + 12);

        if (row[0].includes('特') && row[0].includes('生')) {
          ctx.setFillStyle('#dc2626');
        } else {
          ctx.setFillStyle('#111827');
        }
        ctx.setFontSize(13);
        ctx.fillText(row[1], valueX, y + 12);
      });

      ctx.setFillStyle('#f9fafb');
      ctx.fillRect(avatarX, avatarY, avatarW, avatarH);
      ctx.setStrokeStyle('#d1d5db');
      ctx.setLineWidth(1);
      ctx.strokeRect(avatarX, avatarY, avatarW, avatarH);
      if (avatarPath) {
        ctx.drawImage(
          avatarPath,
          avatarX + 1,
          avatarY + 1,
          avatarW - 2,
          avatarH - 2
        );
      } else {
        ctx.setFillStyle('#9ca3af');
        ctx.setFontSize(11);
        ctx.setTextAlign('center');
        ctx.fillText(
          this.$t('register.not_uploaded').split('')[0] || 'No',
          avatarX + avatarW / 2,
          avatarY + avatarH / 2 - 4
        );
        ctx.fillText(this.$t('register.not_uploaded').split('')[1] || 'Photo', avatarX + avatarW / 2, avatarY + avatarH / 2 + 14);
      }

      // ====== 绘制条形码 ======
      const totalRows = topRows.length + bottomRows.length;
      const barcodeY = startY + totalRows * rowH + 12;
      const barcodeW = 260,
        barcodeH = 60;
      const barcodeX = (W - barcodeW) / 2;
      this.drawBarcode128B(
        ctx,
        t.ticket_no,
        barcodeX,
        barcodeY,
        barcodeW,
        barcodeH
      );

      // 条形码下方文字
      ctx.setFillStyle('#111827');
      ctx.setFontSize(12);
      ctx.setTextAlign('center');
      ctx.fillText(t.ticket_no, W / 2, barcodeY + barcodeH + 16);

      // 底部提示
      const footerY = cardY + cardH - 54;
      ctx.setFillStyle('#f9fafb');
      ctx.fillRect(cardX, footerY - 4, cardW, 58);
      ctx.setFillStyle('#9ca3af');
      ctx.setFontSize(10);
      ctx.setTextAlign('center');
      ctx.fillText(this.$t('ticket.footer_tip1'), W / 2, footerY + 10);
      ctx.fillText(this.$t('ticket.footer_tip2'), W / 2, footerY + 26);
      ctx.fillText(this.$t('ticket.footer_tip3'), W / 2, footerY + 42);

      ctx.draw(false, () => {
        setTimeout(() => {
          uni.canvasToTempFilePath(
            {
              canvasId: 'ticketCanvas',
              width: W,
              height: H,
              destWidth: W * DPR,
              destHeight: H * DPR,
              fileType: 'png',
              quality: 1,
              success: (res) => {
                uni.hideLoading();
                uni.saveImageToPhotosAlbum({
                  filePath: res.tempFilePath,
                  success: () => {
                    uni.showToast({ title: this.$t('ticket.save_success'), icon: 'success' });
                  },
                  fail: (err) => {
                    if (err.errMsg && err.errMsg.includes('auth deny')) {
                      uni.showModal({
                        title: this.$t('common.info'),
                        content: this.$t('ticket.allow_save'),
                        confirmText: this.$t('ticket.go_setting'),
                        success: (modalRes) => {
                          if (modalRes.confirm) {
                            uni.openSetting();
                          }
                        },
                      });
                    } else {
                      uni.showToast({ title: this.$t('ticket.save_failed'), icon: 'none' });
                    }
                  },
                });
              },
              fail: () => {
                uni.hideLoading();
                uni.showToast({ title: '生成图片失败', icon: 'none' });
              },
            },
            this
          );
        }, 500);
      });
    },
    drawBarcode128B(ctx, text, x, y, w, h) {
      const CODE128B_START = 104;
      const CODE128_STOP = 106;
      const CODE128_PATTERNS = [
        '11011001100',
        '11001101100',
        '11001100110',
        '10010011000',
        '10010001100',
        '10001001100',
        '10011001000',
        '10011000100',
        '10001100100',
        '11001001000',
        '11001000100',
        '11000100100',
        '10110011100',
        '10011011100',
        '10011001110',
        '10111001100',
        '10011101100',
        '10011100110',
        '11001110010',
        '11001011100',
        '11001001110',
        '11011100100',
        '11001110100',
        '11101101110',
        '11101001100',
        '11100101100',
        '11100100110',
        '11101100100',
        '11100110100',
        '11100110010',
        '11011011000',
        '11011000110',
        '11000110110',
        '10100011000',
        '10001011000',
        '10001000110',
        '10110001000',
        '10001101000',
        '10001100010',
        '11010001000',
        '11000101000',
        '11000100010',
        '10110111000',
        '10110001110',
        '10001101110',
        '10111011000',
        '10111000110',
        '10001110110',
        '11101110110',
        '11010001110',
        '11000101110',
        '11011101000',
        '11011100010',
        '11011101110',
        '11101011000',
        '11101000110',
        '11100010110',
        '11101101000',
        '11101100010',
        '11100011010',
        '11101111010',
        '11001000010',
        '11110001010',
        '10100110000',
        '10100001100',
        '10010110000',
        '10010000110',
        '10000101100',
        '10000100110',
        '10110010000',
        '10110000100',
        '10011010000',
        '10011000010',
        '10000110100',
        '10000110010',
        '11000010010',
        '11001010000',
        '11110111010',
        '11000010100',
        '10001111010',
        '10100111100',
        '10010111100',
        '10010011110',
        '10111100100',
        '10011110100',
        '10011110010',
        '11110100100',
        '11110010100',
        '11110010010',
        '11011011110',
        '11011110110',
        '11110110110',
        '10101111000',
        '10100011110',
        '10001011110',
        '10111101000',
        '10111100010',
        '11110101000',
        '11110100010',
        '10111011110',
        '10111101110',
        '11101011110',
        '11110101110',
        '11010000100',
        '11010010000',
        '11010011100',
        '1100011101011',
      ];

      let codes = [CODE128B_START];
      let checksum = CODE128B_START;
      for (let i = 0; i < text.length; i++) {
        const code = text.charCodeAt(i) - 32;
        codes.push(code);
        checksum += code * (i + 1);
      }
      codes.push(checksum % 103);
      codes.push(CODE128_STOP);

      let pattern = '';
      for (const c of codes) {
        pattern += CODE128_PATTERNS[c];
      }

      // 白色底
      ctx.setFillStyle('#ffffff');
      ctx.fillRect(x, y, w, h);

      // 绘制条码
      const barW = w / pattern.length;
      ctx.setFillStyle('#000000');
      for (let i = 0; i < pattern.length; i++) {
        if (pattern[i] === '1') {
          ctx.fillRect(x + i * barW, y, barW + 0.5, h);
        }
      }
    },
  },
};
</script>

<style>
.ticket-card {
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.08);
}
.ticket-scroll {
  width: 100%;
}
.ticket-card-wrap {
  min-width: 680rpx;
  padding: 0 8rpx;
  box-sizing: border-box;
}
.ticket-row {
  display: flex;
  align-items: center;
  padding: 16rpx 0;
  border-bottom: 1rpx solid #f3f4f6;
}
.ticket-main {
  display: flex;
  align-items: flex-start;
  margin-bottom: 10rpx;
}
.ticket-info {
  flex: 1;
  min-width: 0;
  padding-right: 22rpx;
}
.ticket-full-rows {
  width: 100%;
}
.ticket-full-rows .ticket-row:first-child {
  border-top: 1rpx solid #f3f4f6;
}
.ticket-row:last-child {
  border-bottom: none;
}
.ticket-row-compact {
  padding: 14rpx 0;
}
.ticket-label {
  width: 132rpx;
  font-size: 28rpx;
  color: #6b7280;
  flex-shrink: 0;
}
.ticket-value {
  flex: 1;
  font-size: 28rpx;
  color: #111827;
}
.ticket-avatar-wrap {
  width: 200rpx;
  flex-shrink: 0;
  padding-top: 8rpx;
  margin-left: -2rpx;
}
.ticket-avatar {
  width: 200rpx;
  height: 268rpx;
  border-radius: 12rpx;
  border: 1rpx solid #d1d5db;
  background: #f9fafb;
}
.ticket-avatar-placeholder {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
}
.ticket-avatar-placeholder-text {
  font-size: 22rpx;
  color: #9ca3af;
}
.ticket-avatar-upload-text {
  margin-top: 8rpx;
  font-size: 20rpx;
  color: #3b82f6;
}
</style>
