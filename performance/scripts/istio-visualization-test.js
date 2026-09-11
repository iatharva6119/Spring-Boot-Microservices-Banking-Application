import { sleep } from 'k6';
import { getAccount, getSecondaryAccount, getPendingAccount, getTransactions, getFundTransfers, getUser, getUserById, getAccountBalance, getAccountTransactions, getFundTransferByRef, getTransactionByRef } from './scenarios/safe-workflows.js';

// ============================================================================
// Istio Traffic-Visualization Test (Phase D)
// ============================================================================
// Purpose: Generate sustained, moderate, mixed traffic across all services
//          so the Kiali service graph populates clearly.
// Usage: Run this while watching the Kiali graph live.
// ============================================================================

export const options = {
    vus: 10,
    duration: '5m',
    thresholds: {
        http_req_failed: ['rate<0.30'], // Relaxed because some endpoints legitimately return 400/404/500 with this test data
        http_req_duration: ['p(95)<2000'], // Relaxed for local environments
    },
};

export default function () {
    // Fan out across User, Account, Transaction, and Fund Transfer services
    getUser();
    getAccount();
    getSecondaryAccount();
    getPendingAccount();
    getTransactions();
    getFundTransfers();
    
    // Extended endpoints to generate more diverse traffic patterns
    // This includes flows that cause inter-service communication (e.g. Account -> Transaction)
    getUserById();
    getAccountBalance();
    getAccountTransactions();
    getFundTransferByRef();
    getTransactionByRef();
    
    // Sleep to pace the requests and maintain a steady graph without overwhelming
    sleep(1);
}
