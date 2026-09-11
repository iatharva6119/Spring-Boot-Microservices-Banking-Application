import { sleep } from 'k6';
import safeWorkflows from './scenarios/safe-workflows.js';

export let options = {
    // A baseline test should run with low VUs to measure optimal conditions.
    vus: 5,
    duration: '30s',
    thresholds: {
        http_req_duration: ['p(95)<1000'], // 95% of requests must complete below 1.0s
        http_req_failed: ['rate<0.05'],    // <5% errors
    },
};

export default function () {
    safeWorkflows();
    sleep(1);
}
