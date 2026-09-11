import { sleep } from 'k6';
import safeWorkflows from './scenarios/safe-workflows.js';

export let options = {
    // Normal expected load.
    stages: [
        { duration: '30s', target: 20 },  // Ramp up to 20 users
        { duration: '1m', target: 20 },   // Sustain 20 users for 1 min
        { duration: '30s', target: 0 },   // Ramp down to 0 users
    ],
    thresholds: {
        http_req_duration: ['p(95)<2000'], // 95% of requests must complete below 2.0s
        http_req_failed: ['rate<0.05'],
    },
};

export default function () {
    safeWorkflows();
    sleep(1);
}
