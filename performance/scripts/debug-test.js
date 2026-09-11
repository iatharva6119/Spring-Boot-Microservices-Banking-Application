import http from 'k6/http';
import { config, getHeaders } from '../config/test-config.example.js';

export default function () {
    console.log("Testing transaction-service GET /transactions");
    let res = http.get(`${config.BASE_URL}/transactions?accountId=${config.TEST_ACCOUNT_ID}`, { headers: getHeaders() });
    console.log(`Status: ${res.status}`);
    console.log(`Body: ${res.body}`);
    
    console.log("Testing account-service GET /accounts/{accountId}/transactions");
    let res2 = http.get(`${config.BASE_URL}/accounts/${config.TEST_ACCOUNT_ID}/transactions`, { headers: getHeaders() });
    console.log(`Status: ${res2.status}`);
    console.log(`Body: ${res2.body}`);
}
