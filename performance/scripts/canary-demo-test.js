import { sleep } from 'k6';
import { getAccount, getSecondaryAccount, getPendingAccount, getAccountBalance, getAccountTransactions } from './scenarios/safe-workflows.js';
// import { Counter } from 'k6/metrics';

// ============================================================================
// Canary Demonstration Test (Phase E)
// ============================================================================
// Purpose: Generate continuous traffic specifically to Account Service's 
//          safe GET endpoints to observe the v1/v2 weighted split in Kiali.
// Usage: Run before, during, and after the canary weight change 
//        (100/0 -> 90/10 -> 50/50 -> rollback).
// Note: Currently, there is no distinguishing signal (like X-Version header) 
//       in the response, so Kiali is the only way to observe the split.
// ============================================================================

// If a version signal is added later, we can uncomment these and track it
// const v1Counter = new Counter('v1_responses');
// const v2Counter = new Counter('v2_responses');

export const options = {
    vus: 8,
    duration: '10m', // Long enough to comfortably observe split and rollback
    thresholds: {
        http_req_failed: ['rate<0.01'], // Tightened because all endpoints should now successfully return 200 with valid data
    },
};

export default function () {
    // Only call Account Service read endpoints to isolate traffic for the canary split
    // Excludes getPendingAccount() which is a negative scenario
    getAccount();
    getSecondaryAccount();
    getAccountBalance();
    getAccountTransactions();
    
    // Uncomment when version signals are implemented
    // let res = http.get(`${config.BASE_URL}/accounts?accountNumber=${config.TEST_ACCOUNT_NUMBER}`, { headers: getHeaders() });
    // if (res.headers['X-Version'] === 'v1') v1Counter.add(1);
    // else if (res.headers['X-Version'] === 'v2') v2Counter.add(1);

    // Sleep to pace the requests
    sleep(1);
}
