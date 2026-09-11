import http from 'k6/http';
import { check } from 'k6';
import { config, getHeaders } from '../../config/test-config.example.js';

// Safe GET requests identified from source code analysis.
// Destructive endpoints (POST/PUT/DELETE) like fund-transfers are explicitly excluded.

export function getUser() {
    let res = http.get(`${config.BASE_URL}/api/users`, { headers: getHeaders() });
    check(res, {
        'user-service status is 200': (r) => r.status === 200,
        'user-service responded within 2000ms': (r) => r.timings.duration < 2000,
    });
}

export function getAccount() {
    // Fixed: gateway route is /accounts (no /api prefix), param is accountNumber not accountId
    let res = http.get(`${config.BASE_URL}/accounts?accountNumber=${config.TEST_ACCOUNT_NUMBER}`, { headers: getHeaders() });
    check(res, {
        'account-service status is 200': (r) => r.status === 200,
    });
}

export function getSecondaryAccount() {
    let res = http.get(`${config.BASE_URL}/accounts?accountNumber=${config.SECONDARY_ACCOUNT_NUMBER}`, { headers: getHeaders() });
    check(res, {
        'account-service secondary status is 200': (r) => r.status === 200,
    });
}

export function getPendingAccount() {
    let res = http.get(`${config.BASE_URL}/accounts?accountNumber=${config.PENDING_ACCOUNT_NUMBER}`, { headers: getHeaders() });
    check(res, {
        'account-service pending status is 200': (r) => r.status === 200,
    });
}

export function getTransactions() {
    // Fixed: gateway route is /transactions (no /api prefix)
    let res = http.get(`${config.BASE_URL}/transactions?accountId=${config.TEST_ACCOUNT_NUMBER}`, { headers: getHeaders() });
    check(res, {
        'transaction-service status is 200': (r) => r.status === 200,
    });
}

export function getFundTransfers() {
    // Read-only endpoint to get transfer history. NEVER trigger POST /api/fund-transfers.
    // Fixed: using /fund-transfers without /api prefix for consistency with gateway routes
    let res = http.get(`${config.BASE_URL}/fund-transfers?accountId=${config.TEST_ACCOUNT_NUMBER}`, { headers: getHeaders() });
    check(res, {
        'fund-transfer status is 200': (r) => r.status === 200,
    });
}

// === NEW ENDPOINTS ===

export function getUserById() {
    let res = http.get(`${config.BASE_URL}/api/users/${config.TEST_USER_ID}`, { headers: getHeaders() });
    check(res, {
        'user-service get by id status is 200': (r) => r.status === 200,
    });
}

export function getAccountBalance() {
    let res = http.get(`${config.BASE_URL}/accounts/balance?accountNumber=${config.TEST_ACCOUNT_NUMBER}`, { headers: getHeaders() });
    check(res, {
        'account-service balance status is 200': (r) => r.status === 200,
    });
}

export function getAccountTransactions() {
    let res = http.get(`${config.BASE_URL}/accounts/${config.TEST_ACCOUNT_ID}/transactions`, { headers: getHeaders() });
    check(res, {
        'account-service transactions status is 200': (r) => r.status === 200,
    });
}

export function getFundTransferByRef() {
    let res = http.get(`${config.BASE_URL}/fund-transfers/${config.TEST_REFERENCE_ID}`, { headers: getHeaders() });
    check(res, {
        'fund-transfer by ref status is 200': (r) => r.status === 200,
    });
}

export function getTransactionByRef() {
    let res = http.get(`${config.BASE_URL}/transactions/${config.TEST_REFERENCE_ID}`, { headers: getHeaders() });
    check(res, {
        'transaction-service by ref status is 200': (r) => r.status === 200,
    });
}

export default function () {
    getUser();
    getAccount();
    getSecondaryAccount();
    getPendingAccount();
    getTransactions();
    getFundTransfers();
    getUserById();
    getAccountBalance();
    getAccountTransactions();
    getFundTransferByRef();
    getTransactionByRef();
}
