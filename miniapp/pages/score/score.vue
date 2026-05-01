<template>
	<view class="score-page bg-gray-50">
		<view class="px-4 pt-3 pb-2 bg-gray-50">
			<view class="bg-white rounded-xl p-3 shadow-sm">
				<view class="flex items-center bg-gray-100 rounded-lg px-3 py-2">
					<input
						class="flex-1 text-sm"
						v-model="ticketNoQuery"
						:placeholder="$t('score.search_placeholder')"
						confirm-type="search"
						@input="onTicketInput"
						@confirm="searchByTicketNo"
					/>
					<text v-if="ticketNoQuery" class="text-gray-400 text-xs ml-2" @tap="clearTicketNo">{{ $t('score.clear') }}</text>
				</view>
				<view class="flex mt-2">
					<view class="w-full bg-blue-500 rounded-lg py-2 text-center" @tap="searchByTicketNo">
						<text class="text-white text-xs">{{ $t('score.search_by_ticket') }}</text>
					</view>
				</view>
			</view>
		</view>

		<view v-if="loading" class="flex justify-center items-center pt-24">
			<text class="text-gray-400 text-sm">{{ $t('common.loading') }}</text>
		</view>

		<view
			v-else-if="scoreItems.length === 0"
			class="flex flex-col items-center pt-24 px-6"
		>
			<text class="iconfont icon-trophy text-gray-300 text-5xl mb-4"></text>
			<text class="text-gray-500 text-base font-medium mb-2">{{ $t('score.no_score') }}</text>
			<text class="text-gray-400 text-xs text-center px-4">{{ $t('score.my_score_tip') }}</text>
		</view>

		<scroll-view v-else scroll-y class="score-list px-4 py-3 box-border">
			<view
				v-for="item in scoreItems"
				:key="item._id || item.ticket_no"
				class="bg-white rounded-xl shadow-sm p-4 mb-3"
			>
				<view class="flex items-center flex-wrap">
					<text class="text-gray-800 text-base font-semibold">{{ item.name || '-' }}</text>
					<text class="text-gray-500 text-sm ml-2">{{ item.gender === 'male' ? $t('register.gender_male') : item.gender === 'female' ? $t('register.gender_female') : '-' }}</text>
					<text class="text-gray-400 text-sm ml-2">{{ item.phone || '-' }}</text>
				</view>
				<text class="text-gray-500 text-sm block mt-1">{{ $t('ticket.ticket_no') }}：{{ item.ticket_no || '-' }}</text>
				<text class="text-gray-500 text-sm block mt-1">{{ $t('ticket.events') }}：{{ item.event_name || '-' }}</text>
				<text class="text-orange-600 text-sm block mt-1">{{ $t('score.total') }}：{{ calcTotalPoints(item) }}</text>

				<view class="mt-3 pt-2 border-t border-gray-100">
					<view v-if="!item.event_scores || item.event_scores.length === 0" class="text-gray-400 text-sm">
						{{ $t('score.no_match') }}
					</view>
					<view v-else>
						<view
							v-for="(score, idx) in item.event_scores"
							:key="(item.ticket_no || item._id || idx) + '-' + score.event_name"
							class="flex items-center justify-between py-1"
						>
							<text class="text-gray-700 text-sm">{{ score.event_name || '-' }}</text>
							<view class="flex items-center">
								<text class="text-blue-600 font-medium text-sm mr-3">{{ $t('score.score') }}：{{ score.score || '-' }}</text>
								<text class="text-orange-600 font-medium text-sm">{{ $t('score.points') }}：{{ score.points || '-' }}</text>
							</view>
						</view>
					</view>
				</view>
			</view>
		</scroll-view>
	</view>
</template>

<script>
import { useUserStore } from '@/services/store/user.js';
import { getMyScores, getScoresByTicketNo } from '@/services/api/register-api.js';

export default {
	data() {
		return {
			loading: true,
			scoreItems: [],
			ticketNoQuery: '',
		};
	},
	onShow() {
		uni.setNavigationBarTitle({
			title: this.$t('score.title')
		});
	},
	onLoad() {
		this.loadMyScores();
	},
	methods: {
		clearTicketNo() {
			this.ticketNoQuery = '';
			this.loadMyScores();
		},
		onTicketInput(e) {
			const value = String((e && e.detail && e.detail.value) || this.ticketNoQuery || '').trim();
			if (!value) {
				this.loadMyScores();
			}
		},
		calcTotalPoints(item) {
			const scores = item?.event_scores || [];
			let total = 0;
			for (const s of scores) {
				const num = Number(s?.points);
				if (!Number.isNaN(num)) total += num;
			}
			return total;
		},
		async loadMyScores() {
			this.loading = true;
			try {
				const userStore = useUserStore();
				if (!userStore.isLoggedIn || !userStore.userInfo?.openid) {
					try {
						await userStore.login();
					} catch (e) {}
				}

				const openid = userStore.userInfo?.openid || userStore.openid || '';
				if (!openid) {
					uni.showToast({ title: this.$t('message.login_expired'), icon: 'none' });
					return;
				}

				const myScoresRes = await getMyScores();

				if (myScoresRes?.code === 200) {
					this.scoreItems = myScoresRes.data?.items || [];
				} else {
					this.scoreItems = [];
					console.warn('我的成绩查询失败:', myScoresRes?.message || myScoresRes);
				}
			} catch (e) {
				console.error('查询成绩失败:', e);
				uni.showToast({ title: this.$t('message.request_failed'), icon: 'none' });
			} finally {
				this.loading = false;
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
				const res = await getScoresByTicketNo(ticketNo);

				if (res?.code === 200 && res.data?.item) {
					this.scoreItems = [res.data.item];
				} else {
					this.scoreItems = [];
					uni.showToast({ title: res?.message || this.$t('score.no_match'), icon: 'none' });
				}
			} catch (e) {
				console.error('按证书查询成绩失败:', e);
				uni.showToast({ title: this.$t('message.request_failed'), icon: 'none' });
			} finally {
				this.loading = false;
			}
		}
	}
};
</script>

<style>
page {
  height: 100%;
}
.score-page {
  height: 100%;
  display: flex;
  flex-direction: column;
}
.score-list {
  flex: 1;
  min-height: 0;
}
</style>