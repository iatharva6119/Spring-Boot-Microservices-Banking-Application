import { sleep } from 'k6';
import safeWorkflows from './scenarios/safe-workflows.js';

export let options = {
    // Spike test to observe autoscaling and circuit breaker behaviors
    stages: [
        { duration: '10s', target: 5 },   // Baseline
        { duration: '10s', target: 100 }, // Sudden Spike
        { duration: '20s', target: 100 }, // Sustain Spike
        { duration: '10s', target: 5 },   // Sudden Drop
        { duration: '20s', target: 5 },   // Recovery
    ],
    thresholds: {
        http_req_duration: ['p(95)<3000'],
    },
};

export default function () {
    safeWorkflows();
    sleep(1);
}
