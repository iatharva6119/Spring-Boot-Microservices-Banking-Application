import { sleep } from 'k6';
import safeWorkflows from './scenarios/safe-workflows.js';

export let options = {
    // Stress test to find limits. Capped at 100 to avoid crashing Docker Desktop.
    stages: [
        { duration: '30s', target: 20 },
        { duration: '30s', target: 50 },
        { duration: '30s', target: 100 },
        { duration: '1m', target: 100 },
        { duration: '30s', target: 0 },
    ],
    thresholds: {
        http_req_duration: ['p(95)<3000'], // P95 < 3s under stress
        http_req_failed: ['rate<0.10'],    // < 10% errors under stress
    },
};

export default function () {
    safeWorkflows();
    sleep(1);
}
