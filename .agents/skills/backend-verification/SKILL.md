---
name: backend-verification
description: migrated specialist procedure for backend-verification
---

# Backend Verification

## Role

Prove backend behavior directly before consumer or frontend integration. Use this skill as the backend verification owner; use `docs/runtime-adapters.md` only when an external capability is required for contract, MCP, browser, or cross-boundary routing.

## Method

1. Define changed claims: entry boundary, business result, important failures, final state or side effects, rollback or idempotency, dependencies, contract, traceability, and performance only when claimed.
2. Exercise backend through nearest real boundary: HTTP handler, service API, command, worker input, queue message, scheduled entrypoint, or webhook receiver.
3. Prove success and important failure behavior. Validate trust-boundary inputs and authorization where applicable.
4. Assert durable state and side effects. Include rollback, retry, duplicate delivery, idempotency, or partial-failure behavior when material.
5. Run contract proof when a canonical contract governs changed behavior, using repository-supported contract checks. When the exercised boundary is HTTP/API, a machine-readable schema exists, material API behavior changed, and generated schema/property checks add meaningful coverage, resolve `schema-driven API evidence` through `docs/runtime-adapters.md`. Treat it as supplemental evidence; it does not prove durable state, side effects, authorization, dependency semantics, rollback, retries, duplicate handling, idempotency, or representative-operation traceability.
6. Run real-dependency proof when database, queue, cache, filesystem, external service, or infrastructure semantics are material. Avoid mocks that erase behavior under test.
7. Reconstruct one representative operation using existing logs, correlation or trace IDs, job/message IDs, dependency records, or test instrumentation when traceability is material.
8. Run fresh focused automated checks and record exact command, exit status, failures, skips, and relevant evidence.
9. Hand failures to `systematic-debugging`, implementation loops to `test-driven-development`, consumer integration to `full-stack-integration`, and final claims to `verification-before-completion`.

## Evidence Output

- direct boundary exercised
- success and important failures proven
- final state and side effects asserted
- rollback/idempotency disposition
- contract and real-dependency disposition
- contract evidence, when applicable:
  - canonical schema/reference
  - exercised endpoint or operation scope
  - invocation/provider and result status
  - durable artifact path when one exists
  - known coverage limits
- representative-operation trace mechanism and result when applicable
- fresh automated command and result
- remaining blocker or `none`

Frontend, browser, client, mock, and MCP output may support evidence but never replace direct backend proof.
