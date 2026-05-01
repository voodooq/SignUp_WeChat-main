import { GET, POST } from './request.js';

/**
 * 获取场馆列表
 */
export function getGymList(params = {}) {
  let url = '/api/gym/list?';
  const query = [];
  if (params.lng) query.push(`lng=${params.lng}`);
  if (params.lat) query.push(`lat=${params.lat}`);
  if (params.sort_by) query.push(`sort_by=${params.sort_by}`);
  return GET(url + query.join('&'));
}

/**
 * 获取场馆详情
 * @param {string} id 场馆ID
 */
export function getGymDetail(id) {
  return GET(`/api/gym/${id}`);
}

/**
 * 提交完攀记录
 */
export function submitAttempt(data) {
  return POST('/api/gym/attempt', data);
}

/**
 * 获取线路评价列表
 */
export function getRouteAttempts(routeId) {
  return GET(`/api/gym/route/${routeId}/attempts`);
}
