// Test data below is sourced from banking_application_extracted_data.md
// (real DB records extracted from the running application), NOT invented.
// Re-verify with a live SELECT before any run that matters, since the
// extraction came from screenshots and individual fields (esp. UUIDs)
// may contain OCR errors even though the shape/relationships are correct.

export const config = {
    // The Base URL of the API Gateway or Istio Ingress
    // Defaults to localhost:8088 (Istio Ingress Gateway port-forward)
    BASE_URL: __ENV.BASE_URL || 'http://localhost:8088',

    // --- Primary test identity: account_number 060014000003 / user_id 1 ---
    // Chosen because it's the busiest account in the dataset: it appears as
    // both sender and receiver across 8 of the 9 fund_transfer records, so
    // GET /accounts/balance, GET /accounts/{id}/transactions, and
    // GET /fund-transfers all return non-empty, realistic results for it.
    TEST_USER_ID: __ENV.TEST_USER_ID || '1',
    TEST_ACCOUNT_ID: __ENV.TEST_ACCOUNT_ID || '0600140000003',                 // API expects the 12-digit account number here
    TEST_ACCOUNT_NUMBER: __ENV.TEST_ACCOUNT_NUMBER || '0600140000003', // account.account_number (query param used by /accounts, /accounts/balance)

    // A real completed internal-transfer reference (paired debit/credit
    // transaction rows share this reference_id) — use for GET /transactions/{referenceId}
    // and GET /fund-transfers/{referenceId}.
    TEST_REFERENCE_ID: __ENV.TEST_REFERENCE_ID || '40f50462-2db7-4451-b815-126a4e0996cf',

    // A second account with paired traffic, useful for a "two distinct
    // accounts" scenario (e.g. transfer history involving two parties).
    SECONDARY_ACCOUNT_NUMBER: __ENV.SECONDARY_ACCOUNT_NUMBER || '0600140000004',

    // A PENDING (not yet ACTIVE) account — deliberately NOT the default,
    // use this only when a test needs to exercise the "account not
    // active" / non-happy-path response.
    PENDING_ACCOUNT_NUMBER: __ENV.PENDING_ACCOUNT_NUMBER || '0600140000007',

    // Optional Keycloak Token if the API enforces authentication
    // Passed via k6 run --env K6_TOKEN="ey..."
    TOKEN: __ENV.K6_TOKEN || null
};

export function getHeaders() {
    let headers = {
        'Content-Type': 'application/json',
        'Accept': 'application/json'
    };
    if (config.TOKEN) {
        headers['Authorization'] = `Bearer ${config.TOKEN}`;
    }
    return headers;
}
