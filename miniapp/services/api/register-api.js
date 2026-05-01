/**
 * 报名相关 API
 */
import { POST, GET } from './request';

/** 提交报名 */
export function submitRegistration(data) {
  return POST('/api/register/submit', data);
}

/** 更新头像 */
export function updateAvatar(data) {
  return POST('/api/register/update-avatar', data);
}

/** 检查重复报名 */
export function checkDuplicate(idCard) {
  return POST('/api/register/check-duplicate', { id_card: idCard });
}

/** 获取赛事设置（无需登录） */
export function getSettings() {
  return GET('/api/register/settings');
}

/** 获取参赛须知图片（无需登录） */
export function getNoticeImages() {
  return GET('/api/register/notice-images');
}

/** 获取我的报名记录 */
export function getMyRegistrations() {
  return GET('/api/register/my-registrations');
}

/** 获取证书信息 */
export function getTicket(ticketNo) {
  return GET(`/api/register/ticket?ticket_no=${ticketNo}`);
}

/** 查询我的成绩 */
export function getMyScores() {
  return GET('/api/register/my-scores');
}

/** 按证书编号查成绩 */
export function getScoresByTicketNo(ticketNo) {
  return GET(`/api/register/scores-by-ticket?ticket_no=${ticketNo}`);
}

/** 获取排行榜数据 */
export function getLeaderboard(compId) {
  return GET(`/api/register/leaderboard/${compId}`);
}
