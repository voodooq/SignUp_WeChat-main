/**
 * 支付相关 API
 */
import { POST, GET } from './request';

/** 创建支付订单 */
export function createOrder(registrationId) {
  return POST('/api/payment/create-order', { registration_id: registrationId });
}

/** 模拟支付 */
export function mockPay(registrationId) {
  return POST('/api/payment/mock-pay', { registration_id: registrationId });
}

/** 查询订单状态 */
export function queryOrder(registrationId) {
  return POST('/api/payment/query-order', { registration_id: registrationId });
}

/** 获取订阅配置 */
export function getSubscribeConfig() {
  return GET('/api/payment/subscribe-config');
}
