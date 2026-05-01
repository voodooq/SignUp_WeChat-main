/**
 * 管理员相关 API
 */
import { GET, POST, PUT, DELETE } from './request';

// ========== 报名管理 ==========
export function searchRegistrations(params = {}) {
  const qs = new URLSearchParams(params).toString();
  return GET(`/api/admin/registrations?${qs}`);
}

export function getRegistrationDetail(id) {
  return GET(`/api/admin/registration/${id}`);
}

export function getRegistrationStats() {
  return GET('/api/admin/registration-stats');
}

export function manualRegister(data) {
  return POST('/api/admin/manual-register', data);
}

// ========== 项目管理 ==========
export function listEvents() {
  return GET('/api/admin/events');
}

export function addEvent(data) {
  return POST('/api/admin/events', data);
}

export function updateEvent(id, data) {
  return PUT(`/api/admin/events/${id}`, data);
}

export function deleteEvent(id) {
  return DELETE(`/api/admin/events/${id}`);
}

// ========== 轮播图管理 ==========
export function listBanners(position) {
  return GET(`/api/admin/banners${position ? '?position=' + position : ''}`);
}

export function addBanner(data) {
  return POST('/api/admin/banners', data);
}

export function updateBanner(id, data) {
  return PUT(`/api/admin/banners/${id}`, data);
}

export function deleteBanner(id) {
  return DELETE(`/api/admin/banners/${id}`);
}

// ========== 赛事图片管理 ==========
export function listEventImages() {
  return GET('/api/admin/event-images');
}

export function addEventImage(data) {
  return POST('/api/admin/event-images', data);
}

export function updateEventImage(id, data) {
  return PUT(`/api/admin/event-images/${id}`, data);
}

export function deleteEventImage(id) {
  return DELETE(`/api/admin/event-images/${id}`);
}

// ========== 须知图片管理 ==========
export function listNoticeImages() {
  return GET('/api/admin/notice-images');
}

export function addNoticeImage(data) {
  return POST('/api/admin/notice-images', data);
}

export function updateNoticeImage(id, data) {
  return PUT(`/api/admin/notice-images/${id}`, data);
}

export function deleteNoticeImage(id) {
  return DELETE(`/api/admin/notice-images/${id}`);
}

export function reorderNoticeImages(orderedIds) {
  return POST('/api/admin/notice-images/reorder', { ordered_ids: orderedIds });
}

// ========== 设置管理 ==========
export function getSettings() {
  return GET('/api/admin/settings');
}

export function updateSettings(settings) {
  return PUT('/api/admin/settings', { settings });
}

// ========== 学校管理 ==========
export function listSchools() {
  return GET('/api/admin/schools');
}

export function addSchool(data) {
  return POST('/api/admin/schools', data);
}

export function updateSchool(id, data) {
  return PUT(`/api/admin/schools/${id}`, data);
}

export function deleteSchool(id) {
  return DELETE(`/api/admin/schools/${id}`);
}

// ========== 成绩管理 ==========
export function importScores(scores) {
  return POST('/api/admin/scores/import', { scores });
}

export function clearScores() {
  return DELETE('/api/admin/scores');
}

export function listScores(params = {}) {
  const qs = new URLSearchParams(params).toString();
  return GET(`/api/admin/scores?${qs}`);
}

export function exportStudents() {
  return GET('/api/admin/export-students');
}
